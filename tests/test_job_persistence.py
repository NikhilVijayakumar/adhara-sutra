"""Durable job metadata and recovery (FR-JOB-009, FR-JOB-011)."""

import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import Application, SQLiteDatabase, SQLiteJobStore


class JobPersistenceTests(unittest.IsolatedAsyncioTestCase):
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
