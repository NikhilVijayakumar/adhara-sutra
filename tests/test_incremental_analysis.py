"""Incremental analysis reuses unchanged files and refreshes changed ones (FR-DISC-011)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nikhi.adhara_sutra.discovery import AnalysisCache, ProjectInspector


class IncrementalAnalysisTests(unittest.TestCase):
    def test_unchanged_files_are_not_reanalyzed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0.1.0"\n', encoding="utf-8")
            (root / "a.py").write_text("import httpx\n", encoding="utf-8")
            (root / "b.py").write_text("import sqlite3\n", encoding="utf-8")
            cache = AnalysisCache()
            calls = []
            original = ProjectInspector._inspect_python

            def counting(inspector, path, *args):
                calls.append(path.name)
                return original(inspector, path, *args)

            with mock.patch.object(ProjectInspector, "_inspect_python", counting):
                first = ProjectInspector(root, cache=cache).inspect()
                self.assertEqual(sorted(calls), ["a.py", "b.py"])

                calls.clear()
                second = ProjectInspector(root, cache=cache).inspect()
                self.assertEqual(calls, [])
                self.assertEqual(first.findings, second.findings)

                (root / "a.py").write_text("import requests\n", encoding="utf-8")
                calls.clear()
                third = ProjectInspector(root, cache=cache).inspect()
                self.assertEqual(calls, ["a.py"])
                self.assertIn("requests", [dependency["name"] for dependency in third.dependencies])

    def test_cache_drops_removed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "gone.py").write_text("import httpx\n", encoding="utf-8")
            cache = AnalysisCache()
            ProjectInspector(root, cache=cache).inspect()
            self.assertIn("gone.py", cache.files)
            (root / "gone.py").unlink()
            ProjectInspector(root, cache=cache).inspect()
            self.assertEqual(cache.files, {})


if __name__ == "__main__":
    unittest.main()
