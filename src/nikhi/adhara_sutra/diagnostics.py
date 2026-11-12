"""Structured, request-correlated diagnostics kept off the protocol stream."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, TextIO

_REQUEST: ContextVar[dict[str, Any]] = ContextVar("adhara_request", default={})
_STRUCTURED = "_adhara_structured"
_REDACTED = "[REDACTED]"
_SENSITIVE_WORDS = ("password", "passwd", "secret", "token", "apikey", "authorization", "credential",
                    "privatekey", "accesskey", "cookie", "sessionid")
_SENSITIVE_ASSIGNMENT = re.compile(
    r"""(?i)(\b(?:password|passwd|secret|token|api[_-]?key|authorization|credential|private[_-]?key|"""
    r"""access[_-]?key|client[_-]?secret)\b["']?\s*\]?\s*[=:]\s*)(["'])(.*?)\2""")
_AUTH_HEADER = re.compile(r"(?i)\b(authorization\s*[:=]\s*)(?:bearer|basic|token)\s+[^\s,;]+")
_SENSITIVE_PLAIN = re.compile(
    r"""(?i)(\b(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret)\b\s*=\s*)"""
    r"""([^\s&,;"']+)""")


def _sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return any(word in normalized for word in _SENSITIVE_WORDS)


def redact(value: Any) -> Any:
    """Return a copy of a value with sensitive keys and quoted assignments masked."""
    if isinstance(value, dict):
        return {key: _REDACTED if isinstance(key, str) and _sensitive_key(key) else redact(item)
                for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        value = _SENSITIVE_ASSIGNMENT.sub(
            lambda match: f"{match.group(1)}{match.group(2)}{_REDACTED}{match.group(2)}", value)
        return _AUTH_HEADER.sub(lambda match: f"{match.group(1)}{_REDACTED}", value)
    return value


def redact_text(value: str) -> str:
    """Redact quoted or bare sensitive assignments from free-form text."""
    return _SENSITIVE_PLAIN.sub(lambda match: f"{match.group(1)}{_REDACTED}", redact(value))


class RequestContextFilter(logging.Filter):
    """Attach the active request's correlation fields to a log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = _REQUEST.get()
        record.request_id = context.get("request_id")
        record.action = context.get("action")
        record.job_id = context.get("job_id")
        return True


def _redact_arg(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, BaseException):
        return redact_text(str(value))
    return value


class RedactionFilter(logging.Filter):
    """Redact sensitive assignments before any handler, including the default one, formats a record."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)
        if isinstance(record.args, tuple):
            record.args = tuple(_redact_arg(arg) for arg in record.args)
        elif isinstance(record.args, dict):
            record.args = {key: _redact_arg(value) for key, value in record.args.items()}
        if record.exc_info and not record.exc_text:
            record.exc_text = redact_text(logging.Formatter().formatException(record.exc_info))
        return True


class JsonFormatter(logging.Formatter):
    """Render one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage()),
            "request_id": getattr(record, "request_id", None),
            "action": getattr(record, "action", None),
            "job_id": getattr(record, "job_id", None),
        }
        if record.exc_info:
            payload["exception"] = redact_text(self.formatException(record.exc_info))
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
