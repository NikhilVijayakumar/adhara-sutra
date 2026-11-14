"""Executable protocol contract tests (FR-TEST-002, NFR-TEST-003)."""

import asyncio
import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, ConnectorError, PROTOCOL_VERSION


def envelope(action, payload=None, request_id="req-1", version=PROTOCOL_VERSION):
    return {"kind": "request", "protocol_version": version, "request_id": request_id,
            "action": action, "payload": payload or {}}


class ProtocolContractTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = Application(f"protocol_contract_{uuid4().hex}", "1.0")

        @self.app.action("echo")
        def echo(payload, context):
            context.emit("progress", {"step": 1})
            return {"echo": payload}

        @self.app.action("validated", validate=self._validate)
        def validated(payload, context):
            return payload

        @self.app.action("fail")
        def fail(payload, context):
            raise ValueError("boom")

        @self.app.action("connector")
        def connector(payload, context):
            raise ConnectorError("offline", retryable=True, details={"outcome": "not_sent"})

        @self.app.action("bad_output", output=self._bad_output)
        def bad_output(payload, context):
            return {}

        @self.app.job("wait")
        async def wait(payload, context):
            await asyncio.sleep(30)

        @self.app.job("done")
        async def done(payload, context):
            return {"complete": True}

        await self.app.start()

    async def asyncTearDown(self):
        await self.app.stop()

    @staticmethod
    def _validate(payload):
        if "name" not in payload:
            raise ValueError("name is required")
        return payload

    @staticmethod
    def _bad_output(result):
        raise ValueError("not serializable by the action")

    async def test_jobs_share_exact_session_mapping_and_scopes_are_isolated(self):
        app = Application(f"session_scope_{uuid4().hex}", "1.0")
        seen_actions, seen_jobs = [], []

        @app.action("submit")
        def submit(payload, context):
            seen_actions.append(context.session_state)
            return {"job_id": context.jobs.submit("update", payload)}

        @app.action("read")
        def read(payload, context):
            return dict(context.session_state)

        @app.job("update")
        async def update(payload, context):
            seen_jobs.append(context.session_state)
            context.session_state["job_value"] = payload["value"]

        await app.start()
        try:
            empty, populated, separate = {}, {"existing": True}, {}
            for scope, value in ((empty, "empty"), (populated, "populated")):
                response = await app.dispatch(envelope("submit", {"value": value}), session_state=scope)
                self.assertTrue(response["success"])
                await app.context.jobs.wait(response["data"]["job_id"])
                self.assertIs(seen_actions[-1], scope)
                self.assertIs(seen_jobs[-1], scope)
                self.assertEqual(scope["job_value"], value)
            self.assertEqual(populated["existing"], True)
            self.assertEqual((await app.dispatch(envelope("read"), session_state=separate))["data"], {})
            self.assertEqual((await app.dispatch(envelope("read"), session_state=empty))["data"]["job_value"], "empty")
            for value in ("first", "second"):
                response = await app.dispatch(envelope("submit", {"value": value}))
                await app.context.jobs.wait(response["data"]["job_id"])
                self.assertIs(seen_actions[-1], seen_jobs[-1])
            self.assertIsNot(seen_actions[-1], seen_actions[-2])
            self.assertEqual(seen_actions[-1], {"job_value": "second"})
            self.assertEqual(separate, {})
        finally:
            await app.stop()

    async def test_hello_reports_protocol_and_identity(self):
        response = await self.app.dispatch(envelope("system.hello"))
        self.assertTrue(response["success"])
        self.assertEqual(response["kind"], "response")
        self.assertEqual(response["request_id"], "req-1")
        data = response["data"]
        self.assertEqual(data["protocol_version"], PROTOCOL_VERSION)
        self.assertIn(PROTOCOL_VERSION, data["supported_protocol_versions"])
        self.assertEqual((data["name"], data["version"]), (self.app.name, "1.0"))

    async def test_help_lists_actions_and_jobs(self):
        data = (await self.app.dispatch(envelope("system.help")))["data"]
        names = {action["name"] for action in data["actions"]}
        self.assertTrue({"echo", "validated", "fail", "connector", "bad_output"} <= names)
        self.assertIsInstance(data["jobs"], list)

    async def test_unknown_action_reports_available_actions(self):
        response = await self.app.dispatch(envelope("missing"))
        self.assertFalse(response["success"])
        error = response["error"]
        self.assertEqual((error["code"], error["category"]), ("ACTION_NOT_FOUND", "action"))
        self.assertIn("echo", error["details"]["available_actions"])

    async def test_invalid_envelopes_are_protocol_errors(self):
        cases = (
            ({"kind": "event", "protocol_version": PROTOCOL_VERSION, "request_id": "1",
              "action": "echo", "payload": {}}, "PROTOCOL_INVALID_MESSAGE"),
            ({"kind": "request", "protocol_version": "9.9", "request_id": "1",
              "action": "echo", "payload": {}}, "PROTOCOL_UNSUPPORTED_VERSION"),
            ({"kind": "request", "protocol_version": PROTOCOL_VERSION,
              "action": "echo", "payload": {}}, "PROTOCOL_INVALID_MESSAGE"),
        )
        for request, code in cases:
            with self.subTest(code=code):
                error = (await self.app.dispatch(request))["error"]
                self.assertEqual((error["code"], error["category"]), (code, "protocol"))

    async def test_validation_and_output_errors_are_validation_categories(self):
        missing = await self.app.dispatch(envelope("validated", {}))
        self.assertEqual((missing["error"]["code"], missing["error"]["category"]),
                         ("ACTION_VALIDATION_FAILED", "validation"))
        output = await self.app.dispatch(envelope("bad_output"))
        self.assertEqual((output["error"]["code"], output["error"]["category"]),
                         ("ACTION_OUTPUT_INVALID", "validation"))

    async def test_connector_and_unexpected_failures_are_classified(self):
        failure = await self.app.dispatch(envelope("fail"))
        self.assertEqual((failure["error"]["code"], failure["error"]["category"]),
                         ("RUNTIME_EXECUTION_FAILED", "internal"))
        connector = await self.app.dispatch(envelope("connector"))
        self.assertEqual((connector["error"]["code"], connector["error"]["category"]),
                         ("CONNECTOR_FAILURE", "connector"))
        self.assertTrue(connector["error"]["retryable"])
        self.assertEqual(connector["error"]["details"], {"outcome": "not_sent"})

    async def test_events_are_correlated_before_the_terminal_response(self):
        events = []
        response = await self.app.dispatch(envelope("echo", {"value": 1}), emit=events.append)
        self.assertTrue(response["success"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "event")
        self.assertEqual(events[0]["request_id"], "req-1")
        self.assertEqual((events[0]["event"], events[0]["data"]), ("progress", {"step": 1}))

    async def test_health_reports_readiness(self):
        data = (await self.app.dispatch(envelope("system.health")))["data"]
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["state"], "ready")

    async def test_job_status_validates_and_requires_readiness(self):
        unstarted = Application(f"status_not_ready_{uuid4().hex}", "1.0")
        response = await unstarted.dispatch(envelope("system.jobs.get", {"job_id": "x"}))
        self.assertEqual(response["error"]["code"], "RUNTIME_NOT_READY")
        for payload in ({}, {"job_id": ""}, {"job_id": None}, {"job_id": 2}):
            with self.subTest(payload=payload):
                error = (await self.app.dispatch(envelope("system.jobs.get", payload)))["error"]
                self.assertEqual(error["code"], "ACTION_VALIDATION_FAILED")
                self.assertEqual(error["details"], "job_id")
        data = (await self.app.dispatch(envelope("system.jobs.get", {"job_id": "missing"})))["data"]
        self.assertEqual(data, {"job_id": "missing", "status": None})

    async def test_job_status_reports_active_completed_and_cancelled(self):
        active_id = self.app.context.jobs.submit("wait")
        await asyncio.sleep(0)
        async def query(job_id):
            response = await self.app.dispatch(envelope("system.jobs.get", {"job_id": job_id}))
            self.assertTrue(response["success"])
            self.assertEqual(set(response["data"]), {"job_id", "status"})
            self.assertEqual(response["data"]["job_id"], job_id)
            self.assertEqual(response["data"]["status"], self.app.context.jobs.status(job_id))
            return response["data"]["status"]
        self.assertIn((await query(active_id))["state"], ("queued", "running"))
        done_id = self.app.context.jobs.submit("done")
        await self.app.context.jobs.wait(done_id)
        self.assertEqual((await query(done_id))["state"], "succeeded")
        self.app.context.jobs.cancel(active_id)
        await self.app.context.jobs.wait(active_id)
        self.assertEqual((await query(active_id))["state"], "cancelled")

    async def test_cancel_requires_a_job_and_reports_unknown_jobs(self):
        invalid = await self.app.dispatch(envelope("system.cancel", {}))
        self.assertEqual(invalid["error"]["code"], "ACTION_VALIDATION_FAILED")
        unknown = await self.app.dispatch(envelope("system.cancel", {"job_id": "missing"}))
        self.assertEqual(unknown["data"], {"job_id": "missing", "cancelled": False,
                                           "cancellation": "unsupported", "status": None})

    async def test_cancel_reports_phase_and_status_for_active_and_terminal_jobs(self):
        job_id = self.app.context.jobs.submit("wait")
        await asyncio.sleep(0)
        data = (await self.app.dispatch(envelope("system.cancel", {"job_id": job_id})))["data"]
        self.assertTrue(data["cancelled"])
        self.assertIn(data["cancellation"], ("requested", "completed"))
        if data["cancellation"] == "completed":
            self.assertEqual(data["status"]["state"], "cancelled")
        self.assertEqual((await self.app.context.jobs.wait(job_id))["state"], "cancelled")
        again = (await self.app.dispatch(envelope("system.cancel", {"job_id": job_id})))["data"]
        self.assertFalse(again["cancelled"])
        self.assertEqual(again["cancellation"], "unsupported")
        self.assertEqual(again["status"]["state"], "cancelled")
