"""In-process background jobs with bounded concurrency, progress, and cancellation."""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from typing import Any, Callable
from uuid import uuid4

from .diagnostics import _REQUEST, RedactionFilter

_LOG = logging.getLogger(__name__)
_LOG.addFilter(RedactionFilter())
_TERMINAL = {"succeeded", "failed", "cancelled"}


class JobQueueFull(RuntimeError):
    """The bounded job queue cannot accept another submission."""


class JobManager:
    """Own registered job handlers and the in-process execution records."""

    def __init__(self, registry: dict[str, tuple[Callable[..., Any], float | None]],
                 context_factory: Callable[[str, str, Callable | None, dict[str, Any]], Any], *,
                 max_concurrent: int = 4, max_queued: int = 64):
        self._registry = registry
        self._context_factory = context_factory
        self._max_concurrent = max_concurrent
        self._max_queued = max_queued
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._jobs: dict[str, dict[str, Any]] = {}
        self._tasks: set[asyncio.Task] = set()

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
        context = self._context_factory(job_id, name, emit, session_state)
        task = asyncio.create_task(self._run(record, self._registry[name], payload, context))
        record["task"] = task
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(lambda done: self._finalize(record, done))
        return job_id

    @staticmethod
    def _finalize(record: dict[str, Any], task: asyncio.Task) -> None:
        """Record a terminal state for a task that ended outside the normal path."""
        if record["state"] not in _TERMINAL:
            record["state"] = "cancelled" if task.cancelled() else "failed"
            if record["state"] == "failed":
                record["error"] = {"code": "JOB_FAILED", "message": "Job task ended unexpectedly"}
            record["finished_at"] = record["finished_at"] or time.time()
            record["event"].set()

    async def _run(self, record: dict[str, Any], entry: tuple[Callable[..., Any], float | None],
                   payload: Any, context: Any) -> None:
        handler, timeout = entry
        token = _REQUEST.set({"request_id": None, "action": f"job.{record['name']}", "job_id": record["job_id"]})
        try:
            async with self._semaphore:
                record["state"] = "running"
                record["started_at"] = time.time()
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
        record["task"].cancel()
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
                record["task"].cancel()
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
