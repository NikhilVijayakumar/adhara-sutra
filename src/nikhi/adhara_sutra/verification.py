"""Deterministic architecture conformance checks over a discovered project."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .discovery import Evidence, Finding, ProjectProfile

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
    Rule("ARCH-FW-001", "Framework application", "error",
         "The project creates an Application with the framework."),
    Rule("ARCH-FW-002", "Registered actions", "warning",
         "The application registers at least one action."),
    Rule("ARCH-ENTRY-001", "Runtime entry point", "error",
         "The application has an entry point that starts the framework runtime."),
    Rule("ARCH-CONN-001", "Managed HTTP connector", "warning",
         "HTTP access goes through the managed connector instead of a direct client."),
    Rule("ARCH-CONN-002", "Managed external CLI connector", "warning",
         "External programs run through the managed connector instead of subprocess."),
    Rule("ARCH-CONN-003", "Managed SQLite connector", "warning",
         "Database access goes through the managed connector instead of sqlite3 directly."),
    Rule("ARCH-STATE-001", "Scoped application state", "warning",
         "Application state is accessed through the request-scoped context."),
    Rule("ARCH-JOB-001", "Managed job execution", "warning",
         "Long-running work uses the managed job manager."),
)
_CATALOG = {rule.id: rule for rule in RULE_CATALOG}


@dataclass(frozen=True)
class ArchitectureProfile:
    """A versioned set of project requirements used to select and configure rules."""

    version: str = "1"
    required_files: tuple[str, ...] = ()
    required_directories: tuple[str, ...] = ()
    forbidden_imports: tuple[tuple[str, str], ...] = ()


def default_profile() -> ArchitectureProfile:
    return ArchitectureProfile(version="1", required_files=("pyproject.toml",))


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

    def to_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "title": self.title, "status": self.status,
                "severity": self.severity, "detail": self.detail,
                "evidence": [asdict(item) for item in self.evidence],
                "remediation": self.remediation}


@dataclass
class VerificationResult:
    """The deterministic result of evaluating an architecture profile."""

    profile_version: str
    checks: list[Check]

    @property
    def status(self) -> str:
        statuses = {check.status for check in self.checks}
        if FAIL in statuses:
            return FAIL
        if NEEDS_REVIEW in statuses:
            return NEEDS_REVIEW
        if PASS in statuses:
            return PASS
        return NOT_CHECKED

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": {"version": self.profile_version},
            "status": self.status,
            "summary": {status: sum(1 for check in self.checks if check.status == status)
                        for status in _STATUSES},
            "checks": [check.to_dict() for check in self.checks],
        }


def verify(project: ProjectProfile, profile: ArchitectureProfile | None = None) -> VerificationResult:
    """Evaluate the rule catalog against one inspected project."""
    profile = profile or default_profile()
    checks = [
        _required_files(project, profile),
        _required_directories(project, profile),
        _modules(project),
        _parse_errors(project),
        _forbidden_imports(project, profile),
        _framework(project),
        _actions(project),
        _entry_point(project),
        _connector(project, "ARCH-CONN-001", "HTTP", "use the managed HttpClient"),
        _connector(project, "ARCH-CONN-002", "external CLI", "use the managed ExternalCommand"),
        _connector(project, "ARCH-CONN-003", "SQLite", "use the managed SQLiteDatabase"),
        _state(project),
        _jobs(project),
    ]
    return VerificationResult(profile_version=profile.version, checks=checks)


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
    evidence = tuple(item for error in project.errors[:5] for item in error.evidence)
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
        evidence = tuple(Evidence(**item) for _, _, items in found[:3] for item in items[:3])
        detail = "; ".join(f"{name}: {remediation}" for name, remediation, _ in found)
        return _check("ARCH-DEP-001", FAIL, detail=detail, evidence=evidence,
                      remediation="Replace the forbidden dependencies with supported alternatives")
    return _check("ARCH-DEP-001", PASS, detail="No forbidden dependencies found")


def _framework(project: ProjectProfile) -> Check:
    applications = project.by_kind("application")
    if not applications:
        return _check("ARCH-FW-001", FAIL, detail="No Application was created with the framework",
                      remediation="Create an Application and register the project's actions")
    return _check("ARCH-FW-001", PASS, detail=f"Application found: {applications[0].name}",
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
    runtime = [entry for entry in entries if entry.name in ("app.run()", "application.run()")]
    if runtime:
        return _check("ARCH-ENTRY-001", PASS, detail="The application starts through the framework runtime",
                      evidence=runtime[0].evidence)
    if entries:
        return _check("ARCH-ENTRY-001", NEEDS_REVIEW,
                      detail="An entry point was found, but it does not call the framework runtime",
                      evidence=tuple(item for entry in entries[:3] for item in entry.evidence),
                      remediation="Call app.run() or app.serve() from the application entry point")
    return _check("ARCH-ENTRY-001", FAIL, detail="No application entry point was found",
                  remediation="Add an entry point that starts the application runtime")


def _connector(project: ProjectProfile, rule_id: str, integration: str, remediation: str) -> Check:
    if not project.by_kind("application"):
        return _check(rule_id, NOT_CHECKED, detail="No Application was detected")
    findings = [finding for finding in project.by_kind("integration") if finding.name == integration]
    direct = [finding for finding in findings if not _is_framework_path(finding)]
    if direct:
        evidence = tuple(item for finding in direct[:3] for item in finding.evidence)
        return _check(rule_id, NEEDS_REVIEW,
                      detail=f"{len(direct)} direct {integration} integration(s) detected",
                      evidence=evidence, remediation=remediation)
    return _check(rule_id, PASS, detail=f"No direct {integration} integration detected")


def _state(project: ProjectProfile) -> Check:
    findings = project.by_kind("state")
    if not findings:
        return _check("ARCH-STATE-001", NOT_CHECKED, detail="No application state access detected")
    return _check("ARCH-STATE-001", PASS, detail="Application state is accessed through the request context",
                  evidence=tuple(item for finding in findings[:5] for item in finding.evidence))


def _jobs(project: ProjectProfile) -> Check:
    jobs = project.by_kind("job")
    access = project.by_kind("job_access")
    if not jobs and not access:
        return _check("ARCH-JOB-001", NOT_CHECKED, detail="No job execution detected")
    evidence = tuple(item for finding in [*jobs[:3], *access[:3]] for item in finding.evidence)
    return _check("ARCH-JOB-001", PASS, detail="Long-running work uses the managed job manager",
                  evidence=evidence)


def _is_framework_path(finding: Finding) -> bool:
    return any("nikhi/adhara_sutra/" in evidence.path for evidence in finding.evidence)
