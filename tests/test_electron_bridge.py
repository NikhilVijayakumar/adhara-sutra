"""Electron bridge tests run against a representative Python runtime fixture (FR-TEST-009)."""

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class ElectronBridgeIntegrationTests(unittest.TestCase):
    def test_bridge_against_python_fixture(self):
        result = subprocess.run(["node", "--test", "bridge/test/bridge.test.js"],
                                cwd=ROOT, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
