"""The shipped examples stay runnable and show supported integration patterns (FR-DEV-003)."""

import unittest

from examples.basic_app import app as basic_app
from examples.sqlite_repository import create_app
from nikhi.adhara_sutra import ApplicationTestClient


class ExampleTests(unittest.IsolatedAsyncioTestCase):
    async def test_basic_app_answers_the_documented_action(self):
        async with ApplicationTestClient(basic_app) as client:
            self.assertEqual(await client.call("greeting.create", {"name": "world"}),
                             {"message": "Hello, world!"})
            self.assertEqual(await client.call("greeting.create"), {"message": "Hello, world!"})

    async def test_repository_example_persists_through_the_managed_connector(self):
        async with ApplicationTestClient(create_app("repository_test_example")) as client:
            self.assertEqual(await client.call("items.add", {"name": "beta"}), {"added": "beta"})
            await client.call("items.add", {"name": "alpha"})
            self.assertEqual(await client.call("items.list"), {"items": ["alpha", "beta"]})


if __name__ == "__main__":
    unittest.main()
