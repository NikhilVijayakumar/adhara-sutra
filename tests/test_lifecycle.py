"""Executable lifecycle tests for runtime, services, jobs, and connectors (NFR-TEST-004)."""

import asyncio
import logging
import sys
import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, ConnectorError, ExternalCommand, SQLiteDatabase


def setUpModule():
    logging.disable(logging.CRITICAL)


def tearDownModule():
    logging.disable(logging.NOTSET)


def application(label, **options):
    return Application(f"{label}_{uuid4().hex}", "1.0", **options)


class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_application_and_service_lifecycle(self):
        events = []

        class Service:
            def __enter__(self):
                events.append("enter")
                return {"value": 1}

            def __exit__(self, *exc):
                events.append("exit")
                return False

        app = application("lifecycle")
        app.service("service", lambda context: Service())
        await app.start()
        self.assertEqual(app.state, "ready")
        self.assertEqual(app.context.services["service"], {"value": 1})
        await app.stop()
        self.assertEqual(app.state, "stopped")
        self.assertEqual(events, ["enter", "exit"])
        await app.stop()
        self.assertEqual(events, ["enter", "exit"])

    async def test_job_lifecycle_succeeds_fails_and_cancels(self):
        app = application("jobs")

        @app.job("ok")
        async def ok(payload, context):
            return {"done": True}

        @app.job("fail")
        async def fail(payload, context):
            raise ValueError("boom")

        @app.job("long")
        async def long(payload, context):
            await asyncio.sleep(30)

        await app.start()
        try:
            ok_id = app.context.jobs.submit("ok")
            ok_status = await app.context.jobs.wait(ok_id)
            self.assertEqual(ok_status["state"], "succeeded")
            self.assertEqual(ok_status["result"], {"done": True})

            fail_id = app.context.jobs.submit("fail")
            fail_status = await app.context.jobs.wait(fail_id)
            self.assertEqual(fail_status["state"], "failed")
            self.assertEqual(fail_status["error"]["code"], "JOB_FAILED")

            long_id = app.context.jobs.submit("long")
            await asyncio.sleep(0.01)
            self.assertTrue(app.context.jobs.cancel(long_id))
            self.assertEqual((await app.context.jobs.wait(long_id))["state"], "cancelled")
            self.assertFalse(app.context.jobs.cancel(long_id))
        finally:
            await app.stop()

    async def test_connector_lifecycle_owns_its_connection(self):
        app = application("sqlite")
        app.service("db", lambda context: SQLiteDatabase(":memory:"))
        await app.start()
        try:
            db = app.context.get_service("db")
            db.execute("CREATE TABLE items (id INTEGER)")
            db.execute("INSERT INTO items VALUES (1)")
            self.assertEqual(db.query("SELECT id FROM items"), [{"id": 1}])
            self.assertTrue(db.health())
        finally:
            await app.stop()
        with self.assertRaises(ConnectorError):
            db.query("SELECT 1")

    async def test_external_process_lifecycle_reports_unknown_timeouts(self):
        command = ExternalCommand(sys.executable)
        with command:
            result = await command.run(["-c", "print('ok')"])
            self.assertTrue(result.ok)
            self.assertEqual(result.stdout_text.strip(), "ok")
            with self.assertRaises(ConnectorError) as caught:
                await command.run(["-c", "import time; time.sleep(5)"], timeout=0.1)
        self.assertEqual(caught.exception.details["outcome"], "unknown")

    async def test_startup_failure_cleans_up_initialized_resources(self):
        closed = []

        class Resource:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                closed.append(True)

        def failing(context):
            raise RuntimeError("startup failed")

        app = application("partial")
        app.service("first", lambda context: Resource())
        app.service("second", failing, depends_on=("first",))
        with self.assertRaises(RuntimeError):
            await app.start()
        self.assertEqual(closed, [True])
        self.assertEqual(app.state, "failed")
        self.assertEqual(app.context.services, {})

    async def test_shutdown_honors_the_configured_timeout(self):
        class Slow:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                await asyncio.sleep(5)

        app = application("slow", shutdown_timeout=0.01)
        app.service("slow", lambda context: Slow())
        await app.start()
        with self.assertRaises(TimeoutError):
            await app.stop()
        self.assertEqual(app.state, "failed")

    async def test_shutdown_cancels_jobs_and_terminates_subprocesses(self):
        app = application("shutdown")

        @app.job("long")
        async def long(payload, context):
            await asyncio.sleep(30)

        app.service("command", lambda context: ExternalCommand(sys.executable))
        await app.start()
        job_id = app.context.jobs.submit("long")
        await asyncio.sleep(0.01)
        command = app.context.get_service("command")
        running = asyncio.create_task(command.run(["-c", "import time; time.sleep(30)"]))
        await asyncio.sleep(0.1)
        await app.stop()
        self.assertEqual(app.context.jobs.status(job_id)["state"], "cancelled")
        result = await asyncio.wait_for(running, 5)
        self.assertNotEqual(result.exit_code, 0)
        await app.stop()
        self.assertEqual(app.context.jobs.status(job_id)["state"], "cancelled")

    async def test_shutdown_failure_is_reported_and_retry_is_harmless(self):
        class Broken:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                raise RuntimeError("cleanup failed")

        app = application("broken")
        app.service("broken", lambda context: Broken())
        await app.start()
        with self.assertRaises(RuntimeError):
            await app.stop()
        self.assertEqual(app.state, "failed")
        await app.stop()
        self.assertEqual(app.state, "failed")
