import json
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import PathBoundary, PathViolation


class FileUtilitiesTests(unittest.TestCase):
    def test_text_and_json_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            files = PathBoundary(directory)
            files.write_text("note.txt", "hello \u2603")
            self.assertEqual(files.read_text("note.txt"), "hello \u2603")
            files.write_json("data.json", {"name": "\u2603", "items": [1, True]})
            self.assertEqual(files.read_json("data.json"), {"name": "\u2603", "items": [1, True]})
            with self.assertRaises(json.JSONDecodeError):
                files.read_json("note.txt")
            with self.assertRaises(ValueError):
                files.write_json("data.json", float("nan"))
            self.assertEqual(files.read_json("data.json")["name"], "\u2603")

    def test_rejects_outside_paths_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            files = PathBoundary(root)
            outside = Path(directory) / "outside.txt"
            for write in (lambda: files.write_text(outside, "bad"),
                          lambda: files.write_json("../outside.txt", {})):
                with self.assertRaises(PathViolation):
                    write()
            self.assertFalse(outside.exists())
            with self.assertRaises(FileNotFoundError):
                files.write_text("missing/file.txt", "bad")


if __name__ == "__main__":
    unittest.main()
