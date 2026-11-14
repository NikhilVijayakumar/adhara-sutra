"""Architecture rules as automated, reproducible tests (FR-TEST-007, FR-ARCH-009)."""

import json
import io
from contextlib import redirect_stdout, redirect_stderr
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ArchitectureProfile, ProjectInspector, Rule, check_for, verify
from nikhi.adhara_sutra.cli import main
from nikhi.adhara_sutra.profiles import resolve_profile
from nikhi.adhara_sutra.verification import FAIL, NEEDS_REVIEW, NOT_CHECKED, PASS

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
        self.assertEqual(statuses["ARCH-LAYER-001"], NOT_CHECKED)
        self.assertEqual(statuses["ARCH-PROTO-001"], PASS)
        self.assertEqual(statuses["ARCH-JOB-002"], PASS)

    def test_profile_configuration_and_selection_validation(self):
        project = self.make_project(**{"pyproject.toml": '[tool.adhara]\nprofile = "minimal"\nprofile_version = "1"\n',
                                        "src/app.py": APP,
                                        "src/ui/screen.py": "import app.data\n"})
        root = Path(project.root)
        config = root / ".adhara-profile.json"
        config.write_text(json.dumps({"layer_boundaries": [["src/ui", "app.data", "use adapter"]]}), encoding="utf-8")
        captured = ProjectInspector(root).inspect()
        profile = resolve_profile(root, captured_files=captured.configuration_files)
        result = verify(captured, profile)
        self.assertEqual(self.statuses(result)["ARCH-LAYER-001"], FAIL)
        config.write_text("{}", encoding="utf-8")
        self.assertEqual(resolve_profile(root, captured_files=captured.configuration_files), profile)
        self.assertNotEqual(verify(ProjectInspector(root).inspect(), resolve_profile(root)).profile_digest, result.profile_digest)
        for bad in ({"required_files": ["../outside"]}, {"required_directories": ["C:/outside"]},
                    {"layer_boundaries": [["../outside", "x", "fix"]]}, {"unknown": []}):
            config.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                resolve_profile(root)
        config.write_text("{}", encoding="utf-8")
        for args in (("--profile", "unknown"), ("--profile-version", "2")):
            for command in ("verify", "migrate"):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(main([command, str(root), *args]), 2)
        (root / "pyproject.toml").write_text('[tool.adhara]\nprofile_version = 1\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            resolve_profile(root)

    def test_supported_application_aliases_and_serve_are_recognized(self):
        for imported, constructor in (("from nikhi.adhara_sutra import Application as App", "App"),
                                      ("import nikhi.adhara_sutra as framework", "framework.Application")):
            with self.subTest(imported=imported):
                source = (f"{imported}\nservice = {constructor}('demo', '1')\n"
                          "@service.action('ping')\ndef ping(payload, context):\n    return {}\n"
                          "async def main():\n    await service.serve()\n")
                project = self.make_project(**{"pyproject.toml": "", "app.py": source})
                checks = self.statuses(verify(project))
                self.assertEqual(checks["ARCH-FW-001"], PASS)
                self.assertEqual(checks["ARCH-FW-002"], PASS)
                self.assertEqual(checks["ARCH-ENTRY-001"], PASS)
                self.assertIn("service.serve()", [f.name for f in project.by_kind("entry_point")])

    def test_unrelated_and_dynamic_bindings_are_not_proven(self):
        unrelated = self.make_project(**{"app.py": "class Application: pass\napp = Application()\n"})
        self.assertNotEqual(self.statuses(verify(unrelated))["ARCH-FW-001"], PASS)
        cases = (
            "from nikhi.adhara_sutra import Application\nfactory = Application\napp = factory('x', '1')\n",
            "from nikhi.adhara_sutra import Application as App\nApp = other\napp = App('x', '1')\n",
            "from nikhi.adhara_sutra import Application\napp = Application('x', '1')\napp = other\n",
        )
        for source in cases:
            with self.subTest(source=source):
                result = verify(self.make_project(**{"app.py": source}))
                self.assertNotEqual(self.statuses(result)["ARCH-FW-001"], PASS)
                self.assertIn("ARCH-FW-001", result.coverage["mandatory_unresolved"])
        dynamic = self.make_project(**{"app.py": "from nikhi.adhara_sutra import Application\n"
                                    "app = Application('x','1')\n"
                                    "other = app\n@other.action('x')\ndef work(p,c): pass\n"})
        self.assertEqual(self.statuses(verify(dynamic))["ARCH-FW-002"], NEEDS_REVIEW)

    def test_job_and_protocol_claims_are_bounded(self):
        project = self.make_project(**{"app.py": APP + "\ndef do_work(context):\n    return context.jobs\n"})
        checks = {c.rule: c for c in verify(project).checks}
        self.assertEqual(checks["ARCH-JOB-001"].status, PASS)
        self.assertIn("Recognized", checks["ARCH-JOB-001"].detail)
        self.assertNotIn("Long-running work uses", checks["ARCH-JOB-001"].detail)
        self.assertIn("syntax", checks["ARCH-PROTO-001"].detail)

    def test_layer_boundaries_are_enforced(self):
        files = {"app/main.py": APP,
                 "app/ui/screen.py": "from app.data import store\n",
                 "app/data/store.py": ""}
        forbidden = ArchitectureProfile(
            layer_boundaries=(("app/ui", "app.data", "use the store adapter"),))
        self.assertEqual(self.statuses(verify(self.make_project(**files), forbidden))["ARCH-LAYER-001"],
                         FAIL)

        allowed = ArchitectureProfile(
            layer_boundaries=(("app/data", "app.ui", "keep data independent"),))
        self.assertEqual(self.statuses(verify(self.make_project(**files), allowed))["ARCH-LAYER-001"],
                         PASS)

    def test_protocol_bypass_needs_review(self):
        statuses = self.statuses(verify(self.make_project(**{"app.py": APP + "\nprint('debug')\n"})))
        self.assertEqual(statuses["ARCH-PROTO-001"], NEEDS_REVIEW)

        stream = self.make_project(**{"app.py": APP, "helper.py": "import sys\nsys.stdout.write('x')\n"})
        self.assertEqual(self.statuses(verify(stream))["ARCH-PROTO-001"], NEEDS_REVIEW)

    def test_unmanaged_background_work_needs_review(self):
        source = APP + "\nimport asyncio\n\nasync def work():\n    pass\n\nasyncio.create_task(work())\n"
        self.assertEqual(self.statuses(verify(self.make_project(**{"app.py": source})))["ARCH-JOB-002"],
                         NEEDS_REVIEW)

        managed = APP + "\n\n@app.job('work')\nasync def work(payload, context):\n    pass\n"
        self.assertEqual(self.statuses(verify(self.make_project(**{"app.py": managed})))["ARCH-JOB-002"],
                         PASS)

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

    def test_custom_rules_extend_verification(self):
        rule = Rule("APP-DOC-001", "Project README", "warning", "The project documents itself.")

        def evaluate(project, profile):
            if "README.md" in project.files:
                return check_for(rule, PASS, detail="README.md is present")
            return check_for(rule, FAIL, detail="README.md is missing", remediation="Add README.md")

        project = self.make_project(**{"pyproject.toml": "", "app.py": APP})
        check = next(item for item in verify(project, rules=[(rule, evaluate)]).checks
                     if item.rule == "APP-DOC-001")
        self.assertEqual((check.status, check.title, check.remediation),
                         (FAIL, "Project README", "Add README.md"))
        documented = self.make_project(**{"pyproject.toml": "", "app.py": APP, "README.md": ""})
        self.assertEqual(self.statuses(verify(documented, rules=[(rule, evaluate)]))["APP-DOC-001"], PASS)

    def test_custom_rule_must_return_its_own_check(self):
        rule = Rule("APP-DOC-002", "Custom rule", "warning", "x")
        other = Rule("APP-DOC-003", "Other rule", "warning", "x")
        project = self.make_project(**{"app.py": APP})
        with self.assertRaises(ValueError):
            verify(project, rules=[(rule, lambda project, profile: check_for(other, PASS))])

    def test_parse_errors_are_reported(self):
        project = self.make_project(**{"pyproject.toml": "", "broken.py": "def ("})
        statuses = self.statuses(verify(project))
        self.assertEqual(statuses["ARCH-STRUCT-004"], FAIL)


if __name__ == "__main__":
    unittest.main()
