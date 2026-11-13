"""Packaged runtime discovery and executable diagnostics (FR-PKG-005/006/007/009)."""

import sys
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ExternalCommand, locate_backend
from nikhi.adhara_sutra.runtime import RuntimeDiscoveryError, supported_platforms


class RuntimeDiscoveryTests(unittest.TestCase):
    def test_supported_platforms_are_defined(self):
        self.assertEqual(set(supported_platforms()), {"win32", "darwin", "linux"})

    def test_environment_override_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            interpreter = Path(directory) / "python-custom"
            interpreter.write_text("", encoding="utf-8")
            resolved = locate_backend(env={"ADHARA_PYTHON": str(interpreter)})
        self.assertEqual(Path(resolved), interpreter.resolve())

    def test_missing_override_is_reported(self):
        with self.assertRaises(RuntimeDiscoveryError):
            locate_backend(env={"ADHARA_PYTHON": "Z:/missing/python.exe"})

    def test_bundled_interpreter_is_found_relative_to_app_root(self):
        with tempfile.TemporaryDirectory() as directory:
            bundled = Path(directory) / "backend" / "python.exe"
            bundled.parent.mkdir()
            bundled.write_text("", encoding="utf-8")
            resolved = locate_backend(app_root=directory, bundled=("backend/python.exe",), env={})
        self.assertEqual(Path(resolved), bundled.resolve())

    def test_falls_back_to_running_interpreter(self):
        resolved = locate_backend(env={})
        self.assertTrue(Path(resolved).is_file())


class ExternalExecutableDiagnosticsTests(unittest.TestCase):
    def test_diagnose_resolves_configured_path(self):
        report = ExternalCommand(sys.executable).diagnose()
        self.assertTrue(report["found"])
        self.assertEqual(report["source"], "configured path")
        self.assertEqual(Path(report["resolved"]), Path(sys.executable).resolve())

    def test_diagnose_reports_missing_executable_without_starting(self):
        report = ExternalCommand("adhara-definitely-missing-tool").diagnose()
        self.assertFalse(report["found"])
        self.assertIsNone(report["resolved"])
        self.assertEqual(report["source"], "search path")


if __name__ == "__main__":
    unittest.main()
