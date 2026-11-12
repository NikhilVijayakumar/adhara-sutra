"""Structured, request-correlated diagnostics kept off the protocol stream."""

from __future__ import annotations

import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, TextIO

_REQUEST: ContextVar[dict[str, Any]] = ContextVar("adhara_request", default={})
_STRUCTURED = "_adhara_structured"


class RequestContextFilter(logging.Filter):
    """Attach the active request's correlation fields to a log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = _REQUEST.get()
        record.request_id = context.get("request_id")
        record.action = context.get("action")
        record.job_id = context.get("job_id")
        return True


class JsonFormatter(logging.Formatter):
    """Render one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "action": getattr(record, "action", None),
            "job_id": getattr(record, "job_id", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int | None = None, stream: TextIO | None = None) -> logging.Handler:
    """Install a structured stderr handler; stdout stays reserved for protocol messages.

    The level defaults to ADHARA_LOG_LEVEL (INFO when unset or invalid).
    """
    if level is None:
        level = getattr(logging, os.environ.get("ADHARA_LOG_LEVEL", "INFO").upper(), None)
        if not isinstance(level, int):
            level = logging.INFO
    root = logging.getLogger()
    for existing in root.handlers:
        if getattr(existing, _STRUCTURED, False):
            return existing
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    setattr(handler, _STRUCTURED, True)
    root.addHandler(handler)
    root.setLevel(level)
    return handler
