"""Process exit-code semantics for the CLI protocol (FR-CLI-007)."""

import io
import json
import logging
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

from nikhi.adhara_sutra import Application, ConnectorError, ExternalCommand, PROTOCOL_VERSION


def setUpModule():
    logging.disable(logging.CRITICAL)


def tearDownModule():
    logging.disable(logging.NOTSET)


def application(label, **options):
    return Application(f"exit_{label}_{uuid4().hex}", "1.0", **options)


def envelope(action, payload=None, version=PROTOCOL_VERSION, request_id="req-1"):
    return {"kind": "request", "protocol_version": version, "request_id": request_id,
            "action": action, "payload": payload or {}}


async def invoke(app, request=None, *, persistent=False):
    stdin = io.StringIO("" if request is None else json.dumps(request) + "\n")
    stdout = io.StringIO()
    code = await app.serve(persistent=persistent, stdin=stdin, stdout=stdout)
    return code, [json.loads(line) for line in stdout.getvalue().splitlines()]


class ExitCodeTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_and_missing_request(self):
        app = application("success")

        @app.action("echo")
        def echo(payload, context):
            return payload
        code, responses = await invoke(app, envelope("echo", {"value": 1}))
        self.assertEqual(code, 0)
        self.assertTrue(responses[-1]["success"])
        code, responses = await invoke(application("empty"), None)
        self.assertEqual(code, 2)
        self.assertEqual(responses, [])

    async def test_input_protocol_and_action_failures(self):
        app = application("failures")

        @app.action("fail")
        def fail(payload, context):
            raise ValueError("boom")
        code, responses = await invoke(app, envelope("fail"))
        self.assertEqual(code, 4)
        self.assertEqual(responses[-1]["error"]["code"], "RUNTIME_EXECUTION_FAILED")
        code, _ = await invoke(application("unknown"), envelope("missing"))
        self.assertEqual(code, 4)
        code, responses = await invoke(application("version"), envelope("system.hello", version="9.9"))
        self.assertEqual(code, 8)
        self.assertEqual(responses[-1]["error"]["code"], "PROTOCOL_UNSUPPORTED_VERSION")
        stdin, stdout = io.StringIO("{not json\n"), io.StringIO()
        app = application("json")
        self.assertEqual(await app.serve(stdin=stdin, stdout=stdout), 8)

    async def test_startup_failure_reports_initialization_code(self):
        app = application("startup")

        def broken(context):
            raise RuntimeError("cannot start")
        app.service("broken", broken)
        code, _ = await invoke(app, envelope("system.hello"))
        self.assertEqual(code, 3)
        self.assertEqual(app.state, "failed")

    async def test_connector_failure_and_timeout_use_distinct_codes(self):
        def connector_app(label, error):
            app = application(label)

            @app.action("run")
            def run(payload, context):
                raise error
            return app
        code, responses = await invoke(connector_app("offline", ConnectorError("offline", retryable=False)),
                                       envelope("run"))
        self.assertEqual(code, 7)
        self.assertEqual(responses[-1]["error"]["code"], "CONNECTOR_FAILURE")
        code, responses = await invoke(connector_app("timeout", ConnectorError(
            "timed out", retryable=True, code="CONNECTOR_TIMEOUT", details={"outcome": "unknown"})),
            envelope("run"))
        self.assertEqual(code, 5)
        error = responses[-1]["error"]
        self.assertEqual(error["code"], "CONNECTOR_TIMEOUT")
        self.assertEqual(error["category"], "connector")
        self.assertTrue(error["retryable"])

    async def test_external_command_timeout_exits_five(self):
        app = application("external")
        app.service("command", lambda context: ExternalCommand(sys.executable))

        @app.action("slow")
        async def slow(payload, context):
            return await context.get_service("command").run(
                ["-c", "import time; time.sleep(5)"], timeout=0.1)
        code, responses = await invoke(app, envelope("slow"))
        self.assertEqual(code, 5)
        error = responses[-1]["error"]
        self.assertEqual(error["code"], "CONNECTOR_TIMEOUT")
        self.assertEqual(error["details"]["outcome"], "unknown")

    async def test_persistent_session_survives_action_failures(self):
        app = application("persistent")

        @app.action("fail")
        def fail(payload, context):
            raise ValueError("boom")
        hello = envelope("system.hello")
        stdin = io.StringIO(json.dumps(hello) + "\n" + json.dumps(envelope("fail", request_id="req-2")) + "\n")
        stdout = io.StringIO()
        code = await app.serve(persistent=True, stdin=stdin, stdout=stdout)
        self.assertEqual(code, 0)
        responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
        self.assertTrue(responses[0]["success"])
        self.assertFalse(responses[1]["success"])

class RunTests(unittest.TestCase):
    def test_interrupt_reports_cancellation(self):
        async def interrupted(*args, **kwargs):
            raise KeyboardInterrupt
        with patch.object(Application, "serve", interrupted):
            self.assertEqual(application("interrupt").run(), 6)

    def test_unexpected_runtime_failure_reports_internal_code(self):
        async def broken(*args, **kwargs):
            raise RuntimeError("boom")
        with patch.object(Application, "serve", broken):
            self.assertEqual(application("broken").run(), 10)


if __name__ == "__main__":
    unittest.main()
