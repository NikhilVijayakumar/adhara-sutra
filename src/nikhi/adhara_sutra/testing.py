"""Reusable helpers for testing applications without the CLI protocol."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from .application import Application


class ApplicationTestClient:
    """Start an application and dispatch requests directly, bypassing the protocol transport."""

    def __init__(self, app: Application) -> None:
        self.app = app
        self._started = False

    async def __aenter__(self) -> "ApplicationTestClient":
        if self.app.state == "created":
            self._started = True
            await self.app.start()
        elif self.app.state != "ready":
            raise RuntimeError(f"Application is not testable in state {self.app.state!r}")
        return self

    async def __aexit__(self, *exc: Any) -> bool:
        if self._started:
            await self.app.stop()
        return False

    async def dispatch(self, action: str, payload: dict[str, Any] | None = None, *,
                       request_id: str | None = None) -> dict[str, Any]:
        """Dispatch an action and return the full response envelope."""
        return await self.app.dispatch({"kind": "request", "protocol_version": "1.0",
                                        "request_id": request_id or uuid4().hex,
                                        "action": action, "payload": payload or {}})

    async def call(self, action: str, payload: dict[str, Any] | None = None, *,
                   request_id: str | None = None) -> Any:
        """Dispatch an action and return its data, raising AssertionError on failure."""
        response = await self.dispatch(action, payload, request_id=request_id)
        if not response["success"]:
            error = response["error"]
            raise AssertionError(f"{action} failed: {error['code']}: {error['message']}")
        return response["data"]
