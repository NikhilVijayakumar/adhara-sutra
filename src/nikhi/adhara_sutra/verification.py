"""Deterministic architecture conformance checks over a discovered project."""

from __future__ import annotations

import json
import hashlib
from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterable

from .discovery import Evidence, Finding, ProjectProfile

ANALYZER_VERSION = "static-2"

PASS = "pass"
FAIL = "fail"
NEEDS_REVIEW = "needs_review"
NOT_CHECKED = "not_checked"
_STATUSES = (PASS, FAIL, NEEDS_REVIEW, NOT_CHECKED)


@dataclass(frozen=True)
class Rule:
    """One catalogued conformance rule."""

    id: str
    title: str
    severity: str
    description: str


RULE_CATALOG: tuple[Rule, ...] = (
    Rule("ARCH-STRUCT-001", "Required project files", "error",
         "The project contains the files required by the architecture profile."),
    Rule("ARCH-STRUCT-002", "Required project directories", "error",
         "The project contains the directories required by the architecture profile."),
    Rule("ARCH-STRUCT-003", "Python modules", "error",
         "The project contains at least one analyzable Python module."),
    Rule("ARCH-STRUCT-004", "Parseable sources", "error",
         "Every Python module can be parsed, so the analysis is complete."),
    Rule("ARCH-DEP-001", "Forbidden dependencies", "error",
         "The project does not import dependencies forbidden by the architecture profile."),
    Rule("ARCH-LAYER-001", "Module-layer boundaries", "error",
         "Imports respect the module-layer boundaries configured by the architecture profile."),
    Rule("ARCH-FW-001", "Framework application", "error",
         "The project creates an Application with the framework."),
    Rule("ARCH-FW-002", "Registered actions", "warning",
         "The application registers at least one action."),
    Rule("ARCH-ENTRY-001", "Runtime entry point", "error",
         "The application has an entry point that starts the framework runtime."),
    Rule("ARCH-PROTO-001", "CLI protocol integrity", "warning",
         "Recognizes selected direct standard stream access syntax."),
    Rule("ARCH-CONN-001", "Managed HTTP connector", "warning",
         "HTTP access goes through the managed connector instead of a direct client."),
    Rule("ARCH-CONN-002", "Managed external CLI connector", "warning",
         "External programs run through the managed connector instead of subprocess."),
    Rule("ARCH-CONN-003", "Managed SQLite connector", "warning",
         "Database access goes through the managed connector instead of sqlite3 directly."),
    Rule("ARCH-STATE-001", "Scoped application state", "warning",
         "Recognizes selected context state access syntax."),
    Rule("ARCH-JOB-001", "Managed job execution", "warning",
         "Recognizes job decorator or context.jobs access syntax."),
    Rule("ARCH-JOB-002", "Managed background work", "warning",
         "Recognizes selected unmanaged task and thread creation syntax."),
)
_CATALOG = {rule.id: rule for rule in RULE_CATALOG}


DEFAULT_MANDATORY_RULES = ("ARCH-STRUCT-001", "ARCH-STRUCT-003", "ARCH-STRUCT-004",
                           "ARCH-FW-001", "ARCH-FW-002", "ARCH-ENTRY-001")


@dataclass(frozen=True)
class ArchitectureProfile:
    """A versioned set of project requirements used to select and configure rules."""

    version: str = "1"
    required_files: tuple[str, ...] = ()
    required_directories: tuple[str, ...] = ()
    forbidden_imports: tuple[tuple[str, str], ...] = ()
    # (source path prefix, imported module prefix, remediation)
    layer_boundaries: tuple[tuple[str, str, str], ...] = ()
    name: str = "custom"
    mandatory_rules: tuple[str, ...] = DEFAULT_MANDATORY_RULES


def default_profile() -> ArchitectureProfile:
    return ArchitectureProfile(version="1", required_files=("pyproject.toml",), name="minimal")


@dataclass(frozen=True)
class Check:
    """The outcome of evaluating one rule."""

    rule: str
    title: str
    status: str
    severity: str
    detail: str = ""
    evidence: tuple[Evidence, ...] = ()
    remediation: str = ""
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "title": self.title, "status": self.status,
                "severity": self.severity, "detail": self.detail,
                "evidence": [asdict(item) for item in self.evidence],
                "remediation": self.remediation, "acknowledged": self.acknowledged}


RuleEvaluator = Callable[[ProjectProfile, ArchitectureProfile], Check]


def check_for(rule: Rule, status: str, *, detail: str = "",
              evidence: tuple[Evidence, ...] = (), remediation: str = "") -> Check:
    """Build a check for a custom rule; status must be one of the documented statuses."""
    if status not in _STATUSES:
        raise ValueError(f"unknown check status: {status}")
    return Check(rule.id, rule.title, status, rule.severity, detail, evidence, remediation)


@dataclass
class VerificationResult:
    """The deterministic result of evaluating an architecture profile."""

    profile_version: str
    checks: list[Check]
    source_fingerprint: str | None = None
    analyzer_version: str | None = None
    profile_digest: str | None = None
    custom_identity_complete: bool = True
    rules_identity: str | None = None
    profile_name: str = "custom"
    mandatory_rules: tuple[str, ...] = DEFAULT_MANDATORY_RULES

    @property
    def status(self) -> str:
        statuses = {check.status for check in self.checks if not check.acknowledged}
        if FAIL in statuses:
            return FAIL
        if NEEDS_REVIEW in statuses:
            return NEEDS_REVIEW
        if PASS in statuses:
            return PASS
        return NOT_CHECKED

    @property
    def coverage(self) -> dict[str, list[str]]:
        evaluated = sorted({check.rule for check in self.checks if check.status != NOT_CHECKED})
        not_checked = sorted({check.rule for check in self.checks if check.status == NOT_CHECKED} - set(evaluated))
        unresolved = sorted(rule for rule in self.mandatory_rules
                            if len([check for check in self.checks if check.rule == rule]) != 1
                            or next(check for check in self.checks if check.rule == rule).status != PASS)
        return {"evaluated": evaluated, "not_checked": not_checked, "mandatory_unresolved": unresolved}

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": {"name": self.profile_name, "version": self.profile_version},
            "mandatory_rules": list(self.mandatory_rules),
            "coverage": self.coverage,
            "source_fingerprint": self.source_fingerprint,
            "analyzer_version": self.analyzer_version,
            "profile_digest": self.profile_digest,
            "custom_identity_complete": self.custom_identity_complete,
            "rules_identity": self.rules_identity,
            "status": self.status,
            "acknowledged": sum(1 for check in self.checks if check.acknowledged),
            "summary": {status: sum(1 for check in self.checks if check.status == status)
                        for status in _STATUSES},
            "checks": [check.to_dict() for check in self.checks],
        }


BASELINE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class BaselineEntry:
    """One documented, scoped exception for a known violation location."""

    rule: str
    path: str
    snippet: str
    reason: str = ""


@dataclass(frozen=True)
class Baseline:
    """A versioned set of acknowledged violation locations.

    Matching ignores line numbers so unrelated edits do not invalidate the
    baseline, and a check is acknowledged only when every location it reports is
    listed. New locations for the same rule therefore keep blocking.
    """

    entries: tuple[BaselineEntry, ...] = ()
    schema_version: str = BASELINE_SCHEMA_VERSION

    @classmethod
    def capture(cls, result: VerificationResult) -> "Baseline":
        """Build a baseline from the current failing and needs-review evidence."""
        entries = []
        for check in result.checks:
            if check.status not in (FAIL, NEEDS_REVIEW):
                continue
            for item in check.evidence:
                key = (check.rule, item.path, item.snippet)
                entries.append(BaselineEntry(*key))
        return cls(tuple(entries))

    def acknowledges(self, check: Check) -> bool:
        keys = Counter((entry.rule, entry.path, entry.snippet) for entry in self.entries)
        required = Counter((check.rule, item.path, item.snippet) for item in check.evidence)
        return bool(required) and all(keys[key] >= count for key, count in required.items())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Baseline":
        if data.get("schema_version") != BASELINE_SCHEMA_VERSION:
            raise ValueError(f"unsupported baseline schema version: {data.get('schema_version')!r}")
        raw = data.get("entries")
        if not isinstance(raw, list):
            raise ValueError("baseline entries must be a list")
        entries = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise ValueError(f"baseline entry {index} must be an object")
            missing = [name for name in ("rule", "path", "snippet")
                       if not isinstance(item.get(name), str)]
            if missing:
                raise ValueError(f"baseline entry {index} is missing {', '.join(missing)}")
            reason = item.get("reason", "")
            if not isinstance(reason, str):
                raise ValueError(f"baseline entry {index} has a non-text reason")
            entries.append(BaselineEntry(item["rule"], item["path"], item["snippet"], reason))
        return cls(tuple(entries))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version,
                "entries": [asdict(entry) for entry in self.entries]}

    @classmethod
    def load(cls, path: str | Path) -> "Baseline":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except OSError as exc:
            raise ValueError(f"cannot read baseline {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"baseline {path} is not valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"baseline {path} must be a JSON object")
        return cls.from_dict(data)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def apply_baseline(result: VerificationResult, baseline: Baseline) -> VerificationResult:
    """Mark checks whose every reported location is acknowledged in the baseline."""
    return replace(result, checks=[
        replace(check, acknowledged=True) if baseline.acknowledges(check) else check
        for check in result.checks])


def verify(project: ProjectProfile, profile: ArchitectureProfile | None = None, *,
           rules: Iterable[tuple[Rule, RuleEvaluator]] = (),
           rules_identity: str | None = None) -> VerificationResult:
    """Evaluate the rule catalog and any custom rules against one inspected project."""
    profile = profile or default_profile()
    checks = [
        _required_files(project, profile),
        _required_directories(project, profile),
        _modules(project),
        _parse_errors(project),
        _forbidden_imports(project, profile),
        _layer_boundaries(project, profile),
        _framework(project),
        _actions(project),
        _entry_point(project),
        _protocol(project),
        _connector(project, "ARCH-CONN-001", "HTTP", "use the managed HttpClient"),
        _connector(project, "ARCH-CONN-002", "external CLI", "use the managed ExternalCommand"),
        _connector(project, "ARCH-CONN-003", "SQLite", "use the managed SQLiteDatabase"),
        _state(project),
        _jobs(project),
        _background_work(project),
    ]
    rules = tuple(rules)
    for rule, evaluate in rules:
        check = evaluate(project, profile)
        if not isinstance(check, Check) or check.rule != rule.id:
            raise ValueError(f"custom rule {rule.id} must return a Check for that rule")
        checks.append(check)
    config = asdict(profile)
    digest = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    return VerificationResult(profile_version=profile.version, checks=checks,
                              source_fingerprint=project.source_fingerprint, analyzer_version=ANALYZER_VERSION,
                              profile_digest=digest, custom_identity_complete=not rules or bool(rules_identity and rules_identity.strip()),
                              rules_identity=rules_identity if rules else None, profile_name=profile.name,
                              mandatory_rules=profile.mandatory_rules)


def _check(rule_id: str, status: str, *, detail: str = "",
           evidence: tuple[Evidence, ...] = (), remediation: str = "") -> Check:
    rule = _CATALOG[rule_id]
    return Check(rule.id, rule.title, status, rule.severity, detail, evidence, remediation)


def _required_files(project: ProjectProfile, profile: ArchitectureProfile) -> Check:
    if not profile.required_files:
        return _check("ARCH-STRUCT-001", NOT_CHECKED, detail="No required files configured")
    present = set(project.files)
    missing = [path for path in profile.required_files if path not in present]
    if missing:
        return _check("ARCH-STRUCT-001", FAIL, detail=f"Missing required files: {', '.join(missing)}",
                      remediation="Add the missing project files")
    return _check("ARCH-STRUCT-001", PASS, detail=f"Required files present: {', '.join(profile.required_files)}")


def _required_directories(project: ProjectProfile, profile: ArchitectureProfile) -> Check:
    if not profile.required_directories:
        return _check("ARCH-STRUCT-002", NOT_CHECKED, detail="No required directories configured")
    missing = [directory for directory in profile.required_directories
               if not (Path(project.root) / directory).is_dir()]
    if missing:
        return _check("ARCH-STRUCT-002", FAIL, detail=f"Missing required directories: {', '.join(missing)}",
                      remediation="Add the missing project directories")
    return _check("ARCH-STRUCT-002", PASS,
                  detail=f"Required directories present: {', '.join(profile.required_directories)}")


def _modules(project: ProjectProfile) -> Check:
    if not project.modules:
        return _check("ARCH-STRUCT-003", FAIL, detail="No Python modules were found",
                      remediation="Add Python source files to the project")
    return _check("ARCH-STRUCT-003", PASS, detail=f"{len(project.modules)} Python modules found")


def _parse_errors(project: ProjectProfile) -> Check:
    if not project.errors:
        return _check("ARCH-STRUCT-004", PASS, detail="Every Python module parsed")
    evidence = tuple(item for error in project.errors for item in error.evidence)
    return _check("ARCH-STRUCT-004", FAIL, detail=f"{len(project.errors)} module(s) could not be analyzed",
                  evidence=evidence, remediation="Fix the syntax errors and inspect the project again")


def _forbidden_imports(project: ProjectProfile, profile: ArchitectureProfile) -> Check:
    if not profile.forbidden_imports:
        return _check("ARCH-DEP-001", NOT_CHECKED, detail="No forbidden dependencies configured")
    found = []
    for name, remediation in profile.forbidden_imports:
        for dependency in project.dependencies:
            if dependency["name"] == name:
                found.append((name, remediation, dependency["evidence"]))
    if found:
        evidence = tuple(Evidence(**item) for _, _, items in found for item in items)
        detail = "; ".join(f"{name}: {remediation}" for name, remediation, _ in found)
        return _check("ARCH-DEP-001", FAIL, detail=detail, evidence=evidence,
                      remediation="Replace the forbidden dependencies with supported alternatives")
    return _check("ARCH-DEP-001", PASS, detail="No forbidden dependencies found")


def _layer_boundaries(project: ProjectProfile, profile: ArchitectureProfile) -> Check:
    if not profile.layer_boundaries:
        return _check("ARCH-LAYER-001", NOT_CHECKED, detail="No layer boundaries configured")
    violations = []
    for source, imported, remediation in profile.layer_boundaries:
        for name, locations in project.imports.items():
            if name != imported and not name.startswith(imported + "."):
                continue
            for location in locations:
                if _under(location.path, source):
                    violations.append((source, imported, remediation, location))
    if violations:
        detail = "; ".join(f"{source} must not import {imported}: {remediation}"
                           for source, imported, remediation, _ in violations[:3])
        return _check("ARCH-LAYER-001", FAIL, detail=detail,
                      evidence=tuple(location for *_, location in violations),
                      remediation="Route the dependency through the allowed layer or an adapter")
    return _check("ARCH-LAYER-001", PASS,
                  detail=f"Respected {len(profile.layer_boundaries)} configured layer boundary(ies)")


def _under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


def _framework(project: ProjectProfile) -> Check:
    applications = project.by_kind("application")
    if not applications and project.by_kind("framework_unresolved"):
        return _check("ARCH-FW-001", NEEDS_REVIEW, detail="Application binding is outside the supported static subset",
                      evidence=tuple(item for finding in project.by_kind("framework_unresolved") for item in finding.evidence),
                      remediation="Use or review a direct framework Application binding")
    if not applications:
        return _check("ARCH-FW-001", FAIL, detail="No supported framework Application binding was found",
                      remediation="Create an Application and register the project's actions")
    return _check("ARCH-FW-001", PASS, detail=f"Recognized direct framework Application binding: {applications[0].name}",
                  evidence=applications[0].evidence)


def _actions(project: ProjectProfile) -> Check:
    if not project.by_kind("application"):
        return _check("ARCH-FW-002", NOT_CHECKED, detail="No Application was detected")
    actions = project.by_kind("action")
    if not actions:
        return _check("ARCH-FW-002", NEEDS_REVIEW, detail="No registered actions were found",
                      remediation="Register actions with @app.action")
    return _check("ARCH-FW-002", PASS, detail=f"{len(actions)} action(s) registered",
                  evidence=tuple(item for action in actions[:5] for item in action.evidence))


def _entry_point(project: ProjectProfile) -> Check:
    entries = project.by_kind("entry_point")
    runtime = [entry for entry in entries if entry.detail == "application runtime entry"]
    if runtime:
        return _check("ARCH-ENTRY-001", PASS, detail="Recognized a bound application run/serve call",
                      evidence=runtime[0].evidence)
    if entries:
        return _check("ARCH-ENTRY-001", NEEDS_REVIEW,
                      detail="An entry point was found, but it does not call the framework runtime",
                      evidence=tuple(item for entry in entries[:3] for item in entry.evidence),
                      remediation="Call app.run() or app.serve() from the application entry point")
    return _check("ARCH-ENTRY-001", FAIL, detail="No application entry point was found",
                  remediation="Add an entry point that starts the application runtime")


def _protocol(project: ProjectProfile) -> Check:
    if not project.by_kind("application"):
        return _check("ARCH-PROTO-001", NOT_CHECKED, detail="No Application was detected")
    bypasses = project.by_kind("protocol_bypass")
    if bypasses:
        evidence = tuple(item for finding in bypasses for item in finding.evidence)
        return _check("ARCH-PROTO-001", NEEDS_REVIEW,
                      detail=f"{len(bypasses)} direct standard stream use(s) detected",
                      evidence=evidence,
                      remediation="Emit events through context.emit and let the framework runtime own stdin/stdout")
    return _check("ARCH-PROTO-001", PASS, detail="No direct print or sys.stdin/sys.stdout syntax was recognized")


def _connector(project: ProjectProfile, rule_id: str, integration: str, remediation: str) -> Check:
    if not project.by_kind("application"):
        return _check(rule_id, NOT_CHECKED, detail="No Application was detected")
    findings = [finding for finding in project.by_kind("integration") if finding.name == integration]
    direct = [finding for finding in findings if not _is_framework_path(finding)]
    if direct:
        evidence = tuple(item for finding in direct for item in finding.evidence)
        return _check(rule_id, NEEDS_REVIEW,
                      detail=f"{len(direct)} direct {integration} integration(s) detected",
                      evidence=evidence, remediation=remediation)
    return _check(rule_id, PASS, detail=f"No direct {integration} integration detected")


def _state(project: ProjectProfile) -> Check:
    findings = project.by_kind("state")
    if not findings:
        return _check("ARCH-STATE-001", NOT_CHECKED, detail="No application state access detected")
    return _check("ARCH-STATE-001", PASS, detail="Recognized context state access syntax",
                  evidence=tuple(item for finding in findings[:5] for item in finding.evidence))


def _jobs(project: ProjectProfile) -> Check:
    jobs = project.by_kind("job")
    access = project.by_kind("job_access")
    if not jobs and not access:
        return _check("ARCH-JOB-001", NOT_CHECKED, detail="No job execution detected")
    evidence = tuple(item for finding in [*jobs[:3], *access[:3]] for item in finding.evidence)
    return _check("ARCH-JOB-001", PASS, detail="Recognized job decorator or context.jobs access syntax",
                  evidence=evidence)


def _background_work(project: ProjectProfile) -> Check:
    if not project.by_kind("application"):
        return _check("ARCH-JOB-002", NOT_CHECKED, detail="No Application was detected")
    tasks = project.by_kind("unmanaged_task")
    if tasks:
        evidence = tuple(item for finding in tasks for item in finding.evidence)
        return _check("ARCH-JOB-002", NEEDS_REVIEW,
                      detail=f"{len(tasks)} unmanaged background task(s) detected",
                      evidence=evidence,
                      remediation="Register the work with @app.job so it is managed, cancellable, and observable")
    return _check("ARCH-JOB-002", PASS, detail="No supported unmanaged task or thread syntax was recognized")


def _is_framework_path(finding: Finding) -> bool:
    return any("nikhi/adhara_sutra/" in evidence.path for evidence in finding.evidence)
