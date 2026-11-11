# AdharaSutra — Migration Framework Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/migration-framework.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Development Tooling and Application Modernization Architecture  
**Architecture Style:** Evidence-Based Planning, Incremental Migration, Controlled Transformation, Behavioral Preservation  
**Primary Language:** Python 3.12+  
**Additional Languages:** TypeScript, JavaScript, JSON, TOML, YAML  
**Developer Interface:** `adhara migrate` — Proposed

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`
- `docs/design/electron-integration.md`
- `docs/design/connector-framework.md`
- `docs/design/state-management.md`
- `docs/design/job-and-process-management.md`
- `docs/design/configuration-and-lifecycle.md`
- `docs/design/error-handling-and-observability.md`
- `docs/design/project-scaffolding.md`
- `docs/design/architecture-discovery.md`
- `docs/design/architecture-verification.md`

---

# 1. Purpose

This document defines the architecture of AdharaSutra's Migration Framework.

The Migration Framework enables developers to analyze existing applications, understand their current architecture, select an AdharaSutra target architecture, plan changes, apply authorized transformations, and verify that required behavior remains intact.

It must support both applications that already use portions of AdharaSutra and legacy applications with entirely custom infrastructure.

The primary objective is to replace duplicated technical infrastructure while preserving application-owned business functionality.

## 1.1 Central Principle

**Migration changes infrastructure ownership and architectural organization without unnecessarily changing the application's business behavior.**

A successful migration is not simply one where architecture verification passes.

It is one where the application satisfies its approved target architecture **and** its required existing behavior remains demonstrably intact.

## 1.2 Objectives

The Migration Framework shall:

1. Analyze existing application architecture.
2. Identify current infrastructure and integration patterns.
3. Select and validate a target architecture profile.
4. Compare current and target architectures.
5. Identify architectural gaps.
6. Classify migration opportunities.
7. Generate explicit migration plans.
8. Identify dependencies between migration tasks.
9. Estimate change impact and uncertainty.
10. Generate reviewable file-level changes.
11. Support incremental and partial migration.
12. Preserve application business behavior.
13. Protect existing application data.
14. Support compatibility adapters.
15. Require authorization for source modifications.
16. Validate source freshness before applying changes.
17. Verify transformed code.
18. Run approved regression tests.
19. Support rollback and recovery.
20. Produce migration evidence and reports.
21. Integrate with architecture baselines.
22. Support coding-agent workflows.
23. Avoid requiring an LLM.
24. Maintain separation from normal application runtime dependencies.

---

# 2. Scope

## 2.1 In Scope

The framework covers:

- Migration discovery.
- Target architecture selection.
- Architecture gap analysis.
- Migration strategy selection.
- Migration task generation.
- Dependency-aware task ordering.
- Transformation classification.
- Source transformation planning.
- Compatibility adapters.
- Configuration migration.
- CLI communication migration.
- Electron integration migration.
- Connector adoption.
- State-management migration.
- Job-management migration.
- Lifecycle migration.
- Error and observability migration.
- Persistence migration planning.
- File-change preview.
- Approval requirements.
- Backup and rollback.
- Validation and regression testing.
- Migration reporting.
- Partial-completion tracking.
- Migration baseline integration.

## 2.2 Out of Scope

The initial Migration Framework does not promise:

- Fully automatic migration of arbitrary applications.
- Automatic understanding of all business logic.
- Guaranteed preservation of untested behavior.
- Arbitrary database-schema migration without application input.
- Automated deployment to production.
- Automatic recovery of all external side effects.
- Unrestricted repository rewriting.
- Automatic approval of migration plans.
- Automatic replacement of every third-party library.
- Automatic generation of domain entities.
- Guaranteed semantic equivalence from AST transformations alone.
- A mandatory LLM or external AI provider.
- Distributed migration orchestration.

---

# 3. Migration Principles

## MIG-001 — Non-Destructive by Default

The default migration command shall analyze and plan without modifying application source.

## MIG-002 — Explicit Authorization

Source transformations require an explicit apply operation and applicable approval checks.

## MIG-003 — Business Behavior Preservation

Migration shall preserve existing business behavior unless a specific behavior change is separately authorized.

## MIG-004 — Evidence-Based Planning

Migration recommendations shall reference discovered architecture evidence and relevant verification rules.

## MIG-005 — Incremental Adoption

Applications shall be able to adopt framework capabilities one subsystem at a time.

## MIG-006 — Adapter-First Strategy

Compatibility adapters shall be preferred when they reduce migration risk and avoid unnecessary business rewrites.

## MIG-007 — Target Architecture Independence

Target architecture shall be defined by an approved versioned profile rather than invented during transformation.

## MIG-008 — Source Freshness

A migration plan shall not be applied blindly after its underlying source has changed.

## MIG-009 — Reviewable Changes

Planned source changes shall be inspectable before application.

## MIG-010 — Explicit Risk Classification

Transformations shall be classified according to automation safety, behavioral risk, and evidence completeness.

## MIG-011 — Verification After Change

Every applied migration step shall have an appropriate validation strategy.

## MIG-012 — No False Success

Architecture conformance alone shall not be presented as proof of behavioral compatibility.

## MIG-013 — Controlled Rollback

Migration operations shall define rollback or recovery procedures appropriate to the changes made.

## MIG-014 — No Hidden Business Rewrites

The framework shall not silently rewrite domain algorithms, business decisions, or user-facing workflows.

## MIG-015 — Deterministic Core

Migration planning and supported mechanical transformations shall function without LLM inference.

## MIG-016 — Evidence Preservation

Migration results shall identify source revisions, transformation versions, approvals, and executed verification evidence.

## MIG-017 — Bounded Change Scope

A migration step shall not modify unrelated source or configuration.

## MIG-018 — Failure Transparency

Partial migration, validation failures, and unresolved work shall remain visible.

## MIG-019 — Application Ownership

The consuming application retains ownership of its source code, configuration, business models, and domain data.

## MIG-020 — Separate Planning and Execution

Discovery, verification, planning, transformation, and validation shall remain distinct logical responsibilities.

---

# 4. High-Level Migration Architecture

```text
┌──────────────────────────────────────────────────────┐
│               EXISTING APPLICATION                   │
│                                                      │
│ Python / Electron / Configuration / Persistence      │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Architecture Discovery│
               │ Current Implementation│
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Current Architecture  │
               │ Evidence and Coverage │
               └───────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌──────────────────────┐   ┌──────────────────────┐
   │ Target Architecture  │   │ Existing Verification│
   │ Profile and Rules    │   │ Violations / Baseline │
   └───────────┬──────────┘   └──────────┬───────────┘
               │                         │
               └────────────┬────────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Architecture Gap    │
                 │ Analysis            │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Migration Planner   │
                 │                     │
                 │ Strategy            │
                 │ Tasks               │
                 │ Dependencies        │
                 │ Risk                │
                 │ Validation          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Migration Plan      │
                 │ Review and Approval │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Controlled Apply    │
                 │                     │
                 │ Revalidate Source   │
                 │ Stage Changes       │
                 │ Apply Approved Diff │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Validation          │
                 │                     │
                 │ Syntax              │
                 │ Architecture        │
                 │ Contracts           │
                 │ Regression Tests    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Migration Report    │
                 │ Remaining Gaps      │
                 │ Evidence            │
                 └─────────────────────┘
```

## 4.1 Architecture Boundaries

| Subsystem | Responsibility |
|---|---|
| Discovery | Describe existing implementation |
| Verification | Evaluate current architecture |
| Target Profile Registry | Define desired architecture |
| Gap Analyzer | Identify differences |
| Migration Planner | Determine proposed changes |
| Transformation Engine | Produce controlled changes |
| Apply Engine | Apply authorized changes safely |
| Validation Engine | Check resulting implementation |
| Report Generator | Record results and evidence |

The Migration Framework shall reuse shared discovery and verification contracts.

It must not implement independent, competing source-analysis or architecture-rule systems.

---

# 5. Proposed Module Structure

```text
src/adharasutra/tooling/migration/
│
├── __init__.py
├── contracts.py
├── engine.py
├── configuration.py
├── errors.py
│
├── assessment/
│   ├── current_state.py
│   ├── target_state.py
│   ├── gap_analysis.py
│   ├── compatibility.py
│   └── risk_analysis.py
│
├── planning/
│   ├── planner.py
│   ├── tasks.py
│   ├── dependencies.py
│   ├── sequencing.py
│   ├── estimates.py
│   └── validation_plan.py
│
├── transformations/
│   ├── registry.py
│   ├── contracts.py
│   ├── python/
│   ├── typescript/
│   ├── configuration/
│   └── adapters/
│
├── execution/
│   ├── preview.py
│   ├── source_validation.py
│   ├── staging.py
│   ├── apply.py
│   ├── journaling.py
│   ├── rollback.py
│   └── recovery.py
│
├── validation/
│   ├── syntax.py
│   ├── architecture.py
│   ├── contracts.py
│   ├── regression.py
│   └── evidence.py
│
├── baselines/
│   ├── integration.py
│   └── comparison.py
│
└── reporting/
    ├── models.py
    ├── markdown.py
    └── json.py
```

This is a proposed logical structure.

Implementation may simplify the physical package layout without merging responsibilities that require separate safety or ownership boundaries.

The Migration Framework is development tooling and shall not be required by packaged application runtimes.

---

# 6. Migration Entry Points

## 6.1 New Migration Assessment

An assessment begins with:

- An application repository.
- A selected target architecture profile.
- A discovery snapshot.
- An applicable verification result.
- An optional existing migration baseline.

## 6.2 Existing Migration Continuation

A previously created migration plan may be resumed or revalidated.

The framework shall not assume that the repository remains unchanged since the previous planning session.

## 6.3 Migration Modes

The system should support three principal strategies.

| Strategy | Description | Typical use |
|---|---|---|
| Adapter-first | Wrap existing infrastructure through compatible boundaries | Lower-risk adoption |
| Incremental refactor | Replace infrastructure subsystem by subsystem | Established applications |
| Rebuild | Replace selected architecture layers while retaining approved business contracts | Severely coupled legacy systems |

## 6.4 Strategy Selection

The developer selects the migration strategy, optionally informed by framework recommendations.

The framework must not automatically choose a destructive rebuild solely because an existing architecture has many violations.

## 6.5 Migration Scope

A migration may target:

- Entire application.
- Selected subsystem.
- Package.
- Module.
- Connector.
- CLI communication.
- Electron integration.
- Job infrastructure.
- State or persistence integration.

Partial scope must be explicit.

---

# 7. Source Assessment

## 7.1 Discovery Input

Migration shall consume the current ApplicationArchitecture model.

The model contains:

- Repository identity.
- Source snapshot.
- Packages.
- Modules.
- Dependencies.
- Entry points.
- CLI implementation.
- Electron relationships.
- Connector patterns.
- State ownership.
- Jobs and processes.
- Configuration and lifecycle.
- Evidence.
- Coverage.
- Unresolved findings.

## 7.2 Source Completeness

The Migration Framework must inspect discovery coverage.

Missing or uncertain information shall affect automation eligibility.

## 7.3 Unsupported Implementations

Unsupported frameworks or language constructs must be identified rather than silently ignored.

## 7.4 Existing Behavior

The framework should inventory existing behavior contracts such as:

- CLI inputs and outputs.
- Application actions.
- Error codes.
- File formats.
- Persistent storage structures.
- External executable invocation.
- API interactions.
- Job progress and cancellation.
- Electron IPC contracts.

## 7.5 Behavioral Baseline

Before modifying an existing application, the migration workflow should establish behavioral regression evidence appropriate to the affected components.

If regression coverage is unavailable, the plan must identify the resulting risk and require explicit review before high-risk transformations.

---

# 8. Target Architecture Selection

## 8.1 Purpose

The target profile defines the architecture the application is intended to adopt.

## 8.2 Target Description

The target shall identify:

- Architecture structure.
- Required AdharaSutra version constraints.
- CLI interface.
- Electron interface, if applicable.
- Selected connectors.
- State-management capabilities.
- Job execution model.
- Configuration approach.
- Architecture rules.
- Required verification.

## 8.3 Target Example

```yaml
target:
  framework: adharasutra

  architecture:
    structure: ddd

    interfaces:
      - electron-cli

    capabilities:
      - process
      - sqlite
      - state
      - jobs
```

This is an illustrative target declaration, not an approved final schema.

## 8.4 Target Compatibility

The planner shall validate:

- Profile compatibility.
- Framework API compatibility.
- Python version support.
- Electron bridge requirements.
- Selected connector availability.
- Required capability dependencies.

## 8.5 Target Changes

Changing the target profile after plan generation shall require reassessment of affected migration tasks.

---

# 9. Architecture Gap Analysis

## 9.1 Purpose

The Gap Analyzer compares existing architecture with the selected target.

## 9.2 Gap Categories

| Category | Example |
|---|---|
| Missing capability | No framework application bootstrap |
| Competing infrastructure | Custom subprocess manager |
| Boundary violation | Domain imports concrete database |
| Compatibility gap | Existing CLI uses incompatible response format |
| Lifecycle gap | Resource cleanup not centrally managed |
| Configuration gap | Multiple inconsistent configuration loaders |
| Verification gap | Required runtime test unavailable |
| Unresolved gap | Dynamic implementation cannot be classified |

## 9.3 Gap Model

Each gap should identify:

- Gap ID.
- Affected architecture element.
- Current implementation.
- Target requirement.
- Applicable rule.
- Supporting evidence.
- Confidence.
- Risk.
- Suggested migration strategy.
- Required validation.

## 9.4 Example Gap

```json
{
  "gap_id": "gap-process-001",
  "category": "competing_infrastructure",
  "current": {
    "pattern": "direct_subprocess",
    "source": "src/app/audio/runner.py"
  },
  "target": {
    "capability": "adharasutra.process"
  },
  "verification_rule": "JPM-VER-005",
  "automation": "candidate",
  "behavioral_risk": "medium"
}
```

This example is illustrative.

## 9.5 Gap Versus Violation

Not every difference from the target is a violation.

For example, an application may use a library that is permitted by the selected profile.

The Gap Analyzer must distinguish mandatory architectural changes from optional modernization opportunities.

---

# 10. Migration Transformation Classification

## 10.1 Purpose

Transformations require different levels of confidence and approval.

## 10.2 Proposed Classes

| Class | Description | Automation policy |
|---|---|---|
| T0 | Informational recommendation | No source changes |
| T1 | Deterministic mechanical change | Preview and explicit apply |
| T2 | Structured change requiring contextual review | Review before apply |
| T3 | Behavior-sensitive transformation | Manual implementation or supervised change |
| T4 | Destructive or externally consequential change | Separate explicit authorization and recovery plan |

## 10.3 T0 — Advisory

Examples:

- Recommend a connector.
- Identify a lifecycle gap.
- Suggest a composition root.

No source changes occur.

## 10.4 T1 — Mechanical

Examples:

- Add a supported configuration key.
- Create an approved directory.
- Add a dependency declaration.
- Update a known import where a verified mapping exists.

The transformation must still check preconditions and preserve unrelated source.

## 10.5 T2 — Contextual

Examples:

- Move connector initialization to a composition root.
- Introduce an adapter interface.
- Replace a known application-specific wrapper with a framework interface.

These changes may require contextual review.

## 10.6 T3 — Behavior-Sensitive

Examples:

- Change asynchronous execution behavior.
- Replace job cancellation logic.
- Convert persistent process communication.
- Change transaction ownership.
- Reorganize domain service dependencies.

Such changes must not be treated as safely mechanical solely because an AST transformation can produce syntactically valid code.

## 10.7 T4 — Destructive

Examples:

- Delete database tables.
- Remove persisted data.
- Replace critical project configuration.
- Change externally exposed business contracts.
- Delete unknown application files.

These require an explicit, specific approval and appropriate recovery preparation.

## 10.8 Automation Eligibility

Automation eligibility shall depend on:

- Transformation class.
- Evidence completeness.
- Source preconditions.
- Rule compatibility.
- Behavioral risk.
- Existing tests.
- Approval policy.

A transformation's class is not sufficient on its own to establish that it is safe.

---

# 11. Migration Plan Model

## 11.1 Purpose

The Migration Plan represents the exact approved target, required changes, risks, dependencies, and verification obligations.

## 11.2 Plan Structure

```text
MigrationPlan
│
├── SchemaVersion
├── PlanIdentity
├── SourceSnapshot
├── TargetArchitecture
├── FrameworkCompatibility
│
├── Assessment
│   ├── CurrentArchitecture
│   ├── VerificationSummary
│   ├── Gaps
│   └── UnresolvedAreas
│
├── Strategy
├── MigrationPhases
│   └── MigrationTasks
│
├── ChangeSets
├── ApprovalRequirements
├── ValidationPlan
├── RollbackPlan
├── RiskRegister
└── GenerationMetadata
```

## 11.3 Required Plan Fields

A plan shall include:

- Unique plan ID.
- Schema version.
- Creation timestamp.
- Source revision and fingerprints.
- Target profile and version.
- Relevant framework versions.
- Migration strategy.
- Task inventory.
- Dependency ordering.
- Transformation classifications.
- Affected source locations.
- Required approvals.
- Validation requirements.
- Rollback limitations.
- Unresolved questions.

## 11.4 Plan Stability

A plan must not silently change after approval.

Changes to planned transformations shall produce a new plan revision or explicitly recorded amendment.

---

# 12. Migration Task Model

## 12.1 Task Identity

Every migration task shall have a stable identifier within its plan.

## 12.2 Task Fields

| Field | Purpose |
|---|---|
| `task_id` | Stable task identifier |
| `title` | Intended migration change |
| `description` | Scope and objective |
| `source_refs` | Supporting evidence |
| `target_rules` | Applicable target constraints |
| `dependencies` | Prerequisite tasks |
| `transformation_class` | Automation risk category |
| `affected_files` | Expected file changes |
| `preconditions` | Conditions required before execution |
| `postconditions` | Expected observable result |
| `validation` | Required checks |
| `rollback` | Recovery approach |
| `status` | Current task state |

## 12.3 Task Status

Proposed statuses:

- `planned`
- `ready`
- `blocked`
- `approved`
- `applying`
- `applied`
- `validating`
- `verified`
- `failed`
- `rolled_back`
- `needs_review`

A task shall not become `verified` merely because a patch was successfully applied.

## 12.4 Task Ordering

Task dependencies shall form an acyclic graph.

## 12.5 Independent Tasks

Independent tasks may be grouped into separate change sets.

## 12.6 Task Granularity

Tasks should be small enough to:

- Review.
- Apply.
- Test.
- Revert where feasible.
- Attribute failures accurately.

Avoid combining unrelated infrastructure migrations into one large, difficult-to-review change set.

---

# 13. Migration Dependency Planning

## 13.1 Purpose

Infrastructure migrations often depend on one another.

## 13.2 Example

```text
Introduce AdharaSutra Bootstrap
             │
             ▼
Configure Application Runtime
             │
             ▼
Register Process Connector
             │
             ▼
Introduce Audio Adapter
             │
             ▼
Migrate Audio Service
             │
             ▼
Verify Audio Execution
             │
             ▼
Remove Legacy Process Runner
```

## 13.3 Dependency Validation

The planner shall detect cycles and missing prerequisites.

## 13.4 Migration Sequencing

The default approach should favor:

1. Establish verification baseline.
2. Introduce framework alongside existing infrastructure.
3. Add compatibility adapters.
4. Migrate one capability.
5. Verify behavior.
6. Remove redundant infrastructure.
7. Repeat for remaining capabilities.

## 13.5 Avoiding Premature Removal

Legacy code should not be deleted before its replacement has passed applicable validation.

---

# 14. Adapter-First Migration Strategy

## 14.1 Purpose

Adapter-first migration reduces risk by preserving existing implementations while introducing approved framework boundaries.

## 14.2 Example

An existing application may expose:

```python
class LegacyAudioRunner:
    def generate(self, text: str) -> str:
        ...
```

Instead of rewriting audio-generation logic immediately, an application adapter may preserve this implementation behind an application-defined port.

The framework's Action Router can invoke that port.

## 14.3 Migration Sequence

```text
Existing Business Use Case
          │
          ▼
Application Port
          │
          ▼
Compatibility Adapter
          │
          ▼
Legacy Implementation
```

Later:

```text
Existing Business Use Case
          │
          ▼
Application Port
          │
          ▼
AdharaSutra-Based Adapter
          │
          ▼
Framework Connector
```

## 14.4 Benefits

- Smaller changes.
- Easier regression comparison.
- Reduced interruption.
- Earlier framework integration.
- Clear transition boundaries.

## 14.5 Limitations

Compatibility adapters may preserve technical debt temporarily.

They must not be presented as proof that legacy infrastructure has been completely removed.

## 14.6 Transitional Exceptions

Known violations may remain visible in the architecture baseline while the migration is underway.

---

# 15. Python Application Bootstrap Migration

## 15.1 Current Patterns

Existing applications may use:

- A custom `main.py`.
- Direct CLI parsing.
- Multiple initialization functions.
- Custom service registries.
- Custom shutdown hooks.

## 15.2 Target

The application shall use AdharaSutra's approved bootstrap, composition, and lifecycle mechanisms.

## 15.3 Migration Approach

1. Identify current entry points.
2. Record current startup behavior.
3. Introduce AdharaSutra application registration.
4. Wrap existing services where necessary.
5. Register actions.
6. Connect lifecycle ownership.
7. Verify startup and shutdown.
8. Remove obsolete bootstrapping code after validation.

## 15.4 Behavior Preservation

Migration must preserve required:

- Initialization order.
- Configuration behavior.
- Command outputs.
- Exit statuses.
- Resource cleanup.
- Existing automation compatibility.

## 15.5 One-Shot and Persistent Execution

The migration plan must explicitly identify whether the application requires one-shot, persistent, or both execution modes.

---

# 16. CLI Protocol Migration

## 16.1 Purpose

Move custom command-routing and communication infrastructure toward AdharaSutra's unified protocol.

## 16.2 Existing Patterns

Examples:

- Direct command-line arguments.
- Plain-text stdout.
- JSON stdout.
- Custom NDJSON messages.
- Custom stdin command loops.
- Local HTTP bridges.

## 16.3 Target

Registered AdharaSutra actions exposed through the versioned CLI protocol.

## 16.4 Migration Steps

1. Inventory existing commands.
2. Record input contracts.
3. Record output contracts.
4. Record error semantics.
5. Identify progress and cancellation behavior.
6. Map commands to registered actions.
7. Introduce protocol adapters.
8. Verify request and response compatibility.
9. Migrate callers.
10. Remove legacy protocol paths after verification.

## 16.5 stdout Safety

Plain-text logging must not corrupt protocol stdout.

## 16.6 Backward Compatibility

Applications may retain legacy human-friendly commands that internally route through framework actions.

## 16.7 Request and Job Semantics

Migration must not accidentally change a synchronous operation into an acknowledged background job without an explicit contract change.

---

# 17. Electron Integration Migration

## 17.1 Purpose

Replace custom Electron-to-Python communication with the shared AdharaSutra bridge.

## 17.2 Existing Responsibilities to Discover

- Python executable lookup.
- Process startup.
- stdin writes.
- stdout parsing.
- stderr collection.
- IPC handlers.
- Request correlation.
- Event subscriptions.
- Progress.
- Cancellation.
- Shutdown.
- Crash recovery.

## 17.3 Migration Target

```text
Renderer
   │
   ▼
Restricted Preload API
   │
   ▼
Electron Main
   │
   ▼
AdharaSutra Electron Bridge
   │
   ▼
AdharaSutra CLI Runtime
```

## 17.4 Recommended Sequence

1. Preserve current IPC contracts.
2. Introduce the shared bridge in Electron main.
3. Add compatibility wrappers for existing frontend operations.
4. Connect Python action registration.
5. Migrate one operation.
6. Test communication and lifecycle.
7. Migrate remaining operations.
8. Remove custom process communication infrastructure.

## 17.5 Security Review

Migration shall review:

- Renderer process access.
- Context isolation.
- Preload APIs.
- IPC caller authorization.
- Executable path control.
- Artifact access.

## 17.6 Packaging

Migration must verify that production Electron builds can locate and launch the Python runtime.

Development-mode success alone is insufficient.

---

# 18. Connector Migration

## 18.1 HTTP

Existing HTTP clients may be replaced by framework-managed HTTP connector instances.

Business endpoint mapping remains in application adapters.

## 18.2 External CLI

Existing direct subprocess execution may be migrated to the Process Connector.

The migration must preserve:

- Executable identity.
- Argument semantics.
- Working directory.
- Environment.
- stdout/stderr interpretation.
- Exit-code behavior.
- Timeout behavior.
- Cancellation behavior.
- Output artifacts.

## 18.3 SQLite

Existing connection management may move to the SQLite Connector.

Application repositories and SQL semantics remain application-owned.

## 18.4 WebSocket

Existing connection lifecycle management may move to the WebSocket Connector.

Service-specific message semantics remain in application adapters.

## 18.5 Filesystem

Common path, temporary-file, and artifact-management infrastructure may adopt framework facilities.

## 18.6 Connector Replacement Risk

Replacing a connector implementation can change timing, retry behavior, resource ownership, and error semantics.

Such transformations require appropriate behavioral validation.

---

# 19. State Management Migration

## 19.1 Purpose

Replace unmanaged state infrastructure where beneficial.

## 19.2 Existing Patterns

- Module-level dictionaries.
- Custom singleton stores.
- Session caches.
- JSON-file preferences.
- SQLite settings tables.
- Electron-maintained backend state mirrors.

## 19.3 Scope Classification

Each state value should be classified as:

- Request.
- Session.
- Process.
- Job.
- Persistent.
- UI-only.

## 19.4 Migration Requirements

Migration must preserve:

- State initialization.
- Value schemas.
- Persistence.
- Concurrency semantics.
- Notifications.
- Restore behavior.
- Cleanup.

## 19.5 Persistence Safety

In-memory state must not be represented as durable after migration.

## 19.6 Domain Repositories

Complete business entities should generally remain in application repositories rather than be moved into generic framework state merely for consistency.

## 19.7 Electron Synchronization

State synchronization changes require verification of snapshot, subscription, revision, and renderer-reload behavior.

---

# 20. Job and Process Migration

## 20.1 Existing Patterns

Applications may use:

- `asyncio.create_task`.
- Thread pools.
- Direct subprocess calls.
- Custom queues.
- Custom job dictionaries.
- SQLite job tracking.
- Custom progress callbacks.

## 20.2 Target

Use the AdharaSutra Job Manager for managed long-running work and the Process Connector for external executables.

## 20.3 Migration Sequence

1. Inventory execution mechanisms.
2. Identify actual execution owners.
3. Record concurrency behavior.
4. Record cancellation behavior.
5. Define job contracts.
6. Introduce framework execution.
7. Map progress and errors.
8. Verify terminal outcomes.
9. Validate shutdown and recovery.
10. Remove obsolete infrastructure.

## 20.4 Durable Execution

Persisted metadata does not imply durable execution.

The migration planner must not claim existing jobs can survive process termination without evidence of an independent execution owner.

## 20.5 Cancellation Risk

Migrating a process's cancellation behavior may be a high-risk transformation, especially when external programs launch descendants.

## 20.6 CPU and GPU Workloads

Execution-strategy changes must account for actual workload requirements rather than assuming threads, async tasks, and subprocesses are interchangeable.

---

# 21. Configuration and Lifecycle Migration

## 21.1 Configuration Migration

The planner shall map existing configuration sources into the approved AdharaSutra schema.

It must preserve required environment behavior and secret references.

## 21.2 Precedence

Configuration precedence changes can affect behavior.

The migration plan must identify differences between existing and target precedence.

## 21.3 Lifecycle Migration

The planner shall map:

- Initialization.
- Service dependencies.
- Connector startup.
- State restoration.
- Readiness.
- Shutdown.
- Resource cleanup.

## 21.4 Partial Startup

Applications must handle failure after partial initialization.

## 21.5 Shutdown

The migration must preserve or explicitly improve cleanup and termination behavior.

## 21.6 Optional Dependencies

Migration should not introduce unused optional connectors into application startup.

---

# 22. Error and Observability Migration

## 22.1 Error Mapping

Existing application errors may be mapped to the framework-wide error catalog.

## 22.2 Public Compatibility

The migration must identify error codes or messages relied on by existing callers.

## 22.3 Logging

Custom logging infrastructure may be migrated to framework-managed structured logging.

## 22.4 stdout

Existing plain-text diagnostic output must be separated from structured CLI protocol output.

## 22.5 Correlation

The migration may introduce:

- Request IDs.
- Job IDs.
- Execution attempt IDs.
- Process execution IDs.

## 22.6 Behavioral Risk

Changing public errors or logging side effects may affect automation and tests.

The migration plan must identify these dependencies.

---

# 23. Persistence and Database Migration

## 23.1 Separate Infrastructure and Data Migration

Changing SQLite connection management is different from changing application database schemas.

The framework must distinguish these operations.

## 23.2 Connection Migration

Moving connection ownership to AdharaSutra may preserve existing tables and queries.

## 23.3 Schema Migration

Schema transformations require application-owned migration definitions.

## 23.4 Data Protection

Data-affecting operations must have appropriate backup, validation, and recovery procedures.

## 23.5 Transaction Safety

The migration must respect transaction boundaries and commit semantics.

## 23.6 Incompatible Schema Changes

Destructive or incompatible schema changes require explicit authorization.

## 23.7 Database Backup

SQLite backups should use an appropriate consistent backup mechanism.

Raw file copies must not be assumed safe while a database is active.

## 23.8 External Side Effects

The framework shall not claim atomic rollback of operations spanning databases, files, HTTP services, and external executables.

---

# 24. Transformation Engine

## 24.1 Purpose

The Transformation Engine creates proposed source changes from approved transformation definitions.

## 24.2 Transformation Contract

Each transformation should declare:

- Identifier.
- Version.
- Supported language.
- Applicable patterns.
- Required evidence.
- Preconditions.
- Expected modifications.
- Postconditions.
- Validation requirements.
- Reversibility.
- Risk class.

## 24.3 Transformation Methods

Potential methods include:

- Structured configuration edits.
- Python syntax-aware transformations.
- TypeScript syntax-aware transformations.
- File creation.
- Controlled import rewriting.
- Compatibility adapter generation.

## 24.4 Syntax Preservation

Source transformations should preserve unrelated source formatting, comments, and structure where feasible.

AST analysis alone may not be sufficient for source-preserving edits.

## 24.5 Candidate Tools

Python transformations may use a concrete syntax tree library where justified.

TypeScript transformations may use TypeScript-aware source transformation tooling.

No specific implementation dependency is approved by this document.

## 24.6 Prohibited Behavior

Transformations shall not rely on unrestricted search-and-replace when a structural transformation is required for correctness.

## 24.7 Conflict Handling

If a transformation's preconditions fail, the engine shall reject or replan the operation rather than guessing how to modify source.

---

# 25. Transformation Planning and Preview

## 25.1 Dry Run

Migration planning shall be read-only by default.

## 25.2 Preview Output

A preview should contain:

- Migration plan ID.
- Target architecture.
- Affected files.
- Proposed modifications.
- Transformation class.
- Dependencies.
- Expected architecture impact.
- Required tests.
- Risks.
- Approvals required.

## 25.3 Diff Generation

Supported transformations should produce reviewable unified diffs or equivalent structured changes.

## 25.4 Risk Markers

Behavior-sensitive transformations must be clearly marked.

## 25.5 Unresolved Areas

The preview must identify areas where deterministic transformation is not possible.

## 25.6 Preview Accuracy

The preview must not imply that a patch will apply successfully if source preconditions have not been validated.

---

# 26. Apply Engine

## 26.1 Purpose

The Apply Engine applies authorized changes to the application repository.

## 26.2 Apply Preconditions

Before writing, it shall validate:

1. Approved migration plan.
2. Authorized scope.
3. Source snapshot freshness.
4. Expected file contents.
5. Transformation compatibility.
6. Required prerequisites.
7. Destination safety.
8. Available recovery mechanism.

## 26.3 Source Drift

If affected source has changed, the apply operation must stop or require an explicit replan.

It must not silently overwrite newer user changes.

## 26.4 Staging

Changes should be generated and validated in a temporary staging area where practical.

## 26.5 Atomicity Limitations

A set of filesystem writes is not universally atomic across all filesystems and environments.

The framework must report actual application status.

## 26.6 Partial Application

If one operation fails after others succeed, the engine shall record exactly which changes were applied.

## 26.7 User Edits

Preexisting application changes must be protected.

## 26.8 Locking

The engine should support an operation-level lock or equivalent coordination mechanism to reduce conflicting concurrent migration applies.

A lock cannot guarantee that arbitrary external tools will not modify the same files.

---

# 27. Migration Authorization

## 27.1 Authorization Levels

The migration system should distinguish:

- Analysis.
- Plan generation.
- Preview.
- Source modification.
- Test execution.
- External operation.
- Destructive data modification.

## 27.2 Read-Only Default

Analysis and planning shall not require authorization to modify files because they do not modify application source.

## 27.3 Source Apply

Source modifications require explicit user or trusted workflow authorization.

## 27.4 Higher-Risk Changes

Behavior-sensitive transformations require additional review according to policy.

## 27.5 Destructive Changes

Destructive data operations require specific approval identifying the affected resources.

## 27.6 Coding Agents

Agent involvement does not bypass normal approval or source-safety rules.

## 27.7 Approval Evidence

The migration report should record the applicable approval context.

The framework must not claim that an approval was organizationally authorized without a trusted approval mechanism.

---

# 28. Backup and Rollback

## 28.1 Purpose

The framework should enable recovery from failed or unwanted migration changes.

## 28.2 Source Backup

Before modifying existing files, the apply engine shall preserve sufficient original content or require an approved version-control recovery strategy.

## 28.3 Git Integration

Git may provide useful change tracking.

However, the framework shall not assume every application uses Git.

## 28.4 Dirty Worktrees

A dirty worktree may contain valuable uncommitted changes.

The framework must not reset or overwrite those changes without specific authorization.

## 28.5 Rollback Journal

The apply engine should record:

- Operation ID.
- Modified paths.
- Original fingerprints.
- New fingerprints.
- Applied transformation.
- Backup reference.
- Completion status.

## 28.6 File Rollback

Rollback should restore only changes owned by the migration operation.

## 28.7 External Side Effects

Rollback of source files does not reverse:

- HTTP requests already sent.
- Emails or notifications.
- External processes that completed.
- Database transactions already committed.
- Files modified by external tools.

Such operations require separate compensation or recovery plans.

## 28.8 Database Rollback

Database recovery must use an appropriate database-specific procedure.

## 28.9 Rollback Verification

After rollback, the system should verify restoration of expected source fingerprints and relevant application behavior where feasible.

## 28.10 Rollback Failure

A failed rollback must be reported explicitly.

The framework shall not claim the repository is restored without sufficient evidence.

---

# 29. Validation Framework

## 29.1 Purpose

Migration validation determines whether the applied changes satisfy their declared postconditions.

## 29.2 Validation Levels

| Level | Purpose |
|---|---|
| Syntax | Generated source parses |
| Structural | Required files and declarations exist |
| Architecture | Target rules evaluated |
| Contract | Public interfaces retain required behavior |
| Unit | Affected functions work |
| Integration | Affected components work together |
| End-to-end | Representative application workflows work |
| Packaging | Production artifacts remain valid |

## 29.3 Transformation-Specific Validation

Each transformation shall declare its required validation checks.

## 29.4 Validation Order

A typical sequence:

```text
Apply Change
      │
      ▼
Syntax Validation
      │
      ▼
Architecture Verification
      │
      ▼
Focused Contract Tests
      │
      ▼
Affected Unit Tests
      │
      ▼
Integration Tests
      │
      ▼
Representative End-to-End Tests
      │
      ▼
Migration Step VERIFIED
```

Not every stage is required for every low-risk change.

The required stages must be specified in the approved plan.

## 29.5 Validation Failure

If required validation fails, the migration step shall not be marked verified.

## 29.6 Unexecuted Tests

Tests that could not run shall be recorded as NOT_CHECKED.

## 29.7 Source Freshness

Test evidence shall correspond to the post-transformation source snapshot.

---

# 30. Behavioral Preservation

## 30.1 Purpose

The framework must preserve application behavior unless changes are explicitly authorized.

## 30.2 Behavioral Contracts

Relevant contracts may include:

- CLI command input.
- CLI command output.
- Exit codes.
- Electron IPC calls.
- File output names.
- File content formats.
- API requests.
- Database writes.
- Job status transitions.
- Progress events.
- Error codes.
- Cancellation behavior.
- Configuration precedence.

## 30.3 Baseline Tests

The migration planner should identify existing tests that establish expected behavior.

## 30.4 Missing Coverage

If behavior is not covered by tests, the planner should recommend characterization tests before modifying it.

## 30.5 Differential Testing

Where feasible, the old and new implementations may be executed against equivalent controlled inputs.

Their observable outputs can then be compared.

## 30.6 Nondeterministic Behavior

Differences caused by timestamps, random values, concurrency, or external services require explicit normalization or documented comparison rules.

## 30.7 External Service Tests

Live external-service tests should not be required for every local migration step.

Controlled fixtures may verify adapter behavior.

## 30.8 Evidence Standard

Passing architecture verification is necessary for applicable architecture changes but insufficient by itself to establish behavioral preservation.

---

# 31. Incremental Migration

## 31.1 Purpose

AdharaSutra shall support migration over multiple independent changes.

## 31.2 Migration States

An application may be:

- Not assessed.
- Assessed.
- Planned.
- Partially migrated.
- Migration verification pending.
- Target-compliant with verified required behavior.
- Migration blocked.
- Migration failed.

These states describe migration workflow progress, not runtime availability.

## 31.3 Migration Baseline

The Architecture Verification subsystem provides baseline support.

The Migration Framework shall consume that mechanism instead of creating a competing violation-suppression system.

## 31.4 Existing Violations

Existing violations remain visible.

## 31.5 New Violations

New architecture violations should be blocked according to the selected migration enforcement policy.

## 31.6 Resolved Violations

Each migration phase should record which baseline violations were resolved.

## 31.7 Remaining Work

Incomplete migration tasks must remain visible.

## 31.8 No Premature Completion

An application must not be marked fully migrated while mandatory unresolved tasks or required validation remain incomplete.

---

# 32. Migration State Persistence

## 32.1 Purpose

Migration plans and execution records may span multiple development sessions.

## 32.2 Persisted Artifacts

Potential artifacts:

- Architecture assessment.
- Migration plan.
- Gap report.
- Approval metadata.
- Transformation previews.
- Apply journal.
- Validation results.
- Rollback records.
- Completion report.

## 32.3 Storage

Migration metadata should be stored in a documented developer-tooling location.

It must not be confused with application business state.

## 32.4 Repository Files

Reviewable plan and baseline artifacts may be stored in the repository when explicitly selected.

## 32.5 Source Ownership

The migration engine must not create hidden state inside unrelated application source directories.

## 32.6 Compatibility

Persisted migration plans shall have versioned schemas.

## 32.7 Recovery

After interrupted apply operations, the engine should inspect its journal and current source fingerprints before offering resume or rollback.

---

# 33. Migration Reports

## 33.1 Report Types

The subsystem should produce:

1. Assessment report.
2. Architecture gap report.
3. Migration plan.
4. Transformation preview.
5. Apply result.
6. Validation report.
7. Rollback report.
8. Final migration summary.

## 33.2 Markdown Reporting

Markdown output should be suitable for review by developers and coding agents.

## 33.3 JSON Reporting

JSON output shall preserve machine-readable task identities, evidence, and statuses.

## 33.4 Final Report Structure

A final report should include:

- Source revision before migration.
- Target profile and version.
- Source revision after migration.
- Applied tasks.
- Skipped tasks.
- Remaining gaps.
- Architecture verification.
- Executed tests.
- Unexecuted tests.
- Behavioral compatibility evidence.
- Rollback limitations.
- Warnings.
- Overall migration status.

## 33.5 Report Accuracy

A completed transformation is not equivalent to a verified migration.

The reporting model must preserve that distinction.

---

# 34. Developer CLI

## 34.1 Proposed Commands

Analyze and plan:

```bash
adhara migrate plan ./my-application \
  --target ddd
```

Plan Electron integration:

```bash
adhara migrate plan ./my-application \
  --target ddd \
  --interface electron-cli
```

Plan selected capabilities:

```bash
adhara migrate plan ./my-application \
  --target ddd \
  --with process,sqlite,state,jobs
```

Preview changes:

```bash
adhara migrate preview ./migration-plan.json
```

Apply an approved task:

```bash
adhara migrate apply ./migration-plan.json \
  --task MIG-001
```

Validate applied changes:

```bash
adhara migrate validate ./migration-plan.json
```

Inspect status:

```bash
adhara migrate status ./migration-plan.json
```

Rollback an operation:

```bash
adhara migrate rollback ./migration-operation.json
```

Export a report:

```bash
adhara migrate report ./migration-plan.json \
  --format markdown
```

These commands are proposed and are not implemented functionality.

## 34.2 CLI Defaults

The default migration workflow shall be:

- Read-only assessment.
- No automatic source rewrite.
- No automatic dependency installation.
- No arbitrary application execution.
- No destructive database changes.
- No automatic approval.

## 34.3 Machine-Readable Interface

The CLI shall support JSON output for automation and coding agents.

## 34.4 Exit Codes

The developer CLI should distinguish:

- Success.
- Validation failure.
- Source drift.
- Approval required.
- Apply failure.
- Rollback failure.
- Incomplete migration.
- Internal tooling error.

The exact exit-code assignments must be reconciled with the developer CLI specification.

---

# 35. Coding Agent Integration

## 35.1 Purpose

Coding agents may assist with migration planning, source editing, testing, and documentation.

## 35.2 Supported Agents

The migration architecture must remain independent of a particular coding-agent implementation.

Examples include:

- Claude Code.
- Codex.
- OpenCode.
- Other compatible development agents.

## 35.3 Agent Workflow

```text
Architecture Discovery
        │
        ▼
Migration Planning
        │
        ▼
Review Plan
        │
        ▼
Assign Scoped Migration Task
        │
        ▼
Agent Modifies Application
        │
        ▼
Architecture Verification
        │
        ▼
Regression Tests
        │
        ▼
Review Results
```

## 35.4 Deterministic Tooling

Agents should use AdharaSutra's structured discovery, verification, and migration reports rather than independently inventing architecture assessments.

## 35.5 Agent-Assisted Transformations

An agent may propose source changes for transformations that are not safely automatable.

Such changes remain subject to:

- Approved task scope.
- Source review.
- Behavioral tests.
- Architecture verification.
- Application ownership rules.

## 35.6 LLM Independence

The migration engine's mandatory planning and mechanical transformation capabilities shall not require an LLM.

## 35.7 Agent-Generated Evidence

Agent statements such as "migration complete" are not substitutes for executable validation results.

---

# 36. Security Architecture

## 36.1 Untrusted Repository Input

Migration shall treat inspected repositories as untrusted source data.

## 36.2 Default Execution

Planning shall not execute application code.

## 36.3 Transformation Trust

Custom transformation plugins are executable tooling code and must be explicitly trusted.

## 36.4 Path Boundaries

Changes shall remain within approved filesystem roots.

## 36.5 Symlink Handling

The apply engine must consider logical paths and resolved targets.

It must not follow unsafe links into unauthorized locations.

## 36.6 Secret Handling

Migration reports and diffs shall not unnecessarily expose credentials.

## 36.7 Source Modification

Modifications require explicit apply authorization.

## 36.8 Arbitrary Commands

The migration engine shall not execute commands embedded in a repository without explicit authorization and documented trust boundaries.

## 36.9 Dependency Installation

Installing or updating application dependencies is a separate side-effecting operation and must be explicitly authorized.

## 36.10 Database Safety

Destructive data operations require specific approval and an appropriate recovery plan.

## 36.11 Auditability

Apply operations should retain enough metadata to establish which changes the migration tool performed.

---

# 37. Performance and Resource Management

## 37.1 Performance Principles

Migration planning should reuse discovery and verification results where valid.

## 37.2 Incremental Planning

Changes to a subset of source files should not require regenerating unrelated migration tasks unnecessarily.

## 37.3 Cache Validity

Cached assessments must be invalidated when relevant source, profiles, rule definitions, or transformation versions change.

## 37.4 Resource Limits

Migration tooling should support limits on:

- Analysis duration.
- Transformation duration.
- Number of files modified.
- Total patch size.
- Temporary storage.
- Parallel operations.
- Report size.

## 37.5 Bounded Tasks

Large migrations should be divided into reviewable phases and tasks.

## 37.6 Parallelism

Independent assessment or planning work may run concurrently.

Concurrent source modifications to overlapping files must be prevented or explicitly coordinated.

---

# 38. Error Architecture

## 38.1 Proposed Error Codes

```text
MIGRATION_SOURCE_UNAVAILABLE
MIGRATION_DISCOVERY_INCOMPLETE
MIGRATION_TARGET_INVALID
MIGRATION_PROFILE_INCOMPATIBLE
MIGRATION_GAP_UNRESOLVED
MIGRATION_PLAN_INVALID
MIGRATION_PLAN_STALE
MIGRATION_PRECONDITION_FAILED
MIGRATION_APPROVAL_REQUIRED
MIGRATION_TRANSFORMATION_UNSUPPORTED
MIGRATION_TRANSFORMATION_FAILED
MIGRATION_APPLY_CONFLICT
MIGRATION_APPLY_PARTIAL
MIGRATION_VALIDATION_FAILED
MIGRATION_ROLLBACK_FAILED
MIGRATION_RECOVERY_REQUIRED
```

These identifiers remain proposed and must be reconciled with the framework-wide error catalog.

## 38.2 Error Context

Migration failures should identify:

- Plan ID.
- Task ID.
- Transformation ID.
- Affected source.
- Failure stage.
- Primary cause.
- Files changed before failure.
- Available recovery options.

## 38.3 Partial Failure

The engine must not report a completely failed or completely successful operation when only part of the planned changes occurred.

## 38.4 Recovery

Recovery actions must use journal and current source evidence.

---

# 39. Migration Testing Strategy

## 39.1 Planning Tests

Verify:

- Target selection.
- Gap classification.
- Task generation.
- Dependency ordering.
- Risk classification.
- Validation requirements.

## 39.2 Transformation Tests

Verify:

- Correct source modifications.
- Preservation of unrelated source.
- Handling of syntax variants.
- Preconditions.
- Postconditions.
- Formatting preservation where required.

## 39.3 Source Drift Tests

Verify:

- Changed files.
- Deleted files.
- Renamed files.
- Modified symlink targets.
- Stale plans.
- Concurrent edits.

## 39.4 Apply Tests

Verify:

- Dry run.
- Approved apply.
- Conflicting destination.
- Partial apply.
- Journal accuracy.
- File permission errors.

## 39.5 Rollback Tests

Verify:

- Restoration of modified files.
- Preservation of unrelated changes.
- Partial rollback.
- Failed rollback.
- Recovery after interruption.

## 39.6 Behavioral Tests

Verify representative application behavior before and after migration.

## 39.7 Architecture Tests

Verify that applied tasks resolve their target violations without introducing prohibited new violations.

## 39.8 Database Tests

Use controlled test databases to validate data preservation and migration recovery.

## 39.9 Electron Tests

Verify:

- Shared bridge communication.
- Renderer authorization.
- Python startup.
- Job events.
- Cancellation.
- Shutdown.
- Packaged execution.

## 39.10 Failure Injection

Simulate:

- Parser failure.
- Stale discovery.
- Invalid target profile.
- Patch conflict.
- Disk write failure.
- Process termination during apply.
- Test failure.
- Missing dependency.
- Rollback failure.
- Uncertain external side effects.

---

# 40. Migration Verification Rules

These rules evaluate the Migration Framework's process integrity rather than the application's architecture itself.

| Rule ID | Description |
|---|---|
| MIG-VER-001 | Migration plan identifies source snapshot |
| MIG-VER-002 | Target architecture profile is versioned |
| MIG-VER-003 | Migration gaps reference applicable evidence |
| MIG-VER-004 | Transformations declare safety classifications |
| MIG-VER-005 | Migration tasks define affected scope |
| MIG-VER-006 | Task dependencies are acyclic |
| MIG-VER-007 | Source modifications require explicit apply |
| MIG-VER-008 | Source freshness is validated before apply |
| MIG-VER-009 | Existing unrelated files are protected |
| MIG-VER-010 | High-risk changes have required approval |
| MIG-VER-011 | Apply operations produce audit records |
| MIG-VER-012 | Recovery or rollback procedures are documented |
| MIG-VER-013 | Applied changes receive required validation |
| MIG-VER-014 | Failed tests prevent verified status |
| MIG-VER-015 | Unexecuted tests remain NOT_CHECKED |
| MIG-VER-016 | Migration baselines preserve existing violations |
| MIG-VER-017 | New architecture violations remain visible |
| MIG-VER-018 | Final reports distinguish applied and verified changes |
| MIG-VER-019 | Migration tooling is excluded from production runtime dependencies |
| MIG-VER-020 | Migration operates without an LLM |

---

# 41. Representative End-to-End Scenarios

## MIG-S01 — Legacy Python CLI

**Given** a Python application with custom `argparse` routing,

**When** migration planning targets AdharaSutra CLI,

**Then** the framework shall identify existing commands and propose mapping them into registered actions.

**And** preserve required command behavior through compatibility wrappers where needed.

## MIG-S02 — Legacy Electron Communication

**Given** an Electron application with custom stdin/stdout Python communication,

**When** migration planning targets `electron-cli`,

**Then** the framework shall identify relevant Electron and Python communication components.

**And** propose a staged migration toward the shared bridge.

## MIG-S03 — Direct Subprocess Execution

**Given** an application uses `subprocess.run` to execute an external tool,

**When** migration targets the Process Connector,

**Then** the planner shall identify the invocation and its relevant behavior contracts.

**And** require validation of argument, output, timeout, and cancellation semantics.

## MIG-S04 — Existing SQLite Database

**Given** an application has an existing SQLite database,

**When** connection management is migrated,

**Then** the framework shall preserve application-owned schema and data unless a separate schema migration is authorized.

## MIG-S05 — Global State

**Given** an application stores mutable state in module globals,

**When** state migration is planned,

**Then** the planner shall identify likely scope and concurrency concerns.

**And** require review when ownership cannot be determined reliably.

## MIG-S06 — Existing Job Manager

**Given** an application uses a custom job scheduler,

**When** migration targets AdharaSutra Jobs,

**Then** the plan shall account for execution ownership, concurrency, progress, cancellation, and shutdown.

## MIG-S07 — Incomplete Discovery

**Given** relevant source cannot be analyzed,

**When** migration planning runs,

**Then** the framework shall not classify affected behavior-sensitive transformations as safely automatic.

## MIG-S08 — Source Drift

**Given** a migration plan was generated against an earlier source snapshot,

**When** affected source changes before apply,

**Then** the framework shall stop the apply operation and require revalidation or replanning.

## MIG-S09 — Dirty Git Worktree

**Given** an application contains uncommitted changes,

**When** migration applies approved changes,

**Then** unrelated uncommitted changes shall remain protected.

## MIG-S10 — Partial Apply Failure

**Given** a migration applies some file changes before a later operation fails,

**When** the Apply Engine records the failure,

**Then** the report shall identify exactly which changes occurred.

**And** offer only supported recovery procedures.

## MIG-S11 — Validation Failure

**Given** an applied transformation breaks a required regression test,

**When** validation executes,

**Then** the task shall not be marked verified.

## MIG-S12 — Architecture Pass, Behavior Failure

**Given** migration resolves all applicable architecture violations,

**When** a required behavioral test fails,

**Then** migration shall remain incomplete.

## MIG-S13 — Baseline Improvement

**Given** a legacy application has existing architecture violations,

**When** an incremental migration resolves some violations,

**Then** the verification baseline comparison shall report resolved, remaining, and new violations separately.

## MIG-S14 — Data Migration Risk

**Given** a proposed transformation would delete persisted application data,

**When** planning runs,

**Then** the change shall be classified as destructive.

**And** require explicit approval and a recovery plan before execution.

## MIG-S15 — Agent-Assisted Migration

**Given** a coding agent performs a supervised source change,

**When** it reports completion,

**Then** AdharaSutra shall require the applicable architecture and behavioral verification evidence before marking the task verified.

## MIG-S16 — Interrupted Migration

**Given** the migration process terminates during apply,

**When** migration tooling restarts,

**Then** it shall inspect operation journal and current source fingerprints.

**And** determine whether safe resume, rollback, or manual recovery is required.

## MIG-S17 — Framework Upgrade

**Given** an application already uses AdharaSutra,

**When** the target framework version changes,

**Then** the planner shall identify relevant public API and configuration compatibility changes.

**And** avoid rewriting unrelated application business logic.

## MIG-S18 — Fully Verified Migration

**Given** all mandatory migration tasks are complete,

**When** architecture verification and required regression tests pass,

**Then** the framework may report migration completion for the approved target and validated scope.

**And** shall retain limitations for any explicitly excluded or untested areas.

---

# 42. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| MIG-D01 | Default operation | Read-only planning |
| MIG-D02 | Current architecture | Shared discovery model |
| MIG-D03 | Target architecture | Versioned profile |
| MIG-D04 | Gap evaluation | Evidence and rule-based |
| MIG-D05 | Migration strategy | Adapter-first, incremental, rebuild |
| MIG-D06 | Transformation classification | T0–T4 |
| MIG-D07 | Source changes | Explicit apply |
| MIG-D08 | Source freshness | Mandatory validation |
| MIG-D09 | Planning | Task dependency graph |
| MIG-D10 | Transformation preview | Reviewable diffs |
| MIG-D11 | Source editing | Syntax-aware where required |
| MIG-D12 | Existing edits | Protected |
| MIG-D13 | Apply journal | Required |
| MIG-D14 | Rollback | Operation-scoped |
| MIG-D15 | Database changes | Separate explicit authorization |
| MIG-D16 | Behavioral preservation | Required regression evidence |
| MIG-D17 | Architecture validation | Shared verifier |
| MIG-D18 | Baselines | Shared verification baseline |
| MIG-D19 | Partial migration | Supported |
| MIG-D20 | Progress reporting | Applied versus verified |
| MIG-D21 | Coding agents | Optional assisted implementation |
| MIG-D22 | LLM dependency | None |
| MIG-D23 | Reports | Markdown and JSON |
| MIG-D24 | Production runtime | Migration tooling excluded |
| MIG-D25 | Completion | Target conformance plus required behavior validation |

All decisions remain proposed until reviewed.

---

# 43. Outstanding Questions

## MIG-OQ-001 — Initial Automation Scope

Which transformations should be implemented first?

**Recommendation:** Begin with low-risk configuration, bootstrap, and known import/registration transformations. Keep behavioral changes supervised.

## MIG-OQ-002 — Transformation Library

Should Python modifications use LibCST or another source-preserving library?

**Recommendation:** Evaluate tools capable of preserving comments and formatting for supported transformations.

## MIG-OQ-003 — TypeScript Transformations

Should Electron migration use the TypeScript compiler API or another structural transformation library?

**Recommendation:** Prefer language-aware transformations rather than broad text substitutions.

## MIG-OQ-004 — Migration Plan Storage

Should plans be stored inside the application repository?

**Recommendation:** Support explicit repository-local plans for review, with a framework-managed external location as an alternative.

## MIG-OQ-005 — Apply Granularity

Should developers apply whole plans or individual tasks?

**Recommendation:** Support task-level and approved change-set-level application.

## MIG-OQ-006 — Git Requirements

Should Git be mandatory for migration?

**Recommendation:** No. Git is preferred for developer workflows, but the framework must support safe file operations and backups without it.

## MIG-OQ-007 — Automatic Rollback

Should failed validation automatically revert changes?

**Recommendation:** Support configurable rollback only when the operation can safely restore exactly its owned changes. Otherwise require review.

## MIG-OQ-008 — Behavior Characterization

Should migration tooling automatically generate characterization tests?

**Recommendation:** Generate useful test scaffolds and candidate cases, but do not claim observed behavior without executing approved tests.

## MIG-OQ-009 — Framework Upgrade Migration

Should the same migration engine manage AdharaSutra version upgrades?

**Recommendation:** Yes, using versioned compatibility rules and upgrade-specific transformations.

## MIG-OQ-010 — Database Migrations

Should schema migration execution be part of this tool?

**Recommendation:** Keep application-owned database migration execution separate, while allowing the planner to coordinate approved steps and validation.

## MIG-OQ-011 — Agent Assistance

Should agent-assisted migrations be invoked directly through the developer CLI?

**Recommendation:** Begin with machine-readable tasks and reports usable across coding agents. Add optional orchestration only if necessary.

## MIG-OQ-012 — Source Change Limits

Should a migration plan impose maximum files or lines modified per task?

**Recommendation:** Support configurable limits and require additional approval for unexpectedly large changes.

## MIG-OQ-013 — Migration Completion

Should the framework allow completion with outstanding low-severity findings?

**Recommendation:** Completion criteria should follow the selected approved target and enforcement policy, while retaining visibility of exceptions and remaining limitations.

## MIG-OQ-014 — External Tool Setup

Should migration automatically install Python packages, npm dependencies, or external executables?

**Recommendation:** No by default. Make these separate, explicitly authorized operations.

## MIG-OQ-015 — Transformation Confidence

Should the framework assign numeric confidence scores to migration transformations?

**Recommendation:** Use explicit safety classifications, precondition checks, and unresolved-evidence flags rather than uncalibrated numeric scores.

## MIG-OQ-016 — Multi-Repository Migration

Should the framework coordinate migration across multiple repositories?

**Recommendation:** Begin with one repository or monorepo workspace. Defer distributed migration coordination.

---

# 44. Functional Requirement Traceability

| Requirement group | Migration responsibility |
|---|---|
| FR-MIG | Migration planning, execution, recovery |
| FR-DISC | Existing architecture assessment |
| FR-ARCH | Target conformance evaluation |
| FR-SCAF | Template and profile compatibility |
| FR-RUN | Bootstrap migration |
| FR-CLI | CLI protocol migration |
| FR-ELC | Electron bridge migration |
| FR-CON | Connector adoption |
| FR-HTTP | HTTP infrastructure migration |
| FR-EXT | Process infrastructure migration |
| FR-DB | SQLite infrastructure migration |
| FR-WS | WebSocket integration migration |
| FR-FS | File and artifact migration |
| FR-STATE | State scope migration |
| FR-JOB | Job and process migration |
| FR-CFG | Configuration migration |
| FR-DI | Composition migration |
| FR-ERR | Error contract migration |
| FR-LOG | Logging migration |
| FR-TEST | Regression validation |
| FR-REP | Migration reports |
| FR-SEC | Safe source and data modification |
| FR-DEV | Developer CLI integration |
| FR-PKG | Framework upgrade compatibility |

---

# 45. Non-Functional Requirement Traceability

| Quality attribute | Architectural mechanism |
|---|---|
| Reliability | Controlled transformations and validation |
| Security | Read-only defaults and explicit approvals |
| Maintainability | Incremental infrastructure replacement |
| Compatibility | Public contract preservation |
| Testability | Characterization and regression testing |
| Reproducibility | Versioned plans and source snapshots |
| Extensibility | Pluggable transformation contracts |
| Portability | Cross-platform file operations |
| Resource efficiency | Scoped planning and bounded changes |
| Observability | Apply journals and evidence reports |
| Architecture conformance | Shared verifier and target profiles |
| Migration safety | Non-destructive planning and rollback |
| Developer experience | Previewable plans and CLI workflows |

---

# 46. Acceptance Criteria

The Migration Framework design may be approved when:

- [ ] Migration is read-only by default.
- [ ] Discovery and verification remain separate shared subsystems.
- [ ] Target profiles are versioned.
- [ ] Architecture gaps are evidence-backed.
- [ ] Migration strategies are defined.
- [ ] Transformation safety classes are defined.
- [ ] Migration plans contain source and target identities.
- [ ] Task dependencies are represented.
- [ ] Source modifications require explicit apply authorization.
- [ ] Source freshness is checked before apply.
- [ ] Changes can be previewed.
- [ ] Unrelated application files are protected.
- [ ] Dirty worktrees are handled safely.
- [ ] Transformation preconditions and postconditions are defined.
- [ ] Behavior-sensitive changes require appropriate review.
- [ ] Destructive data changes require explicit approval.
- [ ] Apply journals record actual modifications.
- [ ] Partial apply failures are reported accurately.
- [ ] Rollback and recovery limitations are documented.
- [ ] Existing behavior contracts are inventoried.
- [ ] Regression evidence is required according to risk.
- [ ] Architecture checks alone cannot establish behavioral preservation.
- [ ] Existing violation baselines remain visible.
- [ ] New violations are distinguished from historical violations.
- [ ] Partial migration is supported.
- [ ] Job and process migration preserves ownership semantics.
- [ ] Electron migration preserves IPC and process lifecycle requirements.
- [ ] Database migration preserves data and transaction guarantees.
- [ ] CLI and error compatibility are addressed.
- [ ] Coding-agent assistance remains subject to verification.
- [ ] No mandatory LLM dependency exists.
- [ ] JSON and Markdown reports are defined.
- [ ] Migration tooling remains outside production runtime dependencies.
- [ ] Required tests and failure scenarios are identified.
- [ ] Critical outstanding decisions are approved or deferred.

---

# 47. Final Architecture Summary

AdharaSutra's Migration Framework provides a controlled, evidence-based approach to adopting the framework in existing applications.

It reuses:

- Architecture Discovery to understand the current implementation.
- Architecture Verification to identify target violations and establish baselines.
- Versioned architecture profiles to define the desired structure.
- Shared framework contracts to guide infrastructure replacement.

The Migration Framework owns:

- Gap analysis.
- Strategy selection.
- Migration planning.
- Task dependency ordering.
- Transformation classification.
- Change previews.
- Authorized application.
- Apply journaling.
- Validation coordination.
- Rollback and recovery.
- Migration reporting.

It supports adapter-first integration, incremental refactoring, and explicitly approved rebuilding where necessary.

The system shall preserve application business behavior, protect existing data, and avoid replacing working domain logic merely to achieve framework adoption.

A transformation is considered applied when its approved source changes have been performed.

A transformation is considered verified only when its required postconditions and validation checks have succeeded.

A migration is complete only when the approved target architecture and required behavioral contracts have been satisfied within the declared scope.

The central guarantee is:

**Every migration change is justified by evidence, limited to an approved scope, reviewable before application, and validated before completion.**

---

# 48. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending migration architecture review

**Next Document:** `docs/design/testing-strategy.md`

The next document should define the complete testing architecture for AdharaSutra itself and consuming applications, including unit tests, contract tests, protocol testing, connector integration, subprocess fixtures, Electron end-to-end tests, architecture tests, migration regression tests, cross-platform testing, performance benchmarks, and CI quality gates.

---

**AdharaSutra — Build once. Standardize everywhere.**
