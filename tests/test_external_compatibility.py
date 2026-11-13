"""External tools keep their own conventions without changing the protocol (FR-EXT-009)."""

import sys
import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, ApplicationTestClient, ConnectorError, ExternalCommand


class ExternalCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_exit_status_and_output_are_preserved(self):
        with ExternalCommand(sys.executable) as command:
            result = await command.run(
                ["-c", "import sys; print('--format=other'); print('warn', file=sys.stderr); sys.exit(42)"])
        self.assertEqual(result.exit_code, 42)
        self.assertFalse(result.ok)
        self.assertEqual(result.stdout_text.strip(), "--format=other")
        self.assertEqual(result.stderr_text.strip(), "warn")
        with self.assertRaises(ConnectorError) as raised:
            result.raise_for_status()
        self.assertFalse(raised.exception.retryable)
        self.assertEqual(raised.exception.details, {"connector": "external", "exit_code": 42})

    async def test_connector_failure_keeps_the_protocol_envelope(self):
        app = Application(f"external_compat_{uuid4().hex}", "1.0")
        app.service("command", lambda context: ExternalCommand(sys.executable))

        @app.action("strict")
        async def strict(payload, context):
            result = await context.get_service("command").run(["-c", "import sys; sys.exit(7)"])
            return result.raise_for_status().stdout_text

        async with ApplicationTestClient(app) as client:
            response = await client.dispatch("strict")
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "CONNECTOR_FAILURE")
        self.assertEqual(response["error"]["category"], "connector")
        self.assertEqual(response["error"]["details"]["exit_code"], 7)
        self.assertEqual(response["error"]["details"]["connector"], "external")


if __name__ == "__main__":
    unittest.main()
