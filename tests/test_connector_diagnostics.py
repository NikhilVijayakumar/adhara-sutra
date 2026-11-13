"""Connector failures expose identity and failure category (NFR-OBS-003)."""

import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from uuid import uuid4

from nikhi.adhara_sutra import (Application, ApplicationTestClient, ConnectorError,
                                ExternalCommand, HttpClient, SQLiteDatabase)


class ConnectorIdentityTests(unittest.IsolatedAsyncioTestCase):
    async def test_builtin_connector_errors_report_their_identity(self):
        app = Application(f"diagnostics_{uuid4().hex}", "1.0")
        app.service("client", lambda context: nullcontext(HttpClient()))

        @app.action("fetch")
        def fetch(payload, context):
            return context.get_service("client").get("https://example.invalid")
        async with ApplicationTestClient(app) as client:
            response = await client.dispatch("fetch")
        error = response["error"]
        self.assertEqual(error["category"], "connector")
        self.assertEqual(error["details"]["connector"], "http")
        self.assertFalse(error["retryable"])

    async def test_external_command_error_reports_its_identity(self):
        command = ExternalCommand("definitely-missing-executable")
        with self.assertRaises(ConnectorError) as raised:
            command.__enter__()
        self.assertEqual(raised.exception.details["connector"], "external")
        self.assertFalse(raised.exception.retryable)

    async def test_sqlite_error_reports_its_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing" / "db.sqlite"
            with self.assertRaises(ConnectorError) as raised:
                with SQLiteDatabase(str(path)):
                    pass
        self.assertEqual(raised.exception.details["connector"], "sqlite")

    async def test_application_connector_keeps_details_alongside_identity(self):
        app = Application(f"diagnostics_{uuid4().hex}", "1.0")

        @app.action("fail")
        def fail(payload, context):
            raise ConnectorError("billing offline", retryable=False,
                                 details={"outcome": "not_sent"}, connector="billing")
        async with ApplicationTestClient(app) as client:
            response = await client.dispatch("fail")
        self.assertEqual(response["error"]["details"],
                         {"connector": "billing", "outcome": "not_sent"})
        self.assertEqual(response["error"]["category"], "connector")


if __name__ == "__main__":
    unittest.main()
