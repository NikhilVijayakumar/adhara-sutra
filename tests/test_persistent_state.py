import gc
import io
import json
import shutil
import tempfile
import unittest
import weakref
from contextlib import nullcontext
from pathlib import Path
from uuid import uuid4

from nikhi.adhara_sutra import (Application, ApplicationTestClient, ConnectorError, SQLiteDatabase,
                                SQLiteState)


class BackupAndRecoveryTests(unittest.TestCase):
    def test_backup_is_consistent_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.sqlite"
            backup = Path(directory) / "backup.sqlite"
            with SQLiteDatabase(str(path)) as db:
                db.execute("CREATE TABLE items (name TEXT NOT NULL)")
                db.execute("INSERT INTO items VALUES ('one')")
                self.assertEqual(db.integrity_check(), ["ok"])
                db.backup(backup)
                self.assertTrue(backup.is_file())
                with self.assertRaises(ConnectorError):
                    db.backup(backup)
            with SQLiteDatabase(str(backup)) as db:
                self.assertEqual(db.query("SELECT name FROM items"), [{"name": "one"}])
                self.assertEqual(db.integrity_check(), ["ok"])

    def test_backup_is_rejected_inside_a_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "backup.sqlite"
            with SQLiteDatabase() as db:
                with db.transaction(), self.assertRaises(ConnectorError):
                    db.backup(destination)
            self.assertFalse(destination.exists())

    def test_integrity_check_detects_damage_and_verified_backup_recovers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.sqlite"
            backup = Path(directory) / "backup.sqlite"
            with SQLiteDatabase(str(path)) as db:
                db.execute("CREATE TABLE items (name TEXT NOT NULL)")
                db.execute("INSERT INTO items VALUES ('one')")
                db.backup(backup)
            path.write_bytes(b"not a database")
            with self.assertRaises(ConnectorError):
                with SQLiteDatabase(str(path)) as db:
                    db.integrity_check()
            shutil.copyfile(backup, path)
            with SQLiteDatabase(str(path)) as db:
                self.assertEqual(db.integrity_check(), ["ok"])
                self.assertEqual(db.query("SELECT name FROM items"), [{"name": "one"}])


class SQLiteStateTests(unittest.TestCase):
    def test_values_persist_across_restarts_and_are_isolated_by_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.sqlite"
            with SQLiteDatabase(str(path)) as db:
                state = SQLiteState(db, "settings")
                state["items"] = [1, {"name": "one"}]
                state["count"] = 2
                self.assertEqual(len(state), 2)
                self.assertEqual(sorted(state), ["count", "items"])
                self.assertNotIn("items", SQLiteState(db, "other"))
                with self.assertRaises(KeyError):
                    state["missing"]
                with self.assertRaises(TypeError):
                    state[1] = "bad key"
                with self.assertRaises(ValueError):
                    state["count"] = float("nan")
                with self.assertRaises(ValueError):
                    SQLiteState(db, "")
            with SQLiteDatabase(str(path)) as db:
                restored = SQLiteState(db, "settings")
                self.assertEqual(restored["items"], [1, {"name": "one"}])
                snapshot = restored["items"]
                snapshot.append(2)
                self.assertEqual(restored["items"], [1, {"name": "one"}])
                del restored["count"]
                with self.assertRaises(KeyError):
                    del restored["count"]


class PersistentStateApplicationTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def create_app(path):
        app = Application("persistent_" + uuid4().hex, "1.0")
        app.service("db", lambda context: SQLiteDatabase(path))
        app.service("persisted", lambda context: nullcontext(SQLiteState(context.get_service("db"), "app")),
                    depends_on=("db",))

        @app.action("state.set")
        def set_state(payload, context):
            context.get_service("persisted")[payload["key"]] = payload["value"]
            return {}

        @app.action("state.get")
        def get_state(payload, context):
            return {"value": context.get_service("persisted")[payload["key"]]}
        return app

    async def test_configured_state_is_restored_on_the_next_start(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "state.sqlite")
            async with ApplicationTestClient(self.create_app(path)) as client:
                await client.call("state.set", {"key": "theme", "value": "dark"})
                self.assertEqual(await client.call("state.get", {"key": "theme"}), {"value": "dark"})
            async with ApplicationTestClient(self.create_app(path)) as client:
                self.assertEqual(await client.call("state.get", {"key": "theme"}), {"value": "dark"})


class SessionCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_session_state_is_shared_then_released_and_request_state_is_fresh(self):
        app = Application(f"cleanup_{uuid4().hex}", "1.0")
        references = {}

        class Marker:
            pass

        @app.action("session.remember")
        def remember(payload, context):
            marker = Marker()
            references["weak"] = weakref.ref(marker)
            references["strong"] = marker
            context.session_state["marker"] = marker
            return {"session": sorted(context.session_state)}

        @app.action("session.keys")
        def keys(payload, context):
            return {"session": sorted(context.session_state)}

        @app.action("request.keys")
        def request_keys(payload, context):
            seen = sorted(context.request_state)
            context.request_state["seen"] = True
            return {"request": seen}

        def envelope(action, request_id):
            return {"kind": "request", "protocol_version": "1.0", "request_id": request_id,
                    "action": action, "payload": {}}

        lines = [envelope("system.hello", "req-1"),
                 envelope("session.remember", "req-2"),
                 envelope("session.keys", "req-3"),
                 envelope("request.keys", "req-4"),
                 envelope("request.keys", "req-5")]
        stdin = io.StringIO("".join(json.dumps(line) + "\n" for line in lines))
        stdout = io.StringIO()
        self.assertEqual(await app.serve(persistent=True, stdin=stdin, stdout=stdout), 0)
        responses = {response["request_id"]: response
                     for response in (json.loads(line) for line in stdout.getvalue().splitlines())}
        self.assertEqual(responses["req-2"]["data"]["session"], ["marker"])
        self.assertEqual(responses["req-3"]["data"]["session"], ["marker"])
        self.assertEqual(responses["req-4"]["data"]["request"], [])
        self.assertEqual(responses["req-5"]["data"]["request"], [])
        del references["strong"]
        gc.collect()
        self.assertIsNone(references["weak"]())

