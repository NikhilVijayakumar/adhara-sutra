"""Scaffolding produces runnable, documented starter projects (FR-DOC-002)."""

import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra.scaffolding import generate


class ScaffoldingTests(unittest.TestCase):
    def test_generate_writes_initial_documentation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "sample"
            written = generate(root, name="sample", profile="minimal", connectors=("sqlite",))
            self.assertIn("README.md", written)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("# sample", readme)
            self.assertIn("`minimal` profile", readme)
            self.assertIn("sqlite", readme)
            self.assertIn("pip install -e", readme)
            self.assertIn("pytest", readme)
            self.assertTrue((root / "pyproject.toml").is_file())
            self.assertTrue((root / "tests" / "test_app.py").is_file())


if __name__ == "__main__":
    unittest.main()
