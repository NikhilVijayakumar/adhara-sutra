"""Architecture rules are documented once with stable identifiers (FR-DOC-005)."""

import re
import unittest
from pathlib import Path

from nikhi.adhara_sutra.verification import RULE_CATALOG

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs" / "architecture-rules.md"


class RuleReferenceTests(unittest.TestCase):
    def test_every_catalogued_rule_is_documented_with_its_purpose(self):
        text = REFERENCE.read_text(encoding="utf-8")
        rows = re.findall(r"^\| `(ARCH-[A-Z]+-\d{3})` \| (.+?) \| (error|warning) \| (.+?) \|$",
                          text, re.MULTILINE)
        self.assertEqual({row[0] for row in rows}, {rule.id for rule in RULE_CATALOG})
        for rule in RULE_CATALOG:
            self.assertIn((rule.id, rule.title, rule.severity, rule.description), rows)

    def test_rule_identifiers_are_unique_and_well_formed(self):
        identifiers = [rule.id for rule in RULE_CATALOG]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for identifier in identifiers:
            self.assertRegex(identifier, r"^ARCH-[A-Z]+-\d{3}$")


if __name__ == "__main__":
    unittest.main()
