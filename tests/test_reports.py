"""Reports expose stable, structured context for coding agents (FR-DEV-005)."""

import json
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import (ProjectInspector, analyze_migration, implementation_report,
                                migration_report, render_json, render_markdown, verify,
                                verification_report)

APP = '''\
from nikhi.adhara_sutra import Application

app = Application("report_fixture", "1.0")


@app.action("ping")
def ping(payload, context):
    return {"pong": True}


if __name__ == "__main__":
    raise SystemExit(app.run())
'''


class ReportTests(unittest.TestCase):
    def inspect(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "pyproject.toml").write_text("", encoding="utf-8")
        (root / "app.py").write_text(APP, encoding="utf-8")
        (root / "ui" / "screen.py").parent.mkdir()
        (root / "ui" / "screen.py").write_text("import httpx\n", encoding="utf-8")
        return ProjectInspector(root).inspect()

    def test_implementation_report_cites_evidence(self):
        report = implementation_report(self.inspect(), generated_at="fixed")
        self.assertEqual(report["schema_version"], "1")
        self.assertEqual(report["kind"], "implementation")
        self.assertEqual(report["generated_at"], "fixed")
        self.assertIn("root", report["source"])
        finding = next(item for item in report["findings"]
                       if item["kind"] == "integration" and item["name"] == "HTTP")
        self.assertEqual(finding["confidence"], "inferred")
        self.assertEqual(finding["evidence"][0]["path"], "ui/screen.py")
        self.assertGreater(finding["evidence"][0]["line"], 0)
        self.assertIn("`HTTP` (inferred)", render_markdown(report))

    def test_verification_report_carries_rules_evidence_and_remediation(self):
        result = verify(self.inspect())
        report = verification_report(result, generated_at="fixed")
        self.assertEqual(report["kind"], "verification")
        self.assertEqual(report["schema_version"], "1")
        self.assertEqual(set(report["summary"]), {"pass", "fail", "needs_review", "not_checked"})
        check = next(item for item in report["checks"] if item["rule"] == "ARCH-CONN-001")
        self.assertEqual(check["status"], "needs_review")
        self.assertEqual(check["evidence"][0]["path"], "ui/screen.py")
        self.assertTrue(check["remediation"])
        self.assertFalse(check["acknowledged"])
        self.assertEqual(json.loads(render_json(report)), report)

    def test_migration_report_lists_verifiable_tasks(self):
        project = self.inspect()
        plan = analyze_migration(project, verify(project))
        self.assertTrue(plan.tasks)
        task = plan.tasks[0]
        report = migration_report(plan, statuses={task.id: "in_progress"}, generated_at="fixed")
        self.assertEqual(report["kind"], "migration")
        self.assertEqual(report["source"]["root"], project.root)
        self.assertTrue(report["constraints"])
        self.assertTrue(report["completion"])
        self.assertTrue(report["rollback"])
        self.assertEqual(report["summary"]["by_status"]["in_progress"], 1)
        item = next(entry for entry in report["tasks"] if entry["id"] == task.id)
        self.assertEqual(item["status"], "in_progress")
        self.assertTrue(item["verification"])
        self.assertTrue(item["rollback"])
        self.assertIn(f"`{task.id}`", render_markdown(report))


if __name__ == "__main__":
    unittest.main()
