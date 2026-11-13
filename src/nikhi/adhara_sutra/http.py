"""Reusable outbound HTTP connector built on the optional httpx dependency."""

from __future__ import annotations

import json as _json
import math
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Mapping

from .application import ConnectorError as _ConnectorError

_INSTALL_HINT = "Install the HTTP extra: pip install nikhi-adhara-sutra[http]"


class ConnectorError(_ConnectorError):
    """HTTP connector failure that reports its connector identity."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, connector="http", **kwargs)


@dataclass(frozen=True)
class HttpResponse:
    """A completed HTTP response with its status, headers, body, and URL."""

    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def text(self, encoding: str = "utf-8") -> str:
        return self.body.decode(encoding, errors="replace")

    def json(self) -> Any:
        return _json.loads(self.body)

    def raise_for_status(self) -> "HttpResponse":
        """Raise a connector error for a non-success status, retrying only when safe."""
        if not self.ok:
            retryable = self.status >= 500 or self.status in (408, 429)
            raise ConnectorError(f"HTTP {self.status} for {self.url}",
                                 retryable=retryable, details={"status": self.status})
        return self


class HttpStreamResponse:
    """A response whose body is consumed incrementally inside its context."""

    def __init__(self, response: Any, httpx: Any) -> None:
        self._response = response
        self._httpx = httpx
        self.status = response.status_code
        self.headers = dict(response.headers)
        self.url = str(response.url)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def raise_for_status(self) -> "HttpStreamResponse":
        if not self.ok:
            raise ConnectorError(f"HTTP {self.status} for {self.url}",
                                 retryable=self.status >= 500 or self.status in (408, 429),
                                 details={"status": self.status})
        return self

    def iter_bytes(self, chunk_size: int | None = None) -> Iterator[bytes]:
        """Yield decoded response bytes; a stream can be consumed only once."""
        try:
            yield from self._response.iter_bytes(chunk_size=chunk_size)
        except self._httpx.HTTPError as exc:
            raise ConnectorError(f"HTTP response stream failed: {exc}", retryable=True,
                                 details={"outcome": "unknown"}) from exc


class HttpClient:
    """A synchronous HTTP client that owns one reusable connection pool."""

    def __init__(self, *, base_url: str = "", timeout: float = 30.0,
                 headers: Mapping[str, str] | None = None,
                 auth: tuple[str, str] | None = None,
                 verify: bool = True, follow_redirects: bool = True,
                 max_retries: int = 0, retry_delay: float = 0.0) -> None:
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        if (isinstance(retry_delay, bool) or not isinstance(retry_delay, (int, float))
                or not math.isfinite(retry_delay) or retry_delay < 0):
            raise ValueError("retry_delay must be a finite non-negative number")
        self.base_url = base_url
        self.timeout = timeout
        self.headers = dict(headers or {})
        self.auth = auth
        self.verify = verify
        self.follow_redirects = follow_redirects
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
        self._httpx = None

    def __enter__(self) -> "HttpClient":
        try:
            import httpx
        except ImportError as exc:
            raise ConnectorError(f"The HTTP connector requires httpx. {_INSTALL_HINT}",
                                 retryable=False) from exc
        self._httpx = httpx
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout,
                                    headers=self.headers, auth=self.auth, verify=self.verify,
                                    follow_redirects=self.follow_redirects)
        return self

    def __exit__(self, *exc: Any) -> bool:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._httpx = None
        return False

    def health(self) -> bool:
        """Report whether the connection pool is initialized."""
        return self._client is not None

    def request(self, method: str, url: str, *, headers: Mapping[str, str] | None = None,
                params: Mapping[str, Any] | None = None, content: bytes | str | None = None,
                json: Any = None, timeout: float | None = None) -> HttpResponse:
        client, httpx = self._client, self._httpx
        if client is None or httpx is None:
            raise ConnectorError("The HTTP connector is not started", retryable=False)
        options: dict[str, Any] = {}
        if timeout is not None:
            options["timeout"] = timeout
        # Limit automatic retries to safe methods and replayable request bodies.
        retries = self.max_retries if method.upper() in {"GET", "HEAD", "OPTIONS"} else 0
        for attempt in range(retries + 1):
            try:
                response = client.request(method, url, headers=headers, params=params,
                                          content=content, json=json, **options)
            except httpx.HTTPError as exc:
                transient = isinstance(exc, (httpx.NetworkError, httpx.TimeoutException,
                                             httpx.RemoteProtocolError))
                if transient and attempt < retries:
                    time.sleep(self.retry_delay)
                    continue
                not_sent = isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout,
                                            httpx.PoolTimeout, httpx.UnsupportedProtocol))
                raise ConnectorError(f"HTTP {method.upper()} {url} failed: {exc}",
                                     retryable=transient, code="CONNECTOR_TIMEOUT"
                                     if isinstance(exc, httpx.TimeoutException) else "CONNECTOR_FAILURE",
                                     details={"outcome": "not_sent" if not_sent else "unknown"}) from exc
            if (response.status_code in (408, 429, 500, 502, 503, 504)
                    and attempt < retries):
                response.close()
                time.sleep(self.retry_delay)
                continue
            break
        return HttpResponse(status=response.status_code, headers=dict(response.headers),
                            body=response.content, url=str(response.url))

    def get(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("GET", url, **kwargs)

    @contextmanager
    def stream(self, method: str, url: str, *, headers: Mapping[str, str] | None = None,
               params: Mapping[str, Any] | None = None, content: bytes | str | None = None,
               json: Any = None, timeout: float | None = None) -> Iterator[HttpStreamResponse]:
        """Open a response stream; exiting the context closes the response."""
        client, httpx = self._client, self._httpx
        if client is None or httpx is None:
            raise ConnectorError("The HTTP connector is not started", retryable=False)
        options: dict[str, Any] = {}
        if timeout is not None:
            options["timeout"] = timeout
        manager = client.stream(method, url, headers=headers, params=params,
                                content=content, json=json, **options)
        try:
            response = manager.__enter__()
        except httpx.HTTPError as exc:
            not_sent = isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout,
                                        httpx.PoolTimeout, httpx.UnsupportedProtocol))
            transient = isinstance(exc, (httpx.NetworkError, httpx.TimeoutException,
                                         httpx.RemoteProtocolError))
            raise ConnectorError(f"HTTP {method.upper()} {url} failed: {exc}",
                                 retryable=transient, code="CONNECTOR_TIMEOUT"
                                 if isinstance(exc, httpx.TimeoutException) else "CONNECTOR_FAILURE",
                                 details={"outcome": "not_sent" if not_sent else "unknown"}) from exc
        try:
            yield HttpStreamResponse(response, httpx)
        finally:
            manager.__exit__(*sys.exc_info())

    def post(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("HEAD", url, **kwargs)
