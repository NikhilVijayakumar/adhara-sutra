# AdharaSutra — Architecture Discovery

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/architecture-discovery.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Development Tooling Architecture  
**Architecture Style:** Evidence-Based Static Analysis, Shared Intermediate Architecture Model  
**Primary Language:** Python 3.12+  
**Additional Languages:** TypeScript, JavaScript, JSON, TOML, YAML  
**Developer Interface:** `adhara inspect` — Proposed

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

---

# 1. Purpose

This document defines how AdharaSutra discovers and represents the existing architecture of a software application.

Architecture discovery is a development-time capability that inspects application repositories and produces a structured, evidence-backed description of their current implementation.

It must work with:

1. New applications generated using AdharaSutra.
2. Existing applications that do not yet use AdharaSutra.
3. Partially migrated applications.
4. Standalone Python CLI applications.
5. Electron applications using Python backends.
6. Applications integrating external HTTP services.
7. Applications executing external CLI programs.
8. Applications using SQLite or other persistence implementations.
9. Applications managing background jobs and state.
10. Applications containing multiple packages or execution entry points.

The discovery system must identify architectural structures, relationships, and implementation patterns without requiring the repository to follow AdharaSutra's conventions beforehand.

## 1.1 Central Principle

**Architecture discovery must describe the application's observed implementation, provide evidence for its findings, and explicitly identify what cannot be determined.**

The discovery engine shall not:

- Invent missing architectural elements.
- Assume a directory name proves a component's responsibility.
- Treat an import as proof that a dependency is used at runtime.
- Claim behavioral correctness from static analysis.
- Silently interpret uncertain patterns as verified facts.

## 1.2 Objectives

The architecture shall:

- Discover project structure and languages.
- Identify application entry points.
- Analyze modules and dependency relationships.
- Identify business and infrastructure boundaries.
- Discover CLI actions and command routing.
- Analyze Electron main, preload, renderer, and Python communication.
- Identify external connectors and subprocess usage.
- Discover state-management patterns.
- Identify jobs, workers, and scheduling mechanisms.
- Discover persistence and configuration mechanisms.
- Collect source-level evidence.
- Represent uncertainty and incomplete coverage.
- Support incremental refresh.
- Produce a reusable intermediate architecture model.
- Support versioned reports.
- Remain deterministic without an LLM.
- Avoid executing source code by default.
- Provide structured information for verification and migration.

---

# 2. Scope and Non-Goals

## 2.1 In Scope

Architecture discovery shall cover:

- Repository identification.
- Workspace and package boundaries.
- Project configuration and manifests.
- Source inventory.
- Python package and module relationships.
- Imports and dependencies.
- Functions, classes, and interfaces relevant to architectural structure.
- Application entry points.
- CLI registration and dispatch.
- Electron integration patterns.
- External services.
- Process execution.
- Persistence access.
- State ownership patterns.
- Job execution patterns.
- Lifecycle and configuration patterns.
- Architectural evidence collection.
- Finding confidence.
- Incremental discovery.
- Report generation.
- Machine-readable output.
- Extension points for custom detectors.

## 2.2 Out of Scope

Initial static discovery shall not promise to:

- Prove business logic is correct.
- Prove complete runtime dependency usage.
- Execute application entry points.
- Perform automated code changes.
- Guarantee identification of dynamically generated imports.
- Determine actual production availability.
- Discover every reflection-based or plugin-loaded dependency.
- Prove thread safety.
- Prove correct process cleanup.
- Prove database transaction correctness.
- Prove security merely from configuration values.
- Infer business intentions from source-code naming alone.
- Install project dependencies automatically.
- Run arbitrary build scripts or project hooks.

Architecture verification and migration are separate subsystems that consume discovery information.

---

# 3. Architecture Principles

## AD-001 — Read-Only by Default

Static discovery shall not modify the inspected application.

## AD-002 — Evidence-Backed Findings

Every source-derived architectural finding shall reference supporting evidence.

## AD-003 — Separation of Observation and Interpretation

The system shall distinguish directly observed facts from inferred architectural roles.

## AD-004 — Explicit Uncertainty

Unsupported, ambiguous, or dynamic implementation patterns shall be reported as uncertain or unresolved.

## AD-005 — No Default Code Execution

The system shall not import or execute arbitrary application source code during ordinary static discovery.

## AD-006 — Language-Aware Analysis

Analysis shall use appropriate parsers and language-specific detectors.

## AD-007 — Framework Independence

Discovery shall work with repositories that do not use AdharaSutra.

## AD-008 — Shared Architecture Representation

Discovery shall produce a versioned intermediate architecture model consumed by verification, migration, and reporting.

## AD-009 — Deterministic Core

Mandatory analysis shall not depend on LLM inference.

## AD-010 — Incremental Analysis

The engine shall avoid unnecessary rescanning of unchanged source inputs.

## AD-011 — Source Traceability

Findings shall identify the source revision or snapshot against which they were produced.

## AD-012 — Coverage Transparency

The engine shall report which files and architectural concerns were analyzed, excluded, or could not be examined.

## AD-013 — Safe Path Handling

Filesystem analysis shall account for symbolic links, path traversal, exclusion policies, and repository boundaries.

## AD-014 — Extensible Detection

Custom detectors may be registered without modifying the core discovery engine.

## AD-015 — No False Compliance Claims

Discovery output shall not be presented as architecture verification results.

---

# 4. High-Level Architecture

```text
                     APPLICATION REPOSITORY
                              │
                              ▼
                  ┌─────────────────────┐
                  │ Repository Analyzer │
                  │ Root / Git / Config │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Source Inventory    │
                  │ Files / Languages   │
                  │ Packages / Excludes │
                  └──────────┬──────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Language-Aware Analysis      │
              │                              │
              │ Python AST                   │
              │ TypeScript / JavaScript      │
              │ JSON / YAML / TOML           │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Architecture Detectors       │
              │                              │
              │ Entry Points                 │
              │ Dependencies                 │
              │ CLI and Actions              │
              │ Electron Communication       │
              │ Connectors / Processes       │
              │ Persistence / State / Jobs   │
              │ Configuration / Lifecycle    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Evidence and Classification  │
              │                              │
              │ Source References            │
              │ Confidence                   │
              │ Uncertainty                  │
              │ Coverage                     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Architecture Model Builder   │
              │ Normalization / Relationships│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ ApplicationArchitecture      │
              │ Versioned Intermediate Model │
              └──────────────┬───────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
            Verification  Migration     Reporting
```

## 4.1 Responsibility Boundaries

**Discovery Engine:** Finds and describes implementation structures.

**Verification Engine:** Evaluates the discovered implementation against architecture rules.

**Migration Engine:** Uses current architecture and target architecture to identify required changes.

**Reporting Engine:** Presents the architecture model and downstream findings in human-readable or machine-readable formats.

These modules shall share contracts without duplicating discovery logic.

---

# 5. Proposed Module Structure

```text
src/adharasutra/tooling/discovery/
│
├── __init__.py
├── contracts.py
├── engine.py
├── configuration.py
├── errors.py
│
├── repository/
│   ├── roots.py
│   ├── workspaces.py
│   ├── revision.py
│   ├── inventory.py
│   ├── exclusions.py
│   └── filesystem.py
│
├── languages/
│   ├── contracts.py
│   ├── python/
│   │   ├── parser.py
│   │   ├── imports.py
│   │   ├── symbols.py
│   │   └── calls.py
│   ├── typescript/
│   │   ├── parser.py
│   │   ├── imports.py
│   │   └── symbols.py
│   └── configuration/
│       ├── json.py
│       ├── yaml.py
│       └── toml.py
│
├── detectors/
│   ├── contracts.py
│   ├── registry.py
│   ├── entrypoints.py
│   ├── dependencies.py
│   ├── cli.py
│   ├── electron.py
│   ├── connectors.py
│   ├── processes.py
│   ├── persistence.py
│   ├── state.py
│   ├── jobs.py
│   ├── configuration.py
│   └── lifecycle.py
│
├── evidence/
│   ├── references.py
│   ├── confidence.py
│   ├── provenance.py
│   └── validation.py
│
├── model/
│   ├── schema.py
│   ├── builder.py
│   ├── relationships.py
│   ├── normalization.py
│   └── serialization.py
│
├── incremental/
│   ├── cache.py
│   ├── fingerprints.py
│   ├── invalidation.py
│   └── refresh.py
│
└── reporting/
    ├── summary.py
    └── diagnostics.py
```

The structure is provisional. Implementation may combine smaller files while preserving module responsibilities.

---

# 6. Discovery Execution Pipeline

The proposed discovery pipeline contains ten stages.

| Stage | Operation | Output |
|---|---|---|
| 1 | Resolve repository | Repository identity |
| 2 | Load analysis policy | Effective scan configuration |
| 3 | Inventory source | File and package catalog |
| 4 | Parse source | Language syntax models |
| 5 | Analyze relationships | Imports and structural references |
| 6 | Run detectors | Architectural observations |
| 7 | Collect evidence | Source-backed findings |
| 8 | Normalize model | Canonical architecture representation |
| 9 | Validate completeness | Coverage and uncertainty |
| 10 | Produce output | Architecture model and report |

## 6.1 Discovery Modes

The engine should support three modes.

### Full Discovery

Analyze all eligible repository inputs and rebuild the architecture model.

### Incremental Discovery

Reanalyze changed inputs and any dependent findings that are invalidated by those changes.

### Scoped Discovery

Analyze selected packages, modules, or architectural concerns.

For example, the developer may request discovery focused on Electron integration or persistence.

Scoped discovery must be clearly identified as incomplete relative to full-project analysis.

---

# 7. Repository Discovery

## 7.1 Repository Identification

The engine shall identify:

- Repository root.
- Git worktree when available.
- Python package roots.
- Electron project roots.
- Nested packages.
- Workspace configuration.
- Project manifests.

## 7.2 Git Support

Where a Git repository is available, discovery metadata should include:

- Commit identifier.
- Branch information where available.
- Worktree state.
- Whether uncommitted modifications affect analyzed files.

A source revision must not be represented solely by the last commit when the worktree contains relevant uncommitted changes.

## 7.3 Non-Git Repositories

Git shall not be mandatory.

Non-Git repositories may be identified using normalized root identity and source fingerprints.

## 7.4 Monorepos

The engine should support repositories containing multiple applications or packages.

For example:

```text
workspace/
├── applications/
│   ├── vani/
│   └── image-studio/
├── shared/
│   └── python-common/
└── packages/
    └── electron-common/
```

Independent application boundaries should be represented separately.

## 7.5 Nested Repositories

Nested Git repositories and submodules must not be silently treated as ordinary files.

Their analysis scope must follow explicit policy.

## 7.6 Repository Boundary

The analyzer shall not inspect unrelated filesystem locations outside the approved root unless the user explicitly authorizes additional source roots.

---

# 8. Source Inventory

## 8.1 Purpose

The source inventory identifies files eligible for architectural analysis.

## 8.2 Relevant Inputs

Potential inputs include:

- Python files.
- TypeScript files.
- JavaScript files.
- `pyproject.toml`.
- `package.json`.
- Electron configuration.
- YAML configuration.
- JSON configuration.
- Requirements files.
- Application manifests.
- Test configuration.
- Architecture profile metadata.

## 8.3 Default Exclusions

Default exclusions should include generated and dependency directories such as:

```text
.git/
.venv/
venv/
node_modules/
__pycache__/
dist/
build/
coverage/
.pytest_cache/
```

Additional exclusions shall be configurable.

## 8.4 Ignore Policies

The engine may support project-specific discovery ignore rules.

It must distinguish intentionally excluded files from unsupported or failed analysis.

## 8.5 Filesystem Limits

Scanning must support configurable limits for:

- File size.
- Total analyzed files.
- Total source bytes.
- Directory depth.
- Analysis duration.

Reaching a limit must produce a coverage warning rather than an assertion that the repository was fully analyzed.

## 8.6 Symbolic Links

Symbolic links must be handled explicitly.

The engine shall:

1. Record the logical link path.
2. Determine its resolved target where safe.
3. Prevent unapproved traversal outside repository boundaries.
4. Detect cycles.
5. Avoid duplicate analysis of the same target where appropriate.
6. Preserve provenance for logical and physical paths.

---

# 9. Language-Aware Analysis

## 9.1 Principle

Different programming languages require appropriate parsing and relationship extraction.

The engine shall not rely exclusively on regular expressions for language structure.

## 9.2 Python Analysis

Python analysis shall use AST-based parsing as its initial foundation.

It should identify:

- Modules and packages.
- Imports.
- Classes.
- Functions.
- Decorators.
- Base classes.
- Function calls.
- Entry-point patterns.
- Selected configuration literals.
- Relevant architectural references.

## 9.3 TypeScript and JavaScript

Electron analysis should use a language-aware parser capable of identifying:

- Import and export relationships.
- Function calls.
- Electron APIs.
- IPC handlers.
- Child-process invocation.
- Preload exposure.
- Bridge imports.
- Renderer-to-main communication patterns.

The choice of parser must be validated against realistic TypeScript syntax, not just JavaScript-compatible subsets.

## 9.4 Configuration Files

Supported configuration formats should use actual parsers.

The engine shall distinguish:

- Valid configuration values.
- Missing fields.
- Unsupported configuration structures.
- Invalid syntax.
- Dynamically computed values unavailable to static analysis.

## 9.5 Parse Failures

If a source file cannot be parsed, the engine shall:

- Record the affected file.
- Record the parser failure.
- Preserve source coverage status.
- Continue analyzing unaffected files where safe.
- Avoid treating incomplete results as complete.

## 9.6 Unsupported Languages

An unsupported language may appear in the source inventory without receiving full semantic analysis.

Its coverage status must reflect that limitation.

---

# 10. Module and Dependency Discovery

## 10.1 Purpose

Discover source modules and their relationships.

## 10.2 Dependency Types

The model should distinguish:

| Relationship | Meaning |
|---|---|
| Import | Static source import |
| Type dependency | Type or interface reference |
| Instantiation | Creation of a concrete implementation |
| Invocation | Identifiable function or method call |
| Registration | Component registered through an API |
| Configuration reference | Named reference in configuration |
| Dynamic dependency | Runtime-computed dependency with incomplete resolution |

## 10.3 Dependency Graph

The engine shall construct a graph of discovered modules and dependencies.

```text
interfaces.cli
      │
      ▼
application.services
      │
      ▼
application.ports
      ▲
      │
infrastructure.adapters
      │
      ▼
adharasutra.connectors
```

A graph represents discovered relationships, not automatically approved architecture.

## 10.4 Internal and External Dependencies

The analyzer should distinguish:

- Internal application modules.
- Framework modules.
- Standard-library modules.
- Third-party packages.
- Unresolved imports.

## 10.5 Dynamic Imports

Patterns such as runtime imports or plugin discovery may not be fully resolvable statically.

The engine shall record evidence of dynamic dependency mechanisms and identify unresolved targets.

## 10.6 Cycles

Detected dependency cycles should be recorded in the architecture model.

Classification as a violation belongs to the verifier and depends on the selected architecture profile.

---

# 11. Entry-Point Discovery

## 11.1 Purpose

Find how applications start and expose operations.

## 11.2 Python Entry Points

Relevant patterns include:

- `if __name__ == "__main__"`.
- Package `__main__.py`.
- Console script declarations.
- CLI framework registrations.
- Direct application runtime execution.
- AdharaSutra application bootstrap.

## 11.3 Multiple Entry Points

An application may have separate:

- CLI entry points.
- Worker entry points.
- Development utilities.
- Test entry points.

The engine must not automatically treat every executable script as a production application entry point.

## 11.4 Entry-Point Metadata

A discovered entry point should identify:

- Entry-point identifier.
- Source location.
- Invocation form where known.
- Target module or function.
- Related runtime or CLI framework.
- Confidence.
- Evidence.

---

# 12. CLI Architecture Discovery

## 12.1 Purpose

Identify how an application receives and routes command-line operations.

## 12.2 Patterns

The engine should recognize supported patterns such as:

- AdharaSutra action registration.
- `argparse`.
- Typer.
- Click.
- Direct `sys.argv` handling.
- Custom command routers.
- JSON stdin parsing.
- stdout response emission.

## 12.3 Action and Command Inventory

The discovery output should identify:

- Action or command name.
- Registration source.
- Handler reference.
- Argument or payload information where statically available.
- Execution mode where determinable.
- Related service dependencies.

## 12.4 Custom CLI Implementations

The engine must not assume a custom CLI is invalid merely because it does not use AdharaSutra.

Discovery describes the current implementation.

Verification later decides whether the pattern conforms to the target architecture.

## 12.5 Dynamic Registration

Dynamically registered commands shall be reported with appropriate uncertainty.

---

# 13. Electron Integration Discovery

## 13.1 Purpose

Identify Electron architecture and how it communicates with Python.

## 13.2 Electron Components

The analyzer should discover:

- Main process entry points.
- Preload scripts.
- Renderer roots.
- IPC handlers.
- IPC send/invoke calls.
- Context bridge exposure.
- Child-process creation.
- Shared AdharaSutra bridge usage.
- Existing custom Python communication layers.

## 13.3 Communication Patterns

Possible patterns include:

- Python subprocess with stdin/stdout.
- One-shot command execution.
- Persistent NDJSON process communication.
- HTTP communication with a Python server.
- Custom sockets.
- AdharaSutra bridge.

An existing application may use a different communication architecture.

The engine shall record that fact without automatically treating it as a violation.

## 13.4 IPC Relationships

Where resolvable, the model should connect:

```text
Renderer Invocation
        │
        ▼
Preload API
        │
        ▼
IPC Handler
        │
        ▼
Python Bridge / Subprocess
        │
        ▼
Python Entry Point
```

## 13.5 Partial Relationships

When a dynamic IPC channel name prevents exact resolution, the engine shall record the observed endpoints and unresolved relationship.

## 13.6 Electron Security Observations

Discovery may record statically visible settings such as:

- `contextIsolation`.
- `nodeIntegration`.
- Preload path.
- IPC authorization patterns.

Determining whether the application is secure belongs to security verification and testing.

---

# 14. Connector Discovery

## 14.1 Purpose

Identify infrastructure used by application modules.

## 14.2 HTTP Patterns

Examples:

- HTTPX client usage.
- Requests library usage.
- `aiohttp` usage.
- Framework HTTP connector usage.
- Custom HTTP wrappers.

## 14.3 WebSocket Patterns

Examples:

- WebSocket client creation.
- Connection lifecycle methods.
- Message subscriptions.
- Reconnection logic.

## 14.4 External Process Patterns

Examples:

- `subprocess.run`.
- `subprocess.Popen`.
- `asyncio.create_subprocess_exec`.
- Framework process connector.
- Custom process runners.
- Electron `spawn` or `exec`.

## 14.5 SQLite Patterns

Examples:

- `sqlite3.connect`.
- Database connection factories.
- ORM engine initialization.
- Custom repositories.
- Framework SQLite connector usage.

## 14.6 Filesystem Patterns

Examples:

- Direct filesystem access.
- Managed artifact directories.
- Temporary file utilities.
- Framework filesystem facilities.

## 14.7 Connector Inventory

For each connector or integration, record:

- Connector category.
- Implementation library.
- Source locations.
- Configuration references.
- Lifecycle ownership where observed.
- Related application adapters.
- Identified external dependency.
- Confidence and evidence.

## 14.8 Avoiding False Classification

A source file importing `httpx` is evidence of an HTTP library dependency.

It is not by itself proof that an HTTP client initializes at runtime.

---

# 15. State Discovery

## 15.1 Purpose

Identify where an application stores and mutates state.

## 15.2 State Patterns

The engine should inspect for:

- Module-level mutable variables.
- Global dictionaries.
- Singleton state managers.
- Framework state registration.
- Session state containers.
- Job state stores.
- JSON-file persistence.
- SQLite-backed settings.
- Electron-side state synchronization.

## 15.3 State Classification

Potential classifications include:

- Request state.
- Session state.
- Process state.
- Job state.
- Persistent state.
- UI-only state.
- Unknown scope.

A classification must be supported by implementation evidence.

## 15.4 Static Limitations

An object declared at module level may not actually be used as shared mutable business state.

Similarly, a local dictionary may escape its originating function through references.

The engine must preserve uncertainty in such cases.

## 15.5 State Ownership

State ownership should be recorded as:

- Observed owner.
- Inferred owner.
- Unknown owner.

The model must not invent persistence guarantees.

---

# 16. Job and Worker Discovery

## 16.1 Purpose

Identify long-running execution patterns.

## 16.2 Patterns

Examples:

- `asyncio.create_task`.
- Thread pools.
- Process pools.
- Background worker classes.
- Custom job managers.
- Queue-based execution.
- Framework job registration.
- External subprocess-based workloads.

## 16.3 Job Relationships

Where possible, record:

- Submission point.
- Handler.
- Execution mechanism.
- State tracking.
- Progress reporting.
- Cancellation handling.
- Result handling.
- Persistence mechanism.
- Execution owner.

## 16.4 Durable Worker Identification

A persisted job table is not sufficient evidence of durable execution.

The analyzer should seek evidence of independent execution ownership, recovery, or worker lifecycle.

If those cannot be established, durability remains unverified.

## 16.5 Job Versus Process

The model shall distinguish a managed job from an operating-system process.

A process invocation does not automatically imply that an application has a job-management architecture.

---

# 17. Configuration and Lifecycle Discovery

## 17.1 Configuration Discovery

The engine should identify:

- Configuration files.
- Environment-variable usage.
- Settings classes.
- Configuration loaders.
- Framework configuration.
- Application-specific overrides.
- Configuration initialization patterns.

## 17.2 Configuration Precedence

Configuration precedence shall only be reported as confirmed where implementation evidence establishes the effective ordering.

Merely finding multiple configuration sources is insufficient.

## 17.3 Lifecycle Discovery

Identify patterns associated with:

- Application bootstrap.
- Service initialization.
- Startup hooks.
- Shutdown hooks.
- Resource cleanup.
- Signal handling.
- Connector lifecycle.
- Worker startup.
- Readiness checks.

## 17.4 Ownership Uncertainty

If lifecycle ownership is distributed across dynamically called functions, the engine may record incomplete relationships.

## 17.5 Failure Behavior

Static discovery may identify exception handlers and cleanup blocks.

It must not claim that all runtime failures are correctly handled without executable evidence.

---

# 18. Shared Intermediate Architecture Model

## 18.1 Purpose

The **ApplicationArchitecture model** is the primary output of discovery.

It provides a common representation consumed by other architecture tools.

## 18.2 Proposed Model

```text
ApplicationArchitecture
│
├── SchemaVersion
├── RepositoryIdentity
├── SourceSnapshot
├── AnalysisMetadata
├── Coverage
│
├── Applications
├── Packages
├── Modules
├── Dependencies
├── EntryPoints
│
├── CLI
│   ├── Commands
│   ├── Actions
│   └── RoutingRelationships
│
├── Electron
│   ├── MainProcesses
│   ├── PreloadAPIs
│   ├── Renderers
│   └── IPCRelationships
│
├── Connectors
├── ExternalDependencies
├── Processes
├── Persistence
├── State
├── Jobs
├── Configuration
├── Lifecycle
│
├── Relationships
├── Evidence
├── UnresolvedReferences
└── AnalysisDiagnostics
```

## 18.3 Model Requirements

The model shall:

- Be versioned.
- Have stable field definitions.
- Support missing and unknown information.
- Preserve source evidence.
- Represent relationships explicitly.
- Support machine-readable serialization.
- Avoid circular serialized object structures.
- Support downstream tools without requiring access to parser internals.

## 18.4 Architecture Model Ownership

Discovery owns population of the current-implementation model.

The architecture-profile subsystem owns the definition of desired target architecture.

Verification owns evaluation results.

Migration owns transformation plans.

## 18.5 Separation of Models

The following are distinct:

```text
CurrentArchitecture
TargetArchitecture
VerificationResult
MigrationPlan
```

The discovery engine produces the first.

It must not silently populate a target architecture by assuming the existing implementation is correct.

---

# 19. Architecture Entity Identity

## 19.1 Purpose

Architecture elements require identifiers suitable for references across reports and tools.

## 19.2 Identity Categories

Potential entities include:

- Application.
- Package.
- Module.
- Function.
- Class.
- Entry point.
- Action.
- Connector.
- State store.
- Job handler.
- Process invocation.
- Configuration source.

## 19.3 Identity Rules

Entity identifiers should be deterministic for a given source snapshot and normalized representation.

Identifiers may incorporate:

- Entity kind.
- Package namespace.
- Qualified symbol name.
- Relative source path.

## 19.4 Identity Stability

Source renames and moves may change identifiers.

The engine must not claim persistent identity across arbitrary refactors without a supported matching mechanism.

## 19.5 Duplicate Detection

Equivalent observations from multiple detectors should be normalized without losing their separate evidence references.

---

# 20. Evidence Architecture

## 20.1 Purpose

Every architectural observation must be traceable to its supporting inputs.

## 20.2 Evidence Sources

Evidence may originate from:

- Source files.
- Package manifests.
- Configuration files.
- Import declarations.
- Function calls.
- Class declarations.
- Decorators.
- Test definitions.
- Explicitly authorized runtime observations.

## 20.3 Evidence Record

A source evidence record should include:

| Field | Purpose |
|---|---|
| `evidence_id` | Stable evidence reference |
| `source_path` | Repository-relative source file |
| `source_hash` | Fingerprint of inspected content |
| `start_line` | Beginning of supporting range |
| `end_line` | End of supporting range |
| `symbol` | Related symbol when known |
| `observation` | What the evidence directly shows |
| `detector_id` | Detector that produced the observation |
| `analysis_method` | Static parser, manifest parser, etc. |

## 20.4 Example Evidence

```json
{
  "evidence_id": "ev-001",
  "source_path": "src/app/services/audio.py",
  "source_hash": "sha256:<digest>",
  "start_line": 24,
  "end_line": 28,
  "symbol": "AudioService.generate",
  "observation": "Calls subprocess.run",
  "detector_id": "python.process.subprocess_call",
  "analysis_method": "python_ast"
}
```

This example is illustrative.

## 20.5 Evidence Granularity

Evidence should point to the smallest useful source range.

Referencing an entire file when a specific statement supports the finding reduces traceability.

## 20.6 Evidence Freshness

Evidence shall be associated with the inspected source content.

If the file changes, the engine must be able to detect that previously collected evidence may be stale.

## 20.7 Evidence Integrity

Evidence records must not be silently reused after their supporting source changes.

---

# 21. Observation, Inference, and Confidence

## 21.1 Classification

A finding may be classified as:

- **Observed:** Directly supported by identifiable source syntax or configuration.
- **Inferred:** Derived from multiple observations or conventions.
- **Unresolved:** Insufficient evidence exists for a reliable conclusion.

## 21.2 Confidence

Proposed confidence levels:

| Confidence | Meaning |
|---|---|
| High | Strong, direct evidence |
| Medium | Reasonable inference with documented assumptions |
| Low | Weak or ambiguous evidence |
| Unknown | Cannot determine |

Confidence is not equivalent to correctness.

High confidence in a static observation does not prove runtime behavior.

## 21.3 Example

Finding:

> The application uses the Python `subprocess` module.

Evidence: A direct `subprocess.run` call.

Classification: Observed.

Confidence: High.

Different finding:

> The application consistently cleans up every child process.

This cannot be established from the same call.

Classification: Unresolved unless additional evidence supports a more specific conclusion.

## 21.4 Conflicting Findings

If detectors produce conflicting interpretations, the model shall retain the conflict or record a documented resolution with supporting evidence.

It must not silently choose whichever finding is more convenient for verification.

---

# 22. Detection Engine Architecture

## 22.1 Detector Contract

Each detector should declare:

- Detector identifier.
- Version.
- Supported languages.
- Applicable source inputs.
- Architectural concern.
- Required analysis facts.
- Produced observation types.
- Known limitations.

## 22.2 Conceptual Interface

```python
from typing import Protocol


class ArchitectureDetector(Protocol):
    detector_id: str

    def analyze(
        self,
        context,
    ):
        ...
```

This is a conceptual interface, not a finalized public API.

## 22.3 Detector Isolation

A detector shall not modify source files.

One detector failure should not automatically discard valid results from unrelated detectors.

## 22.4 Detection Dependencies

Detectors may depend on previously extracted syntax or relationship facts.

Dependencies must be explicit.

## 22.5 Detector Registration

Framework detectors should be registered through a central registry.

Applications may supply approved custom detectors.

## 22.6 Detector Output

Detectors produce architectural observations and evidence.

They do not produce architecture compliance verdicts.

---

# 23. Custom Discovery Extensions

## 23.1 Purpose

Applications may use integration patterns that the default engine does not understand.

## 23.2 Extension Examples

Potential custom detectors:

- A project-specific plugin registry.
- An application-specific job scheduler.
- A custom Electron IPC wrapper.
- A specialized external process adapter.
- A proprietary persistence abstraction.

## 23.3 Extension Constraints

Custom detectors must follow:

- Read-only analysis rules.
- Evidence requirements.
- Model schema contracts.
- Resource limits.
- Error reporting conventions.

## 23.4 Trusted Execution Boundary

Detector plugins are executable tooling code.

Only explicitly trusted detector implementations may be loaded.

Ordinary discovery shall not import arbitrary detector implementations from the repository being inspected.

## 23.5 Versioning

Custom detectors shall declare compatibility with the discovery contract version.

---

# 24. Incremental Discovery

## 24.1 Purpose

Large applications should not require full analysis after every small source change.

## 24.2 Cacheable Information

Potential cached results include:

- File fingerprints.
- Parsed syntax facts.
- Import relationships.
- Detector observations.
- Evidence records.
- Model fragments.

## 24.3 Cache Key

Cached results must be associated with relevant factors such as:

- Source content fingerprint.
- Parser version.
- Detector version.
- Discovery configuration.
- Relevant dependency context.

## 24.4 Changed Files

When a file changes, the engine shall invalidate affected source facts and dependent findings.

## 24.5 Deleted Files

Deleted source files must not remain as current observations.

## 24.6 Renamed Files

Renames must update paths and references.

Content-based reuse may be supported, but current evidence paths must reflect the new source snapshot.

## 24.7 Configuration Changes

Changes to discovery configuration, exclusions, parser options, or detector versions may invalidate cached analysis even if source files are unchanged.

## 24.8 Full Refresh

The developer shall be able to request a complete rescan.

## 24.9 Cache Correctness

Incremental results shall be semantically equivalent to full discovery within the supported analysis contract.

This must be tested.

---

# 25. Source Snapshot and Consistency

## 25.1 Problem

Files may change while discovery is running.

A report must not silently combine incompatible source states and claim that it represents one coherent repository snapshot.

## 25.2 Proposed Approach

Discovery shall record content fingerprints for inspected inputs.

Before finalization, the engine should validate that relevant source content remains consistent or mark the analysis as potentially inconsistent.

## 25.3 Working Tree Changes

A dirty Git worktree is valid input.

However, the report must identify the analyzed worktree state rather than claim to describe only the last committed revision.

## 25.4 Concurrent Changes

If files change during analysis, the engine may:

- Retry affected portions within a bounded limit.
- Report a partial or inconsistent snapshot.
- Require a new scan.

## 25.5 Snapshot Metadata

The model should record:

- Repository identity.
- Commit identifier where available.
- Worktree modification indicator.
- Source fingerprints.
- Analysis timestamp.
- Consistency status.

---

# 26. Analysis Coverage

## 26.1 Purpose

Coverage communicates how much of the relevant repository was actually analyzed.

## 26.2 Coverage Categories

Proposed statuses:

- `analyzed`
- `excluded`
- `unsupported`
- `parse_failed`
- `skipped_limit`
- `unresolved`
- `not_checked`

## 26.3 Coverage Dimensions

The engine should report coverage by:

- Language.
- File category.
- Repository package.
- Architectural concern.
- Detector.

## 26.4 Example

```json
{
  "coverage": {
    "python": {
      "eligible_files": 124,
      "analyzed_files": 121,
      "parse_failed": 3
    },
    "typescript": {
      "eligible_files": 42,
      "analyzed_files": 42
    }
  }
}
```

This example is illustrative.

## 26.5 Coverage and Confidence

High confidence in a specific observation does not imply complete coverage of that architectural concern.

A report may confidently identify one external process call while other unparsed files remain unexplored.

## 26.6 Verification Integration

The verifier must consider discovery coverage before issuing compliance verdicts.

An unexamined source area must not be assumed compliant.

---

# 27. Architecture Model Schema

## 27.1 Versioned JSON Output

The intermediate model should support JSON serialization.

## 27.2 Illustrative Structure

```json
{
  "schema_version": "1.0",
  "repository": {
    "root": ".",
    "revision": "abc123",
    "working_tree_modified": true
  },
  "analysis": {
    "mode": "static",
    "status": "partial"
  },
  "applications": [
    {
      "id": "app.main",
      "name": "example-app"
    }
  ],
  "modules": [
    {
      "id": "module.audio",
      "path": "src/app/audio.py"
    }
  ],
  "dependencies": [],
  "entry_points": [],
  "cli_actions": [],
  "electron_integrations": [],
  "connectors": [],
  "state_stores": [],
  "jobs": [],
  "persistence": [],
  "configuration": [],
  "lifecycle": [],
  "evidence": [],
  "unresolved": [],
  "diagnostics": []
}
```

This example describes the proposed model shape.

A formally versioned schema shall be created during detailed implementation design.

## 27.3 Schema Requirements

The schema shall define:

- Required fields.
- Optional fields.
- Entity identity.
- Relationship representation.
- Evidence references.
- Coverage representation.
- Unknown values.
- Version compatibility.

## 27.4 Unknown Versus Absent

The model must distinguish:

- A component was searched for and not found within a sufficiently analyzed scope.
- A component may exist but its presence is unknown.
- A component is outside the selected discovery scope.

## 27.5 Model Validation

Serialized architecture models shall be validated before being provided to downstream consumers.

---

# 28. Discovery Reporting

## 28.1 Report Types

The Discovery subsystem should support:

1. Architecture inventory.
2. Dependency summary.
3. CLI architecture summary.
4. Electron integration summary.
5. Connector inventory.
6. State and job inventory.
7. Configuration and lifecycle summary.
8. Unresolved findings report.
9. Analysis coverage report.

## 28.2 Markdown Output

Markdown reports should be readable by developers and coding agents.

## 28.3 JSON Output

JSON reports shall preserve machine-readable architecture entities and evidence references.

## 28.4 Report Accuracy

A report must identify:

- Analysis mode.
- Source snapshot.
- Analysis scope.
- Supported languages.
- Detectors used.
- Coverage.
- Findings.
- Unresolved areas.

## 28.5 No Compliance Verdicts

Discovery reports may identify architectural patterns.

They shall not label an implementation compliant or noncompliant without an explicit verification rule evaluation.

---

# 29. Developer CLI

## 29.1 Proposed Commands

Full discovery:

```bash
adhara inspect ./my-application
```

JSON output:

```bash
adhara inspect ./my-application --format json
```

Focused analysis:

```bash
adhara inspect ./my-application --focus electron
```

Incremental refresh:

```bash
adhara inspect ./my-application --incremental
```

Full rescan:

```bash
adhara inspect ./my-application --full
```

Explicit output:

```bash
adhara inspect ./my-application \
  --format markdown \
  --output ./reports/current-architecture.md
```

These commands are proposed, not implemented.

## 29.2 Default Behavior

The initial default should be:

- Read-only.
- Static analysis.
- Full discovery or valid cached refresh.
- No dependency installation.
- No application execution.
- No external network calls.
- No source rewriting.

## 29.3 Exit Status

The CLI shall distinguish:

- Successful complete analysis.
- Successful partial analysis.
- Invalid inputs.
- Repository access failure.
- Unsupported analysis request.
- Internal discovery failure.

The final exit-code mapping will be defined in the developer CLI contract.

---

# 30. Optional Runtime Observation

## 30.1 Purpose

Some architectural behaviors cannot be established statically.

Optional runtime observation may supplement static discovery.

## 30.2 Execution Boundary

Runtime observation must be explicitly requested.

It shall not execute arbitrary repository code as a side effect of ordinary discovery.

## 30.3 Possible Techniques

- Controlled application test execution.
- Instrumented framework runtime.
- Test fixture execution.
- Developer-supplied observation reports.

## 30.4 Trust and Isolation

Runtime observation may execute application code with side effects.

It must use explicit permission, controlled environments, and documented isolation limits.

A subprocess alone is not a security sandbox.

## 30.5 Evidence Classification

Runtime observations must be labeled separately from static evidence.

They must identify:

- Observation method.
- Execution environment.
- Test scenario.
- Timestamp.
- Source revision.
- Relevant limitations.

## 30.6 No Runtime Overclaiming

Observing one execution path does not prove that every possible application path behaves identically.

---

# 31. Optional AI-Assisted Interpretation

## 31.1 Purpose

An optional AI-assisted layer may help explain complex architecture relationships that deterministic analysis cannot classify confidently.

## 31.2 Core Independence

LLM assistance must not be required for mandatory discovery.

## 31.3 Permitted Uses

Potential uses include:

- Suggesting likely architectural roles.
- Explaining complex dependency graphs.
- Summarizing unresolved findings.
- Proposing additional inspection targets.

## 31.4 Evidence Requirements

AI-generated interpretations must remain distinct from deterministic observations.

A plausible interpretation must not be promoted to an observed fact without supporting evidence.

## 31.5 Sensitive Source Handling

Sending application source to external providers requires explicit authorization and appropriate data-handling policies.

The default discovery engine shall remain local-first.

---

# 32. Performance and Resource Management

## 32.1 Performance Goals

The discovery engine should scale to moderately large Python and Electron repositories without requiring repeated full analysis.

## 32.2 Resource Controls

The engine shall support configurable limits for:

- Analysis concurrency.
- File sizes.
- Total analyzed source.
- Memory.
- Cache storage.
- Analysis duration.
- Diagnostic output.

## 32.3 Parallel Analysis

Independent files may be parsed concurrently when the parser and cache mechanisms support safe parallel execution.

## 32.4 Incremental Efficiency

Unchanged source files should avoid repeated parsing where cached results remain valid.

## 32.5 Bounded Reporting

Very large architecture models should support summary and detailed reporting without forcing all findings into one enormous console response.

## 32.6 Performance Metrics

Relevant measurements include:

- Inventory time.
- Parsing time.
- Detector execution time.
- Model construction time.
- Full discovery duration.
- Incremental refresh duration.
- Peak memory.
- Cache hit rate.

Numerical thresholds must be validated against representative repositories.

---

# 33. Security Architecture

## 33.1 Source Code Is Untrusted Input

The engine shall treat inspected repositories as untrusted data.

## 33.2 No Arbitrary Imports

Static discovery shall not import modules from the inspected application.

## 33.3 No Build Hook Execution

Reading `pyproject.toml` or `package.json` shall not trigger their configured scripts or build hooks.

## 33.4 Parser Safety

Parsers shall enforce appropriate resource limits and reject malformed inputs safely.

## 33.5 Path Security

Filesystem traversal must follow approved repository boundaries.

## 33.6 Cache Security

Cached source facts and architecture evidence may reveal sensitive implementation details.

Caches must use appropriate local storage restrictions and cleanup policies.

## 33.7 Report Redaction

Reports must not indiscriminately contain:

- Credentials.
- Environment-secret values.
- Complete private configuration contents.
- Sensitive source snippets unrelated to findings.

## 33.8 Source Paths

Absolute local paths may expose unnecessary environment information.

Reports should prefer normalized repository-relative paths.

## 33.9 Custom Detectors

Custom detectors must be trusted before execution.

## 33.10 External Communication

Static discovery should not require network access.

---

# 34. Errors and Diagnostics

## 34.1 Proposed Error Categories

```text
DISCOVERY_REPOSITORY_NOT_FOUND
DISCOVERY_ACCESS_DENIED
DISCOVERY_INVALID_CONFIGURATION
DISCOVERY_UNSUPPORTED_LANGUAGE
DISCOVERY_PARSE_FAILED
DISCOVERY_DETECTOR_FAILED
DISCOVERY_MODEL_INVALID
DISCOVERY_CACHE_INVALID
DISCOVERY_SOURCE_CHANGED
DISCOVERY_LIMIT_EXCEEDED
DISCOVERY_INCOMPLETE
```

These identifiers must be reconciled with the framework-wide error catalog.

## 34.2 Partial Failure

A parser or detector failure may permit partial discovery.

The resulting model must include affected coverage and diagnostics.

## 34.3 Fatal Failure

Failures preventing construction of a trustworthy model shall produce an explicit discovery failure.

## 34.4 Diagnostic Record

Diagnostics should identify:

- Error category.
- Affected source or detector.
- Analysis phase.
- Whether other analysis continued.
- Relevant evidence.
- Safe remediation advice.

---

# 35. Architecture Verification Integration

## 35.1 Responsibility Separation

Discovery produces observed architecture.

Verification evaluates rules.

For example:

**Discovery finding:**

> `src/app/audio.py` calls `subprocess.run`.

**Verification question:**

> Does this violate the selected application's requirement to use the AdharaSutra Process Connector?

The discovery result is evidence.

The verification result is a rule-based judgment.

## 35.2 Shared Inputs

The verification engine shall consume:

- Architecture model.
- Source evidence.
- Coverage.
- Analysis diagnostics.
- Architecture profile.
- Versioned rule definitions.

## 35.3 Incomplete Discovery

If necessary analysis is unavailable, the verifier shall use `NOT_CHECKED` or `NEEDS_REVIEW` according to the rule's contract.

It shall not issue PASS solely because no violation was discovered.

## 35.4 Rule Evidence

Verification findings should reference the underlying discovery evidence whenever applicable.

## 35.5 No Duplicate Parsing Logic

The verifier should reuse discovery facts rather than create a separate source-analysis pipeline for identical structural observations.

---

# 36. Migration Integration

## 36.1 Purpose

Migration needs an accurate understanding of the current application before planning changes.

## 36.2 Discovery Inputs

The Migration subsystem shall consume:

- Current architecture.
- Source dependencies.
- Entry points.
- CLI communication.
- Connector patterns.
- State and jobs.
- Persistence.
- Configuration.
- Lifecycle.
- Unresolved areas.

## 36.3 Current Versus Target

The migration planner compares:

```text
Current Architecture
         │
         ▼
Target Architecture Profile
         │
         ▼
Architecture Gap Analysis
         │
         ▼
Migration Plan
```

## 36.4 Unknown Behavior

The migration engine must not assume unresolved implementation behavior is safe to replace.

## 36.5 Evidence Preservation

Migration recommendations should reference discovery evidence for affected components.

## 36.6 Refresh After Migration

After code changes, discovery must be refreshed.

Old findings must not remain current when supporting source has changed.

---

# 37. Scaffolding Integration

## 37.1 Purpose

Scaffolding and discovery must use compatible architecture models.

## 37.2 Generated Applications

A newly generated application should be discoverable using the standard Discovery subsystem.

## 37.3 Profile Metadata

Discovery should recognize declared architecture profiles and scaffold provenance.

## 37.4 Current Source Is Authoritative

A scaffold metadata file describes how the project was originally generated.

The current source inventory determines what the application actually contains.

## 37.5 Template Drift

The engine may detect relevant differences between current source and recorded scaffold metadata.

Whether those differences violate architectural requirements belongs to verification.

---

# 38. Architecture Discovery Testing

## 38.1 Unit Tests

Verify:

- Repository root detection.
- Inventory classification.
- Exclusion handling.
- File fingerprinting.
- Parsing.
- Dependency extraction.
- Evidence generation.
- Model validation.

## 38.2 Python Detection Tests

Use fixtures covering:

- Static imports.
- Relative imports.
- Aliased imports.
- Decorators.
- Entry points.
- `argparse`.
- Custom CLI routers.
- Subprocess calls.
- SQLite usage.
- Dynamic imports.

## 38.3 Electron Detection Tests

Use fixtures covering:

- Main-process entry points.
- Preload APIs.
- IPC registration.
- Renderer invocations.
- Child-process creation.
- Shared bridge integration.
- Dynamic IPC channel names.

## 38.4 State and Job Tests

Verify detection of:

- Global state.
- Session state.
- Custom job managers.
- Async tasks.
- Thread pools.
- Process pools.
- Managed framework jobs.

## 38.5 Evidence Tests

Verify:

- Correct source paths.
- Correct line ranges.
- Valid source hashes.
- Detector provenance.
- Stale evidence detection.

## 38.6 Incremental Tests

Verify:

- Unchanged source.
- Modified source.
- Deleted files.
- Renamed files.
- Changed exclusions.
- Changed detector versions.
- Changed parser versions.
- Symbolic-link retargeting.

## 38.7 Equivalence Tests

Full discovery and incremental discovery of the same source snapshot shall produce equivalent canonical architecture models.

## 38.8 Security Tests

Verify:

- Repository traversal prevention.
- Malicious symbolic links.
- Invalid source files.
- Oversized inputs.
- Sensitive configuration redaction.
- No execution of inspected source.

## 38.9 Failure Injection

Simulate:

- Read errors.
- Parse failures.
- Detector exceptions.
- Cache corruption.
- File deletion during analysis.
- Concurrent file changes.
- Output write failure.

---

# 39. Discovery Contract Verification Rules

These rules validate the Discovery subsystem's outputs and operation. They are distinct from application architecture compliance rules.

| Rule ID | Description |
|---|---|
| AD-VER-001 | Discovery is read-only by default |
| AD-VER-002 | Source-derived findings include evidence |
| AD-VER-003 | Evidence references valid analyzed source |
| AD-VER-004 | Source snapshot identity is recorded |
| AD-VER-005 | Unknown and unresolved findings are distinguishable |
| AD-VER-006 | Coverage information is reported |
| AD-VER-007 | Source parse failures are preserved |
| AD-VER-008 | Dependency relationships identify their evidence |
| AD-VER-009 | Dynamic dependencies are not silently treated as resolved |
| AD-VER-010 | Unsupported languages are reported accurately |
| AD-VER-011 | Excluded files are identified in coverage |
| AD-VER-012 | Cached findings are invalidated when necessary |
| AD-VER-013 | Deleted source does not remain as current evidence |
| AD-VER-014 | File renames and path changes are reconciled |
| AD-VER-015 | Source traversal remains within approved boundaries |
| AD-VER-016 | Model schema validation succeeds |
| AD-VER-017 | Detector failures do not create false observations |
| AD-VER-018 | Discovery reports do not fabricate compliance results |
| AD-VER-019 | Runtime observations are distinguished from static findings |
| AD-VER-020 | Discovery remains functional without an LLM |

---

# 40. End-to-End Validation Scenarios

## AD-S01 — New AdharaSutra Application

**Given** a project generated by the AdharaSutra scaffolder,

**When** discovery runs,

**Then** the engine shall identify its application bootstrap, registered actions, declared architecture profile, and selected connectors.

**And** findings shall reference the current source.

## AD-S02 — Existing Python CLI Application

**Given** an application using `argparse` rather than AdharaSutra,

**When** discovery runs,

**Then** the engine shall identify supported command registrations and entry points.

**And** shall not incorrectly claim the application already uses AdharaSutra.

## AD-S03 — Existing Electron Application

**Given** Electron starts a Python subprocess,

**When** discovery runs,

**Then** the engine shall identify the supported process invocation and relevant IPC relationships.

**And** unresolved dynamic routing shall be reported.

## AD-S04 — HTTP Integration

**Given** an application makes HTTP requests through HTTPX,

**When** discovery runs,

**Then** the engine shall record the supported library usage and related source evidence.

**And** shall not infer remote service availability.

## AD-S05 — External CLI Integration

**Given** an application calls `subprocess.run`,

**When** discovery runs,

**Then** the engine shall identify the invocation.

**And** shall not assume the subprocess is managed as a job.

## AD-S06 — SQLite Persistence

**Given** an application uses `sqlite3.connect`,

**When** discovery runs,

**Then** the engine shall identify the connection pattern.

**And** describe repository relationships where supported.

## AD-S07 — Custom State Manager

**Given** an application maintains state in a custom singleton,

**When** discovery runs,

**Then** the engine shall record observed state ownership patterns.

**And** mark unresolved lifetime behavior appropriately.

## AD-S08 — Long-Running Task

**Given** an application uses `asyncio.create_task`,

**When** discovery runs,

**Then** the engine shall record the asynchronous execution pattern.

**And** shall not claim durable execution.

## AD-S09 — Dynamic Import

**Given** a module is loaded using a runtime-computed import,

**When** static discovery cannot resolve the target,

**Then** the engine shall record an unresolved dependency.

## AD-S10 — Parse Failure

**Given** one Python file contains invalid syntax,

**When** discovery runs,

**Then** the engine shall report the parse failure.

**And** continue analyzing unaffected eligible files where safe.

**And** identify incomplete coverage.

## AD-S11 — Incremental Source Change

**Given** a previously analyzed file changes,

**When** incremental discovery runs,

**Then** affected observations and evidence shall be refreshed.

**And** stale findings shall not remain current.

## AD-S12 — Deleted Source File

**Given** a source file is deleted,

**When** discovery refreshes,

**Then** its previously derived entities shall be removed or marked historical rather than represented as current.

## AD-S13 — Symbolic-Link Boundary

**Given** a repository contains a symbolic link to a file outside the approved analysis roots,

**When** discovery scans the repository,

**Then** the engine shall not traverse the external target without authorization.

## AD-S14 — Dirty Git Worktree

**Given** a repository has uncommitted changes,

**When** discovery runs,

**Then** the report shall reflect the inspected worktree snapshot.

**And** shall not claim the report describes only the committed revision.

## AD-S15 — Verification Integration

**Given** discovery identifies a direct subprocess call,

**When** architecture verification evaluates a process-management rule,

**Then** the rule shall use the discovery evidence and selected architecture profile.

## AD-S16 — Migration Integration

**Given** an existing Electron application uses custom Python communication,

**When** migration planning begins,

**Then** the planner shall consume discovered communication relationships and generate evidence-backed migration tasks.

## AD-S17 — Incomplete Analysis

**Given** relevant source files cannot be parsed,

**When** architecture verification executes,

**Then** affected checks shall not be marked PASS merely because a violation was not detected.

## AD-S18 — No Source Execution

**Given** a repository contains code with import-time side effects,

**When** default static discovery runs,

**Then** the application code shall not be executed.

---

# 41. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| AD-D01 | Default discovery mode | Read-only static analysis |
| AD-D02 | Python analysis | AST-based |
| AD-D03 | Electron analysis | TypeScript/JavaScript parser |
| AD-D04 | Configuration analysis | Language-specific data parsers |
| AD-D05 | Architecture representation | Shared intermediate model |
| AD-D06 | Model serialization | Versioned JSON |
| AD-D07 | Evidence | Source ranges and fingerprints |
| AD-D08 | Finding classification | Observed, inferred, unresolved |
| AD-D09 | Confidence | Explicit levels |
| AD-D10 | Coverage | Mandatory metadata |
| AD-D11 | Source identity | Revision plus worktree evidence |
| AD-D12 | Incremental refresh | Fingerprint and dependency invalidation |
| AD-D13 | Full refresh | Supported |
| AD-D14 | Dynamic dependencies | Explicitly unresolved where necessary |
| AD-D15 | Custom detectors | Trusted, versioned extensions |
| AD-D16 | Runtime observation | Optional and explicitly authorized |
| AD-D17 | LLM dependency | None |
| AD-D18 | Reporting | Markdown and JSON |
| AD-D19 | Verification ownership | Separate module |
| AD-D20 | Migration ownership | Separate module |
| AD-D21 | Source execution | Prohibited in default mode |
| AD-D22 | Repository traversal | Approved roots only |
| AD-D23 | Cache correctness | Full/incremental equivalence |
| AD-D24 | Failure handling | Partial results with coverage |
| AD-D25 | Performance | Bounded and configurable |

These decisions remain proposals until architecture review.

---

# 42. Outstanding Questions

## AD-OQ-001 — Python Parsing Technology

Should discovery use the standard Python AST alone or add LibCST for richer source metadata?

**Recommendation:** Use AST for initial structural analysis and evaluate LibCST for detectors requiring more precise syntax preservation.

## AD-OQ-002 — TypeScript Parser

Should Electron discovery use a Node-based TypeScript compiler service or a parser usable directly from Python?

**Recommendation:** Evaluate parsing fidelity, distribution complexity, and dependency isolation before choosing. TypeScript syntax support is more important than keeping every analyzer inside one language runtime.

## AD-OQ-003 — Dependency Graph Library

Should the framework use a dedicated dependency graph library?

**Recommendation:** Start with a lightweight internal graph representation unless supported workloads demonstrate a need for a richer library.

## AD-OQ-004 — Model Identity

Should entity identifiers persist across file moves and renames?

**Recommendation:** Use deterministic snapshot-local identities initially. Introduce cross-revision identity matching only when a reliable algorithm exists.

## AD-OQ-005 — Confidence Representation

Should findings use qualitative confidence levels or numeric scores?

**Recommendation:** Use explicit qualitative categories first, with documented evidence requirements.

## AD-OQ-006 — Discovery Cache Location

Should caches be stored inside the inspected repository?

**Recommendation:** Prefer a framework-managed cache outside the repository by default, avoiding unintended changes to application worktrees.

## AD-OQ-007 — Incremental Scope

Should incremental refresh be supported in the first release?

**Recommendation:** Include basic content-hash caching and invalidation early, but ensure a full rescan remains the correctness reference.

## AD-OQ-008 — Monorepo Support

Should multiple applications in one repository be represented in a single architecture model?

**Recommendation:** Support a workspace-level model containing independently identified applications and shared packages.

## AD-OQ-009 — Runtime Observation

Should optional runtime instrumentation be implemented initially?

**Recommendation:** Defer until the static model and safety contracts are validated.

## AD-OQ-010 — LLM Assistance

Should AI-assisted architectural classification be supported?

**Recommendation:** Keep it optional and advisory; do not let it replace deterministic evidence.

## AD-OQ-011 — Source Evidence Storage

Should the architecture model embed full source snippets?

**Recommendation:** Prefer file references, line ranges, and fingerprints. Include only bounded, appropriately sanitized excerpts when useful.

## AD-OQ-012 — Framework-Specific Detectors

Should AdharaSutra detection rules be embedded in discovery?

**Recommendation:** Discovery may recognize AdharaSutra API patterns, but architecture compliance decisions must remain in verification.

## AD-OQ-013 — Test Discovery

Should the engine recognize existing behavioral and integration tests?

**Recommendation:** Yes, as an inventory and relationship source. Do not claim test passing status without actual execution results.

## AD-OQ-014 — Unsupported Languages

How should repositories containing C++, Rust, or other languages be handled?

**Recommendation:** Inventory those files and report analysis coverage. Add specialized detectors only as justified.

## AD-OQ-015 — Privacy and Sensitive Source

Should discovery reports automatically include raw source excerpts?

**Recommendation:** No. Default to references and redacted summaries to reduce accidental source disclosure.

---

# 43. Functional Requirement Traceability

| Requirement group | Discovery responsibility |
|---|---|
| FR-DISC | Repository analysis and architecture model |
| FR-ARCH | Evidence supplied to verification |
| FR-MIG | Current architecture supplied to migration |
| FR-REP | Current implementation reports |
| FR-RUN | Runtime entry-point identification |
| FR-CLI | CLI implementation discovery |
| FR-ELC | Electron communication discovery |
| FR-CON | Connector pattern inventory |
| FR-HTTP | HTTP usage detection |
| FR-EXT | External process usage detection |
| FR-DB | Persistence and SQLite discovery |
| FR-WS | WebSocket usage detection |
| FR-FS | Filesystem usage and storage pattern discovery |
| FR-STATE | State management discovery |
| FR-JOB | Job and worker discovery |
| FR-CFG | Configuration source analysis |
| FR-DI | Service composition discovery |
| FR-TEST | Test structure inventory |
| FR-DEV | Developer inspection CLI |
| FR-SEC | Source analysis safety |

---

# 44. Non-Functional Requirement Traceability

| Quality attribute | Architectural mechanism |
|---|---|
| Reliability | Explicit coverage and uncertainty |
| Security | Read-only, no-execution defaults |
| Performance | Incremental analysis and bounded resources |
| Scalability | Multi-package discovery and parallel parsing |
| Maintainability | Modular language parsers and detectors |
| Extensibility | Custom detector contracts |
| Testability | Deterministic fixtures and equivalence tests |
| Compatibility | Versioned architecture model |
| Portability | Cross-platform filesystem handling |
| Observability | Analysis diagnostics and evidence |
| Reproducibility | Source snapshots and fingerprints |
| Migration safety | Evidence-backed current-state representation |
| Architecture conformance | Shared facts for deterministic verification |

---

# 45. Acceptance Criteria

The Architecture Discovery design may be approved when:

- [ ] Discovery is read-only by default.
- [ ] The engine can analyze applications without AdharaSutra.
- [ ] Repository and workspace identification is defined.
- [ ] Source inventory and exclusion policies are defined.
- [ ] Python structural analysis is specified.
- [ ] Electron TypeScript/JavaScript analysis is specified.
- [ ] Configuration-file analysis is specified.
- [ ] Module and dependency relationships are represented.
- [ ] Entry-point discovery is defined.
- [ ] CLI routing discovery is defined.
- [ ] Electron communication discovery is defined.
- [ ] Connector discovery is defined.
- [ ] State and job discovery are defined.
- [ ] Configuration and lifecycle discovery are defined.
- [ ] A shared intermediate architecture model is specified.
- [ ] Architecture entity identity rules are defined.
- [ ] Findings include source evidence.
- [ ] Observations and inferences are distinguished.
- [ ] Unresolved and unsupported patterns are reported.
- [ ] Analysis coverage is mandatory.
- [ ] Git and non-Git source snapshots are supported.
- [ ] Incremental refresh invalidates stale evidence.
- [ ] Full and incremental discovery can be compared for equivalence.
- [ ] Symlinks and filesystem boundaries are handled safely.
- [ ] Custom detectors have defined contracts and trust requirements.
- [ ] Optional runtime analysis is separated from static analysis.
- [ ] LLM assistance is optional.
- [ ] JSON and Markdown reporting are defined.
- [ ] Discovery does not produce unsupported compliance verdicts.
- [ ] Verification and migration consume the same architecture model.
- [ ] Security and resource limits are documented.
- [ ] Automated tests and failure-injection scenarios are identified.
- [ ] Critical decisions are approved or explicitly deferred.

---

# 46. Final Architecture Summary

AdharaSutra's Architecture Discovery subsystem provides an evidence-based representation of how an application is currently implemented.

It analyzes repository structure, Python source, Electron integrations, CLI interfaces, dependency relationships, connectors, persistence, state management, jobs, and lifecycle patterns.

Its output is a **versioned ApplicationArchitecture model** containing architectural entities, relationships, evidence, uncertainty, coverage, and analysis diagnostics.

The subsystem shall be:

- Read-only by default.
- Independent of AdharaSutra application adoption.
- Deterministic without an LLM.
- Safe against unintended source execution.
- Incrementally refreshable.
- Evidence-backed and source-traceable.
- Transparent about incomplete analysis.
- Usable by verification, migration, and reporting.

Discovery describes the implementation that exists.

Verification determines whether that implementation satisfies a selected architecture profile.

Migration determines how to move from the current implementation toward the desired architecture.

The central guarantee is:

**Every architectural finding must be traceable to evidence, and every unsupported conclusion must remain explicitly unresolved.**

---

# 47. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architecture discovery review

**Next Document:** `docs/design/architecture-verification.md`

The next document will define the deterministic architecture rule engine, versioned architecture profiles, conformance evaluation, evidence requirements, violation severity, exceptions, baselines, CI integration, and actionable verification reports.

---

**AdharaSutra — Build once. Standardize everywhere.**
