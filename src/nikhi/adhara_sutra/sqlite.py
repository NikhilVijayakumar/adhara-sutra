"""Managed SQLite connector built on the standard library."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Iterator, Sequence

from .application import ConnectorError


class SQLiteDatabase:
    """One SQLite connection owned by the thread that started the application."""

    def __init__(self, path: str = ":memory:", *, timeout: float = 5.0,
                 pragmas: Sequence[str] = ()) -> None:
        self.path = path
        self.timeout = timeout
        self.pragmas = tuple(pragmas)
        self._connection: sqlite3.Connection | None = None
        self._in_transaction = False

    def __enter__(self) -> "SQLiteDatabase":
        try:
            self._connection = sqlite3.connect(self.path, timeout=self.timeout,
                                               isolation_level=None)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            for statement in self.pragmas:
                self._connection.execute(statement)
        except sqlite3.Error as exc:
            raise ConnectorError(f"SQLite startup failed: {exc}", retryable=False) from exc
        return self

    def __exit__(self, *exc: Any) -> bool:
        if self._connection is not None:
            self._connection.close()
        self._connection = None
        self._in_transaction = False
        return False

    def health(self) -> bool:
        try:
            return self._connection is not None and self._connection.execute("SELECT 1").fetchone()[0] == 1
        except sqlite3.Error:
            return False

    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> sqlite3.Cursor:
        return self._run(lambda connection: connection.execute(sql, tuple(parameters)))

    def executemany(self, sql: str, parameters: Iterable[Iterable[Any]]) -> sqlite3.Cursor:
        return self._run(lambda connection: connection.executemany(
            sql, [tuple(row) for row in parameters]))

    def query(self, sql: str, parameters: Iterable[Any] = ()) -> list[dict[str, Any]]:
        return [dict(row) for row in self.execute(sql, parameters).fetchall()]

    def query_one(self, sql: str, parameters: Iterable[Any] = ()) -> dict[str, Any] | None:
        row = self.execute(sql, parameters).fetchone()
        return dict(row) if row is not None else None

    def integrity_check(self) -> list[str]:
        """Return SQLite integrity-check messages; a healthy database returns ['ok']."""
        return self._run(lambda connection: [row[0] for row in
                         connection.execute("PRAGMA integrity_check").fetchall()])

    def backup(self, destination: str | os.PathLike[str]) -> None:
        """Back up to a new file without replacing an existing destination."""
        connection = self._require()
        if connection.in_transaction:
            raise ConnectorError("Cannot back up during a transaction", retryable=False)
        path = os.fspath(destination)
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError as exc:
            raise ConnectorError(f"SQLite backup destination unavailable: {exc}", retryable=False) from exc
        os.close(descriptor)
        target = None
        try:
            target = sqlite3.connect(path)
            connection.backup(target)
            target.close()
            target = None
        except (sqlite3.Error, OSError) as exc:
            if target is not None:
                target.close()
            try:
                os.unlink(path)
            except OSError:
                pass
            raise ConnectorError(f"SQLite backup failed: {exc}", retryable=False) from exc

    def migrate(self, migrations: Sequence[tuple[int, Callable[["SQLiteDatabase"], None]]]) -> list[int]:
        """Apply ordered, application-owned migrations atomically, once per version.

        Migration functions must use this connector and must not manage their own
        transactions. Pending migrations and their version records commit together.
        """
        entries = list(migrations)
        versions = []
        for version, migration in entries:
            if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
                raise ValueError("migration versions must be positive integers")
            if not callable(migration):
                raise TypeError("migration must be callable")
            if versions and version <= versions[-1]:
                raise ValueError("migration versions must be strictly increasing")
            versions.append(version)
        applied_now = []
        # Serialize migration runners before inspecting the recorded history.
        connection = self._require()
        if self._in_transaction:
            raise ConnectorError("Migrations cannot run inside a transaction", retryable=False)
        try:
            connection.execute("BEGIN IMMEDIATE")
            self._in_transaction = True
            self.execute("CREATE TABLE IF NOT EXISTS adhara_schema_migrations "
                         "(version INTEGER PRIMARY KEY)")
            applied = [row["version"] for row in self.query(
                "SELECT version FROM adhara_schema_migrations ORDER BY version")]
            if applied != versions[:len(applied)]:
                raise ConnectorError("Migration history does not match supplied migrations", retryable=False)
            for version, migration in entries[len(applied):]:
                migration(self)
                self.execute("INSERT INTO adhara_schema_migrations (version) VALUES (?)", (version,))
                applied_now.append(version)
            connection.execute("COMMIT")
        except sqlite3.Error as exc:
            if connection.in_transaction:
                connection.rollback()
            raise ConnectorError(f"SQLite migration failed: {exc}", retryable=False) from exc
        except BaseException:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            self._in_transaction = False
        return applied_now

    @contextmanager
    def transaction(self) -> Iterator["SQLiteDatabase"]:
        """Run statements between an explicit BEGIN and COMMIT or ROLLBACK."""
        connection = self._require()
        if self._in_transaction:
            raise ConnectorError("Nested transactions are not supported", retryable=False)
        self._in_transaction = True
        try:
            connection.execute("BEGIN")
            try:
                yield self
            except BaseException:
                try:
                    connection.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
                raise
            else:
                connection.execute("COMMIT")
        except sqlite3.Error as exc:
            raise ConnectorError(str(exc), retryable=False) from exc
        finally:
            self._in_transaction = False

    def _require(self) -> sqlite3.Connection:
        if self._connection is None:
            raise ConnectorError("The SQLite connector is not started", retryable=False)
        return self._connection

    def _run(self, operation: Any) -> Any:
        connection = self._require()
        try:
            return operation(connection)
        except sqlite3.IntegrityError as exc:
            raise ConnectorError(str(exc), retryable=False) from exc
        except sqlite3.OperationalError as exc:
            message = str(exc).lower()
            raise ConnectorError(str(exc),
                                 retryable="locked" in message or "busy" in message) from exc
        except sqlite3.Error as exc:
            raise ConnectorError(str(exc), retryable=False) from exc
