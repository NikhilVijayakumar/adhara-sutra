"""The developer CLI exposes the standard operations consistently (FR-DEV-001)."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from nikhi.adhara_sutra import __version__
from nikhi.adhara_sutra.cli import _load, main


class DeveloperCommandTests(unittest.TestCase):
    def test_help_lists_the_supported_operations(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([]), 0)
        text = output.getvalue()
        for command in ("run", "version", "new", "doctor", "inspect", "verify", "migrate"):
            self.assertIn(command, text)

    def test_version_is_reported(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["version"]), 0)
        self.assertEqual(output.getvalue().strip(), __version__)

    def test_invalid_invocations_share_the_error_status(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main(["unknown"])
        self.assertEqual(raised.exception.code, 2)

        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / "missing")
            for command in ("run", "doctor", "inspect", "verify", "migrate"):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(main([command, missing]), 2, command)

    def test_loader_preserves_standalone_behavior_and_relative_import_cause(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            standalone = root / "standalone.py"
            standalone.write_text('from nikhi.adhara_sutra import Application\napp = Application("standalone_loader", "1")\n', encoding="utf-8")
            self.assertEqual(_load(str(standalone)).name, "standalone_loader")
            package_file = root / "package_app.py"
            package_file.write_text("from .actions import register\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dotted module target") as caught:
                _load(str(package_file))
            self.assertIsInstance(caught.exception.__cause__, ImportError)
            unrelated = root / "unrelated.py"
            unrelated.write_text('raise ImportError("different error")\n', encoding="utf-8")
            with self.assertRaisesRegex(ImportError, "different error"):
                _load(str(unrelated))

    def test_reports_can_be_emitted_for_tooling(self):
        for command in ("doctor", "inspect", "verify", "migrate"):
            output = io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as raised:
                    main([command, "--help"])
            self.assertEqual(raised.exception.code, 0)
            self.assertIn("--json", output.getvalue())
            self.assertIn("--output", output.getvalue())


if __name__ == "__main__":
    unittest.main()
