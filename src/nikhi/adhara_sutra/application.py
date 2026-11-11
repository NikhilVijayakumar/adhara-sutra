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
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from typing import Any, Callable, TextIO
from weakref import WeakValueDictionary

_ACTION = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*$")
_LOG = logging.getLogger(__name__)
_MAX_LINE = 1024 * 1024
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

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


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

    def get_service(self, name: str) -> Any:
        """Return a registered service or raise a clear error."""
        if name not in self.services:
            raise LookupError(f"Unregistered capability: {name}")
        return self.services[name]


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
        self._actions: dict[str, tuple[Callable[..., Any], Callable[..., Any] | None]] = {}
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

    def action(self, name: str, *, validate: Callable[[dict[str, Any]], Any] | None = None) -> Callable:
        """Register a handler accepting (payload, context); validator may raise ValueError."""
        if not isinstance(name, str) or not _ACTION.fullmatch(name) or name.startswith(("system.", "protocol.")):
            raise ValueError("Invalid or reserved action name")

        def register(handler: Callable[..., Any]) -> Callable[..., Any]:
            if name in self._actions:
                raise ValueError(f"Action already registered: {name}")
            self._actions[name] = (handler, validate)
            return handler
        return register

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
                    self._validate_config(self.context.config)
                except (ValueError, TypeError) as exc:
                    raise BootstrapError("INVALID_CONFIGURATION", "Application configuration is invalid") from exc
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

    async def dispatch(self, request: Any) -> dict[str, Any]:
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
                result = {"protocol_version": "1.0", "name": self.name, "version": self.version}
            else:
                if self.state not in ("ready", "running"):
                    raise ProtocolError("RUNTIME_NOT_READY", "Application is not ready")
                if name not in self._actions:
                    raise ProtocolError("ACTION_NOT_FOUND", "Action is not registered")
                handler, validate = self._actions[name]
                if validate is not None:
                    try:
                        payload = validate(payload)
                    except (ValueError, TypeError) as exc:
                        raise ProtocolError("ACTION_VALIDATION_FAILED", "Invalid action payload") from exc
                request_context = ApplicationContext(self.context.services, self.context.config,
                                                     {"request_id": request_id, "action": name})
                result = handler(payload, request_context)
                if inspect.isawaitable(result):
                    result = await result
            json.dumps(result, allow_nan=False)
            return self._response(request_id, data=result)
        except ProtocolError as exc:
            return self._response(request_id, error={"code": exc.code, "message": str(exc), "retryable": False})
        except Exception:
            _LOG.exception("Action execution failed")
            return self._response(request_id, error={"code": "RUNTIME_EXECUTION_FAILED", "message": "Action execution failed", "retryable": None})

    @staticmethod
    def _response(request_id: Any, *, data: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"kind": "response", "protocol_version": "1.0", "request_id": request_id,
                "success": error is None, "data": data, "error": error}

    async def serve(self, *, persistent: bool = False, stdin: TextIO | None = None, stdout: TextIO | None = None) -> None:
        """Serve one request, or a sequential persistent session until EOF."""
        source, target = stdin or sys.stdin, stdout or sys.stdout
        await self.start()
        self._transition("running")
        negotiated = not persistent
        try:
            while True:
                line = await asyncio.to_thread(source.readline, _MAX_LINE + 1)
                if not line:
                    break
                if len(line.encode("utf-8")) > _MAX_LINE or not line.endswith("\n"):
                    response = self._response(None, error={"code": "PROTOCOL_INVALID_MESSAGE", "message": "Message too large or incomplete", "retryable": False})
                    target.write(json.dumps(response) + "\n")
                    target.flush()
                    break
                try:
                    request = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Invalid JSON constant")))
                    if not negotiated and isinstance(request, dict) and request.get("action") != "system.hello":
                        raise ProtocolError("PROTOCOL_INVALID_STATE", "Handshake required")
                    response = await self.dispatch(request)
                    if isinstance(request, dict) and request.get("action") == "system.hello" and response["success"]:
                        negotiated = True
                except (ValueError, ProtocolError) as exc:
                    code = exc.code if isinstance(exc, ProtocolError) else "PROTOCOL_INVALID_MESSAGE"
                    response = self._response(None, error={"code": code, "message": str(exc) if isinstance(exc, ProtocolError) else "Invalid JSON", "retryable": False})
                target.write(json.dumps(response, allow_nan=False) + "\n")
                target.flush()
                if not persistent:
                    break
        finally:
            await self.stop()

    def run(self, *, persistent: bool = False) -> None:
        """Run the CLI from a synchronous application entry point."""
        asyncio.run(self.serve(persistent=persistent))
