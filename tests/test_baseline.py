"""Acknowledged violations stay visible without blocking new ones (FR-ARCH-013/014)."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from nikhi.adhara_sutra import (ArchitectureProfile, Baseline, BaselineEntry, ProjectInspector,
                                apply_baseline, verify)
from nikhi.adhara_sutra.cli import main
from nikhi.adhara_sutra.verification import FAIL, NEEDS_REVIEW, PASS

APP = '''\
from nikhi.adhara_sutra import Application

app = Application("baseline_fixture", "1.0")


@app.action("ping")
def ping(payload, context):
    return {"pong": True}


if __name__ == "__main__":
    raise SystemExit(app.run())
'''


class BaselineTests(unittest.TestCase):
    def project(self, **files):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    @staticmethod
    def checks(result):
        return {check.rule: check for check in result.checks}

    def test_baseline_acknowledges_known_and_blocks_new_violations(self):
        known = verify(ProjectInspector(self.project(**{"pyproject.toml": "",
                                                         "app.py": APP + "\nprint('debug')\n"})).inspect())
        self.assertEqual(known.status, NEEDS_REVIEW)
        baseline = Baseline.capture(known)
        self.assertEqual(len(baseline.entries), 1)

        acknowledged = apply_baseline(known, baseline)
        self.assertEqual(acknowledged.status, PASS)
        self.assertTrue(self.checks(acknowledged)["ARCH-PROTO-001"].acknowledged)
        self.assertEqual(acknowledged.to_dict()["acknowledged"], 1)

        project = ProjectInspector(self.project(**{
            "pyproject.toml": "", "app.py": APP + "\nprint('debug')\n",
            "helper.py": "print('other')\n"})).inspect()
        new = apply_baseline(verify(project), baseline)
        self.assertFalse(self.checks(new)["ARCH-PROTO-001"].acknowledged)
        self.assertEqual(new.status, NEEDS_REVIEW)

    def test_violations_without_evidence_cannot_be_acknowledged(self):
        profile = ArchitectureProfile(required_files=("README.md",))
        result = verify(ProjectInspector(self.project(**{"app.py": APP})).inspect(), profile)
        self.assertEqual(self.checks(result)["ARCH-STRUCT-001"].status, FAIL)
        baseline = Baseline.capture(result)
        self.assertEqual(baseline.entries, ())
        self.assertEqual(apply_baseline(result, baseline).status, FAIL)

    def test_baseline_json_round_trip_and_validation(self):
        baseline = Baseline((BaselineEntry("ARCH-PROTO-001", "app.py", "print('debug')",
                                           "reviewed false positive"),))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            baseline.save(path)
            self.assertEqual(Baseline.load(path), baseline)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"], "1.0")

            path.write_text(json.dumps({"schema_version": "2.0", "entries": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                Baseline.load(path)
            path.write_text(json.dumps({"schema_version": "1.0",
                                        "entries": [{"rule": "ARCH-PROTO-001", "path": "app.py"}]}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                Baseline.load(path)


class BaselineCommandTests(unittest.TestCase):
    def project(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "pyproject.toml").write_text("", encoding="utf-8")
        (root / "app.py").write_text(APP + "\nprint('debug')\n", encoding="utf-8")
        return root

    def test_write_then_apply_baseline(self):
        root = self.project()
        baseline = root / "baseline.json"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["verify", str(root), "--write-baseline", str(baseline)]), 0)
        self.assertTrue(baseline.is_file())

        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["verify", str(root), "--strict", "--baseline", str(baseline)]), 0)

        (root / "helper.py").write_text("print('new')\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["verify", str(root), "--strict", "--baseline", str(baseline)]), 1)

    def test_invalid_baseline_is_rejected(self):
        root = self.project()
        baseline = root / "baseline.json"
        baseline.write_text("{not json", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(main(["verify", str(root), "--baseline", str(baseline)]), 2)
        self.assertIn("baseline", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
