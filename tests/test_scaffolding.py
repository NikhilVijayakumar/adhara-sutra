"""Scaffolding produces runnable, documented starter projects (FR-DOC-002)."""

import io
import json
from contextlib import redirect_stdout, redirect_stderr
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra.scaffolding import generate
from nikhi.adhara_sutra.cli import main

ROOT = Path(__file__).resolve().parents[1]


class ScaffoldingTests(unittest.TestCase):
    def test_generate_writes_initial_documentation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "sample"
            written = generate(root, name="sample", profile="minimal")
            self.assertIn("README.md", written)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("# sample", readme)
            self.assertIn("`minimal` profile", readme)
            self.assertIn("pip install -e", readme)
            self.assertIn("pytest", readme)
            self.assertTrue((root / "pyproject.toml").is_file())
            self.assertTrue((root / "tests" / "test_app.py").is_file())

    def test_generated_profiles_run_documented_module_targets(self):
        request = {"kind": "request", "protocol_version": "1.0", "request_id": "test",
                   "action": "greeting.create", "payload": {"name": "Ada"}}
        for profile in ("minimal", "cli"):
            for connectors in ((), ("sqlite",)):
                with self.subTest(profile=profile, connectors=connectors), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory) / "sample"
                    generate(root, name="sample", profile=profile, connectors=connectors)
                    readme = (root / "README.md").read_text(encoding="utf-8")
                    self.assertIn('pip install -e', readme)
                    self.assertIn('python -m sample', readme)
                    self.assertIn('adhara run sample.app', readme)
                    self.assertNotIn('adhara run src/', readme)
                    env = {**os.environ, "PYTHONPATH": os.pathsep.join((str(root / "src"), str(ROOT / "src")))}
                    for command in ([sys.executable, "-m", "sample"],
                                    [sys.executable, "-m", "nikhi.adhara_sutra.cli", "run", "sample.app"]):
                        result = subprocess.run(command, input=json.dumps(request) + "\n", cwd=root, env=env,
                                                capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        response = json.loads(result.stdout)
                        self.assertTrue(response["success"])
                        self.assertEqual(response["data"], {"message": "Hello, Ada!"})
                    if profile == "cli":
                        result = subprocess.run([sys.executable, "-m", "nikhi.adhara_sutra.cli", "run",
                                                 str(root / "src" / "sample" / "app.py")],
                                                cwd=root, env=env, capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, 2)
                        self.assertIn("package-relative imports", result.stderr)
                        self.assertIn("dotted module target", result.stderr)

    def test_selected_profiles_are_shared_by_verification_and_migration(self):
        for name in ("minimal", "cli"):
            with self.subTest(profile=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "app"
                generate(root, name="demo", package="my_package", profile=name)
                def run(command, *options):
                    output = io.StringIO()
                    with redirect_stdout(output), redirect_stderr(io.StringIO()):
                        code = main([command, str(root), "--json", *options])
                    return code, json.loads(output.getvalue()) if output.getvalue() else None
                code, verified = run("verify")
                self.assertEqual(code, 0, verified)
                self.assertEqual(verified["profile"], {"name": name, "version": "1"})
                statuses = {c["rule"]: c["status"] for c in verified["checks"]}
                self.assertTrue(all(statuses[rule] == "pass" for rule in verified["mandatory_rules"]))
                _, plan = run("migrate")
                self.assertEqual(plan["profile"], verified["profile"])
                self.assertEqual(plan["profile_digest"], verified["profile_digest"])
                if name == "cli":
                    (root / "src" / "my_package" / "actions" / "greeting.py").unlink()
                    code, broken = run("verify")
                    self.assertEqual(code, 1)
                    self.assertEqual(next(c for c in broken["checks"] if c["rule"] == "ARCH-STRUCT-001")["status"], "fail")
                    _, migration = run("migrate")
                    self.assertEqual(migration["profile"]["name"], "cli")
                    self.assertTrue(any(f["rule"] == "ARCH-STRUCT-001" for f in migration["findings"]))
                    _, override = run("verify", "--profile", "minimal")
                    self.assertEqual(override["profile"]["name"], "minimal")
                    self.assertNotEqual(override["profile_digest"], broken["profile_digest"])
                    _, overridden_plan = run("migrate", "--profile", "minimal")
                    self.assertEqual(overridden_plan["profile_digest"], override["profile_digest"])

    def test_generated_minimal_application_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "sample"
            generate(root, name="sample", profile="minimal")
            driver = root / "driver.py"
            driver.write_text(
                "import asyncio\n"
                "from sample.app import app\n"
                "from nikhi.adhara_sutra import ApplicationTestClient\n\n"
                "async def main():\n"
                "    async with ApplicationTestClient(app) as client:\n"
                "        assert await client.call('greeting.create', {'name': 'Ada'}) == "
                "{'message': 'Hello, Ada!'}\n\n"
                "asyncio.run(main())\n", encoding="utf-8")
            env = {**os.environ,
                   "PYTHONPATH": os.pathsep.join((str(root / "src"), str(ROOT / "src")))}
            result = subprocess.run([sys.executable, "driver.py"], cwd=root, env=env,
                                    capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
