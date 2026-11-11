# AdharaSutra — Testing Strategy Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/testing-strategy.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Cross-Cutting Quality Engineering Architecture  
**Architecture Style:** Contract-Driven Testing, Layered Verification, Evidence-Based Quality Gates  
**Primary Language:** Python 3.12+  
**Additional Languages:** TypeScript and JavaScript  
**Test Execution:** Local Development, Automated CI, Controlled Integration Environments

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
- `docs/design/migration-framework.md`

---

# 1. Purpose

This document defines the testing architecture and quality-assurance strategy for AdharaSutra.

AdharaSutra is a reusable framework intended to support independent Python applications and Electron-backed desktop applications.

Because the framework owns critical infrastructure, failures within its implementation may affect multiple consuming applications.

Testing must therefore establish correctness at multiple levels:

1. Individual functions and classes.
2. Public framework contracts.
3. Module integrations.
4. CLI protocol communication.
5. Electron-to-Python interactions.
6. External connector behavior.
7. State and persistence correctness.
8. Job and subprocess lifecycle.
9. Application startup and shutdown.
10. Architecture discovery and verification.
11. Scaffolding and migration workflows.
12. Cross-platform behavior.
13. Performance and resource utilization.
14. Security boundaries.
15. Compatibility between framework releases.

Testing must distinguish implementation correctness from architecture conformance.

## 1.1 Central Principle

**Every important framework contract must have executable evidence appropriate to the behavior it promises.**

Static architecture verification proves supported structural properties.

Unit and integration tests verify executable behavior.

End-to-end tests validate representative workflows.

Performance and reliability tests evaluate behavior under measured conditions.

No single testing level is sufficient to establish overall quality.

## 1.2 Objectives

The Testing Strategy shall:

- Define a consistent testing taxonomy.
- Establish module-specific test responsibilities.
- Provide reusable test fixtures and helpers.
- Support deterministic local tests.
- Avoid requiring external AI models for routine testing.
- Validate CLI protocol framing and concurrency.
- Validate Electron bridge communication.
- Validate connector contracts.
- Verify state ownership and persistence.
- Verify job lifecycle and cancellation.
- Exercise real subprocess behavior safely.
- Verify configuration and application lifecycle.
- Test development tooling.
- Validate incremental migration.
- Establish cross-platform test coverage.
- Measure performance against approved requirements.
- Provide machine-readable evidence.
- Support architecture verification.
- Support automated CI quality gates.
- Support repeatable execution across coding-agent environments.

## 1.3 Non-Goals

The initial framework shall not require:

- A proprietary testing platform.
- A cloud testing service.
- Real ComfyUI or LM Studio servers for every test.
- Downloading large AI models during CI.
- Actual GPU hardware for basic framework verification.
- A mandatory real-browser session for every code change.
- Testing arbitrary application business logic automatically.
- Generating tests through an LLM.
- Running every expensive integration test on every commit.
- Treating code coverage as proof of correctness.
- Treating architecture PASS as equivalent to behavioral correctness.

---

# 2. Testing Principles

## TS-001 — Contract-First Testing

Public framework interfaces shall have explicit behavioral contracts and corresponding tests.

## TS-002 — Test Independence

Tests shall avoid unnecessary dependencies on other tests' execution order or side effects.

## TS-003 — Deterministic Core

Routine tests shall use controlled inputs, fixtures, and environment configuration.

## TS-004 — Appropriate Test Layers

Each behavior shall be tested at the narrowest useful layer, supplemented by integration or end-to-end tests where cross-component behavior matters.

## TS-005 — External Dependency Isolation

Routine tests shall use controlled substitutes for external services.

## TS-006 — Real Boundary Validation

Critical boundaries such as subprocess termination, SQLite transactions, and CLI framing shall also receive tests against real implementations.

## TS-007 — Honest Test Results

Tests that were not executed shall not be reported as passing.

## TS-008 — Evidence Traceability

Test results shall identify the tested source snapshot, environment, and relevant requirements.

## TS-009 — Failure-Path Coverage

Important error, cancellation, timeout, and recovery paths shall be tested explicitly.

## TS-010 — Cross-Platform Validation

Operating-system-dependent behavior shall be tested on each declared supported platform.

## TS-011 — Bounded Resource Usage

Tests shall avoid uncontrolled process creation, unbounded queues, persistent temporary files, and excessive memory consumption.

## TS-012 — Production Boundary Testing

Development-mode success shall not automatically establish packaged runtime correctness.

## TS-013 — Migration Regression Protection

Migration shall preserve required application behavior through executed regression evidence.

## TS-014 — Architectural Test Reuse

Scaffolding, verification, and migration shall reuse common profile and contract definitions.

## TS-015 — No Mandatory LLM

Testing shall operate without coding-agent or external-model inference.

## TS-016 — Reproducible Environments

Test dependencies, execution settings, and relevant environment characteristics shall be recorded.

## TS-017 — No False Durability

Job and state tests shall distinguish persisted metadata from genuine continued execution.

## TS-018 — Secure Test Execution

Tests involving untrusted applications or executable code shall use explicit trust and isolation policies.

---

# 3. Testing Scope

## 3.1 Framework Tests

Tests validating AdharaSutra's own implementation.

Examples:

- Core runtime tests.
- CLI protocol tests.
- Connector contract tests.
- Job lifecycle tests.
- Architecture verifier tests.

These are owned by the framework project.

## 3.2 Consuming Application Tests

Tests validating an application built with AdharaSutra.

Examples:

- Application use cases.
- Domain rules.
- Repository behavior.
- Application-specific connector adapters.
- Electron workflows.

These are owned by consuming applications.

## 3.3 Shared Contract Tests

Tests validating the boundary between AdharaSutra and consuming applications.

Examples:

- Action registration.
- Request/response schemas.
- Connector capabilities.
- State adapters.
- Job handlers.
- Electron bridge compatibility.

The framework shall provide reusable test utilities where practical.

## 3.4 Development Tooling Tests

Tests validating:

- Project scaffolding.
- Architecture discovery.
- Architecture verification.
- Migration planning.
- Source transformations.
- Reporting.

These tests belong to the development-tooling distribution and must not become mandatory application runtime dependencies.

---

# 4. High-Level Testing Architecture

```text
┌────────────────────────────────────────────────────┐
│                REQUIREMENTS AND CONTRACTS          │
│                                                    │
│ Functional Requirements                            │
│ Non-Functional Requirements                        │
│ Architecture Rules                                 │
│ Public API and Protocol Contracts                  │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│                 TEST DEFINITION LAYER              │
│                                                    │
│ Unit Tests                                         │
│ Contract Tests                                     │
│ Integration Tests                                  │
│ End-to-End Tests                                   │
│ Reliability / Security / Performance Tests         │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│                  TEST EXECUTION                    │
│                                                    │
│ Python Test Runner                                 │
│ TypeScript Test Runner                             │
│ Controlled Service Fixtures                        │
│ Process Fixtures                                   │
│ SQLite / Filesystem Fixtures                       │
│ Electron Test Host                                 │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│               TEST EVIDENCE COLLECTOR              │
│                                                    │
│ Results / Coverage / Environment                   │
│ Logs / Failures / Source Revision                  │
└─────────────────────────┬──────────────────────────┘
                          │
               ┌──────────┼─────────────┐
               ▼          ▼             ▼
          CI Gates   Architecture    Migration
                     Verification    Validation
```

## 4.1 Separation of Responsibilities

The test runner executes tests.

The evidence collector records results.

The architecture verifier evaluates applicable architecture rules and compatible test evidence.

The migration validator determines whether specific migration obligations were satisfied.

No subsystem shall independently invent test results.

---

# 5. Testing Levels

AdharaSutra defines the following primary testing levels.

| Level | Primary purpose | Typical execution |
|---|---|---|
| Unit | Isolated logic correctness | Every relevant change |
| Contract | Public interface compatibility | Every relevant change |
| Integration | Component interaction | Pull request / CI |
| End-to-end | Complete representative workflow | CI or release |
| Architecture | Structural conformance | Pull request / CI |
| Security | Supported threat and abuse cases | CI and release |
| Reliability | Failure and recovery behavior | CI / scheduled |
| Performance | Latency, throughput, resources | Benchmark pipeline |
| Packaging | Distributed artifact behavior | Release |
| Compatibility | Supported versions and platforms | CI matrix / release |

## 5.1 Test Pyramid

The default testing strategy should favor many fast unit and contract tests, fewer integration tests, and a focused collection of end-to-end tests.

This is a cost and coverage guideline, not a fixed percentage requirement.

## 5.2 Test Selection

Test selection shall depend on:

- Changed module.
- Public contract impact.
- Architecture profile.
- Supported capability.
- Platform requirements.
- Risk classification.
- Release stage.

---

# 6. Proposed Test Organization

## 6.1 Framework Repository

```text
tests/
│
├── unit/
│   ├── core/
│   ├── cli/
│   ├── connectors/
│   ├── state/
│   ├── jobs/
│   └── observability/
│
├── contracts/
│   ├── application/
│   ├── cli/
│   ├── connectors/
│   ├── state/
│   ├── jobs/
│   └── electron/
│
├── integration/
│   ├── runtime/
│   ├── http/
│   ├── websocket/
│   ├── process/
│   ├── sqlite/
│   └── lifecycle/
│
├── e2e/
│   ├── cli/
│   ├── electron/
│   └── sample_applications/
│
├── reliability/
│   ├── cancellation/
│   ├── crash_recovery/
│   ├── concurrency/
│   └── shutdown/
│
├── security/
│   ├── protocol/
│   ├── subprocess/
│   ├── filesystem/
│   └── electron/
│
├── performance/
│   ├── startup/
│   ├── protocol/
│   ├── connectors/
│   ├── state/
│   └── discovery/
│
├── tooling/
│   ├── scaffolding/
│   ├── discovery/
│   ├── verification/
│   └── migration/
│
├── fixtures/
│   ├── applications/
│   ├── repositories/
│   ├── executables/
│   ├── protocol/
│   └── databases/
│
└── support/
    ├── factories/
    ├── fakes/
    ├── assertions/
    └── evidence/
```

The structure is logical rather than mandatory at the individual-file level.

## 6.2 Electron Bridge Package

The separately distributed TypeScript bridge shall have its own tests.

```text
electron/
└── electron-bridge/
    ├── src/
    └── tests/
        ├── unit/
        ├── contracts/
        ├── integration/
        ├── e2e/
        └── fixtures/
```

## 6.3 Application Test Generation

The scaffolder shall generate test structure appropriate to the selected application profile.

A minimal CLI application should not receive empty test directories for infrastructure it does not use.

---

# 7. Test Tooling Strategy

## 7.1 Python Testing

**Proposed primary runner:** pytest.

Candidate complementary tools:

- `pytest-cov` or coverage.py for coverage.
- `pytest-asyncio` for asynchronous tests.
- HTTPX mocking facilities for controlled HTTP tests.
- Standard-library temporary directory utilities.
- Standard-library subprocess fixtures.
- Approved property-based testing tools where justified.

Selections remain subject to compatibility and dependency review.

## 7.2 TypeScript Testing

A TypeScript test runner shall validate the Electron bridge.

Possible implementations include Vitest or another suitable runner.

The final choice must support:

- TypeScript.
- Async operations.
- Process fixtures.
- Controlled IPC testing.
- Coverage reporting.
- CI execution.

## 7.3 Electron End-to-End Testing

Electron application tests must exercise actual main/preload/renderer boundaries when those behaviors are under test.

A browser-only renderer test does not prove Electron main-process behavior.

A suitable Electron-capable test host shall be selected during implementation.

## 7.4 Tooling Independence

Test contracts shall not expose implementation-specific testing-library types through public framework runtime APIs.

## 7.5 Optional Dependencies

Development test dependencies shall remain separate from production runtime requirements.

---

# 8. Unit Testing Architecture

## 8.1 Purpose

Unit tests verify isolated behavior with controlled dependencies.

## 8.2 Core Runtime Tests

Verify:

- Application registration.
- Duplicate registration rejection.
- Component resolution.
- Lifecycle transition validation.
- Execution context creation.
- Error classification.
- Configuration resolution.

## 8.3 CLI Tests

Verify:

- Envelope parsing.
- Message validation.
- Request correlation.
- Response serialization.
- Error serialization.
- Action lookup.

## 8.4 Connector Tests

Verify common connector registration and configuration behavior without requiring external services.

## 8.5 State Tests

Verify:

- State key registration.
- Scope validation.
- Reads and writes.
- Revision increments.
- Compare-and-set.
- Subscription registration and cleanup.

## 8.6 Job Tests

Verify:

- Job submission.
- Admission.
- State transitions.
- Progress normalization.
- Cancellation state.
- Attempt tracking.

## 8.7 Error and Logging Tests

Verify:

- Stable error codes.
- Exception chaining.
- Safe error details.
- Structured records.
- Redaction.
- Log-level filtering.

## 8.8 Unit Test Isolation

Tests should use controlled substitutes rather than real networking, databases, or operating-system processes unless those operations are the subject of the test.

---

# 9. Contract Testing Architecture

## 9.1 Purpose

Contract tests validate behavior exposed across module or package boundaries.

## 9.2 Contract Categories

| Contract | Producer | Consumer |
|---|---|---|
| Application API | Framework runtime | Python application |
| CLI protocol | Python runtime | Electron bridge / CLI client |
| Electron bridge API | Bridge package | Electron application |
| Connector capability | Connector module | Application adapter |
| State port | State subsystem | Persistence adapter |
| Job executor | Job subsystem | Executor implementation |
| Architecture model | Discovery | Verification / migration |
| Report schema | Development tooling | CI / coding agents |

## 9.3 Provider and Consumer Testing

A public contract should be tested from both sides where practical.

For example:

- Python produces a valid protocol response.
- TypeScript correctly consumes that response.

## 9.4 Schema Compatibility

Contract tests shall validate:

- Required fields.
- Optional fields.
- Unknown fields.
- Version compatibility.
- Invalid values.
- Serialization.
- Deserialization.

## 9.5 Breaking Changes

A public contract change must trigger compatibility evaluation against supported versions.

## 9.6 Shared Fixtures

Protocol and other cross-language contracts should use shared, versioned JSON fixtures to avoid divergent interpretations.

## 9.7 Contract Test Result

Passing a schema test proves the tested contract behavior, not all runtime integration behavior.

---

# 10. CLI Protocol Testing

## 10.1 Purpose

The CLI protocol is one of AdharaSutra's most critical infrastructure boundaries.

Because Electron communicates with Python through a structured subprocess protocol, message framing and output ownership must be reliable.

## 10.2 Protocol Unit Tests

Verify:

- Valid request parsing.
- Invalid JSON rejection.
- Missing required fields.
- Unsupported protocol version.
- Unknown message kinds.
- Message size limits.
- Request identifier handling.
- Standard error envelopes.

## 10.3 NDJSON Framing

Test:

- One message per line.
- Multiple messages in a stream.
- Partial byte chunks.
- Multiple lines in one read.
- UTF-8 boundaries split across chunks.
- Empty lines according to policy.
- Invalid encoding.
- Oversized messages.
- Interrupted stream.

## 10.4 Concurrent Requests

Verify:

- Distinct request IDs.
- Out-of-order responses.
- Correct response correlation.
- Request isolation.
- Bounded concurrency.
- Cancellation targeting.

## 10.5 Events

Verify:

- Event envelopes.
- Job progress.
- Terminal job events.
- Session events.
- Ordering guarantees within defined scopes.

## 10.6 stdout Isolation

No ordinary diagnostic logging shall appear on protocol stdout.

Tests should explicitly attempt:

- Framework logging.
- Application logging.
- Accidental application `print()`.
- External CLI stdout output.

The test must verify the runtime's documented handling of these situations.

## 10.7 stderr

Verify that diagnostic stderr output does not corrupt protocol message parsing.

## 10.8 One-Shot Execution

Verify:

- Action execution.
- Terminal response.
- Process exit status.
- Cleanup.
- No false background-job continuation.

## 10.9 Persistent Execution

Verify:

- Handshake.
- Multiple requests.
- Events.
- Cancellation.
- Session shutdown.
- Resource cleanup.

## 10.10 Broken Transport

Test behavior when stdin closes, stdout becomes unavailable, or the backend exits unexpectedly.

---

# 11. Electron Bridge Testing

## 11.1 Purpose

Validate the reusable TypeScript Electron bridge separately from consuming applications.

## 11.2 Unit Tests

Verify:

- Request ID generation.
- Pending request tracking.
- Timeout handling.
- Message parsing.
- Event subscription.
- Error conversion.
- Process state transitions.

## 11.3 Process Integration

Tests shall start a controlled Python fixture process.

Verify:

- Executable launch.
- stdin writes.
- stdout parsing.
- stderr capture.
- Handshake.
- Process exit detection.
- Restart policy.
- Shutdown.

## 11.4 Renderer Isolation

Verify that the renderer cannot directly access unrestricted backend process controls through the approved preload interface.

## 11.5 IPC Authorization

Test:

- Allowed actions.
- Rejected actions.
- Invalid payloads.
- Unauthorized callers where the selected Electron design requires validation.
- Malformed IPC requests.

## 11.6 Renderer Reload

Verify:

- Existing backend runtime remains active where configured.
- Old subscriptions are cleaned up.
- New subscriptions can be established.
- Current job state can be retrieved.
- Pending renderer operations are handled according to policy.

## 11.7 Multiple Windows

Verify:

- Independent renderer subscriptions.
- Shared backend lifecycle ownership in Electron main.
- Correct event routing.
- No unauthorized access to unrelated job or state information.

## 11.8 Backend Crash

Verify:

- Pending requests receive transport failures.
- Unknown business outcomes remain distinguishable.
- Job metadata is not falsely treated as active execution.
- Optional restart follows bounded policy.

---

# 12. Connector Contract Testing

## 12.1 Purpose

Connectors share common lifecycle and error conventions but expose different technical capabilities.

Tests must respect that distinction.

## 12.2 Common Connector Contract Suite

Every managed connector implementation should pass applicable tests for:

- Registration.
- Configuration validation.
- Initialization.
- Readiness semantics.
- Health capability.
- Technical error mapping.
- Resource ownership.
- Cleanup.
- Repeated close behavior.
- Partial initialization failure.

## 12.3 Capability-Specific Tests

A connector shall only be tested against capabilities it declares.

For example, SQLite transaction behavior is not applicable to an ordinary HTTP connector.

## 12.4 Reusable Test Harness

The framework should provide a connector contract-test harness that connector implementations can reuse.

## 12.5 Application Adapter Tests

Applications should test service-specific adapters independently using fake connector capabilities.

---

# 13. HTTP Connector Testing

## 13.1 Mock HTTP Tests

Verify:

- GET, POST, and other supported methods.
- Headers and query parameters.
- JSON and binary responses.
- Authentication configuration.
- Timeout classification.
- HTTP status handling.
- Request cancellation.
- Streaming.
- Error mapping.

## 13.2 Controlled Local HTTP Server

Integration tests should use a local server fixture where real network-stack behavior matters.

## 13.3 Retry Tests

Verify:

- Retry eligibility.
- Backoff policy.
- Maximum attempts.
- Deadline propagation.
- No unintended retries of non-idempotent operations.

## 13.4 Connection Pooling

Test client reuse and cleanup.

## 13.5 Remote Outcome Uncertainty

A request timeout shall not automatically be interpreted as proof that the remote operation had no effect.

## 13.6 External AI Services

Live ComfyUI or LM Studio tests are optional integration suites.

Routine framework tests shall not require them.

---

# 14. WebSocket Connector Testing

## 14.1 Connection Tests

Verify:

- Connection establishment.
- Message sending.
- Message reception.
- Graceful close.
- Unexpected close.

## 14.2 Reconnection

Verify configured reconnection policies without assuming message replay is safe.

## 14.3 Message Handling

Test:

- Text messages.
- Binary messages where supported.
- Invalid messages.
- Large messages.
- Message ordering.

## 14.4 Backpressure

Verify bounded message buffering.

## 14.5 Session Ownership

Verify connection cleanup when the owning session or job ends.

## 14.6 Controlled Fixtures

Use a local WebSocket server rather than relying on a public endpoint.

---

# 15. External Process Testing

## 15.1 Purpose

External process management requires real operating-system tests because mocks cannot prove process launch, pipe handling, or termination behavior.

## 15.2 Controlled Executable Fixtures

The framework should include small test programs implementing predictable behaviors.

Recommended fixtures:

| Fixture | Behavior |
|---|---|
| `exit_success` | Exit with code zero |
| `exit_failure` | Exit nonzero |
| `stdout_stream` | Emit incremental stdout |
| `stderr_stream` | Emit incremental stderr |
| `large_output` | Produce bounded high-volume output |
| `sleep_process` | Remain active until timeout or termination |
| `ignore_termination` | Exercise escalation where supported |
| `spawn_child` | Create a descendant process |
| `invalid_encoding` | Emit malformed text bytes |
| `generate_artifact` | Produce a deterministic output file |

These are test fixture names, not required executable filenames.

## 15.3 Required Process Tests

Verify:

- Executable discovery.
- Argument preservation.
- Paths containing spaces.
- Working directory.
- Environment handling.
- stdout/stderr capture.
- Concurrent stream draining.
- Exit status.
- Startup failure.
- Timeout.
- Cancellation.
- Escalated termination.
- Resource cleanup.

## 15.4 Process Trees

Test descendant-process cleanup on supported operating systems.

## 15.5 PID Reuse and Ownership

Recovery tests must not assume that an operating-system PID alone identifies the same process across time.

## 15.6 Shell Safety

Verify structured arguments and shell-disabled defaults.

## 15.7 Test Cleanup

All test-created processes must have explicit cleanup even when assertions fail.

## 15.8 audio.cpp Integration

The framework's Process Connector tests use controlled executables.

Application-specific audio.cpp tests may use a real tool when available, but are not mandatory for the generic connector contract.

---

# 16. SQLite Testing

## 16.1 Purpose

SQLite testing validates persistence infrastructure using a real local database engine.

## 16.2 Required Tests

Verify:

- Connection creation.
- Transaction commit.
- Transaction rollback.
- Parameterized queries.
- Constraint errors.
- Busy handling.
- Concurrent access.
- Connection ownership.
- Schema migration.
- Backup.
- Cleanup.

## 16.3 Database Isolation

Tests shall use separate temporary databases.

They must not modify actual application databases.

## 16.4 In-Memory Versus File Databases

In-memory databases are useful for fast tests.

File-backed temporary databases are required for behaviors involving durability, locking, backup, and restart.

## 16.5 Crash Recovery

Where practical, test behavior after abrupt termination of a controlled process using a file-backed database.

## 16.6 Schema Migration Tests

Verify:

- Migration ordering.
- Successful migration.
- Interrupted migration behavior.
- Incompatible schema.
- Rollback or recovery according to contract.

## 16.7 Data Integrity

Tests must check actual persisted values, not merely successful method returns.

---

# 17. Filesystem Testing

## 17.1 Purpose

Validate cross-platform path and artifact infrastructure.

## 17.2 Tests

Verify:

- Application directory resolution.
- File creation.
- Directory creation.
- Temporary files.
- Atomic replacement where supported.
- Cleanup.
- Large-file streaming.
- Invalid paths.
- Permission failures.
- Path traversal rejection.

## 17.3 Symbolic Links

Test:

- Valid links.
- Broken links.
- Cyclic links.
- Retargeted links.
- Links escaping approved roots.
- Link and target identity.

## 17.4 Security-Sensitive Access

Tests shall account for path-validation and file-use race conditions where relevant.

## 17.5 Platform Differences

Filesystem case sensitivity and path conventions must be tested according to platform behavior.

---

# 18. State Management Testing

## 18.1 Scope Tests

Verify request, session, process, job, and persistent scopes.

## 18.2 Ownership Tests

Verify that state is cleaned up when its owner ends.

## 18.3 Concurrency Tests

Verify:

- Atomic updates.
- Compare-and-set.
- Revision conflicts.
- Concurrent reads.
- Concurrent writes.
- Isolation.

## 18.4 Snapshot Tests

Verify returned state snapshots cannot bypass controlled mutation policies.

## 18.5 Subscription Tests

Verify:

- Registration.
- Notification.
- Ordering.
- Filtering.
- Slow subscribers.
- Unsubscription.
- Owner cleanup.

## 18.6 Persistence Tests

Verify:

- Durable commits.
- Restoration.
- Schema compatibility.
- Recovery failures.
- Interrupted writes.

## 18.7 Electron Synchronization

Test snapshot-and-event synchronization, missed-event recovery, renderer reload, and multiple-window behavior.

## 18.8 Sensitive State

Verify sensitive values are not automatically exposed through events or logs.

---

# 19. Job Management Testing

## 19.1 Lifecycle Tests

Verify transitions between:

- Pending.
- Running.
- Completed.
- Failed.
- Cancelled.
- Interrupted.

## 19.2 Submission Tests

Verify:

- Valid submission.
- Invalid input.
- Missing executor.
- Queue overflow.
- Duplicate submissions.
- Admission rejection.

## 19.3 Scheduling

Verify:

- FIFO policy.
- Configured concurrency.
- Queue ordering.
- Shutdown admission.
- Applicable priority rules.

## 19.4 Execution Strategies

Test:

- Async execution.
- Thread execution.
- External process execution.
- Optional worker-process execution when implemented.

## 19.5 Cancellation

Verify:

- Cancellation requested.
- Cancellation acknowledged.
- Confirmed cancellation.
- Cancellation unsupported.
- Already-terminal jobs.
- Non-cooperative execution.
- Cancellation/completion races.

## 19.6 Job Attempts

Verify stable job identity and separate execution-attempt histories.

## 19.7 Recovery

Test restart behavior against persisted job metadata.

## 19.8 Durability Truthfulness

A test must not treat restored job metadata as proof that execution continued.

## 19.9 Results

Verify final result validation, partial-result handling, artifact references, and retention.

---

# 20. Configuration and Lifecycle Testing

## 20.1 Configuration Tests

Verify:

- Default values.
- Source precedence.
- Nested merges.
- Scalar replacement.
- List replacement.
- Null versus missing values.
- Environment variables.
- Invalid configuration.
- Unknown keys.
- Secret references.

## 20.2 Composition Tests

Verify:

- Service registration.
- Duplicate registration.
- Missing dependencies.
- Dependency cycles.
- Lifecycle scope violations.
- Lazy initialization.

## 20.3 Startup Tests

Verify dependency-aware startup and readiness.

## 20.4 Partial Initialization Failures

Inject failure after some components initialize.

Verify reverse-dependency cleanup and preservation of the primary error.

## 20.5 Shutdown Tests

Verify:

- New work is rejected during shutdown.
- Active requests follow policy.
- Jobs follow shutdown policy.
- Connectors close at the correct point.
- Resources are released.
- Repeated shutdown is safe.

## 20.6 One-Shot Lifecycle

Verify that a one-shot process does not claim independent background-job execution without a real owner.

## 20.7 Persistent Lifecycle

Verify reusable components remain valid across multiple requests and close correctly on termination.

---

# 21. Error Handling and Observability Testing

## 21.1 Error Taxonomy

Verify registered technical error codes and categories.

## 21.2 Cause Preservation

Verify original exception causes remain available internally where appropriate.

## 21.3 Public Error Safety

Verify exceptions and stack traces are not exposed indiscriminately.

## 21.4 Logging

Verify:

- Structured fields.
- Timestamp formatting.
- Log levels.
- stderr output.
- File rotation.
- Queue limits.
- Sink failure behavior.

## 21.5 Correlation

Verify request, job, attempt, process, and connector correlation.

## 21.6 Redaction

Use controlled synthetic secret values to test:

- Token redaction.
- Authentication headers.
- Environment variables.
- Nested structured data.
- Exception messages.
- Diagnostic exports.

## 21.7 Health and Readiness

Verify the distinction between:

- Initialized connector.
- Reachable remote dependency.
- Healthy component.
- Ready application capability.

---

# 22. Architecture Discovery Testing

## 22.1 Purpose

Validate the evidence-backed repository analysis subsystem.

## 22.2 Fixture Repositories

Maintain controlled repository fixtures with known architecture patterns.

Examples:

- Minimal Python application.
- DDD application.
- Legacy `argparse` application.
- Custom Electron bridge.
- Framework Electron bridge.
- Direct subprocess integration.
- SQLite repository.
- Dynamic import.
- Invalid source file.
- Multi-package workspace.

## 22.3 Evidence Tests

Verify:

- Correct source paths.
- Correct line ranges.
- Valid fingerprints.
- Detector provenance.
- Observation classification.
- Uncertainty reporting.

## 22.4 Incremental Tests

Verify:

- Source modification.
- Source deletion.
- Renaming.
- Exclusion changes.
- Parser-version changes.
- Detector-version changes.
- Symlink retargeting.
- Stale cache invalidation.

## 22.5 Equivalence

Full discovery and incremental discovery shall produce equivalent canonical architecture models for the same supported source snapshot.

## 22.6 Safety

Verify default discovery does not execute inspected application code.

---

# 23. Architecture Verification Testing

## 23.1 Rule Tests

Each active rule shall include fixtures for:

- Compliant implementation.
- Violating implementation.
- Ambiguous implementation.
- Unavailable evidence.

## 23.2 Outcome Tests

Verify:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

## 23.3 Applicability

Verify irrelevant rules are marked nonapplicable and excluded from PASS counts.

## 23.4 Evidence Requirements

A rule shall not return PASS when required discovery coverage is insufficient.

## 23.5 Profile Tests

Verify:

- Minimal profile.
- CLI profile.
- DDD profile.
- Electron capability.
- AI-worker capability.
- Capability combinations.

## 23.6 Baseline Tests

Verify:

- Existing violations.
- New violations.
- Resolved violations.
- Stale baseline entries.

## 23.7 Exception Tests

Verify:

- Valid exceptions.
- Expired exceptions.
- Invalid approvals.
- Nonwaivable constraints.
- Raw verdict preservation.

## 23.8 Determinism

Equivalent inputs shall produce equivalent canonical rule verdicts.

---

# 24. Scaffolding Testing

## 24.1 Purpose

Every supported scaffold profile must generate a valid project foundation.

## 24.2 Template Tests

Verify:

- Manifest validity.
- Template variables.
- Capability resolution.
- Generated imports.
- Package metadata.
- Configuration.
- Documentation.

## 24.3 Generated Project Tests

For each supported baseline profile:

1. Generate a project.
2. Validate syntax.
3. Validate configuration.
4. Run architecture verification.
5. Execute basic runtime smoke tests where available.
6. Inspect result evidence.

## 24.4 Optional Capability Combinations

Maintain a compatibility matrix of representative capability combinations.

## 24.5 Filesystem Safety

Verify existing files are not silently overwritten.

## 24.6 Partial Generation Failure

Verify safe cleanup of newly created files and protection of preexisting content.

## 24.7 Agent Compatibility

Noninteractive generation shall produce deterministic, machine-readable results.

---

# 25. Migration Testing

## 25.1 Purpose

Migration testing verifies both transformation correctness and application behavior preservation.

## 25.2 Planning Tests

Verify:

- Current architecture interpretation.
- Target selection.
- Gap classification.
- Task generation.
- Dependency ordering.
- Risk classification.

## 25.3 Transformation Tests

Verify:

- Source preconditions.
- Intended edits.
- Unrelated source preservation.
- Syntax correctness.
- Formatting preservation where required.

## 25.4 Apply Tests

Verify:

- Dry run.
- Explicit apply.
- Source drift detection.
- Dirty worktree protection.
- Partial failure journaling.

## 25.5 Rollback Tests

Verify safe recovery of migration-owned file changes.

## 25.6 Behavioral Regression

Compare relevant existing behavior before and after migration.

## 25.7 Architecture Conformance

Verify migration resolves the targeted violations without introducing prohibited new violations.

## 25.8 Completion

A migration shall not be marked verified unless required architecture and behavioral checks pass.

## 25.9 External Side Effects

Migration tests must not claim that source rollback reverses external service calls or committed database operations.

---

# 26. End-to-End Testing

## 26.1 Purpose

End-to-end tests validate representative application workflows across their intended runtime boundaries.

## 26.2 Standalone CLI Scenario

```text
CLI Invocation
      │
      ▼
Application Bootstrap
      │
      ▼
Action Registration
      │
      ▼
Request Execution
      │
      ▼
Structured Response
      │
      ▼
Cleanup and Exit
```

## 26.3 Electron Scenario

```text
Electron Renderer
      │
      ▼
Preload IPC
      │
      ▼
Electron Main
      │
      ▼
AdharaSutra Bridge
      │
      ▼
Python Runtime
      │
      ▼
Application Action
      │
      ▼
Framework Connector / Job / State
      │
      ▼
Response or Event
      │
      ▼
Renderer
```

## 26.4 Representative Application Fixtures

The framework should maintain small reference applications.

Examples:

- Minimal CLI application.
- Electron + Python application.
- HTTP-connected application.
- SQLite-backed application.
- External-process worker application.
- Managed-job application.

## 26.5 Real Product Integration

Applications such as an audio workstation or image-generation studio should test their application-specific business operations separately.

Framework release tests should not depend on full AI processing pipelines unless explicitly required by the release scope.

## 26.6 Packaged E2E

At least one representative packaged desktop application should be tested to verify deployment-specific path and runtime resolution.

---

# 27. Failure Injection and Reliability Testing

## 27.1 Purpose

The framework must behave predictably under partial failure and unexpected termination.

## 27.2 Failure Categories

- Invalid requests.
- Connector unavailable.
- Network timeout.
- Database locked.
- Database corruption.
- External process crash.
- Python backend crash.
- Electron process disconnect.
- Job cancellation race.
- Logging sink unavailable.
- Disk full.
- Permission failure.
- Shutdown timeout.

## 27.3 Failure Isolation

A failure in an optional subsystem should not unnecessarily terminate unrelated capabilities.

## 27.4 Process Crash Recovery

Verify that persisted job metadata is reconciled with actual execution ownership.

## 27.5 Unknown Outcomes

Tests shall verify uncertainty remains explicit when final side effects cannot be confirmed.

## 27.6 Resource Cleanup

Failure injection should check for orphaned processes, unclosed connections, temporary-file leaks, and retained subscriptions.

## 27.7 Recovery Evidence

Recovery must be confirmed through observable checks rather than assumed from a successful restart.

---

# 28. Concurrency and Race-Condition Testing

## 28.1 Purpose

Persistent CLI applications may execute requests, jobs, and connector operations concurrently.

## 28.2 Scenarios

Test:

- Simultaneous action requests.
- Duplicate request identifiers.
- Concurrent state writes.
- Concurrent connector initialization.
- Job cancellation during completion.
- Shutdown during job submission.
- Renderer reload during event delivery.
- Process exit during cancellation.
- Configuration initialization races.

## 28.3 Deterministic Scheduling

Where feasible, use barriers, controlled events, and test hooks to reproduce race conditions.

Avoid relying only on arbitrary sleeps.

## 28.4 Repeated Execution

Known race-sensitive tests may be repeated under controlled stress settings.

## 28.5 Resource Bounds

Concurrency tests must enforce timeouts and cleanup policies.

## 28.6 Failure Reporting

A race failure should preserve sufficient correlation information to identify competing operations.

---

# 29. Performance Testing

## 29.1 Purpose

Performance tests establish whether the framework satisfies approved non-functional requirements.

## 29.2 Performance Categories

- Startup latency.
- CLI dispatch latency.
- Protocol processing.
- Request throughput.
- Event latency.
- Connector overhead.
- State read/write performance.
- Job scheduling overhead.
- Process startup overhead.
- Architecture discovery duration.
- Architecture verification duration.
- Memory usage.
- Long-running resource stability.

## 29.3 Existing Provisional Targets

The Non-Functional Requirements document proposes preliminary targets such as:

| Metric | Proposed target |
|---|---|
| Warm CLI dispatch p95 | ≤20 ms |
| Warm CLI dispatch p99 | ≤50 ms |
| Framework initialization p95 | ≤500 ms, excluding Python interpreter startup |
| Processing a 16 KB protocol message p95 | ≤10 ms |
| Lightweight request throughput | ≥1,000 requests/second under defined conditions |
| Event dispatch p95 | ≤50 ms |
| Minimal framework incremental memory | ≤40 MiB |
| Representative 100k-LOC architecture verification | ≤60 seconds |

These values are **draft targets, not verified performance claims or approved release thresholds**.

## 29.4 Benchmark Methodology

Every benchmark shall document:

- Hardware.
- Operating system.
- Python version.
- Framework version.
- Dependencies.
- Workload definition.
- Sample size.
- Warm-up procedure.
- Measurement method.
- Statistical summary.
- Relevant resource utilization.

## 29.5 Benchmark Isolation

Performance tests should run in controlled environments.

Uncontrolled shared CI runners may produce misleading latency measurements.

## 29.6 Regression Evaluation

Performance regressions should be compared against approved baselines using tolerances appropriate to measurement variability.

## 29.7 Test Overhead

The framework must distinguish instrumented testing overhead from normal production behavior.

---

# 30. Resource and Endurance Testing

## 30.1 Purpose

Persistent applications may run for extended periods.

The framework must not gradually accumulate unmanaged resources.

## 30.2 Endurance Scenario

A proposed endurance test should execute a persistent runtime for eight hours, subject to approved NFR validation.

## 30.3 Measurements

Monitor:

- Resident memory.
- Active threads.
- Open file handles.
- Active processes.
- Pending requests.
- Active subscriptions.
- Job queue size.
- Connection count.
- Temporary storage.
- Logging queue growth.

## 30.4 Workload

The endurance test should use repeatable representative actions rather than an entirely idle process.

## 30.5 Leak Criteria

Acceptable growth and stabilization limits must be established before using endurance results as a release gate.

## 30.6 Resource Cleanup

The test shall confirm resources are released after shutdown.

---

# 31. Security Testing

## 31.1 Purpose

Security tests validate supported trust boundaries and dangerous input handling.

## 31.2 CLI Protocol Tests

Verify:

- Invalid payload rejection.
- Message size limits.
- Malformed JSON handling.
- Reserved action protection.
- Unauthorized operation handling.
- Safe error serialization.

## 31.3 Electron Tests

Verify:

- Context isolation.
- Restricted preload exposure.
- Approved IPC actions.
- Renderer-to-main authorization.
- Controlled Python process startup.
- Artifact access restrictions.

## 31.4 Process Tests

Verify:

- Shell-disabled defaults.
- Structured argument handling.
- Executable allowlisting where configured.
- Untrusted executable-path rejection.
- Environment redaction.

## 31.5 Filesystem Tests

Verify:

- Path traversal rejection.
- Symbolic-link boundaries.
- Unauthorized access.
- Temporary resource permissions.

## 31.6 Configuration Tests

Verify secret references are not accidentally exposed.

## 31.7 Logging Tests

Verify synthetic secrets do not appear in ordinary diagnostic outputs.

## 31.8 Limitations

Passing these tests does not prove the application is free of all security vulnerabilities.

Additional dependency, package, and deployment security assessments may be needed.

---

# 32. Cross-Platform Testing

## 32.1 Supported Platforms

The initial target platforms are:

- Windows.
- Linux.
- macOS.

## 32.2 Python Matrix

Python 3.12 is the proposed minimum supported version.

Additional supported Python versions shall be declared and included in the test matrix.

## 32.3 Platform-Specific Concerns

| Concern | Windows | Linux | macOS |
|---|---|---|---|
| Process termination | Windows process semantics | POSIX signals/groups | POSIX signals/groups |
| Paths | Drives and backslashes | POSIX paths | POSIX paths |
| File permissions | Windows ACL behavior | POSIX permissions | POSIX permissions |
| Executable packaging | EXE / bundled runtime | Bundled runtime | App bundle/runtime |
| SQLite | Filesystem locking | Filesystem locking | Filesystem locking |
| Electron | Windows desktop | Linux desktop | macOS desktop |

## 32.4 Test Levels by Platform

Not every unit test requires separate behavior assertions for every OS.

Platform-dependent contracts and release artifacts must receive platform-specific validation.

## 32.5 Unsupported Environments

If a platform's required tests have not run, the release report must state the limitation.

---

# 33. Compatibility Testing

## 33.1 Purpose

AdharaSutra is consumed by multiple applications and may be distributed through Python and npm packages.

Compatibility testing must protect public contracts.

## 33.2 Compatibility Dimensions

- Python runtime versions.
- Framework public APIs.
- CLI protocol versions.
- Electron bridge versions.
- Connector interfaces.
- Configuration schemas.
- Architecture model schemas.
- Rule catalogs.
- Migration plan schemas.
- Package versions.

## 33.3 Python API Tests

Verify supported usage patterns against published public APIs.

## 33.4 Cross-Language Protocol Tests

Use shared fixtures between Python and TypeScript.

## 33.5 Version Negotiation

Test compatible and incompatible protocol-version combinations.

## 33.6 Unknown Fields

Verify forward-compatible behavior where permitted by the protocol contract.

## 33.7 Deprecation

Deprecated interfaces should be covered through the declared support period.

## 33.8 Package Installation

Verify the actual built Python distribution and Electron bridge package rather than only source-tree imports.

---

# 34. Packaging and Release Testing

## 34.1 Python Distribution

Test:

- Wheel construction.
- Distribution metadata.
- Installation into a clean environment.
- Required runtime imports.
- CLI entry point.
- Optional dependency groups.
- Installed resource files.

## 34.2 Development Tooling

Verify that developer-tooling dependencies do not become mandatory for minimal runtime users.

## 34.3 Electron Bridge

Test the produced npm package artifact.

Verify:

- Exported APIs.
- Type definitions.
- Runtime imports.
- Package metadata.
- Supported module format.
- Version compatibility.

## 34.4 Packaged Desktop Application

Verify:

- Python executable resolution.
- Embedded runtime paths.
- Resource availability.
- Connector initialization.
- CLI handshake.
- Logging paths.
- Application data paths.
- Startup and shutdown.

## 34.5 No Development Environment Assumptions

Packaged applications must not depend on a developer's virtual environment, machine-specific paths, or globally installed tools unless explicitly documented.

## 34.6 Release Evidence

Release tests must identify the exact built artifacts being evaluated.

---

# 35. Test Data and Fixture Management

## 35.1 Purpose

Fixtures make tests repeatable and independent of production systems.

## 35.2 Fixture Categories

- Protocol envelopes.
- Application configurations.
- Temporary files.
- SQLite databases.
- HTTP responses.
- WebSocket messages.
- Controlled executables.
- Example project repositories.
- Generated scaffold projects.
- Migration snapshots.

## 35.3 Fixture Ownership

Framework fixtures belong to the framework test suite.

Application-specific fixtures belong to consuming applications.

## 35.4 Versioning

Fixtures representing public contracts should be versioned.

## 35.5 Sensitive Data

Test fixtures must use synthetic data.

Production secrets and sensitive datasets must not be copied into ordinary test repositories.

## 35.6 Cleanup

Fixtures must clean up temporary resources after execution.

## 35.7 Fixture Fidelity

Mocks and fakes should reproduce the relevant contract rather than unrelated implementation details.

---

# 36. Test Doubles and Integration Boundaries

## 36.1 Types

The framework may use:

- Stubs.
- Fakes.
- Mocks.
- Spies.
- Controlled service implementations.

## 36.2 Appropriate Usage

Use test doubles when the behavior under test does not require the real dependency.

## 36.3 Real Boundary Requirement

Do not rely exclusively on mocks for:

- OS process termination.
- SQLite transaction guarantees.
- NDJSON pipe behavior.
- Electron IPC integration.
- Filesystem permissions.

## 36.4 Application Ports

Application use cases should be testable against fake ports.

## 36.5 Connector Contracts

Concrete connectors should be tested against a shared contract suite.

## 36.6 Mock Limitations

A mock that returns expected values proves only how the consuming code responds to the simulated behavior.

It does not establish that the real provider follows the same behavior.

---

# 37. Test Evidence Architecture

## 37.1 Purpose

Test evidence enables verification, migration, release decisions, and historical comparison.

## 37.2 Evidence Record

A test run should capture:

- Run ID.
- Test suite.
- Test identifiers.
- Source revision.
- Worktree state where relevant.
- Framework version.
- Environment.
- Execution timestamp.
- Outcome.
- Duration.
- Logs or failure references.
- Coverage artifact references where applicable.

## 37.3 Canonical Results

Proposed test results:

- `PASS`
- `FAIL`
- `SKIPPED`
- `ERROR`
- `NOT_RUN`

These are test-execution results, distinct from the architecture verifier's four canonical rule verdicts.

## 37.4 Result Mapping

| Test result | Architecture interpretation |
|---|---|
| PASS | May satisfy a rule's declared evidence requirements |
| FAIL | Evidence of failed behavior or requirement |
| SKIPPED | Does not prove the required behavior |
| ERROR | Test execution did not produce a valid passing result |
| NOT_RUN | No execution evidence |

A skipped test shall not automatically become an architecture PASS.

## 37.5 Source Freshness

Test evidence must correspond to the source snapshot being evaluated.

## 37.6 Environmental Applicability

A passing Linux process-termination test does not automatically prove Windows process-termination behavior.

## 37.7 Evidence Integrity

Result artifacts should include stable references and sufficient provenance for verification consumers.

---

# 38. Example Test Evidence Schema

```json
{
  "schema_version": "1.0",
  "run_id": "run-001",
  "source": {
    "revision": "abc123",
    "working_tree_modified": false
  },
  "environment": {
    "operating_system": "linux",
    "python_version": "3.12"
  },
  "suite": "cli-protocol-contracts",
  "summary": {
    "passed": 42,
    "failed": 0,
    "skipped": 1,
    "errors": 0
  },
  "tests": [
    {
      "id": "protocol.valid_response",
      "status": "PASS",
      "duration_ms": 15
    },
    {
      "id": "protocol.unsupported_transport",
      "status": "SKIPPED",
      "reason": "Fixture unavailable"
    }
  ]
}
```

This is an illustrative record, not an executed test result.

## 38.1 Schema Versioning

The test evidence schema shall be versioned.

## 38.2 External Test Runners

Adapters may normalize results from pytest and TypeScript test tools into the common evidence model.

## 38.3 Raw Evidence

Native test artifacts should remain available where useful for debugging.

The normalized model must not falsely claim more detail than the underlying runner provided.

---

# 39. Requirements Traceability

## 39.1 Purpose

Critical requirements should map to appropriate executable tests and validation evidence.

## 39.2 Functional Requirements

Each relevant functional requirement should identify:

- Test level.
- Test cases.
- Expected behavior.
- Applicable platforms.
- Evidence type.
- Release gate.

## 39.3 Non-Functional Requirements

Measurable NFRs should define:

- Measurement method.
- Test environment.
- Threshold.
- Sample size.
- Acceptance policy.

## 39.4 Traceability Example

| Requirement | Test category | Evidence |
|---|---|---|
| FR-CLI | Protocol contract | Request/response test |
| FR-ELC | Electron integration | Main/preload/renderer E2E |
| FR-EXT | Process integration | Controlled executable |
| FR-STATE | State correctness | Scope and concurrency tests |
| FR-JOB | Job lifecycle | Cancellation and recovery tests |
| FR-MIG | Migration safety | Source drift and rollback tests |
| NFR-SEC | Security | Input and boundary tests |
| NFR-PERF | Performance | Benchmark report |
| NFR-PORT | Portability | Platform CI matrix |

## 39.5 Missing Coverage

Requirements without sufficient tests must be visible in the coverage and readiness report.

---

# 40. Code Coverage Strategy

## 40.1 Purpose

Coverage provides useful evidence about executed source paths.

It is not a correctness guarantee.

## 40.2 Provisional Targets

The Non-Functional Requirements document proposes:

- At least **85% core line coverage**.
- At least **90% branch coverage** for critical protocol and error-handling logic.

These are provisional targets pending review and tooling validation.

## 40.3 Coverage Scope

Coverage reporting shall identify which modules are included and excluded.

## 40.4 Branch Coverage

Branch coverage should be prioritized for:

- Protocol validation.
- Error handling.
- Lifecycle transitions.
- Cancellation.
- Security-sensitive input handling.

## 40.5 Exclusions

Coverage exclusions must be documented.

## 40.6 Coverage Gaming

Tests must not be designed merely to execute lines without meaningful assertions.

## 40.7 Change Coverage

Changed-line coverage may supplement total project coverage when useful.

## 40.8 Missing Behavioral Tests

A module may meet coverage thresholds while still lacking important integration or failure-path testing.

Quality gates must therefore combine coverage with contract and behavior evidence.

---

# 41. CI Testing Architecture

## 41.1 Purpose

CI shall provide consistent automated quality evidence for changes and releases.

## 41.2 Proposed Pipeline

```text
Source Change
      │
      ▼
Static Checks
      │
      ▼
Unit Tests
      │
      ▼
Contract Tests
      │
      ▼
Architecture Verification
      │
      ▼
Integration Tests
      │
      ▼
Cross-Platform Tests
      │
      ▼
Build Package Artifacts
      │
      ▼
Package Smoke Tests
      │
      ▼
Release Quality Evaluation
```

Not every stage must execute on every developer commit.

## 41.3 Fast Feedback Pipeline

Recommended for ordinary development:

- Formatting and lint checks.
- Type checks where configured.
- Relevant unit tests.
- Relevant contract tests.
- Architecture verification.

## 41.4 Pull Request Pipeline

Recommended additional stages:

- Full unit suite.
- Contract suite.
- Relevant integration tests.
- Generated-project verification.
- Migration tooling tests where affected.
- Security checks.

## 41.5 Release Pipeline

Release validation should include:

- Cross-platform tests.
- Build artifacts.
- Package installation tests.
- Electron packaged tests.
- Compatibility tests.
- Applicable performance and reliability evidence.

## 41.6 Expensive Suites

Long-running endurance tests and optional external AI integrations may run on a scheduled or release-specific basis.

## 41.7 Failure Handling

CI shall distinguish:

- Failed test.
- Unexecuted test.
- Infrastructure error.
- Skipped test.
- Coverage gap.

---

# 42. Quality Gates

## 42.1 Gate Model

Testing shall be organized into explicit quality gates.

| Gate | Focus | Required evidence |
|---|---|---|
| QG-A | Core correctness | Unit and contract tests |
| QG-B | CLI protocol | Protocol and pipe integration tests |
| QG-C | Connectors | Contract and real-boundary tests |
| QG-D | Electron | Bridge, IPC, and process lifecycle |
| QG-E | State and jobs | Concurrency, cancellation, persistence |
| QG-F | Development tooling | Scaffolding, discovery, verification |
| QG-G | Migration | Transformation and regression evidence |
| QG-H | Security and reliability | Relevant failure and abuse tests |
| QG-I | Packaging and compatibility | Installed artifact and platform tests |
| QG-J | Performance | Benchmarks against approved NFRs |

These gates are testing-quality categories; they complement the functional implementation gates in the requirements documents rather than replacing them.

## 42.2 Gate Outcomes

Proposed gate outcomes:

- `PASSED`
- `FAILED`
- `INCOMPLETE`
- `BLOCKED`

## 42.3 Passing Gate

A gate passes only when its mandatory checks and evidence requirements are satisfied.

## 42.4 Incomplete Gate

A gate is incomplete when necessary evidence is missing or unexecuted.

## 42.5 Blocked Gate

A gate is blocked when prerequisites prevent meaningful execution.

## 42.6 Gate Policy

Exact mandatory tests and thresholds must be approved before a gate becomes release-blocking.

---

# 43. Release Readiness

## 43.1 Purpose

Release readiness combines multiple quality dimensions.

## 43.2 Required Categories

A release assessment should consider:

- Functional correctness.
- Public contract compatibility.
- Architecture conformance.
- Cross-platform behavior.
- Security.
- Reliability.
- Performance.
- Packaging.
- Documentation.
- Known unresolved issues.

## 43.3 Release Evidence

The release report should identify:

- Source revision.
- Package versions.
- Built artifacts.
- Platforms tested.
- Test suites executed.
- Results.
- Coverage.
- Applicable NFR benchmarks.
- Exceptions.
- Unresolved blockers.

## 43.4 Conditional Release

A release with incomplete evidence may only proceed according to an explicit approved release policy.

## 43.5 No False Certification

The framework must not label a release fully verified when required testing has not occurred.

---

# 44. Testing Developer CLI

## 44.1 Purpose

AdharaSutra should provide convenient developer commands for invoking standard test workflows.

## 44.2 Proposed Commands

Run standard tests:

```bash
adhara test ./my-application
```

Run contract tests:

```bash
adhara test ./my-application --suite contracts
```

Run integration tests:

```bash
adhara test ./my-application --suite integration
```

Run architecture verification:

```bash
adhara verify ./my-application
```

Run performance tests:

```bash
adhara test ./my-application --suite performance
```

Generate a test report:

```bash
adhara test ./my-application \
  --format json \
  --output ./reports/test-results.json
```

These are proposed developer interfaces, not existing functionality.

## 44.3 Runner Integration

The developer CLI should coordinate approved test runners rather than reimplement their internal assertion engines.

## 44.4 Test Discovery

Applications should declare or configure their test suites.

The framework should not depend solely on directory-name guesses.

## 44.5 Execution Safety

Running application tests may execute arbitrary application code.

Unlike static architecture inspection, test execution is a side-effecting operation and requires an appropriate trusted environment.

## 44.6 Missing Runner

When a configured test runner is unavailable, the command must report the missing dependency and NOT_RUN status for affected tests.

---

# 45. Testing Integration with Architecture Verification

## 45.1 Shared Evidence

The Architecture Verification subsystem may consume executed test evidence.

## 45.2 Static Versus Behavioral Rules

Static rules use source discovery evidence.

Behavioral rules require compatible test or runtime evidence.

## 45.3 Rule-Level Evidence Mapping

A rule may declare:

```yaml
rule:
  id: JPM-VER-012
  version: 1.0.0

  requires:
    - job_cancellation_contract_test
    - supported_executor_evidence
```

This is illustrative.

## 45.4 Evidence Validation

The verifier should check:

- Source snapshot.
- Test identity.
- Environment.
- Result.
- Rule compatibility.

## 45.5 Evidence Limitations

A passing test from a different source revision shall not be silently treated as proof of the current implementation.

## 45.6 Verdict Mapping

Architecture rules retain their own verdicts:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

Test execution results are normalized into compatible evidence, not substituted directly without evaluation.

---

# 46. Testing Integration with Migration

## 46.1 Purpose

Migration requires evidence that existing application behavior was preserved.

## 46.2 Baseline Before Change

Relevant characterization and regression tests should run before migration where feasible.

## 46.3 Validation After Change

The same behavioral contracts should be evaluated after applying migration changes.

## 46.4 Differential Verification

Where deterministic comparison is possible, old and new implementations may be compared.

## 46.5 Architecture Validation

Migration must also evaluate target architecture rules.

## 46.6 Migration Completion

The migration task becomes verified only when:

1. Approved changes were applied.
2. Required architecture checks passed or satisfied the approved enforcement policy.
3. Required behavioral checks passed.
4. No unresolved mandatory validation remains.

## 46.7 Failure Reporting

Migration validation must identify whether failure originates from:

- Source transformation.
- Architecture conformance.
- Behavioral regression.
- Test infrastructure.
- Missing evidence.

---

# 47. Testing Integration with Scaffolding

## 47.1 Purpose

Newly generated projects should be testable immediately.

## 47.2 Generated Tests

The scaffold shall include tests appropriate to selected profiles and capabilities.

## 47.3 Minimal Example

A minimal project may include a single meaningful action contract test.

## 47.4 Electron Applications

Electron templates should include bridge and IPC test foundations.

## 47.5 Job Applications

Job templates should include lifecycle and cancellation test examples.

## 47.6 Validation

A generated project must not be reported as fully verified unless the relevant tests were executed successfully.

---

# 48. Testing Across Coding Agents

## 48.1 Purpose

AdharaSutra's test evidence and quality gates should remain consistent across development tools.

## 48.2 Agent Independence

The test architecture shall not depend on a specific coding agent.

## 48.3 Recommended Agent Workflow

```text
Implement Change
      │
      ▼
Run Relevant Tests
      │
      ▼
Run Architecture Verification
      │
      ▼
Inspect Failures
      │
      ▼
Fix Implementation
      │
      ▼
Rerun Affected Tests
      │
      ▼
Record Evidence
```

## 48.4 Machine-Readable Results

Test results should be available in JSON.

## 48.5 Agent Claims

An agent's statement that tests passed is not equivalent to recorded test-run evidence.

## 48.6 Unavailable Tools

When a required browser, Electron host, Python environment, executable, or test service is unavailable, the result must explicitly identify the affected tests as unexecuted.

## 48.7 Consistency

Different coding agents using equivalent source, dependencies, configuration, and test environments should obtain equivalent deterministic results.

---

# 49. Testing Failure and Error Architecture

## 49.1 Proposed Tooling Error Codes

```text
TEST_RUNNER_UNAVAILABLE
TEST_CONFIGURATION_INVALID
TEST_FIXTURE_FAILED
TEST_EXECUTION_FAILED
TEST_TIMEOUT
TEST_EVIDENCE_INVALID
TEST_EVIDENCE_STALE
TEST_ENVIRONMENT_UNSUPPORTED
TEST_RESOURCE_LIMIT_EXCEEDED
TEST_REPORT_GENERATION_FAILED
```

These remain proposed and must be reconciled with the framework-wide error catalog.

## 49.2 Failure Classification

Distinguish:

- Test assertion failure.
- Test setup failure.
- Test runner failure.
- Timeout.
- Environment limitation.
- Invalid evidence.
- Internal framework testing-tool failure.

## 49.3 Test Logs

Test execution logs must be bounded and sanitized.

## 49.4 Process Cleanup

A test-runner failure must not leave unmanaged subprocesses where cleanup remains possible.

---

# 50. Testing Strategy Verification Rules

These rules evaluate the testing architecture and evidence process.

| Rule ID | Description |
|---|---|
| TS-VER-001 | Public framework contracts have applicable tests |
| TS-VER-002 | Mandatory test suites are declared |
| TS-VER-003 | Test execution evidence identifies the source snapshot |
| TS-VER-004 | Unexecuted tests are not marked passed |
| TS-VER-005 | Protocol contracts have serialization tests |
| TS-VER-006 | Protocol stdout isolation is tested |
| TS-VER-007 | Connector implementations satisfy applicable contracts |
| TS-VER-008 | External process management has real-process tests |
| TS-VER-009 | State concurrency and persistence have behavioral tests |
| TS-VER-010 | Job cancellation and terminal states have tests |
| TS-VER-011 | Lifecycle startup and shutdown have tests |
| TS-VER-012 | Electron IPC boundaries have applicable tests |
| TS-VER-013 | Architecture discovery incremental equivalence is tested |
| TS-VER-014 | Architecture rules have positive and negative fixtures |
| TS-VER-015 | Generated scaffold profiles have smoke tests |
| TS-VER-016 | Migration transformations have regression tests |
| TS-VER-017 | Sensitive-data redaction is tested |
| TS-VER-018 | Supported platform claims have matching test evidence |
| TS-VER-019 | Coverage reporting follows approved policy |
| TS-VER-020 | Release quality gates identify missing required evidence |

---

# 51. Representative End-to-End Testing Scenarios

## TS-S01 — Minimal CLI Application

**Given** a minimal application generated by AdharaSutra,

**When** its CLI smoke test runs,

**Then** the application shall initialize, execute its registered action, produce the expected response, clean up resources, and exit.

## TS-S02 — Persistent CLI Protocol

**Given** a persistent Python runtime,

**When** multiple valid and invalid requests are submitted,

**Then** valid responses shall correlate to their requests.

**And** invalid requests shall produce classified failures without unnecessary runtime termination.

## TS-S03 — stdout Isolation

**Given** a connector or application produces diagnostic output,

**When** the CLI protocol is active,

**Then** diagnostic output shall not corrupt NDJSON messages.

## TS-S04 — Electron-to-Python Request

**Given** Electron uses the shared bridge,

**When** an authorized renderer submits an application action,

**Then** the request shall reach the Python handler and its response shall return through the approved IPC path.

## TS-S05 — Electron Renderer Reload

**Given** a managed job is active,

**When** the renderer reloads,

**Then** the backend job shall remain under its defined execution owner.

**And** the new renderer shall be able to retrieve authorized status.

## TS-S06 — HTTP Connector Failure

**Given** a controlled HTTP dependency fails,

**When** the application makes a request,

**Then** the connector shall classify the failure appropriately.

## TS-S07 — External Process Cancellation

**Given** a controlled executable is running,

**When** cancellation is requested,

**Then** the Process Connector shall apply the configured termination policy.

**And** report the observed outcome.

## TS-S08 — SQLite Persistence

**Given** persistent state is committed to a temporary file-backed database,

**When** the application restarts,

**Then** committed values shall be restored according to the persistence contract.

## TS-S09 — State Conflict

**Given** concurrent updates use the same expected revision,

**When** they attempt conflicting writes,

**Then** the state store shall enforce the declared conflict semantics.

## TS-S10 — Job Queue Capacity

**Given** the Job Manager reaches its configured capacity,

**When** additional work is submitted,

**Then** admission control shall prevent unbounded resource growth.

## TS-S11 — Python Backend Crash

**Given** Electron has pending requests,

**When** Python terminates unexpectedly,

**Then** the bridge shall report transport failure.

**And** shall not claim unconfirmed business operations failed without side effects.

## TS-S12 — Partial Startup Failure

**Given** some components initialize before a required component fails,

**When** startup aborts,

**Then** lifecycle cleanup shall release owned resources where possible.

**And** preserve the original failure evidence.

## TS-S13 — Architecture Discovery Equivalence

**Given** a repository has been analyzed,

**When** source changes and incremental discovery runs,

**Then** the resulting canonical model shall match a full discovery of the same source snapshot.

## TS-S14 — Architecture Evidence Gap

**Given** required source is not analyzed,

**When** architecture verification executes,

**Then** affected rules shall not report unsupported PASS outcomes.

## TS-S15 — Scaffold Verification

**Given** a new project is generated,

**When** its relevant tests and architecture checks run,

**Then** the result shall distinguish actual passes from unexecuted checks.

## TS-S16 — Migration Regression

**Given** an existing application is migrated,

**When** required regression tests execute,

**Then** migration completion shall depend on actual behavior compatibility, not just structural conformance.

## TS-S17 — Cross-Platform Process Management

**Given** a supported operating system,

**When** process lifecycle tests execute,

**Then** applicable launch, exit, and termination behavior shall satisfy the platform-specific contract.

## TS-S18 — Packaged Electron Application

**Given** a built desktop package,

**When** a packaged smoke test launches it,

**Then** the embedded Python runtime and shared bridge shall initialize without relying on development-only paths.

## TS-S19 — Sensitive Diagnostic Data

**Given** synthetic credentials are present in test configuration,

**When** errors and logs are produced,

**Then** unauthorized diagnostic outputs shall not expose the values.

## TS-S20 — Required Test Not Executed

**Given** a required test environment is unavailable,

**When** quality evaluation runs,

**Then** that test shall be reported as NOT_RUN or an equivalent unexecuted state.

**And** the affected mandatory gate shall not be marked PASSED.

---

# 52. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| TS-D01 | Python runner | pytest |
| TS-D02 | TypeScript runner | Suitable TypeScript-capable runner |
| TS-D03 | Testing layers | Unit, contract, integration, E2E |
| TS-D04 | Routine external dependencies | Controlled fixtures |
| TS-D05 | Process verification | Real controlled executables |
| TS-D06 | SQLite verification | Real temporary databases |
| TS-D07 | Electron verification | Actual IPC/Electron test host |
| TS-D08 | Shared protocol contracts | Versioned JSON fixtures |
| TS-D09 | Test evidence | Versioned machine-readable model |
| TS-D10 | Architecture integration | Evidence consumed by verifier |
| TS-D11 | Migration integration | Before/after regression evidence |
| TS-D12 | Scaffolding integration | Profile-specific generated tests |
| TS-D13 | Code coverage | Measured, not sole acceptance criterion |
| TS-D14 | Performance | Dedicated benchmark environment |
| TS-D15 | Cross-platform | Windows, Linux, macOS |


Continuing `docs/design/testing-strategy.md` from TS-D16, where the previous response was interrupted. The following completes the remaining sections without repeating the earlier content.

## 52. Architectural Decisions (continued)

| ID     | Decision                      | Proposed direction                             |
| ------ | ----------------------------- | ---------------------------------------------- |
| TS-D16 | Test execution defaults       | Fast deterministic suites for development      |
| TS-D17 | Expensive integration tests   | Separate CI and release suites                 |
| TS-D18 | External AI services          | Optional integration tests                     |
| TS-D19 | GPU dependency                | Not mandatory for core framework tests         |
| TS-D20 | Failure injection             | Mandatory for critical lifecycle boundaries    |
| TS-D21 | Concurrency testing           | Controlled scheduling and repeated execution   |
| TS-D22 | Performance thresholds        | Approved, measurable NFR baselines             |
| TS-D23 | Endurance testing             | Dedicated reliability suite                    |
| TS-D24 | Security testing              | Trust-boundary and abuse-case verification     |
| TS-D25 | Package testing               | Validate actual built artifacts                |
| TS-D26 | Cross-platform validation     | Windows, Linux, and macOS                      |
| TS-D27 | CI quality gates              | Layered, evidence-driven enforcement           |
| TS-D28 | Test results                  | PASS, FAIL, SKIPPED, ERROR, NOT_RUN            |
| TS-D29 | Missing evidence              | Never treated as passing                       |
| TS-D30 | Coverage thresholds           | Provisional until benchmarked and approved     |
| TS-D31 | Test environment metadata     | Required for reproducibility                   |
| TS-D32 | Regression testing            | Mandatory for affected migration behavior      |
| TS-D33 | Test tooling distribution     | Separate from minimal production runtime       |
| TS-D34 | Agent compatibility           | Machine-readable results, independent of agent |
| TS-D35 | Test orchestration            | Reuse established test runners                 |
| TS-D36 | Release readiness             | Combined quality-gate assessment               |
| TS-D37 | Framework test utilities      | Reusable fixtures and contract harnesses       |
| TS-D38 | Untrusted application testing | Explicit trust and isolation policy            |
| TS-D39 | Test evidence freshness       | Validate against tested source snapshot        |
| TS-D40 | LLM dependency                | None required                                  |

All decisions remain proposed until architecture review and approval.

## 53. Outstanding Questions

### TS-OQ-001 — Python Test Framework

Should pytest be the mandatory framework testing tool?

Recommendation: Use pytest as the primary internal testing framework while allowing consuming applications to use compatible alternatives. Public framework contracts must remain independent of pytest-specific implementation types.

### TS-OQ-002 — Async Testing

Should pytest-asyncio be a required development dependency?

Recommendation: Use it for asynchronous framework testing if selected, but keep it out of ordinary application runtime dependencies.

### TS-OQ-003 — TypeScript Test Runner

Should the Electron bridge use Vitest or another test runner?

Recommendation: Select a runner that supports TypeScript, controlled subprocess fixtures, coverage, and Electron integration. The precise choice should be validated during implementation.

### TS-OQ-004 — Electron End-to-End Framework

Should Playwright be the primary Electron E2E framework?

Recommendation: Evaluate Playwright's Electron support and its compatibility with the chosen Electron packaging architecture. Browser-only tests shall not substitute for required Electron main/preload integration testing.

### TS-OQ-005 — Real External Service Tests

Should tests against ComfyUI, LM Studio, or audio.cpp be mandatory?

Recommendation: No. Generic framework tests shall use controlled fixtures. Real integration tests should be application-specific or optional capability-validation suites.

### TS-OQ-006 — GPU Testing

Should AdharaSutra CI require NVIDIA or AMD GPUs?

Recommendation: No. GPU hardware is not required for core infrastructure correctness. Hardware-specific processing tests may be maintained by applications that depend on GPU behavior.

### TS-OQ-007 — Test Fixture Distribution

Should shared test fixtures be included in the production AdharaSutra package?

Recommendation: Keep substantial fixtures in the development/test distribution. Provide a small optional test-support package only if consuming applications benefit from reusable contract harnesses.

### TS-OQ-008 — Test Evidence Format

Should AdharaSutra create a custom JSON format or adopt an established format?

Recommendation: Define a versioned normalized internal evidence schema while supporting imports from established runner outputs such as JUnit XML. Avoid inventing an entirely new test execution system.

### TS-OQ-009 — Code Coverage Targets

Should 85% core coverage and 90% critical branch coverage become mandatory?

Recommendation: Treat them as provisional. Validate achievable thresholds, excluded modules, and critical failure-path coverage before approving release gates.

### TS-OQ-010 — Contract Test Sharing

Should Python and TypeScript use the same protocol fixtures?

Recommendation: Yes. Shared versioned JSON fixtures should be authoritative for cross-language serialization and compatibility tests.

### TS-OQ-011 — Cross-Platform CI

Should every pull request run on Windows, Linux, and macOS?

Recommendation: Run fast critical cross-platform tests on pull requests where economically practical. Require a complete supported-platform matrix for releases.

### TS-OQ-012 — Packaged Electron Testing

Should packaged Electron smoke tests be mandatory for releases?

Recommendation: Yes, for each platform officially supported by the packaged desktop integration. Development-mode tests cannot prove packaged runtime resolution.

### TS-OQ-013 — Endurance Testing

Should an eight-hour persistent-runtime test become mandatory?

Recommendation: Use an eight-hour test as a provisional reference workload. Finalize duration, frequency, and measurable leak thresholds after profiling.

### TS-OQ-014 — Concurrency Stress Tests

How should intermittent concurrency failures be evaluated?

Recommendation: Use deterministic race fixtures where possible, supplemented by repeated stress runs. Reproducible failures must not be dismissed as ordinary test noise.

### TS-OQ-015 — Flaky Test Handling

Should the test orchestrator automatically retry failed tests?

Recommendation: Automatic retries may be used diagnostically, but the original failure must remain visible. A passing retry must not silently erase evidence of an intermittent problem.

### TS-OQ-016 — Architecture Test Execution

Should `adhara verify` run behavioral tests automatically?

Recommendation: No. Static verification should remain read-only and nonexecuting by default. Add an explicit test-enabled verification mode.

### TS-OQ-017 — Migration Regression Baselines

Should the Migration Framework automatically generate before-and-after regression tests?

Recommendation: It may generate test scaffolds or candidate cases, but established behavior must be validated through executed characterization tests.

### TS-OQ-018 — Performance Regression Thresholds

What performance regression tolerance should block releases?

Recommendation: Use benchmark-specific thresholds and statistically meaningful repeated measurements rather than one global percentage.

### TS-OQ-019 — Test Artifact Retention

How long should CI logs, coverage reports, and test evidence be retained?

Recommendation: Use configurable retention policies based on test criticality, release traceability, storage cost, and privacy requirements.

### TS-OQ-020 — Test Execution Authorization

Should `adhara test` execute tests from any repository automatically?

Recommendation: Require a trusted environment and explicit test invocation. Static discovery and verification must never execute repository tests implicitly.

### TS-OQ-021 — Application Test Profiles

Should AdharaSutra define standardized application testing profiles?

Recommendation: Yes. Define reusable test expectations for `minimal`, `cli`, `ddd`, `electron-cli`, and `ai-worker`, with capability-specific requirements.

### TS-OQ-022 — Quality Gate Policy

Should all quality gates be mandatory for every application?

Recommendation: No. Gate applicability should depend on the selected profile and capabilities. Mandatory core safety and compatibility requirements must still be enforced.

### TS-OQ-023 — Test Result Caching

Should test results be reused when source files appear unchanged?

Recommendation: Allow validated caching only when source, dependencies, test configuration, fixtures, and relevant environment inputs are compatible. Avoid treating stale results as current evidence.

### TS-OQ-024 — Failure Injection Framework

Should AdharaSutra introduce its own failure-injection engine?

Recommendation: Start with reusable fixture utilities and test hooks. Build a dedicated engine only if repeated use cases justify the complexity.

### TS-OQ-025 — Agent-Generated Tests

Should tests written by a coding agent receive special treatment?

Recommendation: No. They must satisfy the same execution, coverage, evidence, and quality requirements as developer-written tests.

## 54. Functional Requirement Traceability

| Requirement group | Testing responsibility                             |
| ----------------- | -------------------------------------------------- |
| FR-RUN            | Runtime initialization, action execution, shutdown |
| FR-CLI            | Protocol parsing, framing, responses, errors       |
| FR-ELC            | Electron bridge, IPC, lifecycle                    |
| FR-CON            | Connector contract validation                      |
| FR-HTTP           | HTTP transport and failure handling                |
| FR-EXT            | External executable and process management         |
| FR-DB             | SQLite persistence and transactions                |
| FR-WS             | WebSocket communication                            |
| FR-FS             | Filesystem access and artifact handling            |
| FR-STATE          | State scopes, consistency, subscriptions           |
| FR-JOB            | Scheduling, execution, cancellation, recovery      |
| FR-CFG            | Configuration validation and precedence            |
| FR-ERR            | Error taxonomy and propagation                     |
| FR-LOG            | Structured logging and diagnostics                 |
| FR-DI             | Service composition and dependency lifecycle       |
| FR-SCAF           | Generated application validation                   |
| FR-DISC           | Discovery correctness and evidence integrity       |
| FR-ARCH           | Architecture rule evaluation                       |
| FR-MIG            | Migration regression and recovery                  |
| FR-REP            | Test and verification reports                      |
| FR-TEST           | Test frameworks, fixtures, and execution           |
| FR-DEV            | Developer testing CLI                              |
| FR-PKG            | Distribution and packaged runtime tests            |
| FR-DOC            | Test documentation and reproducibility             |
| FR-SEC            | Security and trust-boundary tests                  |

## 55. Non-Functional Requirement Traceability

| Requirement group | Testing mechanism                            |
| ----------------- | -------------------------------------------- |
| NFR-PERF          | Benchmarks and latency measurements          |
| NFR-RES           | Resource limits, cleanup, endurance tests    |
| NFR-REL           | Failure injection and recovery verification  |
| NFR-AVAIL         | Readiness and degradation scenarios          |
| NFR-SCALE         | Concurrency, throughput, and queue testing   |
| NFR-SEC           | Input validation and security-boundary tests |
| NFR-PORT          | Windows, Linux, macOS test matrix            |
| NFR-MAINT         | Modular fixtures and reusable contracts      |
| NFR-EXT           | Connector and executor contract suites       |
| NFR-TEST          | Coverage, test isolation, evidence           |
| NFR-COMP          | Versioned compatibility test matrices        |
| NFR-ARCH          | Profile-based architecture verification      |
| NFR-MIG           | Behavioral regression and rollback tests     |
| NFR-OBS           | Logging, metrics, and correlation testing    |
| NFR-OPS           | CI, packaging, and operational validation    |
| NFR-DX            | Clear local testing commands and diagnostics |
| NFR-DOC           | Traceability and reproducibility reports     |

Exact identifiers and group names must be reconciled against the approved NFR catalog during final review.

## 56. Testing Strategy Acceptance Criteria

The Testing Strategy Architecture may be approved when:

### Testing Foundation

- Framework and application testing responsibilities are separated.
- Unit, contract, integration, E2E, architecture, performance, reliability, and security testing are defined.
- Python and TypeScript testing approaches are identified.
- Optional test dependencies remain separate from production runtime dependencies.
- Reusable fixtures and contract harnesses are defined.
- Test results identify the source and environment.

### Core Runtime and Protocol

- Application bootstrap has executable tests.
- One-shot and persistent CLI modes have tests.
- NDJSON framing and partial reads are tested.
- Concurrent request correlation is tested.
- Error serialization is tested.
- stdout protocol isolation is tested.
- Cancellation and shutdown communication are tested.

### Electron Integration

- Python process startup is tested.
- Handshake and version negotiation are tested.
- Renderer/preload/main communication is tested.
- IPC authorization is tested.
- Renderer reload behavior is tested.
- Multiple-window behavior is tested.
- Python crash handling is tested.
- Packaged Electron startup is tested on supported platforms.

### Connectors

- Common connector contract tests are defined.
- HTTP failures and timeouts are tested.
- WebSocket lifecycle is tested.
- Real subprocess fixtures validate process behavior.
- SQLite uses real temporary databases.
- Filesystem and symlink safety are tested.
- External AI services remain optional for ordinary tests.

### State, Jobs, and Lifecycle

- State scope isolation is tested.
- Concurrent state updates are tested.
- Persistence and restoration are tested.
- Job state transitions are tested.
- Cancellation races are tested.
- Job recovery semantics are tested.
- Partial initialization failures are tested.
- Graceful shutdown and cleanup are tested.
- Resource leak detection is addressed.

### Architecture Tooling

- Scaffold profiles have generation tests.
- Discovery includes source-evidence tests.
- Incremental and full discovery equivalence is tested.
- Architecture rules have positive, negative, and incomplete-evidence fixtures.
- Verification baselines and exceptions are tested.
- Migration transformations have precondition and postcondition tests.
- Migration regression verification is required.
- Partial apply and rollback recovery are tested.

### Quality and Release

- Cross-platform test expectations are established.
- Performance benchmark methodology is defined.
- Provisional coverage targets are identified.
- Security tests cover major trust boundaries.
- Test evidence has a versioned schema.
- CI quality gates distinguish PASS, FAIL, INCOMPLETE, and BLOCKED.
- Missing tests cannot produce false PASS outcomes.
- Release verification includes actual package artifacts.
- Required test results are traceable to source revisions.
- Testing works without an LLM.
- Open decisions are approved or explicitly deferred.

## 57. Final Architecture Summary

AdharaSutra's Testing Strategy provides a reusable, layered quality-engineering foundation for the framework and its consuming applications.

The architecture covers:

- Unit testing.
- Public contract testing.
- Connector integration testing.
- CLI protocol testing.
- Electron integration and E2E testing.
- State consistency and persistence testing.
- Job scheduling and cancellation testing.
- External subprocess lifecycle testing.
- Application configuration and lifecycle testing.
- Architecture discovery and verification testing.
- Project scaffolding testing.
- Migration regression testing.
- Reliability and failure injection.
- Security testing.
- Cross-platform validation.
- Performance and endurance testing.
- Package and release verification.

Testing shall reuse established testing tools instead of implementing a competing general-purpose test runner.

The framework shall provide reusable fixtures, contract tests, and normalized evidence reporting.

Routine tests must remain practical without cloud services, external AI models, or specialized GPU hardware.

Real operating-system and database behavior must still be exercised where mocks cannot establish the required guarantees.

Architecture verification shall consume compatible test evidence without confusing static conformance with runtime correctness.

Migration shall require behavioral regression evidence before declaring affected changes verified.

CI quality gates shall distinguish successful tests, failed tests, unavailable tests, and incomplete validation.

The central guarantee is:

Every critical AdharaSutra capability has an appropriate verification strategy, and every quality claim is supported by identifiable, executed evidence.

## 58. Document Status

Status: Draft — Architecture Planning\
Version: 0.1.0\
Approval: Pending testing architecture review

Next Document: `docs/design/security-and-reliability.md`

The next document should define the framework-wide security and reliability architecture, including trust boundaries, subprocess safety, Electron IPC authorization, credentials, filesystem restrictions, dependency security, failure isolation, availability, recovery, resource exhaustion protection, and operational threat modeling.

AdharaSutra — Build once. Standardize everywhere.

The continuation completes `testing-strategy.md` through Section 58. The next foundational document is `security-and-reliability.md`.