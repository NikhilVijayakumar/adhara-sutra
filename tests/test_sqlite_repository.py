import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from examples.sqlite_repository import create_app
from nikhi.adhara_sutra import ApplicationTestClient, ConnectorError


class SQLiteRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_repository_uses_managed_connection_and_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "items.sqlite")
            app = create_app("repository_" + uuid4().hex, path)
            async with ApplicationTestClient(app) as client:
                await client.call("items.add", {"name": "one"})
                self.assertEqual(await client.call("items.list"), {"items": ["one"]})
                repository = app.context.get_service("items")
                with self.assertRaises(ConnectorError):
                    repository.add("one")
                self.assertEqual(repository.list_names(), ["one"])
            with self.assertRaises(ConnectorError):
                repository.list_names()
            reopened = create_app("repository_" + uuid4().hex, path)
            async with ApplicationTestClient(reopened) as client:
                self.assertEqual(await client.call("items.list"), {"items": ["one"]})
