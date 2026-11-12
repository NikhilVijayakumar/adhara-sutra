"""Assemble and render structured implementation reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .discovery import ProjectProfile
from .migration import TASK_STATUSES, MigrationPlan
from .verification import VerificationResult

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


def verification_report(result: VerificationResult, *, generated_at: str | None = None) -> dict[str, Any]:
    """Build the versioned, machine-readable verification report for one result."""
    return {"schema_version": REPORT_SCHEMA_VERSION, "kind": "verification",
            "generated_at": generated_at or _now(), **result.to_dict()}


def migration_report(plan: MigrationPlan, *, statuses: dict[str, str] | None = None,
                     generated_at: str | None = None) -> dict[str, Any]:
    """Build the versioned, machine-readable migration report for one plan."""
    statuses = statuses or {}
    known = {task.id for task in plan.tasks}
    unknown = sorted(set(statuses) - known)
    if unknown:
        raise ValueError(f"unknown migration task id(s): {', '.join(unknown)}")
    tasks = []
    for task in plan.tasks:
        item = task.to_dict()
        item["status"] = statuses.get(task.id, task.status)
        tasks.append(item)
    by_status = {status: 0 for status in TASK_STATUSES}
    by_phase: dict[str, int] = {}
    for task in tasks:
        by_status[task["status"]] += 1
        by_phase[task["phase"]] = by_phase.get(task["phase"], 0) + 1
    body = plan.to_dict()
    body.pop("tasks")
    return {"schema_version": REPORT_SCHEMA_VERSION, "kind": "migration",
            "generated_at": generated_at or _now(), **body,
            "summary": {"findings": len(plan.findings), "tasks": len(tasks),
                        "by_status": by_status,
                        "by_phase": {phase: by_phase[phase] for phase in sorted(by_phase)}},
            "tasks": tasks}


def render_markdown(report: dict[str, Any]) -> str:
    """Render an implementation, verification, or migration report as Markdown."""
    kind = report.get("kind")
    if kind == "verification":
        return _render_verification(report)
    if kind == "migration":
        return _render_migration(report)
    return _render_implementation(report)


def _render_migration(report: dict[str, Any]) -> str:
    source = report["source"]
    revision = source.get("revision") or "unavailable"
    dirty = " (uncommitted changes)" if source.get("dirty") else ""
    summary = report["summary"]
    by_status = summary["by_status"]
    lines = ["# Migration plan", "",
             f"- Schema version: {report['schema_version']}",
             f"- Generated: {report['generated_at']}",
             f"- Source: `{source['root']}` at `{revision}`{dirty}",
             f"- Profile version: {report['profile']['version']}",
             f"- Strategy: {report['strategy']}", "",
             "## Summary", "",
             "| Findings | Tasks | Pending | In progress | Done | Deferred | Blocked |",
             "| --- | --- | --- | --- | --- | --- | --- |",
             f"| {summary['findings']} | {summary['tasks']} | {by_status['pending']} | "
             f"{by_status['in_progress']} | {by_status['done']} | {by_status['deferred']} | "
             f"{by_status['blocked']} |", ""]
    if summary["by_phase"]:
        lines += ["Tasks by phase:", ""]
        lines += [f"- {phase}: {count}" for phase, count in summary["by_phase"].items()]
        lines.append("")
    lines += ["## Findings", ""]
    if not report["findings"]:
        lines += ["_None detected._", ""]
    for finding in report["findings"]:
        lines += [f"### `{finding['id']}` - {finding['title']}", "",
                  f"- Severity: {finding['severity']}",
                  f"- Confidence: {finding['confidence']}"]
        if finding["rule"]:
            lines.append(f"- Rule: `{finding['rule']}`")
        if finding["detail"]:
            lines.append(f"- Detail: {finding['detail']}")
        if finding["recommendation"]:
            lines.append(f"- Recommendation: {finding['recommendation']}")
        for evidence in finding["evidence"]:
            lines.append(f"- Evidence: `{evidence['path']}:{evidence['line']}` - `{evidence['snippet']}`")
        lines.append("")
    lines += ["## Tasks", ""]
    for task in report["tasks"]:
        lines += [f"### `{task['id']}` - {task['title']}", "",
                  f"- Phase: {task['phase']}",
                  f"- Status: {task['status']}",
                  f"- Reversible: {'yes' if task['reversible'] else 'no'}"]
        if task["findings"]:
            lines.append(f"- Findings: {', '.join(f'`{item}`' for item in task['findings'])}")
        if task["verification"]:
            lines.append(f"- Verification: {task['verification']}")
        if task["rollback"]:
            lines.append(f"- Rollback: {task['rollback']}")
        lines.append("")
    for title, key in (("Constraints", "constraints"), ("Completion criteria", "completion"),
                       ("Rollback", "rollback")):
        lines += [f"## {title}", ""]
        lines += [f"- {item}" for item in report[key]]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_verification(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = ["# Architecture verification", "",
             f"- Schema version: {report['schema_version']}",
             f"- Generated: {report['generated_at']}",
             f"- Profile version: {report['profile']['version']}",
             f"- Status: {report['status']}", "",
             "## Summary", "",
             "| Pass | Fail | Needs review | Not checked |",
             "| --- | --- | --- | --- |",
             f"| {summary['pass']} | {summary['fail']} | {summary['needs_review']} | {summary['not_checked']} |", "",
             "## Checks", ""]
    for check in report["checks"]:
        lines += [f"### {check['status'].upper()} `{check['rule']}` - {check['title']}", "",
                  f"- Severity: {check['severity']}"]
        if check["detail"]:
            lines.append(f"- Detail: {check['detail']}")
        if check["remediation"]:
            lines.append(f"- Remediation: {check['remediation']}")
        for evidence in check["evidence"]:
            lines.append(f"- Evidence: `{evidence['path']}:{evidence['line']}` - `{evidence['snippet']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_implementation(report: dict[str, Any]) -> str:
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
            detail = f" - {item['detail']}" if item["detail"] else ""
            lines.append(f"- `{item['name']}` ({item['confidence']}){detail}")
            for evidence in item["evidence"]:
                lines.append(f"  - `{evidence['path']}:{evidence['line']}` - `{evidence['snippet']}`")
        lines.append("")
    lines += ["## Dependencies", ""]
    if report["dependencies"]:
        for dependency in report["dependencies"]:
            locations = ", ".join(f"`{evidence['path']}:{evidence['line']}`"
                                  for evidence in dependency["evidence"][:3])
            suffix = f" - {locations}" if locations else ""
            lines.append(f"- `{dependency['name']}` ({dependency['kind']}){suffix}")
    else:
        lines.append("_None detected._")
    lines.append("")
    if report["errors"]:
        lines += ["## Parse errors", ""]
        for error in report["errors"]:
            lines.append(f"- `{error['name']}` ({error['confidence']}) - {error['detail']}")
            for evidence in error["evidence"]:
                lines.append(f"  - `{evidence['path']}:{evidence['line']}` - `{evidence['snippet']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
