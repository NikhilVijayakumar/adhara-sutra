"""Durable job metadata and recovery (FR-JOB-009, FR-JOB-011)."""

import asyncio
import tempfile
from unittest.mock import patch
import unittest
from pathlib import Path

from nikhi.adhara_sutra import Application, SQLiteDatabase, SQLiteJobStore
from nikhi.adhara_sutra.application import BootstrapError
from nikhi.adhara_sutra.jobs import JobManager


class JobPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_initial_save_does_not_consume_capacity(self):
        class FailOnceStore:
            def __init__(self):
                self.records = {}
                self.fail = True

            def save(self, record):
                if self.fail:
                    self.fail = False
                    raise RuntimeError("store unavailable")
                self.records[record["job_id"]] = dict(record)

            def load_all(self):
                return list(self.records.values())

        calls = []
        async def handler(payload, context):
            calls.append(payload)
            return payload

        store = FailOnceStore()
        manager = JobManager({"work": (handler, None)}, lambda *args: object(), max_queued=1, store=store)
        with self.assertRaisesRegex(RuntimeError, "store unavailable"):
            manager.submit("work", "first", None, {})
        self.assertEqual(manager.list(), [])
        self.assertEqual(manager._tasks, set())
        await asyncio.sleep(0)
        self.assertEqual(calls, [])
        job_id = manager.submit("work", "second", None, {})
        self.assertEqual((await manager.wait(job_id))["state"], "succeeded")
        self.assertEqual(calls, ["second"])
        await manager.shutdown()

    async def test_context_failure_does_not_publish_or_persist(self):
        class Store:
            def save(self, record):
                self.fail("store should not be reached")
        def context(*args):
            raise RuntimeError("context failed")
        manager = JobManager({"work": (lambda p, c: None, None)}, context, store=Store())
        with self.assertRaisesRegex(RuntimeError, "context failed"):
            manager.submit("work", None, None, {})
        self.assertEqual(manager.list(), [])
        self.assertEqual(manager._tasks, set())

    async def test_task_creation_failure_closes_coroutine_and_records_failure(self):
        class Store:
            def __init__(self):
                self.records = []
            def save(self, record):
                self.records.append(dict(record))
            def load_all(self):
                return self.records[-1:]
        store = Store()
        manager = JobManager({"work": (lambda p, c: None, None)}, lambda *args: object(), store=store)
        captured = []
        def reject(coroutine):
            captured.append(coroutine)
            raise RuntimeError("task rejected")
        with patch("nikhi.adhara_sutra.jobs.asyncio.create_task", side_effect=reject):
            with self.assertRaisesRegex(RuntimeError, "task rejected"):
                manager.submit("work", None, None, {})
        self.assertIsNone(captured[0].cr_frame)
        self.assertEqual(manager.list(), [])
        self.assertEqual(manager._tasks, set())
        self.assertEqual([r["state"] for r in store.records], ["queued", "failed"])
        self.assertEqual(store.records[-1]["error"]["code"], "JOB_ADMISSION_FAILED")

    async def test_failed_admission_save_can_recover_queued_snapshot(self):
        class Store:
            def __init__(self):
                self.records = []
                self.fail_terminal = True
            def save(self, record):
                if record["state"] == "failed" and self.fail_terminal:
                    raise RuntimeError("terminal save failed")
                self.records = [dict(record)]
            def load_all(self):
                return self.records
        store = Store()
        manager = JobManager({"work": (lambda p, c: None, None)}, lambda *args: object(), store=store)
        with patch("nikhi.adhara_sutra.jobs.asyncio.create_task", side_effect=RuntimeError("task rejected")):
            with self.assertLogs("nikhi.adhara_sutra.jobs", level="ERROR"):
                with self.assertRaisesRegex(RuntimeError, "task rejected"):
                    manager.submit("work", None, None, {})
        self.assertEqual(store.records[0]["state"], "queued")
        self.assertEqual(manager.list(), [])
        recovered = JobManager({}, lambda *args: object(), store=store, recover_on_start=True)
        self.assertEqual(recovered.list()[0]["state"], "interrupted")
        self.assertEqual(store.records[0]["error"]["code"], "JOB_INTERRUPTED")

    async def test_invalid_results_fail_with_and_without_sqlite(self):
        for use_store in (False, True):
            with self.subTest(store=use_store), tempfile.TemporaryDirectory() as directory:
                app = Application(f"invalid_results_{use_store}", "1", job_store="store" if use_store else None)
                if use_store:
                    app.service("db", lambda c: SQLiteDatabase(str(Path(directory) / "jobs.db")))
                    app.service("store", lambda c: SQLiteJobStore(c.get_service("db")), depends_on=("db",))
                @app.job("bad")
                async def bad(payload, context):
                    return {"object": object(), "bytes": b"bad", "nan": float("nan")}[payload]
                await app.start()
                try:
                    for value in ("object", "bytes", "nan"):
                        job_id = app.context.jobs.submit("bad", value)
                        status = await app.context.jobs.wait(job_id)
                        self.assertEqual(status["state"], "failed")
                        self.assertIsNone(status["result"])
                        self.assertEqual(status["error"]["code"], "JOB_OUTPUT_INVALID")
                        self.assertEqual(status["persistence"]["status"], "saved" if use_store else "disabled")
                finally:
                    await app.stop()

    async def test_running_save_failure_prevents_handler_execution(self):
        class Store:
            def save(self, record):
                if record["state"] == "running":
                    raise OSError("running save failed")
            def load_all(self):
                return []
        calls = []
        async def handler(payload, context):
            calls.append(True)
        manager = JobManager({"work": (handler, None)}, lambda *args: object(), store=Store())
        with self.assertLogs("nikhi.adhara_sutra.jobs", level="ERROR"):
            job_id = manager.submit("work", None, None, {})
            status = await asyncio.wait_for(manager.wait(job_id), 1)
        self.assertEqual(calls, [])
        self.assertEqual(status["error"]["code"], "JOB_PERSISTENCE_FAILED")
        self.assertEqual(status["persistence"], {"status": "saved"})
        await manager.shutdown()

    async def test_terminal_save_failure_releases_waiters_and_keeps_local_outcome(self):
        class Store:
            def __init__(self):
                self.records = {}
                self.terminal_attempts = 0
            def save(self, record):
                if record["state"] in ("succeeded", "failed", "cancelled"):
                    self.terminal_attempts += 1
                    raise OSError("terminal save failed")
                self.records[record["job_id"]] = dict(record)
            def load_all(self):
                return list(self.records.values())
        store = Store()
        manager = JobManager({"work": (lambda p, c: {"ok": True}, None)}, lambda *args: object(), store=store)
        loop = asyncio.get_running_loop()
        problems = []
        previous = loop.get_exception_handler()
        loop.set_exception_handler(lambda loop, context: problems.append(context))
        try:
            with self.assertLogs("nikhi.adhara_sutra.jobs", level="ERROR"):
                job_id = manager.submit("work", None, None, {})
                status = await asyncio.wait_for(manager.wait(job_id), 1)
                await asyncio.sleep(0)
            self.assertEqual(status["state"], "succeeded")
            self.assertEqual(status["result"], {"ok": True})
            self.assertEqual(status["persistence"], {"status": "failed", "error_code": "JOB_PERSISTENCE_FAILED"})
            self.assertEqual(store.terminal_attempts, 1)
            self.assertEqual(store.records[job_id]["state"], "running")
            self.assertEqual(problems, [])
            recovered = JobManager({}, lambda *args: object(), store=store, recover_on_start=True)
            self.assertEqual(recovered.status(job_id)["state"], "interrupted")
        finally:
            loop.set_exception_handler(previous)
            await manager.shutdown()

    async def test_cancelled_queued_job_survives_terminal_save_failure(self):
        class Store:
            def __init__(self):
                self.attempts = 0
            def save(self, record):
                if record["state"] == "cancelled":
                    self.attempts += 1
                    raise OSError("save failed")
            def load_all(self):
                return []
        store = Store()
        manager = JobManager({"work": (lambda p, c: None, None)}, lambda *args: object(), store=store)
        loop = asyncio.get_running_loop()
        previous, problems = loop.get_exception_handler(), []
        loop.set_exception_handler(lambda loop, context: problems.append(context))
        try:
            with self.assertLogs("nikhi.adhara_sutra.jobs", level="ERROR"):
                job_id = manager.submit("work", None, None, {})
                self.assertTrue(manager.cancel(job_id))
                status = await asyncio.wait_for(manager.wait(job_id), 1)
                await asyncio.sleep(0)
            self.assertEqual(status["state"], "cancelled")
            self.assertEqual(status["persistence"]["status"], "failed")
            self.assertEqual(store.attempts, 1)
            self.assertEqual(problems, [])
        finally:
            loop.set_exception_handler(previous)
            await manager.shutdown()

    async def test_terminal_signal_occurs_once_for_completion_and_queued_cancellation(self):
        manager = JobManager({"work": (lambda p, c: "ok", None)}, lambda *args: object())
        for cancel in (False, True):
            job_id = manager.submit("work", None, None, {})
            event = manager._jobs[job_id]["event"]
            with patch.object(event, "set", wraps=event.set) as signal:
                if cancel:
                    self.assertTrue(manager.cancel(job_id))
                status = await asyncio.wait_for(manager.wait(job_id), 1)
                await asyncio.sleep(0)
                self.assertEqual(signal.call_count, 1)
                self.assertEqual(status["state"], "cancelled" if cancel else "succeeded")
                self.assertEqual(status["persistence"], {"status": "disabled"})
        await manager.shutdown()

    async def test_named_store_returning_none_fails(self):
        class EmptyStore:
            def __enter__(self):
                return None

            def __exit__(self, *args):
                pass

        app = Application("empty_store", "1", job_store="store")
        app.service("store", lambda context: EmptyStore())
        with self.assertRaises(BootstrapError) as caught:
            await app.start()
        self.assertEqual(caught.exception.code, "INVALID_JOB_STORE")

    async def test_invalid_explicit_store_fails_and_cleans_up(self):
        closed = []

        class Resource:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                closed.append(True)

        app = Application("invalid_store", "1", job_store="missing")
        app.service("resource", lambda context: Resource())
        with self.assertRaises(BootstrapError) as caught:
            await app.start()
        self.assertEqual(caught.exception.code, "INVALID_JOB_STORE")
        self.assertEqual(closed, [True])

    async def test_recovery_requires_a_store(self):
        app = Application("missing_recovery_store", "1", recover_jobs=True)
        with self.assertRaises(BootstrapError) as caught:
            await app.start()
        self.assertEqual(caught.exception.code, "INVALID_JOB_STORE")

    async def test_store_requires_save_and_load(self):
        app = Application("bad_store", "1", job_store=object())
        with self.assertRaises(BootstrapError) as caught:
            await app.start()
        self.assertEqual(caught.exception.code, "INVALID_JOB_STORE")

    async def test_terminal_jobs_persist_across_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "jobs.db"
            app = Application("jobs", "1.0", job_store="store", recover_jobs=True)
            app.service("db", lambda c: SQLiteDatabase(str(db_path)))
            app.service("store", lambda c: SQLiteJobStore(c.get_service("db")), depends_on=("db",))

            @app.job("ok")
            async def ok(payload, context):
                return {"done": True}

            await app.start()
            job_id = app.context.jobs.submit("ok")
            status = await app.context.jobs.wait(job_id)
            self.assertEqual(status["state"], "succeeded")
            await app.stop()

            app2 = Application("jobs2", "1.0", job_store="store", recover_jobs=True)

            @app2.job("ok")
            async def ok2(payload, context):
                return {"done": True}
            app2.service("db", lambda c: SQLiteDatabase(str(db_path)))
            app2.service("store", lambda c: SQLiteJobStore(c.get_service("db")), depends_on=("db",))
            await app2.start()
            try:
                restored = app2.context.jobs.status(job_id)
                self.assertIsNotNone(restored)
                self.assertEqual(restored["state"], "succeeded")
                self.assertEqual(restored["persistence"], {"status": "saved"})
                self.assertEqual(restored["result"], {"done": True})
                self.assertTrue(any(j["job_id"] == job_id for j in app2.context.jobs.list()))
            finally:
                await app2.stop()

    async def test_non_terminal_jobs_are_marked_interrupted_on_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "jobs.db"
            store_db = SQLiteDatabase(str(db_path))
            with store_db:
                store = SQLiteJobStore(store_db)
                # simulate a job left running by a crashed owner
                store.save({"job_id": "orphan", "name": "work", "state": "running",
                            "result": None, "error": None, "created_at": 1.0,
                            "started_at": 2.0, "finished_at": None})

            app = Application("recover", "1.0", job_store="store", recover_jobs=True)
            app.service("db", lambda c: SQLiteDatabase(str(db_path)))
            app.service("store", lambda c: SQLiteJobStore(c.get_service("db")), depends_on=("db",))
            await app.start()
            try:
                status = app.context.jobs.status("orphan")
                self.assertEqual(status["state"], "interrupted")
                self.assertEqual(status["error"]["code"], "JOB_INTERRUPTED")
                self.assertIsNotNone(status["finished_at"])
                self.assertFalse(app.context.jobs.cancel("orphan"))
            finally:
                await app.stop()

    async def test_recovery_failure_reports_resource_and_recovery_actions(self):
        class BrokenStore:
            def load_all(self):
                raise RuntimeError("database image is malformed")

            def save(self, record):
                raise AssertionError("save must not be reached")

        app = Application("broken_store", "1.0", job_store=BrokenStore(), recover_jobs=True)
        with self.assertRaises(BootstrapError) as caught:
            await app.start()
        self.assertEqual(caught.exception.code, "RECOVERY_FAILED")
        self.assertIn("job store", str(caught.exception))
        self.assertIn("backup", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, RuntimeError)
        self.assertEqual(app.state, "failed")

    async def test_no_store_preserves_default_behavior(self):
        app = Application("plain", "1.0")

        @app.job("ok")
        async def ok(payload, context):
            return 1

        await app.start()
        try:
            job_id = app.context.jobs.submit("ok")
            self.assertEqual((await app.context.jobs.wait(job_id))["state"], "succeeded")
        finally:
            await app.stop()


if __name__ == "__main__":
    unittest.main()
