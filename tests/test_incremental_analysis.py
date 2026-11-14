"""Incremental analysis reuses unchanged files and refreshes changed ones (FR-DISC-011)."""

import tempfile
import shutil
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

    def test_fingerprint_tracks_inputs_and_survives_relocation_and_cache(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            root = Path(directory)
            (root / "app.py").write_text("import httpx\n", encoding="utf-8")
            (root / "package.json").write_text("{}", encoding="utf-8")
            cache = AnalysisCache()
            first = ProjectInspector(root, cache=cache).inspect()
            self.assertEqual(len(first.source_fingerprint), 64)
            self.assertEqual(first.source_fingerprint, ProjectInspector(root, cache=cache).inspect().source_fingerprint)
            (root / "report.json").write_text("{}", encoding="utf-8")
            self.assertEqual(first.source_fingerprint, ProjectInspector(root).inspect().source_fingerprint)
            shutil.copytree(root, Path(other) / "copy")
            self.assertEqual(first.source_fingerprint, ProjectInspector(Path(other) / "copy").inspect().source_fingerprint)
            (root / "extra.ts").write_text("const x = 1", encoding="utf-8")
            added = ProjectInspector(root).inspect().source_fingerprint
            self.assertNotEqual(first.source_fingerprint, added)
            (root / "extra.ts").write_text("const x = 2", encoding="utf-8")
            self.assertNotEqual(added, ProjectInspector(root).inspect().source_fingerprint)
            (root / "extra.ts").unlink()
            self.assertEqual(first.source_fingerprint, ProjectInspector(root).inspect().source_fingerprint)
            (root / ".adhara-profile.json").write_text("{}", encoding="utf-8")
            self.assertNotEqual(first.source_fingerprint, ProjectInspector(root).inspect().source_fingerprint)

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
