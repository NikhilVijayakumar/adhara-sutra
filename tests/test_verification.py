"""Architecture rules as automated, reproducible tests (FR-TEST-007, FR-ARCH-009)."""

import json
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ArchitectureProfile, ProjectInspector, verify
from nikhi.adhara_sutra.verification import FAIL, NOT_CHECKED, PASS

APP = '''\
from nikhi.adhara_sutra import Application

app = Application("verification_fixture", "1.0")


@app.action("ping")
def ping(payload, context):
    return {"pong": True}


if __name__ == "__main__":
    raise SystemExit(app.run())
'''


class VerificationTests(unittest.TestCase):
    def make_project(self, **files):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return ProjectInspector(root).inspect()

    @staticmethod
    def statuses(result):
        return {check.rule: check.status for check in result.checks}

    def test_default_profile_covers_applicable_rules(self):
        project = self.make_project(**{"pyproject.toml": "", "app.py": APP})
        statuses = self.statuses(verify(project))
        self.assertEqual(statuses["ARCH-STRUCT-001"], PASS)
        self.assertEqual(statuses["ARCH-STRUCT-003"], PASS)
        self.assertEqual(statuses["ARCH-STRUCT-004"], PASS)
        self.assertEqual(statuses["ARCH-FW-001"], PASS)
        self.assertEqual(statuses["ARCH-FW-002"], PASS)
        self.assertEqual(statuses["ARCH-ENTRY-001"], PASS)
        self.assertEqual(statuses["ARCH-STRUCT-002"], NOT_CHECKED)
        self.assertEqual(statuses["ARCH-DEP-001"], NOT_CHECKED)

    def test_configured_requirements_fail_and_pass(self):
        profile = ArchitectureProfile(required_files=("README.md",),
                                      required_directories=("src",),
                                      forbidden_imports=(("requests", "use the managed HttpClient"),))
        incomplete = self.make_project(**{"app.py": APP + "\nimport requests\n"})
        result = verify(incomplete, profile)
        statuses = self.statuses(result)
        self.assertEqual(statuses["ARCH-STRUCT-001"], FAIL)
        self.assertEqual(statuses["ARCH-STRUCT-002"], FAIL)
        self.assertEqual(statuses["ARCH-DEP-001"], FAIL)
        self.assertEqual(result.status, FAIL)
        detail = {check["rule"]: check["detail"] for check in result.to_dict()["checks"]}
        self.assertIn("requests", detail["ARCH-DEP-001"])

        complete = self.make_project(**{"README.md": "", "pyproject.toml": "",
                                        "src/app.py": APP})
        statuses = self.statuses(verify(complete, profile))
        self.assertEqual(statuses["ARCH-STRUCT-001"], PASS)
        self.assertEqual(statuses["ARCH-STRUCT-002"], PASS)
        self.assertEqual(statuses["ARCH-DEP-001"], PASS)

    def test_results_are_reproducible(self):
        project = self.make_project(**{"pyproject.toml": "", "app.py": APP})
        first = json.dumps(verify(project).to_dict(), sort_keys=True)
        second = json.dumps(verify(project).to_dict(), sort_keys=True)
        self.assertEqual(first, second)

    def test_parse_errors_are_reported(self):
        project = self.make_project(**{"pyproject.toml": "", "broken.py": "def ("})
        statuses = self.statuses(verify(project))
        self.assertEqual(statuses["ARCH-STRUCT-004"], FAIL)


if __name__ == "__main__":
    unittest.main()
