"""Migration tracking, source-match, and completion evidence (FR-MIG-010/013, NFR-MIG-007/009)."""

import json
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ProjectInspector, analyze_migration, migration_report, verify
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

    def test_source_match_detects_revision_change(self):
        project, result, plan = self.fixture()
        self.assertTrue(plan.source_matches(project))
        changed = type(project)(root=project.root, revision="different", dirty=project.dirty,
                                files=project.files, modules=project.modules, dependencies=project.dependencies,
                                findings=project.findings, imports=project.imports, errors=project.errors)
        self.assertFalse(plan.source_matches(changed))

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
        self.assertEqual(bad["status"], "not_evidenced")
        missing = evaluate_migration_completion(plan, _Pass(), statuses=all_done)
        self.assertEqual(missing["status"], "not_evidenced")


if __name__ == "__main__":
    unittest.main()
