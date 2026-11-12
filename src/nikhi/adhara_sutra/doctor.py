"""Environment and application diagnostics for ``adhara doctor``."""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import sqlite3
import sys
from pathlib import Path
from typing import Any

from ._version import __version__
from .application import PROTOCOL_VERSION, SUPPORTED_PROTOCOL_VERSIONS, Application

_MIN_PYTHON = (3, 12)


def _check(name: str, status: str, detail: str, remediation: str | None = None) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail, "remediation": remediation}


def _overall(checks: list[dict[str, Any]]) -> str:
    if any(check["status"] == "fail" for check in checks):
        return "fail"
    return "warn" if any(check["status"] == "warn" for check in checks) else "ok"


def environment_report() -> dict[str, Any]:
    """Report framework, interpreter, dependency, and configuration diagnostics."""
    version = ".".join(map(str, sys.version_info[:3]))
    required = ".".join(map(str, _MIN_PYTHON))
    checks = [
        _check("python", "ok" if sys.version_info[:2] >= _MIN_PYTHON else "fail",
               f"{version} ({platform.python_implementation()})",
               None if sys.version_info[:2] >= _MIN_PYTHON else f"install Python {required} or newer"),
    ]
    has_httpx = importlib.util.find_spec("httpx") is not None
    checks.append(_check("http_connector", "ok" if has_httpx else "warn",
                         "httpx is installed" if has_httpx else "httpx is not installed",
                         None if has_httpx else "install adhara[http] to use the HTTP connector"))
    checks.append(_check("sqlite", "ok", f"sqlite {sqlite3.sqlite_version}"))

    config_file = os.environ.get("ADHARA_CONFIG_FILE")
    if config_file:
        path = Path(config_file)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a JSON object")
            checks.append(_check("config_file", "ok", str(path)))
        except Exception as exc:
            checks.append(_check("config_file", "fail", f"{path}: {exc}",
                                 "fix the file or unset ADHARA_CONFIG_FILE"))
    else:
        checks.append(_check("config_file", "ok", "ADHARA_CONFIG_FILE is not set"))

    keys = sorted(key for key in os.environ if key.startswith("ADHARA_CONFIG_"))
    detail = f"{len(keys)} ADHARA_CONFIG_* variable(s)" + (": " + ", ".join(keys) if keys else "")
    checks.append(_check("config_environment", "ok", detail))

    return {
        "framework": {"version": __version__, "protocol_version": PROTOCOL_VERSION,
                      "supported_protocol_versions": list(SUPPORTED_PROTOCOL_VERSIONS)},
        "platform": {"python": version, "implementation": platform.python_implementation(),
                     "system": platform.system(), "release": platform.release(),
                     "machine": platform.machine()},
        "checks": checks,
        "application": None,
        "status": _overall(checks),
    }


def application_report(report: dict[str, Any], app: Application) -> dict[str, Any]:
    """Add registered capabilities and readiness to an environment report."""
    started = app.state in ("ready", "running")
    checks = list(report["checks"]) + [
        _check("application", "ok" if started else "warn",
               f"{app.name} {app.version} is {app.state}",
               None if started else "run the application to verify startup readiness"),
    ]
    return {
        **report,
        "application": {
            "name": app.name,
            "version": app.version,
            "state": app.state,
            "actions": [action["name"] for action in app.list_actions()],
            "jobs": [job["name"] for job in app.list_jobs()],
            "services": app.list_services(),
        },
        "checks": checks,
        "status": _overall(checks),
    }


def render_text(report: dict[str, Any]) -> str:
    framework = report["framework"]
    platform_info = report["platform"]
    lines = [
        "AdharaSutra doctor",
        f"framework {framework['version']} (protocol {framework['protocol_version']})",
        f"python {platform_info['python']} on {platform_info['system']} "
        f"{platform_info['release']} ({platform_info['machine']})",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"[{check['status']}] {check['name']}: {check['detail']}")
        if check["remediation"]:
            lines.append(f"       {check['remediation']}")
    app = report["application"]
    if app:
        lines += [
            "",
            f"application {app['name']} {app['version']} ({app['state']})",
            f"  actions: {', '.join(app['actions']) or 'none'}",
            f"  jobs: {', '.join(app['jobs']) or 'none'}",
            f"  services: {', '.join(app['services']) or 'none'}",
        ]
    lines += ["", f"overall: {report['status']}"]
    return "\n".join(lines)
