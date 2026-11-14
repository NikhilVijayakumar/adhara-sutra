"""Migration tracking, source-match, and completion evidence (FR-MIG-010/013, NFR-MIG-007/009)."""

import json
import io
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import (MigrationFinding, ProjectInspector, analyze_migration,
                                migration_report, render_markdown, verify)
from nikhi.adhara_sutra.migration import (
    evaluate_migration_completion,
    load_statuses,
    load_test_evidence,
)


APP = '''\
from nikhi.adhara_sutra import Application

app = Application("fixture", "1.0")


@app.action("ping")
def ping(payload, context):
    return {"pong": True}


if __name__ == "__main__":
    raise SystemExit(app.run())
'''


class MigrationTrackingTests(unittest.TestCase):
    def fixture(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "pyproject.toml").write_text("", encoding="utf-8")
        (root / "app.py").write_text(APP, encoding="utf-8")
        (root / "ui").mkdir()
        (root / "ui" / "screen.py").write_text("import httpx\n", encoding="utf-8")
        project = ProjectInspector(root).inspect()
        result = verify(project)
        return project, result, analyze_migration(project, result)

    def test_identity_propagation_and_custom_evaluator_eligibility(self):
        from nikhi.adhara_sutra.verification import ArchitectureProfile, Rule, check_for
        from nikhi.adhara_sutra.report import implementation_report, verification_report
        project, result, plan = self.fixture()
        self.assertEqual(result.source_fingerprint, project.source_fingerprint)
        self.assertEqual(plan.source["source_fingerprint"], project.source_fingerprint)
        self.assertEqual(implementation_report(project)["source"]["source_fingerprint"], project.source_fingerprint)
        self.assertEqual(verification_report(result)["profile_digest"], plan.profile_digest)
        self.assertNotEqual(result.profile_digest, verify(project, ArchitectureProfile(version="different")).profile_digest)
        rule = Rule("CUSTOM", "Custom", "warning", "Custom")
        custom = verify(project, rules=[(rule, lambda p, c: check_for(rule, "pass"))])
        self.assertFalse(custom.custom_identity_complete)
        custom_plan = analyze_migration(project, custom)
        statuses = {"tasks": {t.id: "done" for t in custom_plan.tasks},
                    "findings": {f.id: "done" for f in custom_plan.findings}}
        outcome = evaluate_migration_completion(custom_plan, custom, statuses=statuses,
                    test_evidence={"tests": {"revision": project.revision, "status": "passed"}})
        self.assertFalse(outcome["complete"])
        identified = verify(project, rules=[(rule, lambda p, c: check_for(rule, "pass"))], rules_identity="custom:1")
        self.assertTrue(identified.custom_identity_complete)
        self.assertEqual(identified.rules_identity, "custom:1")
        self.assertFalse(analyze_migration(project, result, analyzers=[lambda p, v: []]).custom_identity_complete)
        self.assertEqual(analyze_migration(project, result, analyzers=[lambda p, v: []], analyzers_identity="extra:1").analyzers_identity, "extra:1")

    def test_completion_requires_matching_identities_tests_and_mandatory_passes(self):
        project, result, plan = self.fixture()
        result = replace(result, checks=[replace(c, status="pass", acknowledged=False) for c in result.checks])
        statuses = {"tasks": {t.id: "done" for t in plan.tasks},
                    "findings": {f.id: "done" for f in plan.findings}}
        evidence = {"tests": {"status": "passed", "source_fingerprint": project.source_fingerprint,
                              "analyzer_version": result.analyzer_version, "profile_digest": result.profile_digest,
                              "results": {key: "passed" for key in plan.required_test_ids}}}
        def evaluate(p=plan, v=result, e=evidence):
            return evaluate_migration_completion(p, v, statuses=statuses, test_evidence=e)
        self.assertTrue(evaluate()["complete"])
        for key in ("source_fingerprint", "analyzer_version", "profile_digest"):
            modified = {"tests": {**evidence["tests"], key: "wrong"}}
            self.assertFalse(evaluate(e=modified)["complete"], key)
            self.assertFalse(evaluate(v=replace(result, **{key: "wrong"}))["complete"], key)
        for value in (None, "skipped", "failed"):
            modified = {"tests": {**evidence["tests"], "results": {**evidence["tests"]["results"], "actions": value}}}
            self.assertFalse(evaluate(e=modified)["complete"])
        checks = [replace(c, status="not_checked", acknowledged=True) if c.rule == "ARCH-FW-001" else c for c in result.checks]
        self.assertFalse(evaluate(v=replace(result, checks=checks))["complete"])
        self.assertFalse(evaluate(p=replace(plan, profile_digest=None))["complete"])
        self.assertFalse(evaluate(e={"tests": {"status": "passed"}})["complete"])
        for invalid in ({"tasks": {"unknown": "done"}}, {"tasks": {plan.tasks[0].id: "bogus"}}):
            with self.assertRaises(ValueError):
                evaluate_migration_completion(plan, result, statuses=invalid, test_evidence=evidence)
            with self.assertRaises(ValueError):
                migration_report(plan, statuses=invalid)

    def test_cli_compares_saved_plan_to_current_inputs(self):
        from nikhi.adhara_sutra.cli import main
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("x = 1\n", encoding="utf-8")
            saved = root / "plan.json"
            def run(*args):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    return main(list(args))
            self.assertEqual(run("migrate", str(root), "--check-source"), 2)
            self.assertEqual(run("migrate", str(root), "--json", "--output", str(saved)), 0)
            self.assertEqual(run("migrate", str(root), "--check-source", "--plan", str(saved)), 0)
            original = json.loads(saved.read_text(encoding="utf-8"))
            for field in ("analyzer_version", "profile_digest"):
                changed = {**original, field: "different"}
                saved.write_text(json.dumps(changed), encoding="utf-8")
                self.assertEqual(run("migrate", str(root), "--check-source", "--plan", str(saved)), 1)
            saved.write_text(json.dumps(original), encoding="utf-8")
            (root / "app.py").write_text("x = 2\n", encoding="utf-8")
            self.assertEqual(run("migrate", str(root), "--check-source", "--plan", str(saved)), 1)
            data = json.loads(saved.read_text(encoding="utf-8"))
            del data["profile_digest"]
            saved.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(run("migrate", str(root), "--check-source", "--plan", str(saved)), 2)

    def test_custom_analyzers_extend_migration_findings(self):
        project, result, _ = self.fixture()

        def analyzer(project, verification):
            return [MigrationFinding(
                id="MIG-TOOL-001", title="Adopt the custom CLI library", severity="warning",
                confidence="observed", detail="A custom CLI layout was detected.",
                recommendation="Route the custom CLI through actions.")]

        plan = analyze_migration(project, result, analyzers=[analyzer])
        finding = next(item for item in plan.findings if item.id == "MIG-TOOL-001")
        self.assertEqual(finding.title, "Adopt the custom CLI library")
        self.assertTrue(any(task.findings == ("MIG-TOOL-001",) for task in plan.tasks))
        report = migration_report(plan, generated_at="fixed")
        self.assertTrue(any(item["id"] == "MIG-TOOL-001" for item in report["findings"]))

    def test_custom_analyzers_must_return_migration_findings(self):
        project, result, _ = self.fixture()
        with self.assertRaises(TypeError):
            analyze_migration(project, result, analyzers=[lambda project, verification: ["nope"]])

    def test_statuses_support_tasks_and_findings(self):
        project, result, plan = self.fixture()
        finding = plan.findings[0]
        task = plan.tasks[0]
        statuses = {"tasks": {task.id: "done"}, "findings": {finding.id: "deferred"}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            path.write_text(json.dumps(statuses), encoding="utf-8")
            loaded = load_statuses(path)
        self.assertEqual(loaded["tasks"][task.id], "done")
        self.assertEqual(loaded["findings"][finding.id], "deferred")
        report = migration_report(plan, statuses=loaded, generated_at="fixed")
        self.assertEqual(next(t for t in report["tasks"] if t["id"] == task.id)["status"], "done")
        self.assertEqual(next(f for f in report["findings"] if f["id"] == finding.id)["status"], "deferred")
        self.assertEqual(report["summary"]["by_status"]["done"], 1)
        self.assertEqual(report["summary"]["findings_by_status"]["deferred"], 1)

    def test_flat_status_file_remains_task_statuses(self):
        project, result, plan = self.fixture()
        task = plan.tasks[0]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            path.write_text(json.dumps({task.id: "in_progress"}), encoding="utf-8")
            loaded = load_statuses(path)
        self.assertEqual(loaded["tasks"][task.id], "in_progress")
        self.assertEqual(loaded["findings"], {})

    def test_dirty_source_change_invalidates_fingerprint_without_git_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "app.py"
            source.write_text("x = 1\n", encoding="utf-8")
            with patch("nikhi.adhara_sutra.discovery._revision", return_value=("same-revision", True)):
                first = ProjectInspector(root).inspect()
                plan = analyze_migration(first, verify(first))
                source.write_text("x = 2\n", encoding="utf-8")
                changed = ProjectInspector(root).inspect()
            self.assertEqual((first.revision, first.dirty), (changed.revision, changed.dirty))
            self.assertFalse(plan.source_matches(changed))

    def test_source_match_detects_revision_change(self):
        project, result, plan = self.fixture()
        self.assertTrue(plan.source_matches(project))
        changed = type(project)(root=project.root, revision="different", dirty=project.dirty,
                                files=project.files, modules=project.modules, dependencies=project.dependencies,
                                findings=project.findings, imports=project.imports, errors=project.errors)
        self.assertFalse(plan.source_matches(changed))

    def test_plan_records_compatibility_risks(self):
        project, result, plan = self.fixture()
        self.assertTrue(any(plan.profile_version in risk for risk in plan.compatibility_risks))
        self.assertTrue(any("schema_version" in risk for risk in plan.compatibility_risks))
        self.assertIn("Compatibility risks", render_markdown(migration_report(plan, generated_at="fixed")))

    def test_plan_identifies_behavioral_regression_tests(self):
        project, result, plan = self.fixture()
        self.assertTrue(any("Action `ping`" in test for test in plan.regression_tests))
        self.assertTrue(any("HTTP" in test for test in plan.regression_tests))
        report = migration_report(plan, generated_at="fixed")
        self.assertEqual(report["regression_tests"], list(plan.regression_tests))
        self.assertIn("Behavioral regression tests", render_markdown(report))

    def test_completion_is_not_evidenced_without_tests(self):
        project, result, plan = self.fixture()
        all_done = {"tasks": {t.id: "done" for t in plan.tasks},
                    "findings": {f.id: "done" for f in plan.findings}}
        evaluation = evaluate_migration_completion(plan, result, statuses=all_done)
        self.assertFalse(evaluation["complete"])
        self.assertIn("test evidence", " ".join(evaluation["reasons"]).lower())

    def test_completion_requires_verification_and_evidence(self):
        project, result, plan = self.fixture()
        all_done = {"tasks": {t.id: "done" for t in plan.tasks},
                    "findings": {f.id: "done" for f in plan.findings}}
        evidence = {"tests": {"status": "passed", "command": "unittest", "revision": project.revision}}
        evaluation = evaluate_migration_completion(plan, result, statuses=all_done, test_evidence=evidence)
        self.assertEqual(evaluation["status"], "incomplete")  # verify not strict-pass in this fixture
        self.assertIn("architecture verification", " ".join(evaluation["reasons"]).lower())
        # when verification and tasks/findings are satisfied, missing/bad tests means not evidenced
        class _Pass:
            status = "pass"

        bad = evaluate_migration_completion(plan, _Pass(), statuses=all_done,
                                            test_evidence={"tests": {"status": "failed", "revision": project.revision}})
        self.assertEqual(bad["status"], "incomplete")
        missing = evaluate_migration_completion(plan, _Pass(), statuses=all_done)
        self.assertEqual(missing["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
