"""Deterministic migration analysis and planning for existing applications."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Iterable

from .discovery import Evidence, Finding, ProjectProfile
from .verification import FAIL, NEEDS_REVIEW, VerificationResult

STRATEGIES = ("adapter-first", "incremental", "rebuild")
TASK_STATUSES = ("pending", "in_progress", "done", "deferred", "blocked")
COMPLETION_STATUSES = ("complete", "incomplete", "not_evidenced")

_PHASE_BY_RULE = {
    "ARCH-STRUCT-001": "structure",
    "ARCH-STRUCT-002": "structure",
    "ARCH-STRUCT-003": "structure",
    "ARCH-STRUCT-004": "structure",
    "ARCH-DEP-001": "dependencies",
    "ARCH-FW-001": "runtime",
    "ARCH-FW-002": "runtime",
    "ARCH-ENTRY-001": "entry-points",
    "ARCH-LAYER-001": "dependencies",
    "ARCH-PROTO-001": "contracts",
    "ARCH-CONN-001": "integrations",
    "ARCH-CONN-002": "integrations",
    "ARCH-CONN-003": "integrations",
    "ARCH-STATE-001": "state-jobs",
    "ARCH-JOB-001": "state-jobs",
    "ARCH-JOB-002": "state-jobs",
}
_VERIFICATION_BY_RULE = {
    "ARCH-STRUCT-001": "`adhara verify` reports ARCH-STRUCT-001 as pass.",
    "ARCH-STRUCT-002": "`adhara verify` reports ARCH-STRUCT-002 as pass.",
    "ARCH-STRUCT-003": "`adhara verify` reports ARCH-STRUCT-003 as pass.",
    "ARCH-STRUCT-004": "`adhara verify` reports ARCH-STRUCT-004 as pass.",
    "ARCH-DEP-001": "`adhara verify` reports ARCH-DEP-001 as pass.",
    "ARCH-FW-001": "The migrated runtime starts and `adhara verify` reports ARCH-FW-001 as pass.",
    "ARCH-FW-002": "The existing behavior is reachable through actions and `adhara verify` reports ARCH-FW-002 as pass.",
    "ARCH-ENTRY-001": "The entry point runs through the framework and `adhara verify` reports ARCH-ENTRY-001 as pass.",
    "ARCH-LAYER-001": "Imports respect the configured layers and `adhara verify` reports ARCH-LAYER-001 as pass.",
    "ARCH-PROTO-001": "The application communicates only through the CLI protocol and `adhara verify` reports ARCH-PROTO-001 as pass.",
    "ARCH-CONN-001": "HTTP behavior matches the existing integration and `adhara verify` reports ARCH-CONN-001 as pass.",
    "ARCH-CONN-002": "External command behavior matches the existing integration and `adhara verify` reports ARCH-CONN-002 as pass.",
    "ARCH-CONN-003": "Database behavior matches the existing integration and `adhara verify` reports ARCH-CONN-003 as pass.",
    "ARCH-STATE-001": "State behavior is preserved and `adhara verify` reports ARCH-STATE-001 as pass.",
    "ARCH-JOB-001": "Job behavior is preserved and `adhara verify` reports ARCH-JOB-001 as pass.",
    "ARCH-JOB-002": "Background work is managed and `adhara verify` reports ARCH-JOB-002 as pass.",
}
_STRATEGY_TASKS = {
    "adapter-first": {
        "phase": "integrations",
        "title": "Adopt managed connectors behind the existing interfaces",
        "verification": "Existing integration tests pass with the connector in place.",
        "rollback": "Restore the direct integration and the previous application version.",
    },
    "incremental": {
        "phase": "runtime",
        "title": "Migrate one action or module at a time and verify each unit",
        "verification": "Each migrated unit passes `adhara verify` and its regression tests before the next unit starts.",
        "rollback": "Revert the current unit with version control; earlier verified units remain.",
    },
    "rebuild": {
        "phase": "runtime",
        "title": "Rebuild captured behaviors on the framework while the old application stays runnable",
        "verification": "Rebuilt behaviors match the captured baseline and `adhara verify` passes.",
        "rollback": "Keep the old application runnable until the rebuild is verified, then remove it.",
    },
}


@dataclass(frozen=True)
class MigrationFinding:
    """An actionable gap between the current implementation and the target architecture."""

    id: str
    title: str
    severity: str
    confidence: str
    detail: str
    evidence: tuple[Evidence, ...] = ()
    rule: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "severity": self.severity,
                "confidence": self.confidence, "detail": self.detail,
                "evidence": [asdict(item) for item in self.evidence],
                "rule": self.rule, "recommendation": self.recommendation}


MigrationAnalyzer = Callable[[ProjectProfile, VerificationResult], Iterable[MigrationFinding]]


@dataclass(frozen=True)
class MigrationTask:
    """An independently verifiable unit of migration work."""

    id: str
    phase: str
    title: str
    status: str = "pending"
    findings: tuple[str, ...] = ()
    verification: str = ""
    rollback: str = ""
    reversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "phase": self.phase, "title": self.title,
                "status": self.status, "findings": list(self.findings),
                "verification": self.verification, "rollback": self.rollback,
                "reversible": self.reversible}


@dataclass
class MigrationPlan:
    """A structured, deterministic plan for adopting the framework in an existing project."""

    profile_version: str
    source: dict[str, Any]
    strategy: str
    constraints: tuple[str, ...]
    findings: list[MigrationFinding]
    tasks: list[MigrationTask]
    completion: tuple[str, ...]
    rollback: tuple[str, ...]
    regression_tests: tuple[str, ...] = ()
    compatibility_risks: tuple[str, ...] = ()
    analyzer_version: str | None = None
    profile_digest: str | None = None
    custom_identity_complete: bool = True
    rules_identity: str | None = None
    analyzers_identity: str | None = None
    required_test_ids: tuple[str, ...] = ()
    profile_name: str = "custom"
    mandatory_rules: tuple[str, ...] = ()
    coverage: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"profile": {"name": self.profile_name, "version": self.profile_version}, "source": self.source,
                "mandatory_rules": list(self.mandatory_rules), "coverage": self.coverage,
                "analyzer_version": self.analyzer_version, "profile_digest": self.profile_digest,
                "custom_identity_complete": self.custom_identity_complete,
                "rules_identity": self.rules_identity, "analyzers_identity": self.analyzers_identity,
                "strategy": self.strategy, "constraints": list(self.constraints),
                "findings": [finding.to_dict() for finding in self.findings],
                "tasks": [task.to_dict() for task in self.tasks],
                "completion": list(self.completion), "rollback": list(self.rollback),
                "regression_tests": list(self.regression_tests),
                "required_test_ids": list(self.required_test_ids),
                "compatibility_risks": list(self.compatibility_risks)}

    def source_matches(self, project: ProjectProfile | dict[str, Any]) -> bool:
        """Return whether the plan's analyzed source matches the given project state."""
        current = project if isinstance(project, dict) else {"source_fingerprint": project.source_fingerprint}
        fingerprint = self.source.get("source_fingerprint")
        return bool(fingerprint and fingerprint == current.get("source_fingerprint"))


def analyze_migration(project: ProjectProfile, verification: VerificationResult,
                      *, strategy: str = "incremental",
                      analyzers: Iterable["MigrationAnalyzer"] = (),
                      analyzers_identity: str | None = None) -> MigrationPlan:
    """Derive a migration plan from discovery and architecture verification results."""
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown migration strategy: {strategy}")
    analyzers = tuple(analyzers)
    findings = _findings(project, verification)
    for analyzer in analyzers:
        extra = list(analyzer(project, verification))
        if any(not isinstance(item, MigrationFinding) for item in extra):
            raise TypeError("migration analyzers must return MigrationFinding objects")
        findings.extend(extra)
    findings = sorted({finding.id: finding for finding in findings}.values(),
                      key=lambda item: item.id)
    tasks = _tasks(project, findings, strategy)
    return MigrationPlan(
        profile_version=verification.profile_version,
        profile_name=verification.profile_name,
        mandatory_rules=verification.mandatory_rules,
        coverage=verification.coverage,
        source={"root": project.root, "revision": project.revision, "dirty": project.dirty,
                "source_fingerprint": project.source_fingerprint},
        analyzer_version=verification.analyzer_version,
        profile_digest=verification.profile_digest,
        rules_identity=verification.rules_identity,
        analyzers_identity=analyzers_identity if analyzers else None,
        custom_identity_complete=verification.custom_identity_complete and (not analyzers or bool(analyzers_identity and analyzers_identity.strip())),
        strategy=strategy,
        constraints=(
            "Existing business behavior is preserved unless a change is explicitly authorized.",
            "Existing CLI commands and Electron IPC contracts remain available during migration.",
            "Persistent data is backed up before any schema or write-path change.",
            "Migration changes are applied incrementally and reviewed before they are verified.",
        ),
        findings=findings,
        tasks=tasks,
        completion=(
            "`adhara verify --strict` passes for the migrated project.",
            "The captured regression tests pass.",
            "Existing CLI and Electron contract tests pass.",
            "A database backup and restore have been exercised when persistence changes.",
        ),
        rollback=(
            "Keep the existing application entry point until the migrated runtime is verified.",
            "The plan changes no source files; revert applied changes with version control.",
            "Restore the database backup and the previous application version when persistence changes.",
            "Tasks marked irreversible require a reviewed backup and recovery procedure.",
        ),
        regression_tests=_regression_tests(project),
        required_test_ids=_required_test_ids(project),
        compatibility_risks=_compatibility_risks(verification),
    )


def load_statuses(path: str | Path) -> dict[str, dict[str, str]]:
    """Load recorded migration statuses for tasks and findings.

    Accepts either ``{"tasks": {...}, "findings": {...}}`` or a legacy flat
    object mapping task ids to statuses.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("the status file must contain a JSON object mapping ids to statuses")
    structured = "tasks" in data or "findings" in data
    if structured:
        if not all(isinstance(data.get(key, {}), dict) for key in ("tasks", "findings")):
            raise ValueError("the status file must map 'tasks' and 'findings' to objects")
        tasks = {str(k): str(v) for k, v in data.get("tasks", {}).items()}
        findings = {str(k): str(v) for k, v in data.get("findings", {}).items()}
    else:
        tasks = {str(key): str(value) for key, value in data.items()}
        findings = {}
    invalid = sorted({value for value in [*tasks.values(), *findings.values()] if value not in TASK_STATUSES})
    if invalid:
        raise ValueError(f"invalid task status(es): {', '.join(invalid)}; "
                         f"expected one of {', '.join(TASK_STATUSES)}")
    return {"tasks": tasks, "findings": findings}


def load_test_evidence(path: str | Path) -> dict[str, Any]:
    """Load migration test/behavioral evidence from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("the evidence file must contain a JSON object")
    return data


def evaluate_migration_completion(plan: MigrationPlan, verification: VerificationResult, *,
                                  statuses: dict[str, Any] | None = None,
                                  test_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Evaluate completion from deterministic verification and supplied evidence.

    Completion requires matching captured input identities, mandatory rule passes,
    and explicit passing results for all required behavioral tests.
    """
    statuses = _normalize_statuses(statuses, plan)
    task_statuses, finding_statuses = statuses["tasks"], statuses["findings"]
    reasons: list[str] = []
    incomplete: list[str] = []
    tests = test_evidence.get("tests") if isinstance(test_evidence, dict) else None
    identities = {"source_fingerprint": plan.source.get("source_fingerprint"),
                  "analyzer_version": plan.analyzer_version, "profile_digest": plan.profile_digest}
    for key, value in identities.items():
        if not isinstance(value, str) or not value.strip() or getattr(verification, key, None) != value \
                or not isinstance(tests, dict) or tests.get(key) != value:
            reasons.append(f"{key} is missing or does not match across plan, verification, and test evidence")
    if (not plan.custom_identity_complete or not getattr(verification, "custom_identity_complete", False)
            or plan.rules_identity != getattr(verification, "rules_identity", None)):
        reasons.append("custom evaluator identity is incomplete or mismatched")
    if verification.status != "pass":
        reasons.append(f"architecture verification is {verification.status}, not pass")
        incomplete.append("verification")
    checks = getattr(verification, "checks", ())
    if not plan.mandatory_rules or tuple(plan.mandatory_rules) != tuple(getattr(verification, "mandatory_rules", ())):
        reasons.append("mandatory profile rules are missing or mismatched")
        if "verification" not in incomplete:
            incomplete.append("verification")
    for rule in plan.mandatory_rules:
        matching = [check for check in checks if check.rule == rule]
        if len(matching) != 1 or matching[0].status != "pass":
            reasons.append(f"mandatory rule {rule} has not passed")
            if "verification" not in incomplete:
                incomplete.append("verification")
    unresolved = [f.id for f in plan.findings
                  if finding_statuses.get(f.id, "pending") in ("pending", "in_progress", "blocked")]
    unfinished = [t.id for t in plan.tasks
                  if task_statuses.get(t.id, t.status) in ("pending", "in_progress", "blocked")]
    if unresolved:
        reasons.append(f"unresolved findings remain: {', '.join(unresolved)}")
        incomplete.append("findings")
    if unfinished:
        reasons.append(f"unfinished tasks remain: {', '.join(unfinished)}")
        incomplete.append("tasks")
    if not isinstance(tests, dict):
        reasons.append("behavioral/regression test evidence has not been supplied")
    else:
        if tests.get("status") != "passed":
            reasons.append("test evidence status is not passed")
        results = tests.get("results")
        if not plan.required_test_ids:
            reasons.append("required test identifiers are missing from the plan")
        elif not isinstance(results, dict):
            reasons.append("required test results are missing")
        else:
            for test_id in plan.required_test_ids:
                if results.get(test_id) != "passed":
                    reasons.append(f"required test {test_id} has not passed")
    if not reasons:
        return {"status": "complete", "complete": True, "reasons": [],
                "evidenced": True, "incomplete": [], "tests": tests}
    return {"status": "incomplete" if incomplete else "not_evidenced", "complete": False,
            "reasons": reasons, "evidenced": False, "incomplete": incomplete, "tests": tests}


def _normalize_statuses(statuses: dict[str, Any] | None, plan: MigrationPlan | None = None) -> dict[str, dict[str, str]]:
    if statuses is None:
        return {"tasks": {}, "findings": {}}
    if not isinstance(statuses, dict):
        raise ValueError("statuses must be an object")
    if "tasks" in statuses or "findings" in statuses:
        if set(statuses) - {"tasks", "findings"} or any(not isinstance(statuses.get(k, {}), dict) for k in ("tasks", "findings")):
            raise ValueError("statuses must contain task and finding objects")
        result = {"tasks": dict(statuses.get("tasks", {})), "findings": dict(statuses.get("findings", {}))}
    else:
        result = {"tasks": dict(statuses), "findings": {}}
    for kind, values in result.items():
        if any(not isinstance(k, str) or not isinstance(v, str) or v not in TASK_STATUSES for k, v in values.items()):
            raise ValueError(f"invalid {kind} status or identifier")
        if plan is not None:
            known = {item.id for item in getattr(plan, kind)}
            unknown = set(values) - known
            if unknown:
                raise ValueError(f"unknown migration {kind} id(s): {', '.join(sorted(unknown))}")
    return result


def _required_test_ids(project: ProjectProfile) -> tuple[str, ...]:
    ids = ["actions", "cli"]
    if project.by_kind("electron-process") or project.by_kind("electron-ipc"):
        ids.append("electron")
    integrations = {item.name for item in project.by_kind("integration")}
    ids.extend(key for name, key in (("HTTP", "http"), ("external CLI", "external"), ("SQLite", "sqlite")) if name in integrations)
    if project.by_kind("state"):
        ids.append("state")
    if project.by_kind("job") or project.by_kind("job_access"):
        ids.append("jobs")
    return tuple(ids)


def _findings(project: ProjectProfile, verification: VerificationResult) -> list[MigrationFinding]:
    findings: list[MigrationFinding] = []
    for check in verification.checks:
        if check.status not in (FAIL, NEEDS_REVIEW):
            continue
        findings.append(MigrationFinding(
            id=f"MIG-{check.rule}", title=check.title, severity=check.severity,
            confidence="observed" if check.evidence else "inferred", detail=check.detail,
            evidence=check.evidence, rule=check.rule,
            recommendation=check.remediation or "Review the check and update the implementation."))
    covered = {finding.rule for finding in findings}
    for integration, rule, title, recommendation in (
            ("HTTP", "ARCH-CONN-001", "Adopt the managed HTTP connector",
             "Replace direct HTTP calls with HttpClient behind the existing interface."),
            ("external CLI", "ARCH-CONN-002", "Adopt the managed external CLI connector",
             "Replace subprocess calls with ExternalCommand behind the existing interface."),
            ("SQLite", "ARCH-CONN-003", "Adopt the managed SQLite connector",
             "Replace direct sqlite3 access with SQLiteDatabase behind the existing interface.")):
        if rule in covered:
            continue
        direct = [finding for finding in project.by_kind("integration")
                  if finding.name == integration and not _is_framework_path(finding)]
        if direct:
            findings.append(MigrationFinding(
                id=f"MIG-INT-{integration.upper().replace(' ', '-')}-001", title=title,
                severity="warning", confidence="inferred",
                detail=f"Direct {integration} usage was detected in the existing implementation.",
                evidence=tuple(item for finding in direct[:3] for item in finding.evidence),
                rule=rule, recommendation=recommendation))
    if project.by_kind("cli") or _scripts(project):
        evidence = _first_evidence(project, "cli") or _first_evidence(project, "entry_point")
        findings.append(MigrationFinding(
            id="MIG-CLI-001", title="Preserve existing CLI commands",
            severity="warning", confidence="observed" if evidence else "inferred",
            detail="Existing CLI commands and their output contracts must remain available.",
            evidence=evidence, recommendation="Add CLI contract tests and route commands through actions "
                                              "while preserving names, arguments, and output."))
    if project.by_kind("electron-process") or project.by_kind("electron-ipc"):
        evidence = _first_evidence(project, "electron-ipc") or _first_evidence(project, "electron-process")
        findings.append(MigrationFinding(
            id="MIG-ELECTRON-001", title="Preserve Electron IPC contracts",
            severity="warning", confidence="observed" if evidence else "inferred",
            detail="Electron IPC channels, payloads, and process boundaries must remain stable.",
            evidence=evidence, recommendation="Keep channel names and payloads stable and test the bridge "
                                              "during and after migration."))
    sqlite = [finding for finding in project.by_kind("integration")
              if finding.name == "SQLite" and not _is_framework_path(finding)]
    if sqlite:
        findings.append(MigrationFinding(
            id="MIG-DATA-001", title="Preserve persistent data",
            severity="warning", confidence="inferred",
            detail="Persistent data is present; schema compatibility and write paths must be preserved.",
            evidence=tuple(item for finding in sqlite[:3] for item in finding.evidence),
            recommendation="Back up the database, verify schema compatibility, and test restore "
                           "before changing persistence."))
    return sorted({finding.id: finding for finding in findings}.values(), key=lambda item: item.id)


def _tasks(project: ProjectProfile, findings: list[MigrationFinding],
           strategy: str) -> list[MigrationTask]:
    tasks: list[MigrationTask] = []
    if project.by_kind("action") or project.by_kind("entry_point") or project.by_kind("cli"):
        tasks.append(MigrationTask(
            id="", phase="baseline", title="Capture current behavior with regression tests",
            verification="The captured regression tests pass against the current application.",
            rollback="Revert test-only changes."))
    for finding in findings:
        phase = _PHASE_BY_RULE.get(finding.rule)
        if phase is None:
            phase = {"MIG-CLI-001": "contracts", "MIG-ELECTRON-001": "contracts",
                     "MIG-DATA-001": "persistence"}.get(finding.id, "integrations")
        tasks.append(MigrationTask(
            id="", phase=phase, title=finding.title, findings=(finding.id,),
            verification=_VERIFICATION_BY_RULE.get(
                finding.rule, "The existing behavior is preserved and the related regression tests pass."),
            rollback="Revert this change with version control; the previous implementation remains runnable.",
            reversible=finding.id != "MIG-DATA-001"))
    strategy_task = _STRATEGY_TASKS[strategy]
    tasks.append(MigrationTask(id="", phase=strategy_task["phase"], title=strategy_task["title"],
                               verification=strategy_task["verification"],
                               rollback=strategy_task["rollback"]))
    tasks.append(MigrationTask(
        id="", phase="verification", title="Run architecture verification and required regression tests",
        verification="`adhara verify --strict` and the regression suite pass.",
        rollback="Not applicable; this task changes no source.", reversible=False))
    order = _phase_order(strategy)
    tasks.sort(key=lambda task: (order.index(task.phase), task.title))
    return [replace(task, id=f"MIG-{index:03d}") for index, task in enumerate(tasks, 1)]


def _phase_order(strategy: str) -> tuple[str, ...]:
    if strategy == "adapter-first":
        return ("baseline", "integrations", "runtime", "entry-points", "state-jobs", "contracts",
                "persistence", "dependencies", "structure", "verification")
    if strategy == "rebuild":
        return ("baseline", "runtime", "structure", "dependencies", "integrations", "entry-points",
                "state-jobs", "contracts", "persistence", "verification")
    return ("baseline", "structure", "dependencies", "runtime", "entry-points", "integrations",
            "state-jobs", "contracts", "persistence", "verification")


def _compatibility_risks(verification: VerificationResult) -> tuple[str, ...]:
    """Name compatibility risks a framework upgrade or profile change can introduce (NFR-COMP-007)."""
    risks = [
        f"The plan targets architecture profile version {verification.profile_version}; "
        "re-run verification after changing the profile or upgrading the framework.",
        "Report schemas are versioned independently of the application version; consumers "
        "must check schema_version and accept additive fields.",
    ]
    risks.extend(f"Architecture check {check.rule} fails: {check.detail or check.title}"
                 for check in verification.checks if check.status == "fail")
    return tuple(risks)


def _regression_tests(project: ProjectProfile) -> tuple[str, ...]:
    """Name the behavioral tests a migration must preserve (FR-TEST-008)."""
    tests: list[str] = []
    for finding in project.by_kind("action"):
        tests.append(f"Action `{finding.name}` preserves its accepted payloads and observable results.")
    for finding in project.by_kind("job"):
        tests.append(f"Job `{finding.name}` preserves its results, progress, and failure behavior.")
    if project.by_kind("cli") or _scripts(project):
        tests.append("Existing CLI commands preserve names, arguments, exit codes, and output.")
    if project.by_kind("electron-process") or project.by_kind("electron-ipc"):
        tests.append("Electron IPC channels preserve names, payloads, and process boundaries.")
    for integration, test in (
            ("HTTP", "Existing HTTP calls preserve endpoints, payloads, and error handling."),
            ("external CLI", "Existing external commands preserve arguments, output, and exit behavior."),
            ("SQLite", "Existing database schema, queries, and write paths preserve stored data.")):
        if any(finding.name == integration and not _is_framework_path(finding)
               for finding in project.by_kind("integration")):
            tests.append(test)
    if project.by_kind("state"):
        tests.append("Existing state behavior preserves request, session, process, and persistent scope.")
    if not tests:
        tests.append("Capture the current application behavior with regression tests before changing it.")
    return tuple(tests)


def _scripts(project: ProjectProfile) -> list[Finding]:
    return [finding for finding in project.by_kind("entry_point")
            if finding.name not in ("__main__", "app.run()", "application.run()")]


def _first_evidence(project: ProjectProfile, kind: str) -> tuple[Evidence, ...]:
    findings = project.by_kind(kind)
    return findings[0].evidence if findings else ()


def _is_framework_path(finding: Finding) -> bool:
    return any("nikhi/adhara_sutra/" in evidence.path for evidence in finding.evidence)
