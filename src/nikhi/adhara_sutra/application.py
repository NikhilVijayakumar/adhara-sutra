"""A small application runtime for versioned JSON-line requests."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import re
import sys
import threading
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter
from typing import Any, Callable, TextIO
from weakref import WeakValueDictionary

from ._version import __version__

_ACTION = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*$")
_LOG = logging.getLogger(__name__)
_MAX_LINE = 1024 * 1024
_EXIT_INVALID_INVOCATION = 2
_EXIT_INITIALIZATION_FAILED = 3
_EXIT_ACTION_FAILED = 4
_EXIT_PROTOCOL_FAILED = 8
_EXIT_INTERNAL_FAILED = 10
_ERROR_EXIT_CODES = {
    "PROTOCOL_INVALID_MESSAGE": _EXIT_PROTOCOL_FAILED,
    "PROTOCOL_INVALID_STATE": _EXIT_PROTOCOL_FAILED,
    "PROTOCOL_UNSUPPORTED_VERSION": _EXIT_PROTOCOL_FAILED,
    "RUNTIME_NOT_READY": _EXIT_INITIALIZATION_FAILED,
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


@dataclass(frozen=True)
class ApplicationContext:
    """Access to registered runtime facilities for a request or the application."""

    services: dict[str, Any]
    config: dict[str, Any]
    metadata: dict[str, Any]
    _emit: Callable[[dict[str, Any]], None] | None = field(default=None, repr=False)

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
        self._emit({"kind": "event", "protocol_version": "1.0",
                    "request_id": self.metadata.get("request_id"), "event": event, "data": data})


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
                 validate_config: Callable[[dict[str, Any]], None] | None = None):
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise ApplicationDefinitionError("INVALID_APPLICATION_NAME", "name", "Application name must be a non-empty string without surrounding whitespace")
        if not isinstance(version, str) or not version.strip() or version != version.strip():
            raise ApplicationDefinitionError("INVALID_APPLICATION_VERSION", "version", "Application version must be a non-empty string without surrounding whitespace")
        if config is not None and not isinstance(config, dict):
            raise ApplicationDefinitionError("INVALID_APPLICATION_CONFIG", "config", "Configuration must be a dictionary")
        self.name, self.version = name, version
        self.context = ApplicationContext({}, dict(config or {}), {})
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
        return [{"name": name, "input_schema": meta["validate"] is not None, "output_schema": meta["output"] is not None}
                for name, meta in sorted(self._actions.items())]

    def service(self, name: str, factory: Callable[[ApplicationContext], Any], *,
                depends_on: tuple[str, ...] = ()) -> None:
        """Register a service or connector factory with its named dependencies."""
        if self.state != "created" or not isinstance(name, str) or not name or name in self._services:
            raise ValueError("Service name must be unique and registration must precede startup")
        if not callable(factory) or not isinstance(depends_on, (list, tuple)) or any(not isinstance(dep, str) or not dep for dep in depends_on):
            raise ValueError("Factory must be callable and dependencies must be service names")
        self._services[name] = (factory, tuple(depends_on))

    async def start(self) -> None:
        self._transition("initializing")
        try:
            if self._validate_config is not None:
                try:
                    validated = self._validate_config(self.context.config)
                except (ValueError, TypeError) as exc:
                    raise BootstrapError("INVALID_CONFIGURATION", "Application configuration is invalid") from exc
                if isinstance(validated, dict):
                    self.context = ApplicationContext(self.context.services, validated, self.context.metadata)
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
        except BaseException:
            self._transition("failed")
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
            await self._stack.aclose()
        except Exception:
            self._transition("failed")
            self.context.services.clear()
            raise
        finally:
            self.context.services.clear()
        self._transition("stopped")

    async def dispatch(self, request: Any, *,
                       emit: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        request_id = request.get("request_id") if isinstance(request, dict) else None
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
            else:
                if self.state not in ("ready", "running"):
                    raise ProtocolError("RUNTIME_NOT_READY", "Application is not ready")
                if name not in self._actions:
                    raise ProtocolError("ACTION_NOT_FOUND", "Action is not registered")
                meta = self._actions[name]
                handler, validate, output = meta["handler"], meta["validate"], meta["output"]
                if validate is not None:
                    try:
                        payload = validate(payload)
                    except (ValueError, TypeError) as exc:
                        raise ProtocolError("ACTION_VALIDATION_FAILED", "Invalid action payload",
                                            details=str(exc) or None) from exc
                request_context = ApplicationContext(self.context.services, self.context.config,
                                                     {"request_id": request_id, "action": name}, emit)
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
            error = {"code": exc.code, "message": str(exc), "retryable": False}
            if exc.details is not None:
                error["details"] = exc.details
            return self._response(request_id, error=error)
        except Exception:
            _LOG.exception("Action execution failed")
            return self._response(request_id, error={"code": "RUNTIME_EXECUTION_FAILED", "message": "Action execution failed", "retryable": None})

    @staticmethod
    def _response(request_id: Any, *, data: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"kind": "response", "protocol_version": "1.0", "request_id": request_id,
                "success": error is None, "data": data, "error": error}

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

        def send_event(event: dict[str, Any]) -> None:
            target.write(json.dumps(event, allow_nan=False) + "\n")
            target.flush()

        try:
            while True:
                line = await asyncio.to_thread(source.readline, _MAX_LINE + 1)
                if not line:
                    break
                handled = True
                fatal = len(line.encode("utf-8")) > _MAX_LINE or not line.endswith("\n")
                if fatal:
                    response = self._response(None, error={"code": "PROTOCOL_INVALID_MESSAGE", "message": "Message too large or incomplete", "retryable": False})
                    exit_code = _EXIT_PROTOCOL_FAILED
                else:
                    try:
                        request = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Invalid JSON constant")))
                        if not negotiated and isinstance(request, dict) and request.get("action") != "system.hello":
                            raise ProtocolError("PROTOCOL_INVALID_STATE", "Handshake required")
                        response = await self.dispatch(request, emit=send_event)
                        if isinstance(request, dict) and request.get("action") == "system.hello" and response["success"]:
                            negotiated = True
                    except (ValueError, ProtocolError) as exc:
                        code = exc.code if isinstance(exc, ProtocolError) else "PROTOCOL_INVALID_MESSAGE"
                        response = self._response(None, error={"code": code, "message": str(exc) if isinstance(exc, ProtocolError) else "Invalid JSON", "retryable": False})
                    exit_code = self._exit_code(response, persistent)
                target.write(json.dumps(response, allow_nan=False) + "\n")
                target.flush()
                if fatal or not persistent:
                    break
            if not persistent and not handled:
                exit_code = _EXIT_INVALID_INVOCATION
            return exit_code
        finally:
            await self.stop()

    @staticmethod
    def _exit_code(response: dict[str, Any], persistent: bool) -> int:
        """Map a response to a process exit code; persistent action failures do not end the session."""
        if response["success"] or persistent:
            return 0
        return _ERROR_EXIT_CODES.get(response["error"]["code"], _EXIT_ACTION_FAILED)

    def run(self, *, persistent: bool = False) -> int:
        """Run the CLI from a synchronous entry point and return its process exit code."""
        try:
            return asyncio.run(self.serve(persistent=persistent))
        except Exception:
            _LOG.exception("Application runtime failed")
            return _EXIT_INTERNAL_FAILED
