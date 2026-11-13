"""Reusable test facilities: contract suite, doubles, fixtures, job failures."""

import json
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from nikhi.adhara_sutra import Application, ApplicationTestClient, CLIContractTests, ExternalCommand


class ShippedContractTests(CLIContractTests):
    def create_application(self):
        app = Application(f"contract_{uuid4().hex}", "1.0")

        @app.action("ping")
        def ping(payload, context):
            return {"pong": True}
        return app


class ConnectorDoubleTests(unittest.IsolatedAsyncioTestCase):
    async def test_connector_is_replaced_with_a_test_double(self):
        class FakeHttp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def get(self, url):
                return {"url": url, "status": 200}

        app = Application(f"doubles_{uuid4().hex}", "1.0")
        app.service("http", lambda context: FakeHttp())

        @app.action("fetch")
        def fetch(payload, context):
            return context.get_service("http").get(payload["url"])

        async with ApplicationTestClient(app) as client:
            data = await client.call("fetch", {"url": "https://example.invalid"})
        self.assertEqual(data, {"url": "https://example.invalid", "status": 200})


class ProcessFixtureTests(unittest.IsolatedAsyncioTestCase):
    async def test_controlled_executable_fixture_runs_with_env_and_cwd(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        script = Path(directory.name) / "fixture.py"
        script.write_text(
            "import json, os\n"
            "print(json.dumps({'cwd': os.getcwd(), 'value': os.environ.get('FIXTURE_VALUE')}))\n",
            encoding="utf-8")
        command = ExternalCommand(sys.executable, env={"FIXTURE_VALUE": "controlled"},
                                  cwd=directory.name)
        with command:
            result = await command.run([str(script)], timeout=30)
        self.assertTrue(result.ok, result.stderr_text)
        data = json.loads(result.stdout_text)
        self.assertEqual(data["value"], "controlled")
        self.assertEqual(Path(data["cwd"]).resolve(), Path(directory.name).resolve())


class JobBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def test_failing_job_is_observable(self):
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)
        app = Application(f"jobs_{uuid4().hex}", "1.0")

        @app.job("fail")
        async def fail(payload, context):
            raise RuntimeError("boom")

        async with ApplicationTestClient(app) as client:
            job_id = client.app.context.jobs.submit("fail")
            status = await client.app.context.jobs.wait(job_id)
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["error"], {"code": "JOB_FAILED", "message": "boom"})


if __name__ == "__main__":
    unittest.main()
