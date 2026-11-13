"""SQLite-backed application state with explicit, JSON-compatible values."""

from __future__ import annotations

import json
from collections.abc import Iterator, MutableMapping
from typing import Any

from .sqlite import SQLiteDatabase


class SQLiteState(MutableMapping[str, Any]):
    """A persistent mapping over a managed SQLiteDatabase in one namespace.

    Values are JSON snapshots: mutate a retrieved value only after assigning it
    back. The owning SQLiteDatabase controls connection lifetime and threading.
    """

    def __init__(self, database: SQLiteDatabase, namespace: str = "default") -> None:
        if not isinstance(namespace, str) or not namespace:
            raise ValueError("namespace must be a non-empty string")
        self.database = database
        self.namespace = namespace
        database.execute("CREATE TABLE IF NOT EXISTS adhara_persistent_state "
                         "(namespace TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, "
                         "PRIMARY KEY (namespace, key))")

    @staticmethod
    def _key(key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("state keys must be strings")
        return key

    def __getitem__(self, key: str) -> Any:
        row = self.database.query_one("SELECT value FROM adhara_persistent_state "
                                      "WHERE namespace = ? AND key = ?", (self.namespace, self._key(key)))
        if row is None:
            raise KeyError(key)
        return json.loads(row["value"])

    def __setitem__(self, key: str, value: Any) -> None:
        encoded = json.dumps(value, allow_nan=False)
        self.database.execute("INSERT INTO adhara_persistent_state (namespace, key, value) VALUES (?, ?, ?) "
                              "ON CONFLICT(namespace, key) DO UPDATE SET value = excluded.value",
                              (self.namespace, self._key(key), encoded))

    def __delitem__(self, key: str) -> None:
        cursor = self.database.execute("DELETE FROM adhara_persistent_state WHERE namespace = ? AND key = ?",
                                       (self.namespace, self._key(key)))
        if not cursor.rowcount:
            raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        rows = self.database.query("SELECT key FROM adhara_persistent_state WHERE namespace = ? ORDER BY key",
                                   (self.namespace,))
        return iter(row["key"] for row in rows)

    def __len__(self) -> int:
        row = self.database.query_one("SELECT COUNT(*) AS count FROM adhara_persistent_state WHERE namespace = ?",
                                      (self.namespace,))
        return row["count"]
