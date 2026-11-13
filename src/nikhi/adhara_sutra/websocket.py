"""Reusable outbound WebSocket connector built on the optional websockets dependency."""

from __future__ import annotations

import asyncio
import sys
from typing import Any, AsyncIterator, Callable

from .application import ConnectorError as _ConnectorError

_INSTALL_HINT = "Install the WebSocket extra: pip install nikhi-adhara-sutra[websocket]"


class ConnectorError(_ConnectorError):
    """WebSocket connector failure that reports its connector identity."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, connector="websocket", **kwargs)


class WebSocketClient:
    """An outbound WebSocket client managed as an application service."""

    def __init__(self, url: str, *, open_timeout: float = 10.0, close_timeout: float = 10.0,
                 max_reconnects: int = 0, reconnect_delay: float = 0.0) -> None:
        if not isinstance(url, str) or not url:
            raise ValueError("url must be a non-empty string")
        if isinstance(max_reconnects, bool) or not isinstance(max_reconnects, int) or max_reconnects < 0:
            raise ValueError("max_reconnects must be a non-negative integer")
        self.url = url
        self.open_timeout = open_timeout
        self.close_timeout = close_timeout
        self.max_reconnects = max_reconnects
        self.reconnect_delay = reconnect_delay
        self._websockets = None
        self._connection: Any = None

    async def __aenter__(self) -> "WebSocketClient":
        try:
            import websockets
        except ImportError as exc:
            raise ConnectorError(f"The WebSocket connector requires websockets. {_INSTALL_HINT}",
                                 retryable=False) from exc
        self._websockets = websockets
        await self.connect()
        return self

    async def __aexit__(self, *exc: Any) -> bool:
        await self.close()
        self._websockets = None
        return False

    def __enter__(self) -> "WebSocketClient":
        raise ConnectorError("WebSocketClient is async; use 'async with WebSocketClient(...)'",
                             retryable=False)

    def __exit__(self, *exc: Any) -> bool:
        return False

    @property
    def connected(self) -> bool:
        connection = self._connection
        if connection is None:
            return False
        closed = getattr(connection, "closed", None)
        if isinstance(closed, bool):
            return not closed
        state = getattr(connection, "state", None)
        name = getattr(state, "name", state)
        return name == "OPEN"

    def health(self) -> bool:
        return self.connected

    async def connect(self) -> None:
        """Open (or reopen) the WebSocket connection."""
        websockets = self._websockets
        if websockets is None:
            try:
                import websockets as websockets  # type: ignore[no-redef]
            except ImportError as exc:
                raise ConnectorError(f"The WebSocket connector requires websockets. {_INSTALL_HINT}",
                                     retryable=False) from exc
            self._websockets = websockets
        try:
            self._connection = await websockets.connect(self.url, open_timeout=self.open_timeout,
                                                        close_timeout=self.close_timeout)
        except asyncio.TimeoutError as exc:
            raise ConnectorError(f"WebSocket connection timed out: {self.url}",
                                 retryable=True, code="CONNECTOR_TIMEOUT") from exc
        except Exception as exc:
            raise ConnectorError(f"WebSocket connection failed: {exc}", retryable=True) from exc

    async def close(self) -> None:
        """Close the connection if it is open."""
        connection = self._connection
        self._connection = None
        if connection is None:
            return
        try:
            await connection.close()
        except Exception:
            pass

    async def send(self, message: str | bytes) -> None:
        """Send a text or binary message."""
        connection = self._require()
        try:
            await connection.send(message)
        except Exception as exc:
            raise self._failure(exc, "send") from exc

    async def receive(self, *, validate: Callable[[Any], Any] | None = None,
                      timeout: float | None = None) -> Any:
        """Receive one message, optionally validating/parsing it."""
        attempts = 0
        while True:
            connection = self._require()
            try:
                message = await asyncio.wait_for(connection.recv(), timeout=timeout)
            except asyncio.TimeoutError as exc:
                raise ConnectorError(f"WebSocket receive timed out: {self.url}",
                                     retryable=True, code="CONNECTOR_TIMEOUT") from exc
            except Exception as exc:
                if attempts < self.max_reconnects:
                    attempts += 1
                    await self._reconnect()
                    continue
                raise self._failure(exc, "receive") from exc
            if validate is None:
                return message
            try:
                return validate(message)
            except Exception as exc:
                raise ConnectorError(f"WebSocket message validation failed: {exc}",
                                     retryable=False, code="CONNECTOR_VALIDATION") from exc

    async def messages(self, *, validate: Callable[[Any], Any] | None = None) -> AsyncIterator[Any]:
        """Yield received messages until the connection closes."""
        while True:
            try:
                yield await self.receive(validate=validate)
            except ConnectorError as exc:
                if exc.retryable and not self.connected and self.max_reconnects <= 0:
                    raise
                raise
            except Exception:
                raise

    async def _reconnect(self) -> None:
        await self.close()
        if self.reconnect_delay:
            await asyncio.sleep(self.reconnect_delay)
        await self.connect()

    def _require(self) -> Any:
        if self._connection is None or not self.connected:
            raise ConnectorError(f"WebSocket is not connected: {self.url}", retryable=False)
        return self._connection

    @staticmethod
    def _failure(exc: Exception, operation: str) -> ConnectorError:
        if isinstance(exc, asyncio.TimeoutError):
            return ConnectorError(f"WebSocket {operation} timed out",
                                  retryable=True, code="CONNECTOR_TIMEOUT")
        return ConnectorError(f"WebSocket {operation} failed: {exc}", retryable=True)
