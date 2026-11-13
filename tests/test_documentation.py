"""Documentation structure and link validation (FR-DOC-001, FR-DOC-006, FR-DOC-007)."""

import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import validate_documentation

ROOT = Path(__file__).resolve().parents[1]


class DocumentationValidationTests(unittest.TestCase):
    def test_migration_guide_has_required_sections(self):
        problems = validate_documentation(
            ROOT / "docs" / "migration.md",
            required_sections=("Scope", "Workflow", "Compatibility requirements",
                               "Limitations", "Recovery procedures"))
        self.assertEqual(problems, [])

    def test_repository_documentation_links_resolve(self):
        for document in sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
            self.assertEqual(validate_documentation(document), [], document.name)

    def test_packaging_guide_covers_compatibility(self):
        problems = validate_documentation(
            ROOT / "docs" / "packaging.md",
            required_sections=("Supported platforms", "Locating the Python backend",
                               "External executables", "Public API", "Deprecation policy",
                               "Compatibility and upgrades"))
        self.assertEqual(problems, [])

    def test_missing_sections_and_broken_links_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "guide.md"
            document.write_text("# Guide\n\n[missing](missing.md)\n", encoding="utf-8")
            problems = validate_documentation(document, required_sections=("Overview",))
        self.assertIn("missing required section: Overview", problems)
        self.assertIn("broken local link: missing.md", problems)


if __name__ == "__main__":
    unittest.main()
