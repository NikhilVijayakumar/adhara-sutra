"""In-process background jobs with bounded concurrency, progress, and cancellation."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import time
from typing import Any, Callable, Protocol
from uuid import uuid4

from .diagnostics import _REQUEST, RedactionFilter

_LOG = logging.getLogger(__name__)
_LOG.addFilter(RedactionFilter())
_TERMINAL = {"succeeded", "failed", "cancelled", "interrupted"}


class JobStore(Protocol):
    """Durable storage for managed job metadata."""

    def save(self, record: dict[str, Any]) -> None: ...
    def load_all(self) -> list[dict[str, Any]]: ...
    def update(self, job_id: str, **changes: Any) -> None: ...


class SQLiteJobStore:
    """Persist job metadata in a managed SQLite database."""

    def __init__(self, database: Any, namespace: str = "jobs") -> None:
        if not isinstance(namespace, str) or not namespace:
            raise ValueError("namespace must be a non-empty string")
        self.database = database
        self.namespace = namespace
        database.execute(
            "CREATE TABLE IF NOT EXISTS adhara_jobs ("
            "namespace TEXT NOT NULL, job_id TEXT NOT NULL, name TEXT NOT NULL, "
            "state TEXT NOT NULL, result TEXT, error TEXT, "
            "created_at REAL, started_at REAL, finished_at REAL, "
            "PRIMARY KEY (namespace, job_id))")

    def __enter__(self) -> "SQLiteJobStore":
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False

    def save(self, record: dict[str, Any]) -> None:
        self.database.execute(
            "INSERT INTO adhara_jobs (namespace, job_id, name, state, result, error, "
            "created_at, started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(namespace, job_id) DO UPDATE SET name=excluded.name, state=excluded.state, "
            "result=excluded.result, error=excluded.error, created_at=excluded.created_at, "
            "started_at=excluded.started_at, finished_at=excluded.finished_at",
            (self.namespace, record["job_id"], record["name"], record["state"],
             json.dumps(record.get("result"), allow_nan=False) if record.get("result") is not None else None,
             json.dumps(record.get("error"), allow_nan=False) if record.get("error") is not None else None,
             record.get("created_at"), record.get("started_at"), record.get("finished_at")))

    def update(self, job_id: str, **changes: Any) -> None:
        fields, values = [], []
        for key, value in changes.items():
            if key in ("result", "error"):
                value = json.dumps(value, allow_nan=False) if value is not None else None
            fields.append(f"{key} = ?")
            values.append(value)
        if not fields:
            return
        values.extend([self.namespace, job_id])
        self.database.execute(f"UPDATE adhara_jobs SET {', '.join(fields)} WHERE namespace = ? AND job_id = ?",
                              values)

    def load_all(self) -> list[dict[str, Any]]:
        rows = self.database.query(
            "SELECT job_id, name, state, result, error, created_at, started_at, finished_at "
            "FROM adhara_jobs WHERE namespace = ? ORDER BY created_at", (self.namespace,))
        records = []
        for row in rows:
            records.append({
                "job_id": row["job_id"], "name": row["name"], "state": row["state"],
                "result": json.loads(row["result"]) if row["result"] is not None else None,
                "error": json.loads(row["error"]) if row["error"] is not None else None,
                "created_at": row["created_at"], "started_at": row["started_at"],
                "finished_at": row["finished_at"],
            })
        return records


class JobQueueFull(RuntimeError):
    """The bounded job queue cannot accept another submission."""


class JobManager:
    """Own registered job handlers and the in-process execution records."""

    def __init__(self, registry: dict[str, tuple[Callable[..., Any], float | None]],
                 context_factory: Callable[[str, str, Callable | None, dict[str, Any]], Any], *,
                 max_concurrent: int = 4, max_queued: int = 64,
                 store: JobStore | None = None, recover_on_start: bool = False):
        self._registry = registry
        self._context_factory = context_factory
        self._max_concurrent = max_concurrent
        self._max_queued = max_queued
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._jobs: dict[str, dict[str, Any]] = {}
        self._tasks: set[asyncio.Task] = set()
        self._store = store
        if store is not None and recover_on_start:
            self._recover()

    def _recover(self) -> None:
        """Mark persisted non-terminal jobs as interrupted (owner no longer running)."""
        for record in self._store.load_all():
            if record["state"] in _TERMINAL:
                self._jobs[record["job_id"]] = {**record, "event": asyncio.Event()}
                self._jobs[record["job_id"]]["event"].set()
                continue
            recovered = {**record, "state": "interrupted",
                         "error": {"code": "JOB_INTERRUPTED",
                                   "message": "Owning process exited before the job reached a terminal state"},
                         "finished_at": record.get("finished_at") or time.time(),
                         "event": asyncio.Event()}
            recovered["event"].set()
            self._jobs[recovered["job_id"]] = recovered
            self._store.save(self._snapshot(recovered))

    @staticmethod
    def _snapshot(record: dict[str, Any]) -> dict[str, Any]:
        return {key: record.get(key) for key in
                ("job_id", "name", "state", "result", "error", "created_at", "started_at", "finished_at")}

    def _persist(self, record: dict[str, Any]) -> None:
        if self._store is not None:
            self._store.save(self._snapshot(record))

    def submit(self, name: str, payload: Any, emit: Callable[[dict[str, Any]], None] | None,
               session_state: dict[str, Any]) -> str:
        """Schedule a registered job and return its identifier."""
        if name not in self._registry:
            raise ValueError(f"Unregistered job: {name}")
        queued = sum(1 for record in self._jobs.values() if record["state"] == "queued")
        if queued >= self._max_queued:
            raise JobQueueFull(f"Job queue is full ({self._max_queued} waiting)")
        job_id = uuid4().hex
        record = {"job_id": job_id, "name": name, "state": "queued", "result": None, "error": None,
                  "created_at": time.time(), "started_at": None, "finished_at": None,
                  "event": asyncio.Event()}
        self._jobs[job_id] = record
        self._persist(record)
        context = self._context_factory(job_id, name, emit, session_state)
        task = asyncio.create_task(self._run(record, self._registry[name], payload, context))
        record["task"] = task
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(lambda done: self._finalize(record, done))
        return job_id

    def _finalize(self, record: dict[str, Any], task: asyncio.Task) -> None:
        """Record a terminal state for a task that ended outside the normal path."""
        if record["state"] not in _TERMINAL:
            record["state"] = "cancelled" if task.cancelled() else "failed"
            if record["state"] == "failed":
                record["error"] = {"code": "JOB_FAILED", "message": "Job task ended unexpectedly"}
            record["finished_at"] = record["finished_at"] or time.time()
            record["event"].set()
            self._persist(record)

    async def _run(self, record: dict[str, Any], entry: tuple[Callable[..., Any], float | None],
                   payload: Any, context: Any) -> None:
        handler, timeout = entry
        token = _REQUEST.set({"request_id": None, "action": f"job.{record['name']}", "job_id": record["job_id"]})
        try:
            async with self._semaphore:
                record["state"] = "running"
                record["started_at"] = time.time()
                self._persist(record)
                outcome = handler(payload, context)
                if inspect.isawaitable(outcome):
                    outcome = await asyncio.wait_for(outcome, timeout)
                record["result"] = outcome
                record["state"] = "succeeded"
        except asyncio.CancelledError:
            record["state"] = "cancelled"
            raise
        except TimeoutError:
            record["state"] = "failed"
            record["error"] = {"code": "JOB_TIMEOUT", "message": "Job timed out"}
            _LOG.error("Job timed out: %s", record["name"])
        except Exception as exc:
            record["state"] = "failed"
            record["error"] = {"code": "JOB_FAILED", "message": str(exc) or type(exc).__name__}
            _LOG.exception("Job failed: %s", record["name"])
        finally:
            record["finished_at"] = time.time()
            record["event"].set()
            self._persist(record)
            _REQUEST.reset(token)

    def status(self, job_id: str) -> dict[str, Any] | None:
        """Return a snapshot of one job, or None when the identifier is unknown."""
        record = self._jobs.get(job_id)
        if record is None:
            return None
        return {key: record[key] for key in ("job_id", "name", "state", "result", "error",
                                             "created_at", "started_at", "finished_at")}

    def list(self) -> list[dict[str, Any]]:
        """Return snapshots of every job in submission order."""
        return [self.status(job_id) for job_id in self._jobs]

    def cancel(self, job_id: str) -> bool:
        """Request cancellation; returns False when the job is unknown or already terminal."""
        record = self._jobs.get(job_id)
        if record is None or record["state"] in _TERMINAL:
            return False
        task = record.get("task")
        if task is None:
            return False
        task.cancel()
        return True

    async def wait(self, job_id: str) -> dict[str, Any]:
        """Wait for a job to reach a terminal state and return its snapshot."""
        record = self._jobs.get(job_id)
        if record is None:
            raise KeyError(f"Unknown job: {job_id}")
        await record["event"].wait()
        return self.status(job_id)

    async def shutdown(self) -> None:
        """Cancel every active job and wait for the tasks to finish."""
        for record in self._jobs.values():
            if record["state"] not in _TERMINAL:
                task = record.get("task")
                if task is not None:
                    task.cancel()
        if self._tasks:
            await asyncio.gather(*list(self._tasks), return_exceptions=True)


class JobService:
    """Per-request job facade that carries the transport and session state."""

    def __init__(self, manager: JobManager, emit: Callable[[dict[str, Any]], None] | None,
                 session_state: dict[str, Any]):
        self._manager = manager
        self._emit = emit
        self._session_state = session_state

    def submit(self, name: str, payload: Any = None) -> str:
        """Submit a registered job and return its identifier."""
        return self._manager.submit(name, payload, self._emit, self._session_state)

    def status(self, job_id: str) -> dict[str, Any] | None:
        return self._manager.status(job_id)

    def list(self) -> list[dict[str, Any]]:
        return self._manager.list()

    def cancel(self, job_id: str) -> bool:
        return self._manager.cancel(job_id)

    async def wait(self, job_id: str) -> dict[str, Any]:
        return await self._manager.wait(job_id)
