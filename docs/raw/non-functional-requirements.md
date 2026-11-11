# AdharaSutra — Non-Functional Requirements

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/non-functional-requirements.md`  
**Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Non-Functional Requirements Specification

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`

---

# 1. Purpose

This document defines the non-functional requirements (NFRs) for AdharaSutra, a CLI-first Python application framework.

While functional requirements describe what the framework must do, non-functional requirements define the quality, performance, reliability, security, maintainability, compatibility, and operational characteristics of those capabilities.

AdharaSutra is intended to serve as the foundational runtime for multiple Python applications, including applications using Electron frontends and integrations with external HTTP services, CLI executables, and SQLite.

Consequently, the framework must remain predictable, efficient, reliable, portable, secure, extensible, testable, and independently maintainable.

## 1.1 Objectives

The non-functional requirements aim to ensure that:

1. The framework introduces minimal unnecessary overhead.
2. Applications can execute CLI actions reliably and predictably.
3. Long-running workloads remain observable and cancellable.
4. External dependencies are isolated and managed consistently.
5. Application state and persistent data remain protected.
6. Runtime failures do not unnecessarily destabilize applications.
7. Applications remain portable across supported operating systems.
8. Framework upgrades do not silently break consuming applications.
9. Architecture verification produces reproducible results.
10. Migration preserves existing application behavior and data.
11. Developers and coding agents can understand and maintain the framework.
12. Optional infrastructure components do not burden applications that do not use them.

## 1.2 Scope

These requirements apply to:

- AdharaSutra's Python runtime.
- CLI protocol and action routing.
- Electron bridge.
- External connector infrastructure.
- State and job management.
- Configuration and lifecycle management.
- Logging and diagnostics.
- Project scaffolding.
- Architecture discovery and verification.
- Migration tooling.
- Packaging and distribution.
- Public framework interfaces.

## 1.3 Measurement Principles

All measurable targets must specify:

- Measurement scope.
- Test environment.
- Workload or input size.
- Measurement method.
- Acceptance threshold.
- Relevant exclusions.

Measurements must distinguish framework overhead from application business logic and external service execution time.

For example, slow image generation in ComfyUI should not automatically be attributed to AdharaSutra.

---

# 2. Requirement Classification

## 2.1 Requirement Identifiers

Every non-functional requirement shall have a stable identifier.

Format:

`NFR-<CATEGORY>-<NUMBER>`

Examples:

- `NFR-PERF-001`
- `NFR-REL-001`
- `NFR-SEC-001`

## 2.2 Priorities

| Priority | Meaning |
|---|---|
| P0 — Critical | Required for framework safety or fundamental correctness |
| P1 — High | Required for production readiness |
| P2 — Medium | Important quality improvement |
| P3 — Optional | Future optimization |

## 2.3 Requirement Status

Requirements may be classified as:

- Proposed
- Under Review
- Approved
- Deferred
- Rejected
- Implemented
- Verified

All requirements in this document are initially **Proposed**.

## 2.4 Verification Methods

Verification methods include:

- Automated benchmarks.
- Unit tests.
- Integration tests.
- Contract tests.
- Load and stress tests.
- Fault-injection tests.
- Static analysis.
- Architecture conformance tests.
- Security tests.
- Compatibility tests.
- Migration regression tests.
- Technical review.

---

# 3. Performance Requirements

**Requirement group:** `NFR-PERF`

AdharaSutra must minimize infrastructure overhead while supporting applications with potentially expensive external workloads.

Performance measurements must isolate the framework from external AI inference, file processing, and third-party execution time.

## NFR-PERF-001 — CLI Dispatch Latency

**Priority:** P1

The framework shall minimize the overhead of validating and dispatching an action.

**Proposed target:**

For an already initialized persistent CLI process:

- p50 framework dispatch overhead: ≤ 5 ms.
- p95 framework dispatch overhead: ≤ 20 ms.
- p99 framework dispatch overhead: ≤ 50 ms.

These measurements exclude business-handler execution and external dependencies.

**Verification:**

Benchmark no-op actions in a warmed process using at least 10,000 requests.

The final target shall be confirmed on a documented reference machine.

## NFR-PERF-002 — CLI Process Startup

**Priority:** P1

The framework shall avoid unnecessary startup overhead.

**Proposed target:**

For a minimal application using no optional integrations:

- p95 time from Python process entry to framework readiness: ≤ 500 ms on the reference machine.

This excludes operating-system process creation and Python interpreter startup unless a separate end-to-end benchmark explicitly includes them.

**Verification:**

Measure startup over at least 100 clean process executions.

## NFR-PERF-003 — Protocol Serialization

**Priority:** P1

JSON request and response serialization shall not introduce disproportionate latency.

**Proposed target:**

- p95 combined validation, serialization, and deserialization overhead: ≤ 10 ms for a 16 KB request/response payload on the reference machine.

**Verification:**

Execute isolated serialization benchmarks with representative schemas.

## NFR-PERF-004 — Persistent CLI Throughput

**Priority:** P1

Persistent CLI execution shall efficiently process repeated requests.

**Proposed target:**

- At least 1,000 lightweight no-op requests per second under a controlled single-client benchmark, excluding business execution.

**Verification:**

Use a warmed persistent CLI process and record throughput, latency, CPU usage, and memory usage.

## NFR-PERF-005 — Progress Event Latency

**Priority:** P1

The framework shall deliver progress events with minimal additional delay.

**Proposed target:**

- p95 event delivery overhead ≤ 50 ms for an uncongested local CLI connection.

**Verification:**

Measure the interval between event publication and Electron bridge receipt.

This measurement excludes delays introduced by external dependencies.

## NFR-PERF-006 — Connector Overhead

**Priority:** P1

Generic connector infrastructure shall avoid significant overhead relative to its underlying transport.

**Proposed target:**

- HTTP connector overhead should remain within 10% of equivalent direct HTTPX execution under controlled local benchmarking.

**Verification:**

Compare identical request workloads using direct HTTPX and the framework connector.

## NFR-PERF-007 — Large Artifact Handling

**Priority:** P0

The framework shall avoid unnecessary duplication of large binary artifacts in memory.

**Acceptance criteria:**

- Large files can be represented through managed file references.
- Binary artifacts are not required to be base64-encoded in CLI protocol messages.
- Streaming operations do not require loading an entire artifact into memory unless explicitly requested.

## NFR-PERF-008 — Optional Component Initialization

**Priority:** P1

Unused optional connectors and integrations shall not be initialized during ordinary startup.

**Verification:**

A minimal application startup test shall confirm that unused connector implementations are not activated.

---

# 4. Resource Efficiency Requirements

**Requirement group:** `NFR-RES`

## NFR-RES-001 — Runtime Memory Overhead

**Priority:** P1

The framework shall minimize memory consumption in applications that use only core capabilities.

**Proposed target:**

- Incremental steady-state memory overhead attributable to the framework: ≤ 40 MiB for a minimal persistent application on the reference environment.

Measurement must compare a documented baseline process against an equivalent application using AdharaSutra.

## NFR-RES-002 — Bounded Queues

**Priority:** P0

Internal event and job queues shall support configurable capacity limits.

**Acceptance criteria:**

- Queues cannot grow without bound under sustained overload.
- Overflow behavior is explicit.
- Critical lifecycle events are not silently discarded.
- Queue metrics or diagnostics expose overload conditions.

## NFR-RES-003 — Resource Cleanup

**Priority:** P0

The framework shall release managed resources when operations complete, fail, time out, or are cancelled.

Resources include:

- Child processes.
- HTTP connections.
- WebSocket connections.
- Database connections.
- Temporary files.
- File handles.
- Event subscriptions.
- Job execution contexts.

## NFR-RES-004 — Long-Running Stability

**Priority:** P1

The persistent CLI runtime shall remain operational during extended execution without uncontrolled resource growth.

**Proposed validation:**

- Execute an eight-hour endurance test.
- Perform repeated actions and connector lifecycle operations.
- Verify that no sustained unbounded memory, handle, or process growth occurs.

## NFR-RES-005 — Configurable Concurrency Limits

**Priority:** P0

The framework shall support explicit limits for concurrent jobs, external processes, and other resource-intensive operations.

Applications shall be able to choose limits appropriate to their workloads.

---

# 5. Reliability Requirements

**Requirement group:** `NFR-REL`

## NFR-REL-001 — Predictable Execution

**Priority:** P0

Given valid configuration and deterministic application handlers, the framework shall provide consistent routing, validation, serialization, and error classification.

## NFR-REL-002 — Failure Isolation

**Priority:** P0

Failures in an individual action or connector shall not unnecessarily terminate the entire persistent application.

**Acceptance criteria:**

- Expected handler exceptions are contained.
- Structured errors are returned where possible.
- Unrelated requests can continue when runtime integrity remains intact.
- Fatal infrastructure failures trigger controlled shutdown when necessary.

## NFR-REL-003 — Partial Initialization Recovery

**Priority:** P0

When startup fails, already initialized resources shall be cleaned up.

The application shall not report readiness after critical initialization failure.

## NFR-REL-004 — External Dependency Failure Handling

**Priority:** P0

Temporary or permanent external dependency failures shall be detected and represented through defined error categories.

The framework shall not assume an external service is operational merely because its configuration exists.

## NFR-REL-005 — Process Failure Detection

**Priority:** P0

The Electron bridge shall detect unexpected Python process termination.

Pending requests shall receive explicit failure outcomes.

## NFR-REL-006 — Cancellation Consistency

**Priority:** P0

Cancellation shall distinguish:

- Cancellation requested.
- Cancellation acknowledged.
- Cancellation completed.
- Cancellation unsupported.
- Cancellation failed.

The framework must not report successful cancellation before the required termination or cooperative cancellation behavior has been confirmed.

## NFR-REL-007 — Idempotent Cleanup

**Priority:** P0

Repeated cleanup and shutdown requests shall not corrupt resource state.

## NFR-REL-008 — Error Traceability

**Priority:** P0

Failures shall be traceable using request identifiers, job identifiers, and appropriate diagnostic context.

## NFR-REL-009 — Communication Failure Recovery

**Priority:** P1

The persistent CLI protocol shall define behavior for broken pipes, malformed messages, interrupted sessions, and unexpected process exits.

## NFR-REL-010 — External Operation Uncertainty

**Priority:** P0

The framework shall distinguish between:

- Confirmed success.
- Confirmed failure.
- Unknown execution outcome.

For example, a connection failure after submitting a non-idempotent HTTP operation must not automatically be treated as proof that the operation failed.

---

# 6. Availability and Recoverability Requirements

**Requirement group:** `NFR-AVAIL`

## NFR-AVAIL-001 — Startup Readiness

**Priority:** P0

The framework shall expose a readiness state only after required initialization succeeds.

## NFR-AVAIL-002 — Optional Dependency Degradation

**Priority:** P1

Where permitted by application configuration, failure of an optional dependency shall not prevent unrelated application functions from operating.

## NFR-AVAIL-003 — Job Recovery Semantics

**Priority:** P1

Persistent jobs shall have explicit recovery behavior after interruption.

Possible outcomes include:

- Resume.
- Retry.
- Mark as interrupted.
- Require manual intervention.

The framework must not claim durable execution without a persistent execution owner.

## NFR-AVAIL-004 — Persistent Data Recovery

**Priority:** P0

Persistent-state facilities shall preserve database integrity across supported failures.

**Acceptance criteria:**

- Transaction boundaries are respected.
- Incomplete transactions do not appear as committed results.
- Database recovery procedures are documented and tested.

## NFR-AVAIL-005 — Crash Recovery

**Priority:** P1

The framework shall support recovering from unexpected application termination without assuming that in-memory state survived.

## NFR-AVAIL-006 — Recovery Diagnostics

**Priority:** P1

When recovery fails, diagnostic reports shall identify affected resources and available recovery actions.

---

# 7. Scalability and Concurrency Requirements

**Requirement group:** `NFR-SCALE`

AdharaSutra primarily targets local applications, not distributed cloud-scale infrastructure.

Scalability requirements therefore focus on efficient local concurrency and extensibility.

## NFR-SCALE-001 — Concurrent Request Handling

**Priority:** P1

Persistent CLI execution shall support multiple active asynchronous requests where configured.

## NFR-SCALE-002 — Concurrency Safety

**Priority:** P0

Shared framework state shall follow documented concurrency rules.

Race conditions must not result in silent corruption of framework-managed metadata.

## NFR-SCALE-003 — Backpressure

**Priority:** P0

The runtime shall support backpressure or bounded buffering when event production exceeds consumer capacity.

## NFR-SCALE-004 — Job Scheduling Limits

**Priority:** P1

Applications shall be able to configure job concurrency according to CPU, memory, GPU, or other resource constraints.

The framework is not required to directly manage GPU allocation in its initial release.

## NFR-SCALE-005 — Connector Independence

**Priority:** P1

Adding additional connector instances shall not require modifications to unrelated connector implementations.

## NFR-SCALE-006 — Application Isolation

**Priority:** P0

Independent applications shall not unintentionally share runtime state, configuration, jobs, or persistent data.

## NFR-SCALE-007 — Large Project Analysis

**Priority:** P1

Architecture discovery and verification shall be designed to handle substantial Python repositories.

**Proposed benchmark target:**

- A repository containing approximately 100,000 lines of supported Python source should complete baseline static architecture verification within 60 seconds on a defined reference machine.

This excludes package installation, full runtime tests, network operations, and optional LLM analysis.

---

# 8. Security Requirements

**Requirement group:** `NFR-SEC`

## NFR-SEC-001 — Secure Process Execution

**Priority:** P0

External CLI execution shall avoid unsafe command construction.

**Acceptance criteria:**

- Executables and arguments are represented separately.
- Shell execution is disabled by default.
- Any shell-enabled execution path requires explicit opt-in and documented risk controls.

## NFR-SEC-002 — Action Authorization Boundary

**Priority:** P0

The runtime shall execute only registered actions that are permitted in the current application context.

## NFR-SEC-003 — Input Validation

**Priority:** P0

Untrusted requests shall be validated before invoking application handlers or infrastructure facilities.

## NFR-SEC-004 — Filesystem Safety

**Priority:** P0

Framework-managed filesystem operations shall support protections against unsafe paths and traversal outside configured boundaries.

Where symbolic links are supported, relevant operations shall account for resolved targets.

## NFR-SEC-005 — Secret Protection

**Priority:** P0

Secrets shall not be included in ordinary logs, error envelopes, or generated diagnostic reports.

## NFR-SEC-006 — Secure Configuration

**Priority:** P0

The framework shall support configuration from protected sources and shall not require embedding secrets in application source code.

## NFR-SEC-007 — Electron Process Isolation

**Priority:** P0

The Electron bridge shall keep operating-system process management outside the renderer process.

## NFR-SEC-008 — Controlled IPC Exposure

**Priority:** P0

Electron preload interfaces shall expose only approved operations.

Renderer input shall not directly control unrestricted executable paths or shell commands.

## NFR-SEC-009 — External Network Safety

**Priority:** P1

HTTP and WebSocket connectors shall support secure transport configuration and appropriate certificate verification.

Insecure transport options must be explicit.

## NFR-SEC-010 — Dependency Security

**Priority:** P1

The framework's release process shall support dependency vulnerability analysis and reproducible dependency resolution.

## NFR-SEC-011 — Safe Diagnostics

**Priority:** P0

Architecture and migration reports shall avoid exposing sensitive runtime information, credentials, or private data not required for analysis.

## NFR-SEC-012 — Unsafe Automated Modification Prevention

**Priority:** P0

Migration and scaffold operations shall not silently overwrite or delete unrelated source files.

---

# 9. Portability Requirements

**Requirement group:** `NFR-PORT`

## NFR-PORT-001 — Supported Operating Systems

**Priority:** P1

The framework shall target:

- Windows.
- Linux.
- macOS.

Support levels and tested versions shall be documented.

## NFR-PORT-002 — Cross-Platform Process Management

**Priority:** P0

Process execution, termination, and cleanup shall account for platform-specific behavior.

The framework must not assume Unix process signals exist on Windows.

## NFR-PORT-003 — Cross-Platform Filesystem Behavior

**Priority:** P0

Path handling shall account for platform-specific separators, permissions, symbolic links, and application data directories.

## NFR-PORT-004 — Python Version Compatibility

**Priority:** P1

The framework shall define a supported Python version range.

**Initial proposed baseline:** Python 3.12 and later explicitly tested releases.

Compatibility shall be established by CI testing rather than inferred solely from version numbering.

## NFR-PORT-005 — Electron Compatibility

**Priority:** P1

The TypeScript Electron bridge shall maintain a documented compatibility matrix for supported Electron and Node.js versions.

## NFR-PORT-006 — External Dependency Portability

**Priority:** P1

The framework shall not assume every external CLI or service is available on every supported operating system.

Applications must be able to declare platform-specific requirements.

## NFR-PORT-007 — Packaged Runtime Portability

**Priority:** P1

The framework shall support deployment arrangements where Python is bundled or otherwise supplied as an application dependency.

A separately installed Python development environment shall not be an undocumented requirement.

---

# 10. Maintainability Requirements

**Requirement group:** `NFR-MAINT`

## NFR-MAINT-001 — Separation of Responsibilities

**Priority:** P0

Framework infrastructure and consuming application business logic shall remain separate.

## NFR-MAINT-002 — Modular Architecture

**Priority:** P0

Framework modules shall have documented responsibilities and dependency boundaries.

## NFR-MAINT-003 — Dependency Direction

**Priority:** P0

Core framework modules shall not depend on optional application-specific integrations.

## NFR-MAINT-004 — Independent Component Testing

**Priority:** P1

Core components shall be testable without requiring an Electron application or live external AI services.

## NFR-MAINT-005 — Explicit Public Interfaces

**Priority:** P1

Public framework APIs shall be distinguishable from internal implementation details.

## NFR-MAINT-006 — Controlled Complexity

**Priority:** P1

New abstractions shall be justified by concrete reuse, isolation, or maintainability requirements.

The framework should avoid introducing a custom ORM, message broker, or dependency-injection container without demonstrated need.

## NFR-MAINT-007 — Consistent Code Standards

**Priority:** P1

The project shall define coding, formatting, typing, testing, and documentation conventions.

## NFR-MAINT-008 — Dependency Minimization

**Priority:** P1

Optional framework capabilities shall not require installing unrelated heavy dependencies.

## NFR-MAINT-009 — Architecture Conformance

**Priority:** P1

Defined module-boundary rules shall be machine-verifiable where feasible.

## NFR-MAINT-010 — Sustainable Release Maintenance

**Priority:** P1

Framework changes shall include appropriate tests, compatibility notes, and documentation updates.

---

# 11. Extensibility Requirements

**Requirement group:** `NFR-EXT`

## NFR-EXT-001 — Connector Extensibility

**Priority:** P1

New connector implementations shall be introducible without modifying core runtime behavior.

## NFR-EXT-002 — Application Extension Points

**Priority:** P0

Applications shall register their business capabilities through stable, documented extension mechanisms.

## NFR-EXT-003 — Optional Plugin Isolation

**Priority:** P1

An unavailable optional plugin shall not prevent unrelated functionality from operating unless declared mandatory by the application.

## NFR-EXT-004 — Architecture Profile Extensibility

**Priority:** P1

Additional architecture profiles shall be definable without rewriting the architecture verifier.

## NFR-EXT-005 — Verification Rule Extensibility

**Priority:** P1

New architecture rules shall be registerable through documented extension interfaces.

## NFR-EXT-006 — Migration Analyzer Extensibility

**Priority:** P1

Migration tooling shall support additional analyzers for new project layouts, CLI libraries, and infrastructure patterns.

## NFR-EXT-007 — Backward-Compatible Extension

**Priority:** P1

Adding new optional extension capabilities should not require changes to existing application business handlers.

---

# 12. Testability Requirements

**Requirement group:** `NFR-TEST`

## NFR-TEST-001 — Deterministic Core Testing

**Priority:** P0

Core framework behavior shall be testable without reliance on external network services.

## NFR-TEST-002 — Mockable Infrastructure

**Priority:** P1

Connectors and application services shall support substitution with test implementations.

## NFR-TEST-003 — Protocol Contract Coverage

**Priority:** P0

All defined protocol message categories shall have executable positive and negative tests.

## NFR-TEST-004 — Lifecycle Test Coverage

**Priority:** P0

Application, connector, process, and job lifecycle transitions shall be covered by automated tests.

## NFR-TEST-005 — Failure Injection

**Priority:** P1

Tests shall be able to simulate:

- External service unavailability.
- Child-process crashes.
- Timeouts.
- Malformed protocol messages.
- Database failures.
- Interrupted jobs.
- Configuration errors.

## NFR-TEST-006 — Code Coverage Targets

**Priority:** P1

**Proposed target:**

- At least 85% line coverage for core framework modules.
- At least 90% branch coverage for protocol validation and error classification modules.

Coverage is supporting evidence and does not replace behavioral testing.

## NFR-TEST-007 — Reproducible Test Environment

**Priority:** P1

Tests shall specify required dependencies, configuration, and external fixtures.

## NFR-TEST-008 — Packaging Tests

**Priority:** P1

Production packaging shall be validated through executable smoke tests on supported platforms.

## NFR-TEST-009 — Migration Regression Evidence

**Priority:** P0

Migration completion shall not be inferred from architecture conformance alone.

Relevant existing application behavior must be independently verified.

---

# 13. Compatibility and Versioning Requirements

**Requirement group:** `NFR-COMP`

## NFR-COMP-001 — Semantic Versioning Policy

**Priority:** P1

Public framework releases shall follow a documented versioning policy.

Semantic Versioning is the proposed approach.

## NFR-COMP-002 — Protocol Versioning

**Priority:** P0

The CLI communication protocol shall have an explicit version independent of the application version.

## NFR-COMP-003 — Schema Versioning

**Priority:** P0

Machine-readable architecture, migration, and implementation report formats shall include schema versions.

## NFR-COMP-004 — Public API Compatibility

**Priority:** P1

Breaking changes to public framework interfaces shall be identified and documented.

## NFR-COMP-005 — Electron Bridge Compatibility

**Priority:** P0

The Electron bridge and Python runtime shall reject unsupported protocol combinations rather than silently misinterpreting messages.

## NFR-COMP-006 — Deprecation Policy

**Priority:** P1

Deprecated public functionality shall have documented replacements and removal conditions.

## NFR-COMP-007 — Migration Compatibility

**Priority:** P1

Migration tooling shall identify compatibility risks associated with framework upgrades and architecture profile changes.

## NFR-COMP-008 — Historical Report Compatibility

**Priority:** P2

The framework should support reading or converting supported older report schemas where practical.

---

# 14. Architecture Verification Quality Requirements

**Requirement group:** `NFR-ARCH`

## NFR-ARCH-001 — Deterministic Verification

**Priority:** P0

Given identical source content, configuration, analyzer versions, and declared environment, deterministic rules shall produce identical results.

## NFR-ARCH-002 — Evidence-Based Findings

**Priority:** P0

Each confirmed violation shall include sufficient evidence to identify the violated rule and relevant implementation location.

## NFR-ARCH-003 — Explicit Verification Coverage

**Priority:** P0

Verification reports shall distinguish executed checks from unsupported or unexecuted checks.

## NFR-ARCH-004 — False Positive Management

**Priority:** P1

The verifier shall support documented exceptions and mechanisms to investigate suspected false positives.

## NFR-ARCH-005 — Stable Rule Identification

**Priority:** P1

Architecture rule identifiers shall remain stable across compatible rule catalog versions.

## NFR-ARCH-006 — Incremental Verification

**Priority:** P2

Where feasible, architecture checks should avoid reprocessing unchanged sources unnecessarily.

## NFR-ARCH-007 — CI Reliability

**Priority:** P1

Noninteractive architecture verification shall produce stable exit statuses and machine-readable reports.

## NFR-ARCH-008 — LLM Independence

**Priority:** P0

Mandatory deterministic architecture checks shall remain executable without an LLM provider or network access.

## NFR-ARCH-009 — Result Transparency

**Priority:** P0

Reports shall not label partially analyzed applications as fully compliant.

## NFR-ARCH-010 — Baseline Integrity

**Priority:** P1

Baseline handling shall not allow new violations to be silently accepted as previously known findings.

---

# 15. Migration Safety Requirements

**Requirement group:** `NFR-MIG`

## NFR-MIG-001 — Business Behavior Preservation

**Priority:** P0

Migration shall prioritize preservation of existing business behavior.

## NFR-MIG-002 — Non-Destructive Analysis

**Priority:** P0

Architecture inspection and migration planning shall not modify application source files or persistent data.

## NFR-MIG-003 — Reviewable Transformations

**Priority:** P0

Automated migration changes shall produce inspectable diffs.

## NFR-MIG-004 — Data Integrity

**Priority:** P0

Migration operations affecting persistent data shall use appropriate integrity, backup, and recovery controls.

## NFR-MIG-005 — Incremental Migration

**Priority:** P1

Migration shall support independently verifiable implementation units.

## NFR-MIG-006 — Rollback Readiness

**Priority:** P1

Migration steps shall document whether they are reversible and identify relevant recovery procedures.

## NFR-MIG-007 — Source Revision Awareness

**Priority:** P0

Migration tools shall detect when the source analyzed for a proposed change no longer matches the current working tree.

## NFR-MIG-008 — Agent Report Accuracy

**Priority:** P0

Generated reports shall distinguish:

- Observed facts.
- Confirmed violations.
- Inferences.
- Recommendations.
- Unverified assumptions.

## NFR-MIG-009 — Migration Completion Evidence

**Priority:** P0

Migration shall not be marked complete solely on the basis of generated code or an LLM assessment.

Required deterministic checks and behavioral tests must pass.

## NFR-MIG-010 — Business Logic Modification Control

**Priority:** P0

Automated migration shall not silently rewrite domain algorithms or business rules.

---

# 16. Documentation Quality Requirements

**Requirement group:** `NFR-DOC`

## NFR-DOC-001 — Documentation Completeness

**Priority:** P1

Public framework capabilities shall have sufficient documentation for supported usage.

## NFR-DOC-002 — Documentation Consistency

**Priority:** P1

Documentation shall be consistent with approved architecture, protocol contracts, and public APIs.

## NFR-DOC-003 — Documentation Traceability

**Priority:** P1

Important architecture rules and public protocol contracts shall be traceable to relevant documentation and verification evidence.

## NFR-DOC-004 — Machine-Readable Reports

**Priority:** P1

Architecture and migration reports shall use versioned machine-readable formats.

## NFR-DOC-005 — Source References

**Priority:** P1

Implementation reports shall include source locations and revision information where supported.

## NFR-DOC-006 — Documentation Freshness

**Priority:** P1

Generated reports shall identify their source revision so stale analysis can be detected.

## NFR-DOC-007 — Documentation Validation

**Priority:** P2

Documentation tooling should verify internal links, required metadata, schema references, and supported executable examples.

## NFR-DOC-008 — Documentation Ownership

**Priority:** P1

Authoritative documentation locations and maintenance responsibilities shall be clearly defined.

---

# 17. Developer Experience Requirements

**Requirement group:** `NFR-DX`

## NFR-DX-001 — Predictable Project Structure

**Priority:** P1

Applications generated using the same architecture profile shall follow consistent conventions.

## NFR-DX-002 — Actionable Error Messages

**Priority:** P1

Developer-facing errors shall identify the failure and provide remediation guidance where appropriate.

## NFR-DX-003 — Consistent Command Interface

**Priority:** P1

Framework developer commands shall use consistent naming, argument patterns, and exit semantics.

## NFR-DX-004 — Minimal New-Project Setup

**Priority:** P1

A generated minimal application shall be runnable after completing its documented dependency installation and setup steps.

## NFR-DX-005 — Discoverable Capabilities

**Priority:** P1

Developers shall be able to identify available actions, connectors, architecture profiles, and framework commands.

## NFR-DX-006 — Cross-Agent Accessibility

**Priority:** P1

Architecture and migration reports shall be usable without requiring a particular coding-agent vendor.

## NFR-DX-007 — Offline Core Development

**Priority:** P1

Core framework development and deterministic verification shall not require continuous external network access once dependencies are installed.

## NFR-DX-008 — Clear Framework Boundaries

**Priority:** P0

Developers shall be able to distinguish framework-owned infrastructure from consuming application business logic through documented interfaces and architecture rules.

---

# 18. Operational and Packaging Requirements

**Requirement group:** `NFR-OPS`

## NFR-OPS-001 — Reproducible Builds

**Priority:** P1

Framework releases shall use documented, reproducible dependency and build configurations.

## NFR-OPS-002 — Production Packaging Validation

**Priority:** P1

The framework shall support validation of packaged applications, not only development environments.

## NFR-OPS-003 — Diagnostic Availability

**Priority:** P1

Production application failures shall produce sufficient diagnostic evidence for troubleshooting without exposing secrets.

## NFR-OPS-004 — Safe Upgrade Behavior

**Priority:** P1

Application upgrades shall account for protocol, schema, configuration, and persistent-state compatibility.

## NFR-OPS-005 — Platform-Specific Dependency Handling

**Priority:** P1

External executable paths and platform-specific dependencies shall be configurable and diagnosable.

## NFR-OPS-006 — Controlled Resource Termination

**Priority:** P0

Application shutdown shall attempt controlled termination and resource cleanup within configurable limits.

## NFR-OPS-007 — Release Artifact Integrity

**Priority:** P1

Release processes shall support verifying artifact integrity and identifying source revisions.

## NFR-OPS-008 — Production Configuration Separation

**Priority:** P1

Development, test, and production configuration shall be distinguishable through documented mechanisms.

---

# 19. Observability Requirements

**Requirement group:** `NFR-OBS`

## NFR-OBS-001 — Structured Diagnostics

**Priority:** P1

The framework shall support structured diagnostic logging.

## NFR-OBS-002 — Request and Job Correlation

**Priority:** P0

Operations shall be traceable using request and job identifiers.

## NFR-OBS-003 — Connector Diagnostics

**Priority:** P1

Connector failures shall expose useful diagnostic metadata, including connector identity and failure category.

## NFR-OBS-004 — Runtime Health

**Priority:** P1

The framework shall expose application readiness and relevant subsystem health information.

## NFR-OBS-005 — Diagnostic Isolation

**Priority:** P0

Diagnostics shall not interfere with structured CLI protocol communication.

## NFR-OBS-006 — Optional Advanced Telemetry

**Priority:** P3

Advanced tracing and metrics integration may be supported through optional extensions.

---

# 20. Reference Benchmark Environment

Performance targets require a defined reference environment before approval.

The following is a proposed baseline, not a representation of benchmark results.

| Parameter | Proposed baseline |
|---|---|
| Operating system | Windows 11 and Ubuntu LTS |
| Python | Supported Python 3.12 environment |
| CPU | Modern 8-core desktop CPU |
| Memory | 16 GB RAM or more |
| Storage | SSD |
| Electron | Supported stable Electron version |
| Protocol | Local stdin/stdout NDJSON |
| Test payload | 1 KB, 16 KB, and 1 MB JSON |
| External network | Mock local HTTP service |
| External CLI | Controlled test executable |
| Database | Temporary local SQLite database |

Measurements should additionally be performed on representative lower-resource environments to identify inappropriate baseline assumptions.

MacOS validation should be added where macOS is a supported release target.

---

# 21. Proposed Performance Acceptance Matrix

| Metric | Initial proposed target | Measurement |
|---|---|---|
| Warm CLI dispatch p95 | ≤ 20 ms | No-op handler benchmark |
| Warm CLI dispatch p99 | ≤ 50 ms | No-op handler benchmark |
| Framework startup p95 | ≤ 500 ms | Minimal runtime initialization |
| 16 KB protocol processing p95 | ≤ 10 ms | Validation and serialization |
| Persistent CLI throughput | ≥ 1,000 requests/s | Local no-op workload |
| Progress event latency p95 | ≤ 50 ms | In-process emit to bridge receipt |
| HTTP connector overhead | ≤ 10% relative | Controlled HTTPX comparison |
| Minimal runtime overhead | ≤ 40 MiB | Incremental steady-state memory |
| Static analysis of 100k LOC | ≤ 60 seconds | Defined repository fixture |
| Long-running stability | 8-hour endurance test | Repeated actions and lifecycle |
| Core line coverage | ≥ 85% | Automated coverage reports |
| Protocol/error branch coverage | ≥ 90% | Automated coverage reports |

**Important:** All numerical thresholds remain provisional until representative benchmarks establish whether they are realistic, useful, and sufficiently portable.

Unrealistic thresholds should be revised explicitly rather than met by excluding important behavior from benchmarks.

---

# 22. Non-Functional Validation Scenarios

## Scenario NFS-01 — Minimal CLI Performance

**Given** a generated minimal AdharaSutra application,

**When** a no-op action is invoked repeatedly through a persistent process,

**Then** framework dispatch latency shall satisfy the approved benchmark target.

**And** the test shall exclude business-handler execution.

## Scenario NFS-02 — External Service Unavailable

**Given** an application uses a configured HTTP connector,

**When** the external service becomes unavailable,

**Then** the framework shall return a classified error.

**And** unrelated healthy application functionality shall remain available where supported.

## Scenario NFS-03 — External CLI Crash

**Given** a running external CLI process,

**When** the process terminates unexpectedly,

**Then** the framework shall detect the termination.

**And** release managed resources.

**And** report the correct failure state.

## Scenario NFS-04 — Concurrent State Updates

**Given** multiple active requests,

**When** those requests update shared framework-managed state,

**Then** the resulting state shall follow documented concurrency semantics without corruption.

## Scenario NFS-05 — Job Cancellation

**Given** a long-running job,

**When** Electron requests cancellation,

**Then** the framework shall report the actual cancellation outcome.

**And** avoid reporting completion before the operation has reached its terminal state.

## Scenario NFS-06 — Persistent CLI Endurance

**Given** a long-running application,

**When** repeated requests, connector operations, and job executions occur over an extended period,

**Then** the framework shall remain operational within approved resource-growth limits.

## Scenario NFS-07 — Architecture Reproducibility

**Given** identical application source, analyzer configuration, and tool versions,

**When** architecture verification is executed repeatedly,

**Then** deterministic findings shall remain identical.

## Scenario NFS-08 — Migration Safety

**Given** an existing application with working business functionality,

**When** an infrastructure migration is performed,

**Then** required regression tests shall verify preserved behavior.

**And** the migration shall not be considered complete solely because architecture rules pass.

## Scenario NFS-09 — Protocol Version Mismatch

**Given** incompatible Electron bridge and Python protocol versions,

**When** communication is attempted,

**Then** the incompatibility shall be detected.

**And** the framework shall fail safely rather than silently misinterpreting messages.

## Scenario NFS-10 — Packaged Application Startup

**Given** a production-packaged Electron application,

**When** the application launches on a supported operating system,

**Then** its Python runtime shall be discoverable and executable without relying on an undeclared developer environment.

---

# 23. Quality Gates

## Gate Q1 — Core Runtime Quality

Required evidence:

- Lifecycle tests.
- CLI protocol contract tests.
- Error-handling tests.
- Minimal runtime benchmarks.
- Resource cleanup verification.

## Gate Q2 — Connector Quality

Required evidence:

- HTTP connector tests.
- External CLI process tests.
- SQLite transaction tests.
- Timeout and cancellation tests.
- Connector failure isolation.

## Gate Q3 — Electron Quality

Required evidence:

- Shared bridge contract tests.
- Process startup and shutdown tests.
- Protocol version mismatch tests.
- Event streaming tests.
- Packaged application smoke tests.

## Gate Q4 — State and Job Quality

Required evidence:

- State concurrency tests.
- Persistent-state restoration tests.
- Job lifecycle tests.
- Cancellation tests.
- Recovery-policy tests.

## Gate Q5 — Architecture Verification Quality

Required evidence:

- Reproducible static rule results.
- Stable rule identifiers.
- Evidence-backed findings.
- Baseline integrity tests.
- Verification coverage reporting.

## Gate Q6 — Migration Quality

Required evidence:

- Non-destructive discovery.
- Source revision validation.
- Reviewable migration diffs.
- Data integrity tests.
- Regression tests.
- Migration completion report.

## Gate Q7 — Production Quality

Required evidence:

- Supported-platform builds.
- Release artifact validation.
- Dependency security checks.
- Compatibility matrix.
- Documentation and upgrade instructions.

---

# 24. Requirement Dependencies and Tradeoffs

Certain quality requirements may conflict.

These conflicts must be resolved explicitly during architecture design.

| Tradeoff | Consideration |
|---|---|
| Startup speed vs extensibility | Eager initialization increases startup work |
| Memory vs throughput | Caching and persistent resources consume memory |
| Reliability vs latency | Retries and health checks may increase response time |
| Simplicity vs configurability | Excessive options complicate maintenance |
| Strong isolation vs performance | Process boundaries introduce overhead |
| Strict architecture vs migration flexibility | Legacy applications need controlled exceptions |
| Detailed logging vs security | Diagnostics must avoid exposing sensitive data |
| Persistent jobs vs complexity | Durable execution requires defined worker ownership |
| Cross-platform behavior vs native features | Some process capabilities differ by OS |
| Automated migration vs safety | Complex refactoring requires review and regression evidence |

Architecture decisions must explicitly account for these tradeoffs.

---

# 25. Non-Functional Requirements Summary

| Group | Category | Count |
|---|---|---:|
| NFR-PERF | Performance | 8 |
| NFR-RES | Resource Efficiency | 5 |
| NFR-REL | Reliability | 10 |
| NFR-AVAIL | Availability and Recovery | 6 |
| NFR-SCALE | Scalability and Concurrency | 7 |
| NFR-SEC | Security | 12 |
| NFR-PORT | Portability | 7 |
| NFR-MAINT | Maintainability | 10 |
| NFR-EXT | Extensibility | 7 |
| NFR-TEST | Testability | 9 |
| NFR-COMP | Compatibility and Versioning | 8 |
| NFR-ARCH | Architecture Verification | 10 |
| NFR-MIG | Migration Safety | 10 |
| NFR-DOC | Documentation Quality | 8 |
| NFR-DX | Developer Experience | 8 |
| NFR-OPS | Operations and Packaging | 8 |
| NFR-OBS | Observability | 6 |
| **Total** | **17 requirement groups** | **139** |

These requirements define the intended quality characteristics of the complete framework.

Not every P1 or P2 capability must be implemented in the first software release.

---

# 26. Review and Approval Checklist

Before approving this document:

- [ ] Confirm supported operating systems.
- [ ] Confirm supported Python versions.
- [ ] Establish representative benchmark environments.
- [ ] Validate proposed performance thresholds.
- [ ] Review memory and resource-overhead targets.
- [ ] Define accepted concurrency and cancellation semantics.
- [ ] Verify security requirements cover Electron and external processes.
- [ ] Confirm SQLite durability and recovery expectations.
- [ ] Review protocol and public API compatibility policies.
- [ ] Validate architecture verification reproducibility requirements.
- [ ] Validate migration safety and data preservation policies.
- [ ] Define the required test evidence for each quality gate.
- [ ] Confirm release and maintenance requirements.
- [ ] Record unresolved tradeoffs.
- [ ] Approve the non-functional requirements baseline.

---

# 27. Open Questions

The following questions require architectural resolution.

### NFR-OQ-001 — Python Runtime Packaging

Should packaged Electron applications primarily bundle a Python runtime, a frozen executable, or support both?

### NFR-OQ-002 — Persistent Process Model

Should the default Electron integration use one persistent Python process per application or favor one-shot execution?

### NFR-OQ-003 — Job Execution Isolation

Should jobs execute in the CLI runtime process, managed child workers, or a configurable combination?

### NFR-OQ-004 — State Persistence

Should SQLite be the default persistent state backend, or remain an explicitly configured optional facility?

### NFR-OQ-005 — Connector Reliability

What retry and health-check policies should be enabled by default for external dependencies?

### NFR-OQ-006 — Architecture Verification Scope

Which checks must be enforced for every application profile, and which checks should be optional?

### NFR-OQ-007 — Migration Automation

Which source transformations are sufficiently safe to perform automatically without agent intervention?

### NFR-OQ-008 — Performance Baseline

What minimum hardware configuration should define the official benchmark reference machine?

### NFR-OQ-009 — Release Compatibility

How long should previously released CLI protocol and public API versions remain supported?

### NFR-OQ-010 — Framework Packaging

Should AdharaSutra begin as one Python distribution with optional extras or as several independently versioned packages?

---

# 28. Document Finalization

This document shall be finalized after:

1. Reviewing all requirements against `vision.md`.
2. Confirming consistency with `functional-requirements.md`.
3. Establishing realistic benchmark methods.
4. Validating representative runtime and connector scenarios.
5. Resolving critical security, reliability, and compatibility decisions.
6. Confirming the required quality gates.
7. Approving the non-functional baseline.

The approved document will serve as the quality reference for subsequent system and module architecture design.

---

# 29. Document Status

**Current status:** Draft  
**Approval:** Pending architecture review  
**Version:** 0.1.0

**Next design document:** `docs/design/system-architecture.md`

The next document should define the high-level system architecture, component boundaries, runtime composition, Electron communication path, connector relationships, and deployment models.

---

# 30. Final Quality Principle

AdharaSutra must provide more than reusable functionality.

It must provide a dependable foundation that is predictable to operate, safe to extend, straightforward to verify, and practical to adopt across existing applications.

Performance, reliability, security, testability, architecture compliance, and migration safety are essential characteristics of the framework—not optional qualities added after implementation.

**AdharaSutra — Build once. Standardize everywhere.**
