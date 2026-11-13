"""Reusable helpers for testing applications without the CLI protocol."""

from __future__ import annotations

import unittest
from typing import Any
from uuid import uuid4

from .application import Application, PROTOCOL_VERSION


class ApplicationTestClient:
    """Start an application and dispatch requests directly, bypassing the protocol transport."""

    def __init__(self, app: Application) -> None:
        self.app = app
        self._started = False

    async def __aenter__(self) -> "ApplicationTestClient":
        if self.app.state == "created":
            self._started = True
            await self.app.start()
        elif self.app.state != "ready":
            raise RuntimeError(f"Application is not testable in state {self.app.state!r}")
        return self

    async def __aexit__(self, *exc: Any) -> bool:
        if self._started:
            await self.app.stop()
        return False

    async def dispatch(self, action: str, payload: dict[str, Any] | None = None, *,
                       request_id: str | None = None) -> dict[str, Any]:
        """Dispatch an action and return the full response envelope."""
        return await self.app.dispatch({"kind": "request", "protocol_version": PROTOCOL_VERSION,
                                        "request_id": request_id or uuid4().hex,
                                        "action": action, "payload": payload or {}})

    async def call(self, action: str, payload: dict[str, Any] | None = None, *,
                   request_id: str | None = None) -> Any:
        """Dispatch an action and return its data, raising AssertionError on failure."""
        response = await self.dispatch(action, payload, request_id=request_id)
        if not response["success"]:
            error = response["error"]
            raise AssertionError(f"{action} failed: {error['code']}: {error['message']}")
        return response["data"]


class CLIContractTests(unittest.IsolatedAsyncioTestCase):
    """Shipped executable tests for the unified CLI protocol.

    Subclass this case and return a fresh, unstarted application from
    ``create_application()``; each inherited test starts and stops its own
    instance.
    """

    def create_application(self) -> Application:
        raise NotImplementedError("create_application() must return a fresh Application")

    def setUp(self):
        if type(self).create_application is CLIContractTests.create_application:
            self.skipTest("CLIContractTests is abstract; implement create_application()")

    async def test_handshake_reports_versions_and_identity(self):
        app = self.create_application()
        async with ApplicationTestClient(app) as client:
            data = await client.call("system.hello")
        self.assertEqual(data["protocol_version"], PROTOCOL_VERSION)
        self.assertIn(PROTOCOL_VERSION, data["supported_protocol_versions"])
        self.assertEqual(data["name"], app.name)

    async def test_help_reports_action_metadata(self):
        async with ApplicationTestClient(self.create_application()) as client:
            data = await client.call("system.help")
        self.assertIsInstance(data["actions"], list)
        self.assertIsInstance(data["jobs"], list)
        for action in data["actions"]:
            self.assertIsInstance(action.get("name"), str)

    async def test_unknown_action_is_a_structured_error(self):
        async with ApplicationTestClient(self.create_application()) as client:
            response = await client.dispatch("contract.missing_action")
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "ACTION_NOT_FOUND")
        self.assertEqual(response["error"]["category"], "action")

    async def test_invalid_envelope_is_rejected(self):
        async with ApplicationTestClient(self.create_application()) as client:
            response = await client.app.dispatch({"kind": "request",
                                                  "protocol_version": PROTOCOL_VERSION,
                                                  "action": "system.hello", "payload": {}})
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "PROTOCOL_INVALID_MESSAGE")

    async def test_unsupported_protocol_version_is_rejected(self):
        async with ApplicationTestClient(self.create_application()) as client:
            response = await client.app.dispatch({"kind": "request", "protocol_version": "0.0",
                                                  "request_id": "contract-1",
                                                  "action": "system.hello", "payload": {}})
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "PROTOCOL_UNSUPPORTED_VERSION")

    async def test_health_reports_readiness(self):
        async with ApplicationTestClient(self.create_application()) as client:
            data = await client.call("system.health")
        self.assertIn(data["status"], ("ok", "degraded"))
        self.assertIn(data["state"], ("ready", "running"))

    async def test_unknown_job_cancellation_is_unsupported(self):
        async with ApplicationTestClient(self.create_application()) as client:
            data = await client.call("system.cancel", {"job_id": "contract-missing-job"})
        self.assertEqual(data, {"job_id": "contract-missing-job", "cancelled": False,
                                "cancellation": "unsupported", "status": None})
