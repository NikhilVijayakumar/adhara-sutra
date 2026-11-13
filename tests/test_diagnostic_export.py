"""Sanitized diagnostics can be exported for support (FR-LOG-007)."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nikhi.adhara_sutra import __version__
from nikhi.adhara_sutra.cli import main


class DiagnosticExportTests(unittest.TestCase):
    def test_doctor_exports_structured_and_text_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "doctor.json"
            with redirect_stdout(io.StringIO()):
                code = main(["doctor", "--json", "--output", str(json_path)])
            self.assertIn(code, (0, 1))
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["framework"]["version"], __version__)
            self.assertIn("checks", report)
            self.assertIn("platform", report)
            self.assertIn(report["status"], ("ok", "warn", "fail"))

            text_path = Path(directory) / "doctor.txt"
            with redirect_stdout(io.StringIO()):
                code = main(["doctor", "--output", str(text_path)])
            self.assertIn(code, (0, 1))
            text = text_path.read_text(encoding="utf-8")
            self.assertIn("AdharaSutra doctor", text)
            self.assertIn(__version__, text)


if __name__ == "__main__":
    unittest.main()
