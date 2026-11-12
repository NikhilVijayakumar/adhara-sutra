"""Assemble and render structured implementation reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .discovery import ProjectProfile

REPORT_SCHEMA_VERSION = "1"

_GROUPS = {
    "entry_point": "Entry points",
    "application": "Applications",
    "action": "Actions",
    "job": "Jobs",
    "service": "Services",
    "integration": "Integrations",
    "cli": "CLI",
    "electron-process": "Electron",
    "electron-ipc": "Electron",
    "state": "State and jobs",
    "job_access": "State and jobs",
}


def implementation_report(profile: ProjectProfile, *, generated_at: str | None = None) -> dict[str, Any]:
    """Build the versioned, machine-readable implementation report for one profile."""
    counts: dict[str, int] = {}
    for finding in profile.findings:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "kind": "implementation",
        "generated_at": generated_at or _now(),
        "source": {"root": profile.root, "revision": profile.revision, "dirty": profile.dirty},
        "summary": {
            "files": len(profile.files),
            "modules": len(profile.modules),
            "dependencies": len(profile.dependencies),
            "findings": counts,
            "parse_errors": len(profile.errors),
        },
        "modules": profile.modules,
        "dependencies": profile.dependencies,
        "findings": [finding.to_dict() for finding in profile.findings],
        "errors": [error.to_dict() for error in profile.errors],
    }


def render_json(report: dict[str, Any]) -> str:
    """Render a report as indented JSON."""
    return json.dumps(report, indent=2, ensure_ascii=False)


def render_markdown(report: dict[str, Any]) -> str:
    """Render a report as human-readable Markdown."""
    source = report["source"]
    revision = source.get("revision") or "unavailable"
    dirty = " (uncommitted changes)" if source.get("dirty") else ""
    lines = ["# Implementation report", "",
             f"- Schema version: {report['schema_version']}",
             f"- Generated: {report['generated_at']}",
             f"- Source: `{source['root']}` at `{revision}`{dirty}", ""]
    summary = report["summary"]
    lines += ["## Summary", "",
              "| Files | Modules | Dependencies | Findings | Parse errors |",
              "| --- | --- | --- | --- | --- |",
              f"| {summary['files']} | {summary['modules']} | {summary['dependencies']} | "
              f"{sum(summary['findings'].values())} | {summary['parse_errors']} |", ""]
    if summary["findings"]:
        lines += ["Findings by kind:", ""]
        lines += [f"- {kind}: {count}" for kind, count in sorted(summary["findings"].items())]
        lines.append("")
    titles = list(dict.fromkeys([*_GROUPS.values(), "Other findings"]))
    for title in titles:
        items = [finding for finding in report["findings"]
                 if _GROUPS.get(finding["kind"], "Other findings") == title]
        if not items:
            continue
        lines += [f"## {title}", ""]
        for item in items:
            detail = f" — {item['detail']}" if item["detail"] else ""
            lines.append(f"- `{item['name']}` ({item['confidence']}){detail}")
            for evidence in item["evidence"]:
                lines.append(f"  - `{evidence['path']}:{evidence['line']}` — `{evidence['snippet']}`")
        lines.append("")
    lines += ["## Dependencies", ""]
    if report["dependencies"]:
        for dependency in report["dependencies"]:
            locations = ", ".join(f"`{evidence['path']}:{evidence['line']}`"
                                  for evidence in dependency["evidence"][:3])
            suffix = f" — {locations}" if locations else ""
            lines.append(f"- `{dependency['name']}` ({dependency['kind']}){suffix}")
    else:
        lines.append("_None detected._")
    lines.append("")
    if report["errors"]:
        lines += ["## Parse errors", ""]
        for error in report["errors"]:
            lines.append(f"- `{error['name']}` ({error['confidence']}) — {error['detail']}")
            for evidence in error["evidence"]:
                lines.append(f"  - `{evidence['path']}:{evidence['line']}` — `{evidence['snippet']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
