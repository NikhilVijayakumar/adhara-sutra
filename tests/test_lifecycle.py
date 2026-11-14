"""Executable lifecycle tests for runtime, services, jobs, and connectors (NFR-TEST-004)."""

import asyncio
import logging
import sys
import unittest
import warnings
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from nikhi.adhara_sutra import Application, ConnectorError, ExternalCommand, SQLiteDatabase, PROTOCOL_VERSION


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

    async def test_sync_job_registration_warns_but_preserves_callable_behavior(self):
        app = application("job_warning")
        calls = []
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            @app.job("async")
            async def async_job(payload, context):
                return "async"
            self.assertEqual(caught, [])

            @app.job("sync")
            def sync_job(payload, context):
                calls.append("sync")
                return "sync"

            @app.job("awaitable")
            def awaitable_job(payload, context):
                calls.append("awaitable")
                async def result():
                    return "awaitable"
                return result()
        self.assertEqual(calls, [])
        self.assertEqual(len(caught), 2)
        for warning in caught:
            self.assertIs(warning.category, DeprecationWarning)
            self.assertIn("inline", str(warning.message))
            self.assertIn("timeout", str(warning.message))
            self.assertEqual(warning.filename, __file__)
        await app.start()
        try:
            for name in ("async", "sync", "awaitable"):
                job_id = app.context.jobs.submit(name)
                status = await app.context.jobs.wait(job_id)
                self.assertEqual((status["state"], status["result"]), ("succeeded", name))
            self.assertEqual(calls, ["sync", "awaitable"])
        finally:
            await app.stop()

    async def test_async_job_allows_health_and_cooperative_cancellation(self):
        app = application("cooperative_job")
        started, cancelled = asyncio.Event(), asyncio.Event()
        @app.job("wait")
        async def wait(payload, context):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        await app.start()
        try:
            job_id = app.context.jobs.submit("wait")
            await started.wait()
            def request(action, payload):
                return {"kind": "request", "protocol_version": PROTOCOL_VERSION,
                        "request_id": "test", "action": action, "payload": payload}
            health = await app.dispatch(request("system.health", {}))
            self.assertTrue(health["success"])
            response = await app.dispatch(request("system.cancel", {"job_id": job_id}))
            self.assertTrue(response["data"]["cancelled"])
            await cancelled.wait()
            self.assertEqual((await app.context.jobs.wait(job_id))["state"], "cancelled")
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

    async def test_job_shutdown_failure_still_cleans_resources(self):
        closed = []
        class Resource:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                closed.append(True)
        app = application("job_shutdown_failure")
        app.service("resource", lambda context: Resource())
        await app.start()
        async def fail():
            raise ValueError("job shutdown failed")
        with patch.object(app._jobs, "shutdown", fail):
            with self.assertRaisesRegex(ValueError, "job shutdown failed"):
                await app.stop()
        self.assertEqual(closed, [True])
        self.assertEqual(app.context.services, {})
        self.assertEqual(app.state, "failed")
        await app.stop()

    async def test_job_timeout_reserves_cleanup_budget(self):
        closed = []
        class Resource:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                closed.append(True)
        app = application("job_timeout", shutdown_timeout=0.1)
        app.service("resource", lambda context: Resource())
        await app.start()
        async def wait_forever():
            await asyncio.Event().wait()
        with patch.object(app._jobs, "shutdown", wait_forever):
            with self.assertRaises(TimeoutError):
                await app.stop()
        self.assertEqual(closed, [True])
        self.assertEqual(app.state, "failed")

    async def test_both_shutdown_errors_are_retained(self):
        class Broken:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                raise ValueError("resource failed")
        app = application("both_fail")
        app.service("resource", lambda context: Broken())
        await app.start()
        async def fail():
            raise RuntimeError("jobs failed")
        with patch.object(app._jobs, "shutdown", fail):
            with self.assertRaises(ExceptionGroup) as caught:
                await app.stop()
        self.assertEqual([str(e) for e in caught.exception.exceptions], ["jobs failed", "resource failed"])
        self.assertEqual(app.state, "failed")
        self.assertEqual(app.context.services, {})

    async def test_cancelled_stop_attempts_resource_cleanup_and_propagates(self):
        entered, closed = asyncio.Event(), []
        class Resource:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                closed.append(True)
        app = application("cancel_stop")
        app.service("resource", lambda context: Resource())
        await app.start()
        async def wait_forever():
            entered.set()
            await asyncio.Event().wait()
        with patch.object(app._jobs, "shutdown", wait_forever):
            stopping = asyncio.create_task(app.stop())
            await entered.wait()
            stopping.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await stopping
        self.assertEqual(closed, [True])
        self.assertEqual(app.state, "failed")
        self.assertEqual(app.context.services, {})

    async def test_captured_facade_rejects_admission_when_shutdown_begins(self):
        entered, cancelled, release = asyncio.Event(), asyncio.Event(), asyncio.Event()
        app = application("admission_closed")
        @app.job("work")
        async def work(payload, context):
            entered.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await release.wait()
                raise
        await app.start()
        facade = app.context.jobs
        job_id = facade.submit("work")
        await entered.wait()
        stopping = asyncio.create_task(app.stop())
        await cancelled.wait()
        with self.assertRaisesRegex(RuntimeError, "Job manager is shutting down"):
            facade.submit("work")
        self.assertEqual(len(facade.list()), 1)
        release.set()
        await stopping
        self.assertEqual(facade.status(job_id)["state"], "cancelled")

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

    @unittest.skipUnless(sys.platform == "win32", "Windows taskkill behavior")
    async def test_failed_taskkill_falls_back_to_owned_process(self):
        command = ExternalCommand(sys.executable)
        process = MagicMock(pid=123, returncode=None)
        process.wait = AsyncMock(return_value=1)
        killer = MagicMock()
        killer.wait = AsyncMock(return_value=1)
        with patch("nikhi.adhara_sutra.external.asyncio.create_subprocess_exec", new=AsyncMock(return_value=killer)):
            await command._terminate(process)
        process.kill.assert_called_once_with()
        process.reset_mock()
        with patch("nikhi.adhara_sutra.external.subprocess.run") as run:
            run.return_value.returncode = 1
            command._kill_sync(process)
        process.kill.assert_called_once_with()
        process.reset_mock()
        with patch("nikhi.adhara_sutra.external.subprocess.run", side_effect=OSError("taskkill unavailable")):
            command._kill_sync(process)
        process.kill.assert_called_once_with()
        process.reset_mock()
        with patch("nikhi.adhara_sutra.external.subprocess.run") as run:
            run.return_value.returncode = 0
            command._kill_sync(process)
        process.kill.assert_not_called()

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
