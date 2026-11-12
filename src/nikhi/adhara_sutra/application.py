"""A small application runtime for versioned JSON-line requests."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import re
import sys
import threading
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter
from typing import Any, Callable, TextIO
from weakref import WeakValueDictionary

from ._version import __version__
from .diagnostics import _REQUEST, configure_logging, redact, redact_text
from .jobs import JobManager, JobService

_ACTION = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*$")
_LOG = logging.getLogger(__name__)
_MAX_LINE = 1024 * 1024
_EXIT_INVALID_INVOCATION = 2
_EXIT_INITIALIZATION_FAILED = 3
_EXIT_ACTION_FAILED = 4
_EXIT_CANCELLED = 6
_EXIT_DEPENDENCY_UNAVAILABLE = 7
_EXIT_PROTOCOL_FAILED = 8
_EXIT_INTERNAL_FAILED = 10
_ERROR_EXIT_CODES = {
    "PROTOCOL_INVALID_MESSAGE": _EXIT_PROTOCOL_FAILED,
    "PROTOCOL_INVALID_STATE": _EXIT_PROTOCOL_FAILED,
    "PROTOCOL_UNSUPPORTED_VERSION": _EXIT_PROTOCOL_FAILED,
    "RUNTIME_NOT_READY": _EXIT_INITIALIZATION_FAILED,
    "CONNECTOR_FAILURE": _EXIT_DEPENDENCY_UNAVAILABLE,
}
_ERROR_CATEGORIES = {
    "PROTOCOL_INVALID_MESSAGE": "protocol",
    "PROTOCOL_INVALID_STATE": "protocol",
    "PROTOCOL_UNSUPPORTED_VERSION": "protocol",
    "ACTION_VALIDATION_FAILED": "validation",
    "ACTION_OUTPUT_INVALID": "validation",
    "ACTION_NOT_FOUND": "action",
    "RUNTIME_NOT_READY": "lifecycle",
    "RUNTIME_EXECUTION_FAILED": "internal",
    "CONNECTOR_FAILURE": "connector",
}
_APPLICATIONS: WeakValueDictionary[str, Application] = WeakValueDictionary()
_APPLICATIONS_LOCK = threading.Lock()


class ApplicationDefinitionError(ValueError):
    """Invalid application definition with a stable code and field name."""

    def __init__(self, code: str, field: str, message: str):
        super().__init__(message)
        self.code = code
        self.field = field


class ProtocolError(Exception):
    """An error safe to return to a protocol caller."""

    def __init__(self, code: str, message: str, *, details: Any = None):
        super().__init__(message)
        self.code = code
        self.details = details


class BootstrapError(RuntimeError):
    """Application startup failed; the original error is available as __cause__."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class ConnectorError(Exception):
    """A connector failure that maps to the connector error category."""

    def __init__(self, message: str, *, retryable: bool = True, details: Any = None):
        super().__init__(message)
        self.retryable = retryable
        self.details = details


def _error(code: str, message: str, *, retryable: bool | None = False,
           details: Any = None) -> dict[str, Any]:
    """Build a protocol error with its stable category."""
    error = {"code": code, "category": _ERROR_CATEGORIES.get(code, "internal"),
             "message": redact_text(message), "retryable": retryable}
    if details is not None:
        error["details"] = redact(details)
    return error


@dataclass(frozen=True)
class ApplicationContext:
    """Access to registered runtime facilities for a request or the application."""

    services: dict[str, Any]
    config: dict[str, Any]
    metadata: dict[str, Any]
    _emit: Callable[[dict[str, Any]], None] | None = field(default=None, repr=False)
    state: dict[str, Any] = field(default_factory=dict)
    session_state: dict[str, Any] = field(default_factory=dict)
    request_state: dict[str, Any] = field(default_factory=dict)
    jobs: Any = None

    def get_service(self, name: str) -> Any:
        """Return a registered service or raise a clear error."""
        if name not in self.services:
            raise LookupError(f"Unregistered capability: {name}")
        return self.services[name]

    def emit(self, event: str, data: Any = None) -> None:
        """Emit a best-effort event correlated with the current request."""
        if self._emit is None:
            return
        if not isinstance(event, str) or not _ACTION.fullmatch(event):
            raise ValueError("Invalid event name")
        envelope = {"kind": "event", "protocol_version": "1.0",
                    "request_id": self.metadata.get("request_id"), "event": event, "data": data}
        if "job_id" in self.metadata:
            envelope["job_id"] = self.metadata["job_id"]
        self._emit(envelope)


_LIFECYCLE_STATES = {"created", "initializing", "ready", "running", "stopping", "stopped", "failed"}
_LIFECYCLE_TRANSITIONS = {
    "created": {"initializing"},
    "initializing": {"ready", "failed"},
    "ready": {"running", "stopping"},
    "running": {"stopping"},
    "stopping": {"stopped", "failed"},
    "stopped": set(),
    "failed": set(),
}


class Application:
    """Register actions and serve requests for a consuming application."""

    def __init__(self, name: str, version: str, *, config: dict[str, Any] | None = None,
                 validate_config: Callable[[dict[str, Any]], None] | None = None,
                 config_file: str | os.PathLike | None = None,
                 max_concurrent_jobs: int = 4, max_queued_jobs: int = 64):
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise ApplicationDefinitionError("INVALID_APPLICATION_NAME", "name", "Application name must be a non-empty string without surrounding whitespace")
        if not isinstance(version, str) or not version.strip() or version != version.strip():
            raise ApplicationDefinitionError("INVALID_APPLICATION_VERSION", "version", "Application version must be a non-empty string without surrounding whitespace")
        if config is not None and not isinstance(config, dict):
            raise ApplicationDefinitionError("INVALID_APPLICATION_CONFIG", "config", "Configuration must be a dictionary")
        if config_file is not None and not isinstance(config_file, (str, os.PathLike)):
            raise ApplicationDefinitionError("INVALID_CONFIG_FILE", "config_file", "Configuration file must be a path")
        if not isinstance(max_concurrent_jobs, int) or max_concurrent_jobs < 1:
            raise ApplicationDefinitionError("INVALID_JOB_CONCURRENCY", "max_concurrent_jobs", "Job concurrency must be a positive integer")
        if not isinstance(max_queued_jobs, int) or max_queued_jobs < 0:
            raise ApplicationDefinitionError("INVALID_JOB_QUEUE", "max_queued_jobs", "Job queue limit must be a non-negative integer")
        self.name, self.version = name, version
        self._state: dict[str, Any] = {}
        self._max_concurrent_jobs, self._max_queued_jobs = max_concurrent_jobs, max_queued_jobs
        self._job_handlers: dict[str, tuple[Callable[..., Any], float | None]] = {}
        self._jobs: JobManager | None = None
        self._base_config = dict(config or {})
        self._config_file = os.fspath(config_file) if config_file is not None else None
        self._config_overrides: dict[str, Any] = {}
        self.context = ApplicationContext({}, dict(self._base_config), {}, state=self._state)
        if validate_config is not None and not callable(validate_config):
            raise ApplicationDefinitionError("INVALID_CONFIG_VALIDATOR", "validate_config", "Configuration validator must be callable")
        self._validate_config = validate_config
        self.state = "created"
        self._actions: dict[str, dict[str, Any]] = {}
        self._services: dict[str, tuple[Callable[..., Any], tuple[str, ...]]] = {}
        self._stack = AsyncExitStack()
        self._lifecycle_handlers: list[Callable[[str, str], Any]] = []
        with _APPLICATIONS_LOCK:
            if name in _APPLICATIONS:
                raise ApplicationDefinitionError("DUPLICATE_APPLICATION_NAME", "name", "Application name is already registered in this process")
            _APPLICATIONS[name] = self

    def on_lifecycle(self, handler: Callable[[str, str], Any]) -> Callable[[str, str], Any]:
        """Register a callback invoked as (previous_state, current_state) on lifecycle transitions."""
        if not callable(handler):
            raise ValueError("Lifecycle handler must be callable")
        self._lifecycle_handlers.append(handler)
        return handler

    def _transition(self, target: str) -> None:
        if target not in _LIFECYCLE_TRANSITIONS.get(self.state, set()):
            raise RuntimeError(f"Invalid lifecycle transition: {self.state} -> {target}")
        previous, self.state = self.state, target
        for handler in list(self._lifecycle_handlers):
            handler(previous, target)

    def action(self, name: str, *, validate: Callable[[dict[str, Any]], Any] | None = None,
               output: Callable[[Any], Any] | None = None) -> Callable:
        """Register a handler (payload, context). Optional validators may transform input/output or raise ValueError/TypeError."""
        if not isinstance(name, str) or not _ACTION.fullmatch(name) or name.startswith(("system.", "protocol.")):
            raise ValueError("Invalid or reserved action name")

        def register(handler: Callable[..., Any]) -> Callable[..., Any]:
            if name in self._actions:
                raise ValueError(f"Action already registered: {name}")
            self._actions[name] = {"handler": handler, "validate": validate, "output": output}
            return handler
        return register

    def list_actions(self) -> list[dict[str, Any]]:
        """Return registered action metadata for diagnostics and documentation."""
        return [{"name": name, "description": inspect.getdoc(meta["handler"]) or "",
                 "input_schema": meta["validate"] is not None, "output_schema": meta["output"] is not None}
                for name, meta in sorted(self._actions.items())]

    def job(self, name: str, *, timeout: float | None = None) -> Callable:
        """Register a background job handler (payload, context); timeout applies to async handlers."""
        if not isinstance(name, str) or not _ACTION.fullmatch(name) or name.startswith(("system.", "protocol.")):
            raise ValueError("Invalid or reserved job name")
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise ValueError("Job timeout must be a positive number")

        def register(handler: Callable[..., Any]) -> Callable[..., Any]:
            if name in self._job_handlers:
                raise ValueError(f"Job already registered: {name}")
            if not callable(handler):
                raise ValueError("Job handler must be callable")
            self._job_handlers[name] = (handler, timeout)
            return handler
        return register

    def list_jobs(self) -> list[dict[str, Any]]:
        """Return registered job metadata for discovery."""
        return [{"name": name, "description": inspect.getdoc(handler) or "", "timeout": timeout}
                for name, (handler, timeout) in sorted(self._job_handlers.items())]

    def service(self, name: str, factory: Callable[[ApplicationContext], Any], *,
                depends_on: tuple[str, ...] = ()) -> None:
        """Register a service or connector factory with its named dependencies."""
        if self.state != "created" or not isinstance(name, str) or not name or name in self._services:
            raise ValueError("Service name must be unique and registration must precede startup")
        if not callable(factory) or not isinstance(depends_on, (list, tuple)) or any(not isinstance(dep, str) or not dep for dep in depends_on):
            raise ValueError("Factory must be callable and dependencies must be service names")
        self._services[name] = (factory, tuple(depends_on))

    def _job_context(self, job_id: str, name: str, emit: Callable[[dict[str, Any]], None] | None,
                     session_state: dict[str, Any]) -> ApplicationContext:
        return ApplicationContext(self.context.services, self.context.config,
                                  {"job_id": job_id, "job": name}, emit,
                                  state=self._state, session_state=session_state, request_state={},
                                  jobs=JobService(self._jobs, emit, session_state))

    def override_config(self, values: dict[str, Any]) -> None:
        """Override configuration at runtime; overrides must precede startup."""
        if not isinstance(values, dict):
            raise ValueError("Configuration overrides must be a dictionary")
        if self.state != "created":
            raise RuntimeError("Configuration overrides must precede startup")
        self._config_overrides.update(values)

    def _merged_config(self) -> dict[str, Any]:
        """Merge defaults, the JSON config file, environment values, then overrides."""
        config = dict(self._base_config)
        path = self._config_file or os.environ.get("ADHARA_CONFIG_FILE")
        if path:
            try:
                with open(path, encoding="utf-8") as handle:
                    loaded = json.load(handle)
            except OSError as exc:
                raise BootstrapError("INVALID_CONFIGURATION", f"Configuration file cannot be read: {path}") from exc
            except ValueError as exc:
                raise BootstrapError("INVALID_CONFIGURATION", f"Configuration file is not valid JSON: {path}") from exc
            if not isinstance(loaded, dict):
                raise BootstrapError("INVALID_CONFIGURATION", f"Configuration file must contain an object: {path}")
            config.update(loaded)
        prefix = "ADHARA_CONFIG_"
        for key, value in os.environ.items():
            if key.startswith(prefix) and len(key) > len(prefix) and key != "ADHARA_CONFIG_FILE":
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
                config[key[len(prefix):].lower()] = value
        config.update(self._config_overrides)
        return config

    async def start(self) -> None:
        self._transition("initializing")
        try:
            config = self._merged_config()
            if self._validate_config is not None:
                try:
                    validated = self._validate_config(config)
                except (ValueError, TypeError) as exc:
                    raise BootstrapError("INVALID_CONFIGURATION", f"Application configuration is invalid: {exc}") from exc
                if isinstance(validated, dict):
                    config = validated
            self.context = ApplicationContext(self.context.services, config, self.context.metadata,
                                              state=self.context.state)
            graph = {name: deps for name, (_, deps) in self._services.items()}
            missing = {dep for deps in graph.values() for dep in deps if dep not in graph}
            if missing:
                raise BootstrapError("MISSING_DEPENDENCY", f"Unregistered dependencies: {', '.join(sorted(missing))}")
            try:
                order = tuple(TopologicalSorter(graph).static_order())
            except CycleError as exc:
                raise BootstrapError("CYCLIC_DEPENDENCY", "Service dependencies contain a cycle") from exc
            for name in order:
                factory, _ = self._services[name]
                resource = factory(self.context)
                if hasattr(resource, "__aenter__"):
                    value = await self._stack.enter_async_context(resource)
                else:
                    value = self._stack.enter_context(resource)
                self.context.services[name] = value
            self._jobs = JobManager(self._job_handlers, self._job_context,
                                    max_concurrent=self._max_concurrent_jobs,
                                    max_queued=self._max_queued_jobs)
            self.context = ApplicationContext(self.context.services, self.context.config,
                                              self.context.metadata, state=self.context.state,
                                              jobs=JobService(self._jobs, None, {}))
        except BaseException:
            self._transition("failed")
            try:
                if self._jobs is not None:
                    await self._jobs.shutdown()
            except Exception:
                _LOG.exception("Job cleanup failed after startup failure")
            try:
                await self._stack.aclose()
            except Exception:
                _LOG.exception("Resource cleanup failed after startup failure")
            self.context.services.clear()
            raise
        self._transition("ready")

    async def stop(self) -> None:
        if self.state in ("stopped", "failed"):
            return
        self._transition("stopping")
        try:
            if self._jobs is not None:
                await self._jobs.shutdown()
            await self._stack.aclose()
        except Exception:
            self._transition("failed")
            self.context.services.clear()
            raise
        finally:
            self.context.services.clear()
        self._transition("stopped")

    async def dispatch(self, request: Any, *,
                       emit: Callable[[dict[str, Any]], None] | None = None,
                       session_state: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = request.get("request_id") if isinstance(request, dict) else None
        action = request.get("action") if isinstance(request, dict) else None
        token = _REQUEST.set({"request_id": request_id, "action": action})
        try:
            if not isinstance(request, dict) or request.get("kind") != "request":
                raise ProtocolError("PROTOCOL_INVALID_MESSAGE", "Expected a request object")
            if request.get("protocol_version") != "1.0":
                raise ProtocolError("PROTOCOL_UNSUPPORTED_VERSION", "Unsupported protocol version")
            if not isinstance(request_id, str) or not request_id:
                raise ProtocolError("PROTOCOL_INVALID_MESSAGE", "A request_id is required")
            name, payload = request.get("action"), request.get("payload")
            if not isinstance(name, str) or not isinstance(payload, dict):
                raise ProtocolError("PROTOCOL_INVALID_MESSAGE", "Action and object payload are required")
            if name == "system.hello":
                result = {"protocol_version": "1.0", "supported_protocol_versions": ["1.0"],
                          "framework_version": __version__, "name": self.name, "version": self.version}
            elif name == "system.help":
                result = {"framework_version": __version__, "actions": self.list_actions(),
                          "jobs": self.list_jobs()}
            elif name == "system.health":
                if self.state not in ("ready", "running"):
                    raise ProtocolError("RUNTIME_NOT_READY", "Application is not ready")
                result = await self._health()
            elif name == "system.cancel":
                if self.state not in ("ready", "running"):
                    raise ProtocolError("RUNTIME_NOT_READY", "Application is not ready")
                job_id = payload.get("job_id")
                if not isinstance(job_id, str) or not job_id:
                    raise ProtocolError("ACTION_VALIDATION_FAILED", "A job_id is required", details="job_id")
                cancelled = bool(self.context.jobs.cancel(job_id))
                result = {"job_id": job_id, "cancelled": cancelled,
                          "status": self.context.jobs.status(job_id)}
            else:
                if self.state not in ("ready", "running"):
                    raise ProtocolError("RUNTIME_NOT_READY", "Application is not ready")
                if name not in self._actions:
                    raise ProtocolError("ACTION_NOT_FOUND", "Action is not registered",
                                        details={"available_actions": sorted(self._actions)})
                meta = self._actions[name]
                handler, validate, output = meta["handler"], meta["validate"], meta["output"]
                if validate is not None:
                    try:
                        payload = validate(payload)
                    except (ValueError, TypeError) as exc:
                        raise ProtocolError("ACTION_VALIDATION_FAILED", "Invalid action payload",
                                            details=str(exc) or None) from exc
                request_context = ApplicationContext(self.context.services, self.context.config,
                                                     {"request_id": request_id, "action": name}, emit,
                                                     state=self._state,
                                                     session_state=session_state if session_state is not None else {},
                                                     request_state={},
                                                     jobs=JobService(self._jobs, emit, session_state or {}) if self._jobs else None)
                result = handler(payload, request_context)
                if inspect.isawaitable(result):
                    result = await result
                if output is not None:
                    try:
                        result = output(result)
                    except (ValueError, TypeError) as exc:
                        raise ProtocolError("ACTION_OUTPUT_INVALID", "Action produced invalid output") from exc
            json.dumps(result, allow_nan=False)
            return self._response(request_id, data=result)
        except ProtocolError as exc:
            return self._response(request_id, error=_error(exc.code, str(exc), details=exc.details))
        except ConnectorError as exc:
            _LOG.error("Connector failure: %s", exc)
            return self._response(request_id, error=_error("CONNECTOR_FAILURE", str(exc) or "Connector failure",
                                                           retryable=exc.retryable, details=exc.details))
        except Exception:
            _LOG.exception("Action execution failed")
            return self._response(request_id, error=_error("RUNTIME_EXECUTION_FAILED", "Action execution failed", retryable=None))
        finally:
            _REQUEST.reset(token)

    @staticmethod
    def _response(request_id: Any, *, data: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"kind": "response", "protocol_version": "1.0", "request_id": request_id,
                "success": error is None, "data": data, "error": error}

    async def _health(self) -> dict[str, Any]:
        """Report services that expose a callable health check."""
        services: dict[str, Any] = {}
        healthy = True
        for name, service in self.context.services.items():
            check = getattr(service, "health", None)
            if not callable(check):
                continue
            try:
                result = check()
                if inspect.isawaitable(result):
                    result = await result
                healthy = healthy and bool(result)
                services[name] = {"status": "ok" if result else "unavailable"}
            except Exception as exc:
                healthy = False
                services[name] = {"status": "unavailable", "error": str(exc) or type(exc).__name__}
        return {"status": "ok" if healthy else "degraded", "state": self.state, "services": services}

    async def serve(self, *, persistent: bool = False, stdin: TextIO | None = None, stdout: TextIO | None = None) -> int:
        """Serve one request, or a sequential persistent session until EOF, and return a process exit code."""
        source, target = stdin or sys.stdin, stdout or sys.stdout
        try:
            await self.start()
        except Exception:
            _LOG.exception("Application initialization failed")
            return _EXIT_INITIALIZATION_FAILED
        self._transition("running")
        negotiated = not persistent
        handled = False
        exit_code = 0
        session_state: dict[str, Any] = {}

        def send_event(event: dict[str, Any]) -> None:
            target.write(json.dumps(event, allow_nan=False) + "\n")
            target.flush()

        failed = False
        try:
            while True:
                line = await asyncio.to_thread(source.readline, _MAX_LINE + 1)
                if not line:
                    break
                handled = True
                fatal = len(line.encode("utf-8")) > _MAX_LINE or not line.endswith("\n")
                if fatal:
                    response = self._response(None, error=_error("PROTOCOL_INVALID_MESSAGE", "Message too large or incomplete"))
                    exit_code = _EXIT_PROTOCOL_FAILED
                else:
                    try:
                        request = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Invalid JSON constant")))
                        if not negotiated and isinstance(request, dict) and request.get("action") != "system.hello":
                            raise ProtocolError("PROTOCOL_INVALID_STATE", "Handshake required")
                        response = await self.dispatch(request, emit=send_event, session_state=session_state)
                        if isinstance(request, dict) and request.get("action") == "system.hello" and response["success"]:
                            negotiated = True
                    except (ValueError, ProtocolError) as exc:
                        code = exc.code if isinstance(exc, ProtocolError) else "PROTOCOL_INVALID_MESSAGE"
                        response = self._response(None, error=_error(code, str(exc) if isinstance(exc, ProtocolError) else "Invalid JSON"))
                    exit_code = self._exit_code(response, persistent)
                target.write(json.dumps(response, allow_nan=False) + "\n")
                target.flush()
                if fatal or not persistent:
                    break
            if not persistent and not handled:
                exit_code = _EXIT_INVALID_INVOCATION
            return exit_code
        except BaseException:
            failed = True
            raise
        finally:
            try:
                await self.stop()
            except Exception:
                _LOG.exception("Application shutdown failed")
                if not failed:
                    raise

    @staticmethod
    def _exit_code(response: dict[str, Any], persistent: bool) -> int:
        """Map a response to a process exit code; persistent action failures do not end the session."""
        if response["success"] or persistent:
            return 0
        return _ERROR_EXIT_CODES.get(response["error"]["code"], _EXIT_ACTION_FAILED)

    def run(self, *, persistent: bool = False) -> int:
        """Run the CLI from a synchronous entry point and return its process exit code."""
        configure_logging()
        try:
            return asyncio.run(self.serve(persistent=persistent))
        except KeyboardInterrupt:
            _LOG.warning("Application interrupted")
            return _EXIT_CANCELLED
        except Exception:
            _LOG.exception("Application runtime failed")
            return _EXIT_INTERNAL_FAILED
