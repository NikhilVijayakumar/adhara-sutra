"""Reusable outbound HTTP connector built on the optional httpx dependency."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from typing import Any, Mapping

from .application import ConnectorError

_INSTALL_HINT = "Install the HTTP extra: pip install nikhi-adhara-sutra[http]"


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


class HttpClient:
    """A synchronous HTTP client that owns one reusable connection pool."""

    def __init__(self, *, base_url: str = "", timeout: float = 30.0,
                 headers: Mapping[str, str] | None = None,
                 verify: bool = True, follow_redirects: bool = True) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.headers = dict(headers or {})
        self.verify = verify
        self.follow_redirects = follow_redirects
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
                                    headers=self.headers, verify=self.verify,
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
        try:
            response = client.request(method, url, headers=headers, params=params,
                                      content=content, json=json, **options)
        except httpx.HTTPError as exc:
            not_sent = isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout,
                                        httpx.PoolTimeout, httpx.UnsupportedProtocol))
            raise ConnectorError(f"HTTP {method.upper()} {url} failed: {exc}",
                                 retryable=True,
                                 details={"outcome": "not_sent" if not_sent else "unknown"}) from exc
        return HttpResponse(status=response.status_code, headers=dict(response.headers),
                            body=response.content, url=str(response.url))

    def get(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("GET", url, **kwargs)

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
