## ADDED Requirements

### Requirement: Evidence-backed architecture verification

The verifier SHALL report findings with traceable evidence and distinguish
unsupported or incomplete checks from successful checks. (FR-ARCH-001, NFR-ARCH-001)

#### Scenario: Required evidence is unavailable

- **WHEN** a rule cannot be evaluated because its required evidence is unavailable
- **THEN** the verifier reports the check as unresolved rather than passing it

### Requirement: Versioned profiles and rule catalog

Verification SHALL evaluate a versioned architecture profile against a catalog
of stable, identified rules. (FR-ARCH-001, FR-ARCH-002, NFR-ARCH-005)

#### Scenario: A rule is evaluated

- **WHEN** verification runs
- **THEN** each result names its stable rule identifier, title, and severity

### Requirement: Explicit verification statuses

Each check SHALL be reported as pass, fail, needs review, or not checked, and
prerequisites that cannot be evaluated SHALL be reported as not checked rather
than passing. (FR-ARCH-010, NFR-ARCH-003)

#### Scenario: A rule has no applicable evidence

- **WHEN** a framework rule is evaluated on a project with no Application
- **THEN** the check is reported as not checked

### Requirement: Deterministic CI verification

Deterministic checks SHALL produce reproducible results without an LLM or
network access, and noninteractive verification SHALL expose meaningful exit
statuses and versioned machine-readable reports.
(FR-ARCH-009, FR-ARCH-011, FR-ARCH-015, NFR-ARCH-001, NFR-ARCH-007, NFR-ARCH-008)

#### Scenario: CI runs verification

- **WHEN** `adhara verify` runs noninteractively
- **THEN** it exits 0 without failures, 1 with failures (or needs-review under `--strict`), and 2 for an invalid invocation

### Requirement: Evidence and remediation

Each violation SHALL report its rule, severity, evidence, and a recommended
remediation where possible. (FR-ARCH-012, NFR-ARCH-002)

#### Scenario: A direct integration is detected

- **WHEN** a project uses a direct HTTP client while using the framework
- **THEN** the check needs review and cites the source location with the managed connector as remediation

### Requirement: Dependency and layer boundaries

The verifier SHALL detect imports forbidden by the profile and imports that
cross configured module-layer boundaries, citing the importing source.
(FR-ARCH-004)

#### Scenario: A layer imports a forbidden layer

- **WHEN** a module under a configured source prefix imports a module matched by that boundary
- **THEN** ARCH-LAYER-001 fails with the source location and the configured remediation

#### Scenario: No layer boundary is configured

- **WHEN** the profile declares no layer boundaries
- **THEN** the check is reported as not checked rather than passing silently

### Requirement: CLI protocol compatibility

The verifier SHALL evaluate whether the application uses the framework runtime
without bypassing the CLI protocol through direct standard streams. (FR-ARCH-006)

#### Scenario: A module writes to stdout directly

- **WHEN** a discovered module uses `print`, `sys.stdout`, or `sys.stdin`
- **THEN** ARCH-PROTO-001 needs review, cites the location, and recommends `context.emit` and the framework runtime

### Requirement: Managed state and background work

The verifier SHALL evaluate applicable state and job-management requirements
using static analysis and executable tests. (FR-ARCH-008)

#### Scenario: Background work bypasses the job manager

- **WHEN** a discovered module starts work with `asyncio.create_task`, `asyncio.ensure_future`, or an unmanaged thread
- **THEN** ARCH-JOB-002 needs review, cites the location, and recommends registering the work with `@app.job`

#### Scenario: State and jobs use the runtime

- **WHEN** the application accesses state through the request context and long-running work through registered jobs
- **THEN** the corresponding checks pass

### Requirement: Baselines and documented exceptions

The verifier SHALL let an existing project acknowledge known violations in a
versioned baseline so new violations keep blocking, while keeping acknowledged
findings visible. Each exception SHALL be scoped to a rule and source location
and MAY carry a documented reason. (FR-ARCH-013, FR-ARCH-014, NFR-ARCH-004,
NFR-ARCH-010)

#### Scenario: An acknowledged violation no longer blocks

- **WHEN** verification runs with a baseline that lists every location of a known violation
- **THEN** the check is reported as acknowledged and excluded from the blocking status while remaining in the report

#### Scenario: A new violation at a new location

- **WHEN** the same rule reports a location that the baseline does not list
- **THEN** the check is not acknowledged and the verification status still reports the violation

#### Scenario: An invalid baseline

- **WHEN** the baseline has an unsupported schema version or an entry without a rule, path, and snippet
- **THEN** verification fails with a clear error instead of ignoring the baseline

### Requirement: Architecture rule reference

Every enforceable rule SHALL have a stable identifier and a documented purpose in
the rule reference. (FR-DOC-005)

#### Scenario: Reading the rule reference

- **WHEN** a developer consults `docs/architecture-rules.md`
- **THEN** every catalogued rule appears once with its identifier, title, severity, and purpose

### Requirement: Reviewable migration

Migration planning SHALL produce reviewable changes and SHALL verify affected
behavior when migration changes are applied. (FR-MIG-012, FR-MIG-013)

#### Scenario: Proposed migration change

- **WHEN** a migration plan proposes a source change
- **THEN** the change is reviewable and is not represented as verified before its required checks succeed

### Requirement: Source-backed discovery

Architecture discovery SHALL record source-backed facts with uncertainty kept
visible. (FR-DISC-001, FR-DISC-009, FR-DISC-010)

#### Scenario: Discovery cannot determine a fact

- **WHEN** discovery cannot establish a fact from available source evidence
- **THEN** it reports the fact as unknown or uncertain rather than inferring a favorable conclusion

### Requirement: Current implementation report

The framework SHALL inspect an existing Python project and report its current
implementation: entry points, registered actions, jobs, services, integrations,
dependencies, state and job access, and Electron boundaries. (FR-DISC-001..008)

#### Scenario: Incremental analysis after source changes

- **WHEN** a project is inspected again with a reusable analysis cache
- **THEN** files whose content is unchanged are not reanalyzed, while changed files are refreshed and reports reflect the current source (FR-DISC-011)

#### Scenario: Inspecting a project

- **WHEN** a developer runs `adhara inspect` on a project directory
- **THEN** the report lists discovered implementation facts with source evidence

#### Scenario: An unreadable module

- **WHEN** a Python module cannot be parsed
- **THEN** the report records a parse error with its location instead of omitting the module silently

### Requirement: Report formats and versioning

Reports SHALL be available as machine-readable JSON and human-readable
Markdown, SHALL identify their schema version, and SHALL record the source
revision when available. (FR-REP-001, FR-REP-004, FR-REP-005, FR-REP-006, FR-REP-007)

#### Scenario: Consuming a report

- **WHEN** a report is generated for tooling
- **THEN** it is valid JSON carrying a schema version and source revision, and the Markdown form carries the same findings

### Requirement: Traceable findings

Each reported finding SHALL carry source evidence where available and SHALL
distinguish observed facts from inferences. (FR-DISC-009, FR-DISC-010, FR-REP-008)

#### Scenario: A finding has no direct evidence

- **WHEN** a fact is inferred from an import or usage pattern rather than a direct declaration
- **THEN** the finding is marked as inferred and still cites the source location

### Requirement: Safe project generation

Scaffolding SHALL NOT silently overwrite application-owned files.
(FR-SCAF-001, FR-SCAF-009)

#### Scenario: Regenerating an existing project

- **WHEN** a scaffold command runs in a project that already contains application-owned files
- **THEN** the generator requires explicit confirmation before replacing any such file

### Requirement: Migration analysis and planning

Migration analysis SHALL combine discovered implementation facts with
architecture verification results, identify gaps, and produce a structured,
deterministic plan of independently verifiable tasks for a selected strategy.
The plan SHALL also identify the behavioral regression tests needed to preserve
existing application functionality. (FR-MIG-001..005, FR-MIG-009, FR-MIG-014,
FR-TEST-008, NFR-MIG-005, NFR-MIG-006)

#### Scenario: Planning an existing application

- **WHEN** migration analysis runs on an existing project
- **THEN** it reports actionable findings with evidence, a plan of tasks each naming its verification and rollback, and the behavioral regression tests that must keep passing

### Requirement: Migration preservation constraints

Migration planning SHALL preserve existing business behavior, CLI and Electron
contracts, and persistent data, and SHALL NOT modify sources or data during
analysis. (FR-MIG-006, FR-MIG-007, FR-MIG-008, NFR-MIG-001, NFR-MIG-002, NFR-MIG-004, NFR-MIG-010)

#### Scenario: Planning a migration

- **WHEN** a plan is generated for an application with CLI commands, Electron IPC, or persistent data
- **THEN** the plan records contract-preservation and backup tasks and changes no source files

### Requirement: Migration reporting and status

Migration reports SHALL list completed, deferred, and unresolved tasks and
findings, record the analyzed source revision, and require deterministic
verification and supplied regression-test evidence before completion is claimed.
(FR-MIG-010, FR-MIG-013, FR-MIG-015, FR-REP-002, FR-REP-003, FR-REP-009, FR-REP-010,
NFR-MIG-007, NFR-MIG-008, NFR-MIG-009)

#### Scenario: Recording progress

- **WHEN** a status file maps planned task and finding ids to recorded statuses
- **THEN** the report reflects task and finding statuses and still requires verification and behavioral-test evidence before claiming completion

#### Scenario: Source changes after analysis

- **WHEN** the working tree no longer matches the source analyzed for a plan
- **THEN** the recorded revision/dirty state identifies the analysis as stale and source-matching can be required before relying on it

#### Scenario: Evaluating completion

- **WHEN** behavioral-test evidence is supplied for a migration plan
- **THEN** completion is reported only when architecture verification passes, no tasks or findings remain unfinished, and the supplied test evidence passed for the analyzed source revision; otherwise the report states it is incomplete or not evidenced

### Requirement: Migration status tracking

Migration SHALL track task and application-level status without presenting a
partially migrated application as conforming. (FR-MIG-009, FR-MIG-010)

#### Scenario: Partially migrated application is verified

- **WHEN** verification runs on an application with unfinished migration tasks
- **THEN** the result reflects remaining gaps rather than reporting full conformance
