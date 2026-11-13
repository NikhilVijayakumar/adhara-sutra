import tempfile
import unittest
from pathlib import Path

from nikhi.adhara_sutra import ConnectorError, SQLiteDatabase


def create_items(db):
    db.execute("CREATE TABLE items (name TEXT NOT NULL)")


def add_item(db):
    db.execute("INSERT INTO items VALUES (?)", ("first",))


class SQLiteMigrationTests(unittest.TestCase):
    def test_versions_persist_and_new_migrations_apply_once(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "db.sqlite")
            with SQLiteDatabase(path) as db:
                self.assertEqual(db.migrate([(1, create_items)]), [1])
                self.assertEqual(db.migrate([(1, create_items)]), [])
            with SQLiteDatabase(path) as db:
                self.assertEqual(db.migrate([(1, create_items), (2, add_item)]), [2])
                self.assertEqual(db.query("SELECT * FROM items"), [{"name": "first"}])
                with self.assertRaises(ConnectorError):
                    db.migrate([(2, add_item)])

    def test_failure_rolls_back_all_pending_changes_and_history(self):
        def fail(db):
            db.execute("INSERT INTO items VALUES ('partial')")
            raise RuntimeError("migration failed")
        with SQLiteDatabase() as db:
            db.migrate([(1, create_items)])
            with self.assertRaises(RuntimeError):
                db.migrate([(1, create_items), (2, add_item), (3, fail)])
            self.assertEqual(db.query("SELECT * FROM items"), [])
            self.assertEqual(db.query("SELECT version FROM adhara_schema_migrations"), [{"version": 1}])
            self.assertEqual(db.migrate([(1, create_items), (2, add_item)]), [2])

    def test_rejects_invalid_versions_and_nested_transaction(self):
        with SQLiteDatabase() as db:
            for entries in [[(0, create_items)], [(1, create_items), (1, add_item)], [(True, create_items)]]:
                with self.subTest(entries=entries), self.assertRaises(ValueError):
                    db.migrate(entries)
            with self.assertRaises(TypeError):
                db.migrate([(1, None)])
            with db.transaction(), self.assertRaises(ConnectorError):
                db.migrate([])
