"""Scaffolding produces runnable, documented starter projects (FR-DOC-002)."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra.scaffolding import generate

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
