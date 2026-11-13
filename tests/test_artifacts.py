import io
import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ArtifactStore


class ArtifactStoreTests(unittest.TestCase):
    def test_put_returns_a_reference_and_supports_read_and_delete(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            reference = store.put(io.BytesIO(b"payload"), media_type="text/plain")
            self.assertEqual(set(reference), {"artifact_id", "size_bytes", "media_type"})
            self.assertEqual(reference["size_bytes"], 7)
            self.assertEqual(reference["media_type"], "text/plain")
            with store.open(reference["artifact_id"]) as handle:
                self.assertEqual(handle.read(), b"payload")
            store.delete(reference["artifact_id"])
            with self.assertRaises(FileNotFoundError):
                store.open(reference["artifact_id"])
            with self.assertRaises(FileNotFoundError):
                store.delete(reference["artifact_id"])

    def test_invalid_sources_and_identifiers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            with self.assertRaises(TypeError):
                store.put(io.StringIO("text"))
            with self.assertRaises(ValueError):
                store.put(io.BytesIO(b"data"), media_type=" ")
            self.assertEqual(list(Path(directory).iterdir()), [])
            for artifact_id in ("../escape", "g" * 32, "abc"):
                with self.subTest(artifact_id=artifact_id), self.assertRaises(ValueError):
                    store.open(artifact_id)


if __name__ == "__main__":
    unittest.main()
