# AdharaSutra — Error Handling and Observability Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/error-handling-and-observability.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Cross-Cutting Infrastructure Architecture  
**Architecture Style:** Structured Errors, Centralized Observability, Explicit Failure Boundaries  
**Primary Language:** Python 3.12+  
**Communication:** Versioned CLI Protocol over stdin/stdout/stderr

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

---

# 1. Purpose

This document defines the proposed Error Handling and Observability Architecture of AdharaSutra.

AdharaSutra manages common runtime infrastructure used by multiple independent applications.

These applications may execute local Python functions, communicate with HTTP services, run external executables, access SQLite databases, and manage long-running jobs.

Failures can occur at any of these boundaries.

The framework must provide a consistent mechanism for identifying, classifying, propagating, recording, and reporting failures.

Observability must make it possible to understand what happened during an application operation, where it failed, which components were involved, and what action may be required.

## 1.1 Objectives

The architecture shall:

1. Establish one framework-wide error taxonomy.
2. Define stable machine-readable error codes.
3. Separate business errors from infrastructure errors.
4. Preserve original exception causes for internal diagnostics.
5. Prevent unhandled request failures from unnecessarily terminating the runtime.
6. Provide consistent error propagation across framework modules.
7. Produce standardized CLI error envelopes.
8. Map Python errors into appropriate Electron-facing errors.
9. Establish centralized structured logging.
10. Separate protocol output from diagnostic output.
11. Support request, job, process, and connector correlation.
12. Expose meaningful runtime health and readiness diagnostics.
13. Support optional metrics and distributed tracing integrations.
14. Protect secrets and sensitive application information.
15. Define logging retention and resource limits.
16. Support development and production diagnostic configurations.
17. Enable error handling to be tested deterministically.
18. Support architecture verification.
19. Support incremental migration of existing logging and error implementations.

## 1.2 Central Principle

**Every failure must have a meaningful classification, an identifiable origin, and an explicit propagation boundary.**

**Every diagnostic record must provide useful context without corrupting application communication or compromising security.**

## 1.3 Non-Goals

The initial architecture does not require:

- A distributed monitoring backend.
- Mandatory cloud telemetry.
- A centralized logging server.
- Automatic uploading of application logs.
- An LLM-based root-cause-analysis system.
- Automatic recovery from every exception.
- Automatic retry of every failed operation.
- Recording every function call.
- Persisting every runtime event.
- Collecting sensitive business payloads by default.
- Replacing application-specific business validation.
- A mandatory OpenTelemetry deployment.

Advanced observability providers may be integrated through optional extensions.

---

# 2. Architecture Principles

## EO-001 — Framework-Owned Technical Error Model

AdharaSutra shall define common error categories and stable technical error codes.

## EO-002 — Application-Owned Domain Errors

Consuming applications shall define business-specific errors and map them through documented framework interfaces.

## EO-003 — Explicit Error Boundaries

Errors shall be translated at clearly defined architectural boundaries.

## EO-004 — Cause Preservation

The framework shall preserve original exception causes for controlled internal diagnostics where available.

## EO-005 — Safe External Representation

Electron-facing error messages shall contain safe, structured information rather than unrestricted Python exceptions or stack traces.

## EO-006 — Failure Isolation

A failure in one action, job, or optional connector shall not unnecessarily terminate unrelated healthy operations.

## EO-007 — Honest Outcome Reporting

The framework shall distinguish confirmed success, confirmed failure, cancellation, timeout, and unknown outcomes.

## EO-008 — Centralized Logging

Framework modules shall use common logging facilities instead of independently configuring competing logging systems.

## EO-009 — Protocol Isolation

Diagnostic logs shall not corrupt the machine-readable CLI protocol stream.

## EO-010 — Correlation

Related requests, jobs, execution attempts, and subprocesses shall be traceable through structured identifiers.

## EO-011 — Sensitive Data Protection

Secrets and sensitive data shall not be indiscriminately included in logs, errors, traces, or diagnostic exports.

## EO-012 — Optional Advanced Observability

Advanced telemetry providers shall remain optional.

## EO-013 — Bounded Resource Usage

Logging queues, retained diagnostics, and event buffers shall have explicit capacity and retention policies.

## EO-014 — Deterministic Testing

Error classification, serialization, and redaction shall be verifiable through automated tests.

## EO-015 — Consistent Cross-Module Semantics

The same technical failure category shall retain consistent meaning across CLI, connectors, state, jobs, and lifecycle components.

## EO-016 — No Silent Failure

Failures shall not be swallowed without an explicitly documented handling or suppression policy.

## EO-017 — No False Recovery Claims

The framework shall not report recovery until the relevant operation or capability has actually reached its required state.

## EO-018 — Local-First Diagnostics

The core observability system shall function without network access or external telemetry services.

---

# 3. High-Level Architecture

## 3.1 Component Diagram

```text
┌─────────────────────────────────────────────────────────┐
│                 CONSUMING APPLICATION                   │
│                                                         │
│ Domain Errors                                           │
│ Business Validation                                     │
│ Application Diagnostics                                 │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   ADHARASUTRA RUNTIME                   │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              ERROR INFRASTRUCTURE                │  │
│  │                                                   │  │
│  │ Error Taxonomy                                    │  │
│  │ Error Registry                                    │  │
│  │ Exception Mapping                                 │  │
│  │ Error Boundaries                                  │  │
│  │ Safe Serialization                                │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │             OBSERVABILITY SERVICES              │  │
│  │                                                   │  │
│  │ Structured Logging                               │  │
│  │ Correlation Context                              │  │
│  │ Health and Readiness                              │  │
│  │ Runtime Diagnostics                              │  │
│  │ Optional Metrics and Traces                      │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│          ┌───────────────┼────────────────┐             │
│          ▼               ▼                ▼             │
│       CLI Router      Connectors        Jobs            │
│          │               │                │             │
│          └───────────────┼────────────────┘             │
│                          │                              │
│             ┌────────────┴────────────┐                 │
│             ▼                         ▼                 │
│      Protocol Responses         Diagnostic Sinks        │
└─────────────┬──────────────────────────┬────────────────┘
              │                          │
              ▼                          ▼
       stdout / NDJSON            stderr / Log Files
              │                          │
              ▼                          ▼
       Electron Bridge            Controlled Diagnostics
```

## 3.2 Primary Architectural Separation

The design separates three concepts:

**Errors** represent failed operations or invalid conditions.

**Logs** record diagnostic information about what happened.

**Telemetry** summarizes or traces runtime behavior.

A single failure may produce an error response, a structured log entry, and an optional metric.

These outputs serve different purposes and must not be treated as interchangeable.

---

# 4. Proposed Module Structure

```text
src/adharasutra/
│
├── core/
│   └── errors/
│       ├── __init__.py
│       ├── base.py
│       ├── categories.py
│       ├── codes.py
│       ├── registry.py
│       ├── mapping.py
│       ├── serialization.py
│       └── boundaries.py
│
├── observability/
│   ├── __init__.py
│   ├── contracts.py
│   ├── configuration.py
│   │
│   ├── logging/
│   │   ├── logger.py
│   │   ├── records.py
│   │   ├── formatting.py
│   │   ├── sinks.py
│   │   ├── filters.py
│   │   └── redaction.py
│   │
│   ├── correlation/
│   │   ├── context.py
│   │   ├── propagation.py
│   │   └── identifiers.py
│   │
│   ├── diagnostics/
│   │   ├── collector.py
│   │   ├── runtime.py
│   │   ├── connectors.py
│   │   ├── jobs.py
│   │   └── export.py
│   │
│   ├── health/
│   │   ├── models.py
│   │   ├── registry.py
│   │   └── checks.py
│   │
│   └── telemetry/
│       ├── metrics.py
│       ├── tracing.py
│       └── exporters.py
│
└── cli/
    └── protocol/
        └── errors.py
```

This is a proposed logical organization.

The initial implementation may consolidate these modules to avoid unnecessary complexity.

## 4.1 Dependency Constraints

The core error model must remain lightweight.

It must not require:

- Electron.
- HTTPX.
- SQLite.
- External process libraries.
- Cloud monitoring clients.
- Architecture analysis tools.
- Application domain modules.

The observability subsystem may depend on core contracts but must not introduce circular dependencies into the runtime.

---

# 5. Framework Error Taxonomy

## 5.1 Purpose

AdharaSutra shall provide a common classification system for technical errors.

An error category describes the general kind of failure.

An error code identifies a specific failure contract.

## 5.2 Primary Error Categories

| Category | Description |
|---|---|
| Protocol | Invalid or incompatible communication |
| Validation | Invalid input or schema |
| Configuration | Invalid or unavailable settings |
| Lifecycle | Startup, readiness, or shutdown failures |
| Runtime | Application execution infrastructure failure |
| Action | Routing or action execution failure |
| Connector | External infrastructure communication failure |
| Process | Operating-system subprocess failure |
| Persistence | Database or state-storage failure |
| State | Managed state access or mutation failure |
| Job | Job execution or scheduling failure |
| Cancellation | Unsupported or unsuccessful cancellation |
| Timeout | Execution deadline exceeded |
| Security | Authorization or access-policy violation |
| Resource | Capacity or resource exhaustion |
| Internal | Unexpected framework failure |

## 5.3 Domain Error Categories

Applications may define their own domain errors.

Examples:

```text
VOICE_PROFILE_NOT_FOUND
AUDIO_FORMAT_UNSUPPORTED
IMAGE_WORKFLOW_INVALID
PROJECT_ALREADY_EXISTS
```

These errors shall use the shared error envelope when exposed through the CLI protocol.

## 5.4 Stable Error Codes

Public error codes must be stable within the applicable compatibility contract.

An existing code must not silently change to represent a materially different failure condition.

## 5.5 Error Identifier Convention

Proposed format:

`CATEGORY_SPECIFIC_CONDITION`

Examples:

```text
PROTOCOL_UNSUPPORTED_VERSION
CONFIG_VALIDATION_FAILED
CONNECTOR_UNAVAILABLE
PROCESS_START_FAILED
STATE_VERSION_CONFLICT
JOB_QUEUE_FULL
LIFECYCLE_INITIALIZATION_FAILED
```

## 5.6 Error Catalog Governance

A central error catalog shall define:

- Code.
- Category.
- Description.
- Typical origin.
- Retryability guidance.
- Exposure policy.
- Relevant protocol status.
- Compatibility notes.

Existing error codes introduced in earlier design documents must be reconciled into this catalog before final approval.

---

# 6. Framework Error Model

## 6.1 Purpose

The common error model represents classified failures without requiring callers to understand underlying implementation exceptions.

## 6.2 Proposed Error Fields

| Field | Description |
|---|---|
| `code` | Stable error identifier |
| `category` | General error category |
| `message` | Safe human-readable explanation |
| `retryable` | True, false, or unknown |
| `details` | Optional safe structured metadata |
| `correlation_id` | Relevant execution correlation |
| `cause` | Internal original exception reference |
| `severity` | Diagnostic impact classification |

Not all fields are required in the public protocol representation.

The internal error model may contain richer diagnostic information.

## 6.3 Conceptual Python Model

```python
from enum import StrEnum


class ErrorCategory(StrEnum):
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    CONNECTOR = "connector"
    PROCESS = "process"
    PERSISTENCE = "persistence"
    JOB = "job"
    INTERNAL = "internal"


class FrameworkError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        category: ErrorCategory,
        retryable: bool | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)

        self.code = code
        self.category = category
        self.retryable = retryable
        self.details = details or {}
```

This example illustrates the proposed error structure.

The final API must define immutable error metadata, safe serialization, and cause preservation.

## 6.4 Exception Cause

Python exception chaining should be preserved where appropriate.

Conceptual example:

```python
try:
    await connector.connect()
except ConnectionError as exc:
    raise FrameworkError(
        code="CONNECTOR_UNAVAILABLE",
        message="External service is unavailable",
        category=ErrorCategory.CONNECTOR,
        retryable=True,
    ) from exc
```

The original exception is available for controlled internal diagnostics.

It is not automatically serialized to Electron.

## 6.5 Immutable Error Identity

Once classified, an error's code and category should not change arbitrarily as it propagates.

Higher layers may map it into a distinct domain or protocol error when justified by an explicit boundary contract.

---

# 7. Error Propagation Architecture

## 7.1 Propagation Principle

Errors should propagate through defined boundaries until an appropriate component can handle or translate them.

## 7.2 Propagation Flow

```text
External Dependency
        │
        ▼
Low-Level Exception
        │
        ▼
Connector Error Mapping
        │
        ▼
Application Adapter
        │
        ▼
Application Use Case
        │
        ▼
Action Execution Boundary
        │
        ▼
Framework Error Normalization
        │
        ▼
CLI Error Envelope
        │
        ▼
Electron Bridge
        │
        ▼
Application UI
```

Not every error must pass through every layer.

For example, an invalid request can fail at protocol validation before any application handler executes.

## 7.3 Handling Versus Translation

**Handling** means a component resolves the failure or applies a documented recovery policy.

**Translation** means a component converts a failure into a representation appropriate to another boundary.

Translating an error does not mean the underlying failure was recovered.

## 7.4 Error Ownership

| Layer | Error responsibility |
|---|---|
| Domain | Business-rule and invariant errors |
| Application | Business error interpretation |
| Adapter | External service-specific translation |
| Connector | Technical transport and resource failures |
| Job Manager | Execution lifecycle failure classification |
| Lifecycle Manager | Initialization and shutdown failures |
| CLI Runtime | Standard error response |
| Electron Bridge | Typed remote and transport errors |
| Renderer | User-facing presentation |

---

# 8. Error Handling Boundaries

## 8.1 Protocol Boundary

Invalid envelopes, unsupported versions, or malformed messages shall fail before application action execution.

## 8.2 Action Boundary

Registered action execution shall have a framework-controlled exception boundary.

Expected application exceptions should not automatically terminate the persistent runtime.

## 8.3 Connector Boundary

Connector implementations shall translate low-level technical failures into standard connector errors.

## 8.4 Job Boundary

Job failures shall update job lifecycle state and publish the relevant terminal outcome.

They shall not be represented as successful job completion.

## 8.5 Lifecycle Boundary

Startup and shutdown failures shall be handled by the lifecycle manager.

Fatal initialization failures prevent readiness.

## 8.6 Persistence Boundary

Database and state-storage failures shall preserve transaction and durability semantics.

A failed write must not be reported as successfully committed.

## 8.7 Security Boundary

Security and authorization failures shall be reported without exposing sensitive validation details that would weaken the boundary.

---

# 9. Expected Versus Unexpected Errors

## 9.1 Expected Errors

Expected errors are anticipated failures defined by application or framework contracts.

Examples:

- Invalid payload.
- Missing configuration.
- Required file not found.
- External service unavailable.
- Job cancellation unsupported.
- SQLite database busy.

These should be converted into classified errors.

## 9.2 Unexpected Errors

Unexpected errors are failures not covered by known handling paths.

Examples:

- Invalid internal assumptions.
- Unhandled programming exceptions.
- Corrupted framework invariants.
- Unexpected execution-state transitions.

## 9.3 Handling Policy

Unexpected exceptions at a request boundary should normally be converted into a safe internal error response when runtime integrity remains intact.

The complete exception may be logged internally.

## 9.4 Fatal Failures

Some failures invalidate runtime integrity.

Examples may include:

- Unrecoverable protocol transport corruption.
- Critical lifecycle corruption.
- Failure of indispensable runtime infrastructure.
- An unexpected state that prevents safe continuation.

These may require controlled shutdown.

## 9.5 Never Hide Unexpected Exceptions

Unexpected errors must not be silently converted into success or default business values.

---

# 10. Error Severity

## 10.1 Purpose

Severity describes diagnostic impact.

It is separate from error category.

## 10.2 Proposed Levels

| Severity | Meaning |
|---|---|
| Debug | Detailed diagnostic condition |
| Info | Expected operation or state information |
| Warning | Degradation or recoverable issue |
| Error | Operation failure |
| Critical | Failure threatening application availability or integrity |

## 10.3 Severity Versus Business Result

Not every business error requires ERROR-level logging.

For example, a user submitting invalid input may be an expected validation outcome.

## 10.4 Severity Rules

The severity must reflect actual operational impact.

The framework should avoid classifying ordinary expected cancellations as critical failures.

---

# 11. Retryability and Outcome Classification

## 11.1 Retryability

Retryability shall be represented as:

- `true` — Retrying is considered safe under the documented conditions.
- `false` — Retrying is not appropriate under the current contract.
- `null` — Retry safety is unknown.

## 11.2 Retry Safety

A temporary network failure does not universally imply that retrying an operation is safe.

The remote operation may already have executed.

## 11.3 Outcome Categories

The framework must distinguish:

- Confirmed success.
- Confirmed failure.
- Cancellation requested.
- Confirmed cancellation.
- Timeout.
- Interrupted execution.
- Unknown outcome.

## 11.4 Unknown Outcomes

When an action's result cannot be established, the framework shall preserve that uncertainty.

It must not mark the operation failed merely because the response was lost.

## 11.5 Retry Ownership

The framework may implement technical retry mechanisms.

The consuming application determines domain-level retry eligibility and idempotency requirements.

## 11.6 Diagnostic Information

Errors may include safe retry metadata, but frontend consumers must not assume `retryable: true` means automatic retry is always desirable.

---

# 12. Standard CLI Error Serialization

## 12.1 Protocol Ownership

The CLI protocol defines the externally visible error envelope.

The Error Infrastructure supplies the classified failure information used by the serializer.

## 12.2 Example

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-001",
  "success": false,
  "data": null,
  "error": {
    "code": "CONNECTOR_UNAVAILABLE",
    "message": "The required external service is unavailable",
    "retryable": true,
    "details": {
      "connector": "comfyui"
    }
  }
}
```

## 12.3 Protocol Compatibility

The public protocol error structure shall remain consistent with `cli-protocol.md`.

Additional internal error fields shall not automatically become mandatory public protocol fields.

## 12.4 Safe Serialization

The serializer shall:

1. Validate the error code.
2. Produce a safe message.
3. Include only approved details.
4. Preserve request correlation.
5. Remove sensitive internal context.
6. Produce valid JSON.
7. Avoid serializing arbitrary exception objects.

## 12.5 Serialization Failure

If an exception cannot be serialized normally, the runtime shall attempt to produce a minimal safe internal-error response where the transport remains functional.

A failed serializer must not recursively attempt unlimited error serialization.

## 12.6 Terminal Response Guarantee

For an accepted request, the framework shall attempt to produce one terminal response.

A process crash or broken transport may prevent delivery.

---

# 13. Electron Error Integration

## 13.1 Purpose

The shared Electron bridge shall expose typed errors while preserving the distinction between Python application failures and communication failures.

## 13.2 Error Categories

The TypeScript bridge should distinguish:

- Remote application error.
- Protocol error.
- Transport error.
- Process startup error.
- Process termination error.
- Client timeout.
- Cancellation outcome.
- Compatibility error.

## 13.3 Conceptual TypeScript Error

```typescript
interface BridgeErrorInfo {
  code: string;
  message: string;
  category: string;
  retryable: boolean | null;
  requestId?: string;
  details?: Record<string, unknown>;
}
```

This is a conceptual type.

The exact TypeScript contract will be finalized with the bridge implementation.

## 13.4 Remote Errors

A valid failed Python response should become a typed remote error.

## 13.5 Transport Errors

A broken pipe or unexpected Python process exit must remain distinguishable from a normal business error.

## 13.6 Unknown Execution Status

If the Python process terminates before returning a response, Electron must not assume the business operation failed without side effects.

## 13.7 UI Presentation

The consuming application decides how errors are displayed.

Examples:

- Inline validation message.
- Nonblocking notification.
- Retry prompt.
- Dependency-unavailable status.
- Fatal backend error screen.

The framework does not own application-specific UI wording or interaction design.

---

# 14. Centralized Logging Architecture

## 14.1 Purpose

AdharaSutra shall provide consistent structured logging for framework and consuming application components.

## 14.2 Logging Responsibilities

The framework shall manage:

- Logger configuration.
- Structured records.
- Log levels.
- Output destinations.
- Correlation metadata.
- Sensitive-value filtering.
- Resource limits.
- Retention policies.
- Diagnostic export.

## 14.3 Recommended Implementation

Use Python's standard `logging` infrastructure as the initial foundation.

Structured JSON formatting and advanced sinks may be implemented through small adapters or optional dependencies.

This avoids making a heavyweight observability library mandatory.

## 14.4 Logger Namespaces

Logger names should identify module ownership.

Examples:

```text
adharasutra.core
adharasutra.cli
adharasutra.connectors.http
adharasutra.connectors.process
adharasutra.jobs
adharasutra.state

application.vani
application.vani.audio
application.vani.persistence
```

## 14.5 Application Logging

Applications shall be able to acquire framework-configured loggers.

They should not need to recreate logging configuration independently.

## 14.6 Configuration Ownership

The application configuration may select log level, output sinks, formatting, and retention within the framework's supported policies.

---

# 15. Structured Log Schema

## 15.1 Purpose

Structured records enable consistent filtering, searching, debugging, and automated diagnostic analysis.

## 15.2 Required Fields

A structured log record should contain:

| Field | Meaning |
|---|---|
| `timestamp` | Event timestamp |
| `level` | Logging severity |
| `logger` | Originating logger |
| `message` | Human-readable diagnostic |
| `application` | Application identifier |
| `component` | Framework or application component |

## 15.3 Optional Correlation Fields

Additional fields may include:

- Request ID.
- Session ID.
- Job ID.
- Execution attempt ID.
- Process execution ID.
- Connector ID.
- Action identifier.
- Error code.
- Duration.
- Lifecycle phase.

## 15.4 Example

```json
{
  "timestamp": "2026-11-11T10:30:00.000Z",
  "level": "ERROR",
  "logger": "adharasutra.connectors.http",
  "application": "vani",
  "component": "http",
  "message": "External service request failed",
  "request_id": "req-001",
  "connector_id": "lmstudio",
  "error_code": "CONNECTOR_UNAVAILABLE",
  "duration_ms": 1200
}
```

This is an illustrative log record, not an actual runtime event.

## 15.5 Timestamp Policy

Timestamps should use a standardized representation.

**Proposed default:** ISO 8601 UTC timestamps.

Local timezone presentation belongs to the consuming UI or diagnostic viewer.

## 15.6 Schema Versioning

Machine-readable log formats should identify their schema version where compatibility with external analysis tools is required.

---

# 16. Logging Levels and Policies

## 16.1 Logging Levels

The framework shall support:

- DEBUG.
- INFO.
- WARNING.
- ERROR.
- CRITICAL.

## 16.2 Default Logging

**Proposed policy:**

Development:

- INFO by default.
- DEBUG when explicitly enabled.

Production:

- INFO or WARNING based on application needs.
- Sensitive payload logging disabled by default.

## 16.3 DEBUG Logging

DEBUG should provide detailed diagnostic context without indiscriminately recording credentials or sensitive business inputs.

## 16.4 Expected Validation Errors

Expected invalid user input does not necessarily require ERROR-level logging.

## 16.5 Repeated Failures

High-frequency repeated failures should not overwhelm log storage.

The framework may support rate limiting or aggregation.

## 16.6 Exception Logging

Unexpected exceptions should include controlled internal stack traces when enabled.

Electron-facing errors must not include unrestricted traces.

---

# 17. Logging Destinations

## 17.1 Supported Destinations

The initial framework should support:

- stderr.
- Rotating local log files.
- Test capture handlers.

Optional destinations may include:

- System logging facilities.
- External telemetry exporters.
- Application-specific sinks.

## 17.2 stdout Restriction

When the AdharaSutra machine-readable CLI protocol is active, stdout is reserved for valid protocol messages.

Normal application logging must not write to stdout.

## 17.3 stderr

stderr is the default diagnostic channel for CLI applications.

It may contain structured logs or configured human-readable diagnostic text.

## 17.4 Log Files

Persistent applications may write logs to configured application log directories.

## 17.5 Multiple Sinks

The logging subsystem may send records to multiple configured destinations.

For example:

```text
Structured Log Record
        │
        ▼
Logging Pipeline
        │
        ├── stderr
        ├── Rotating File
        └── Optional Telemetry Sink
```

## 17.6 Sink Failure

Failure of an optional logging destination should not automatically terminate the application.

Required audit or compliance logging, if introduced later, may have stricter failure policies.

## 17.7 Log Directory

The filesystem subsystem shall resolve appropriate application log locations.

---

# 18. Logging Resource Management

## 18.1 Bounded Logging

Logging infrastructure must avoid unbounded memory and disk growth.

## 18.2 Queue Limits

Asynchronous logging queues shall have configurable limits.

## 18.3 Backpressure

When logging output is slower than log production, the framework must apply a documented overload policy.

## 18.4 Priority Preservation

Critical diagnostic records should be preserved where feasible.

Low-priority repetitive logs may be dropped or aggregated under overload.

## 18.5 Log Retention

Retention may be configured using:

- Maximum file size.
- Maximum number of files.
- Maximum age.
- Total storage budget.

## 18.6 Cleanup

Logging handlers and resources shall be flushed and closed during graceful shutdown.

## 18.7 Abrupt Termination

The framework cannot guarantee that buffered logs survive abrupt operating-system termination.

## 18.8 Log Loss Diagnostics

When log records are dropped due to capacity limits, the framework should expose diagnostic counters.

---

# 19. Correlation Architecture

## 19.1 Purpose

Correlation links related operations across framework modules.

It enables developers to follow an execution from Electron through the CLI protocol to application use cases and external dependencies.

## 19.2 Correlation Hierarchy

```text
Electron Request ID
        │
        ▼
CLI Request ID
        │
        ▼
Application Action
        │
        ├── Connector Operation
        │
        └── Job ID
               │
               ▼
        Execution Attempt ID
               │
               ▼
        Process Execution ID
               │
               ▼
        External Dependency
```

## 19.3 Identifier Responsibilities

| Identifier | Purpose |
|---|---|
| Request ID | One protocol request |
| Session ID | One persistent communication session |
| Job ID | Managed job identity |
| Attempt ID | Individual job execution attempt |
| Process execution ID | Framework-managed subprocess invocation |
| Connector ID | Registered connector instance |
| Correlation ID | Optional broader logical operation |

## 19.4 Identifier Uniqueness

Identifiers must follow documented uniqueness rules for their scopes.

They must not be treated as authentication credentials.

## 19.5 Correlation Propagation

The framework shall propagate appropriate correlation metadata through:

- Action execution.
- Async tasks.
- Job submission.
- Connector calls.
- Process execution.
- Error handling.
- Logging.

## 19.6 Async Context

Python `contextvars` is a candidate mechanism for request-level correlation.

The design must account for how context is copied into background tasks.

## 19.7 Thread and Process Boundaries

Correlation metadata does not automatically propagate into arbitrary threads or subprocesses.

The framework shall explicitly propagate supported identifiers where required.

## 19.8 External Systems

External APIs may support correlation headers or request identifiers.

These should be used only where appropriate and permitted by the external service contract.

---

# 20. Tracing Architecture

## 20.1 Purpose

Tracing describes the sequence and timing of operations.

## 20.2 Initial Tracing

The initial framework should provide lightweight correlation and duration measurement through structured logs.

## 20.3 Optional Advanced Tracing

Advanced tracing may be integrated through optional adapters.

OpenTelemetry is a potential implementation option, not a mandatory dependency.

## 20.4 Trace Boundaries

Potential spans include:

- CLI request.
- Action dispatch.
- Application use case.
- Connector operation.
- Job execution.
- External process.
- Persistence transaction.

## 20.5 Performance

Tracing must not introduce disproportionate overhead.

Sampling or selective instrumentation may be required.

## 20.6 Sensitive Attributes

Trace metadata must not indiscriminately include request bodies, secrets, model prompts, or generated content.

---

# 21. Metrics Architecture

## 21.1 Purpose

Metrics summarize framework behavior over time.

## 21.2 Initial Requirements

The framework should expose lightweight counters and durations through diagnostics.

A metrics server is not required.

## 21.3 Proposed Metrics

| Metric | Meaning |
|---|---|
| `runtime_requests_total` | Total handled requests |
| `runtime_request_errors_total` | Failed requests |
| `runtime_request_duration_ms` | Request duration |
| `jobs_active` | Active managed jobs |
| `jobs_pending` | Pending jobs |
| `jobs_failed_total` | Failed jobs |
| `connector_errors_total` | Connector failures |
| `processes_active` | Active managed subprocesses |
| `process_execution_duration_ms` | Subprocess execution duration |
| `logging_records_dropped_total` | Dropped log records |

These names are illustrative.

## 21.4 Metric Dimensions

Metric dimensions must be controlled to prevent unbounded cardinality.

Arbitrary request IDs, job IDs, filenames, or user-provided strings should not be used as unrestricted metric labels.

## 21.5 Exporting

Optional exporters may support local collection or external monitoring systems.

## 21.6 Privacy

Metrics should avoid collecting unnecessary user content.

---

# 22. Health and Readiness Architecture

## 22.1 Distinction

Health and readiness shall remain separate.

**Health** describes operational condition.

**Readiness** describes whether an operation or capability can accept work.

## 22.2 Health Categories

Proposed statuses:

- Healthy.
- Degraded.
- Unavailable.
- Unknown.
- Not checked.

## 22.3 Runtime Readiness

Runtime readiness is established through required configuration, lifecycle, and protocol initialization.

## 22.4 Connector Health

Connector health may depend on remote service checks.

A connector can be initialized while its remote dependency remains unavailable.

## 22.5 Capability Readiness

Applications may expose capability-level readiness.

Example:

```json
{
  "application": "vani",
  "runtime": "ready",
  "capabilities": {
    "voice_generation": "ready",
    "source_separation": "degraded",
    "project_management": "ready"
  }
}
```

## 22.6 Health Checks

Health checks may be:

- Local and synchronous.
- Asynchronous.
- On demand.
- Periodic when enabled.

## 22.7 Health Check Safety

Health checks must not unexpectedly execute expensive business operations or create unwanted side effects.

## 22.8 Health Result Freshness

Health reports should distinguish the time of the last check from the time the result was requested.

## 22.9 CLI Integration

The reserved `system.health` action shall expose approved health information using the versioned CLI protocol.

---

# 23. Diagnostic Reporting Architecture

## 23.1 Purpose

Diagnostics provide an actionable representation of runtime and configuration state.

## 23.2 Diagnostic Categories

The framework should support diagnostics for:

- Application identity and version.
- Runtime lifecycle state.
- Python environment.
- Operating system.
- CLI protocol compatibility.
- Required connectors.
- Optional connector health.
- Registered services.
- State facilities.
- Job execution.
- Managed processes.
- Configuration validation.
- Recent categorized failures.

## 23.3 Diagnostic Levels

Potential diagnostic modes:

### Summary

Provides high-level component readiness and recent failures.

### Detailed

Provides component-specific information and bounded recent history.

### Support Export

Produces a redacted diagnostic artifact suitable for manual inspection or support workflows.

## 23.4 Example Diagnostic Summary

```json
{
  "application": "example-app",
  "framework_version": "0.1.0",
  "protocol_version": "1.0",
  "runtime": {
    "status": "running",
    "ready": true
  },
  "jobs": {
    "active": 2,
    "pending": 1
  },
  "connectors": {
    "sqlite": "healthy",
    "comfyui": "unavailable"
  }
}
```

This is illustrative rather than a verified runtime report.

## 23.5 Report Safety

Diagnostic exports shall omit or redact secrets.

## 23.6 Diagnostic Completeness

A diagnostic report must distinguish information that was checked from information that was unavailable or not checked.

## 23.7 Source and Runtime Evidence

Runtime diagnostics describe observed runtime conditions.

Architecture verification reports describe source-code or test evidence.

One must not be presented as proof of the other.

---

# 24. Sensitive Data Redaction

## 24.1 Purpose

The observability system shall reduce accidental disclosure of secrets and sensitive information.

## 24.2 Sensitive Data Categories

Examples include:

- Access tokens.
- Passwords.
- API keys.
- Authentication headers.
- Private credentials.
- User-provided confidential content.
- Sensitive environment variables.
- Secret configuration fields.

## 24.3 Redaction Strategy

The framework should support:

1. Schema-aware sensitive fields.
2. Explicit redaction markers.
3. Known sensitive header filtering.
4. Structured record filtering.
5. Safe exception formatting.
6. Sanitized diagnostic exports.

## 24.4 Structured Redaction

Redaction should occur before records reach external logging sinks.

## 24.5 Default Payload Policy

Raw application payloads shall not be logged by default.

## 24.6 Exception Messages

Underlying exception messages may contain secrets or sensitive paths.

They must not be assumed safe for external disclosure.

## 24.7 Redaction Limitations

Pattern-based redaction cannot guarantee removal of every sensitive value from arbitrary text.

The preferred strategy is to avoid collecting unnecessary sensitive content in the first place.

## 24.8 Test Requirements

The framework shall test redaction using representative secret formats and nested structured records.

---

# 25. Framework-Wide Error Scenarios

## 25.1 Configuration Failure

```text
Application Startup
        │
        ▼
Configuration Validation
        │
        ▼
Missing Required Setting
        │
        ▼
CONFIG_REQUIRED_VALUE_MISSING
        │
        ▼
Lifecycle Startup Failure
        │
        ▼
Safe Diagnostic
```

The application shall not report readiness if required configuration validation fails.

## 25.2 HTTP Dependency Failure

```text
Application Action
        │
        ▼
HTTP Connector
        │
        ▼
Connection Refused
        │
        ▼
CONNECTOR_UNAVAILABLE
        │
        ▼
Application Error Mapping
        │
        ▼
CLI Error Response
```

The runtime may remain operational if the affected capability is not globally critical.

## 25.3 External CLI Crash

```text
Managed Job
        │
        ▼
Process Connector
        │
        ▼
Unexpected Exit
        │
        ▼
PROCESS_EXECUTION_FAILED
        │
        ▼
Job FAILED
        │
        ▼
job.failed Event
```

The application may additionally validate outputs and provide a more specific business error.

## 25.4 SQLite Transaction Failure

```text
Application Repository
        │
        ▼
SQLite Connector
        │
        ▼
Transaction Failure
        │
        ▼
Rollback According to Contract
        │
        ▼
PERSISTENCE_TRANSACTION_FAILED
        │
        ▼
Application Error
```

The framework must not report successful persistence unless the required commit guarantee was satisfied.

## 25.5 Python Runtime Crash

```text
Electron Bridge
        │
        ▼
Python Process Exits Unexpectedly
        │
        ▼
Pending Requests Invalidated
        │
        ▼
Transport Error
        │
        ▼
Unknown Business Outcome
```

The bridge must preserve uncertainty where a side-effecting action may have executed.

---

# 26. Error Handling and Job Integration

## 26.1 Job Execution Failure

A failed job shall record:

- Job ID.
- Attempt ID.
- Failure category.
- Error code.
- Safe message.
- Relevant diagnostics.
- Terminal execution state.

## 26.2 Job Versus Request Error

A job-submission request may succeed while the job subsequently fails.

These outcomes must remain separate.

## 26.3 Job Cancellation

A cancellation request may be acknowledged without confirmed termination.

## 26.4 Interrupted Jobs

An interrupted job has lost execution continuity or ownership without a confirmed successful outcome.

It must not be silently classified as completed.

## 26.5 Retry Attempts

Each retry attempt should retain its own diagnostic context.

## 26.6 Job Failure Events

The framework shall publish terminal job failure events through the event subsystem.

## 26.7 Progress Logs

Progress events are not interchangeable with diagnostic logs.

Progress describes work status for consumers.

Logs describe technical observations.

---

# 27. Error Handling and Connector Integration

## 27.1 HTTP Errors

The HTTP connector shall distinguish:

- DNS or connection failure.
- Connection timeout.
- Read timeout.
- HTTP response status.
- Protocol failure.
- Authentication failure.
- Cancellation.

An HTTP response with a non-success status is not necessarily a transport failure.

## 27.2 WebSocket Errors

The WebSocket connector shall distinguish:

- Connection failure.
- Protocol failure.
- Unexpected closure.
- Timeout.
- Reconnection failure.

## 27.3 Process Errors

The process connector shall distinguish:

- Executable missing.
- Permission denied.
- Startup failure.
- Nonzero exit.
- Timeout.
- Termination failure.
- Output limit exceeded.

## 27.4 SQLite Errors

The SQLite connector shall distinguish:

- Connection failure.
- Busy or locked database.
- Transaction failure.
- Constraint violation.
- Schema incompatibility.
- Storage corruption where detectable.

## 27.5 Filesystem Errors

Filesystem facilities shall distinguish:

- File not found.
- Permission denied.
- Invalid path.
- Access boundary violation.
- Storage unavailable.
- Resource exhaustion.

## 27.6 Application Mapping

Service-specific adapters may map technical failures into domain errors while retaining the underlying technical cause internally.

---

# 28. Lifecycle and Failure Recovery

## 28.1 Startup Failures

Startup failures shall preserve:

- Failed phase.
- Failed component.
- Primary error.
- Successfully initialized components.
- Cleanup results.

## 28.2 Cleanup Failures

A cleanup failure shall not erase the original startup or execution failure.

## 28.3 Optional Connector Failure

Failure of an optional connector may degrade a capability without terminating unrelated runtime services.

## 28.4 Fatal Runtime Failure

A fatal runtime failure may trigger coordinated shutdown.

## 28.5 Recovery Evidence

Recovery is confirmed only when required post-recovery checks succeed.

## 28.6 Restart

A restarted Python process creates a new runtime identity and session.

The framework must not claim the previous in-memory execution state survived.

---

# 29. Logging Configuration

## 29.1 Example Configuration

```yaml
observability:
  logging:
    enabled: true
    level: INFO
    format: json

    sinks:
      stderr:
        enabled: true

      file:
        enabled: true
        directory: application_logs
        max_size_mb: 10
        max_files: 5

    redaction:
      enabled: true
      sensitive_fields:
        - password
        - token
        - api_key

  metrics:
    enabled: false

  tracing:
    enabled: false
```

This configuration is illustrative.

The final schema will be aligned with the Configuration subsystem.

## 29.2 Optional Telemetry

Metrics and tracing are disabled unless explicitly configured.

## 29.3 Environment Overrides

Supported logging settings may be changed through trusted configuration sources.

## 29.4 Dynamic Log Levels

Temporary runtime adjustment of log levels may be supported through an authorized diagnostic action.

It is not required in the initial implementation.

---

# 30. Developer Diagnostics

## 30.1 Purpose

Developers require actionable diagnostics when applications fail during development.

## 30.2 Diagnostic Features

The framework should support:

- Detailed initialization errors.
- Missing dependency reports.
- Connector configuration summaries.
- Process executable discovery failures.
- Protocol mismatch explanations.
- Job failure context.
- Recent categorized errors.
- Safe runtime state summaries.

## 30.3 Proposed Developer Commands

```bash
adhara doctor ./my-application

adhara inspect ./my-application

adhara verify ./my-application
```

These commands are proposed development interfaces, not existing functionality.

## 30.4 Distinction Between Commands

`doctor` focuses on configuration and operational environment diagnostics.

`inspect` focuses on discovering implementation structure.

`verify` evaluates architecture conformance.

The tools should share evidence where appropriate without conflating their responsibilities.

---

# 31. Observability Testing Strategy

## 31.1 Error Model Tests

Verify:

- Error categories.
- Stable codes.
- Cause chaining.
- Error metadata.
- Safe serialization.
- Unknown error handling.

## 31.2 Error Boundary Tests

Verify:

- Domain error propagation.
- Connector error mapping.
- Request exception isolation.
- Job failure classification.
- Lifecycle startup errors.
- Cleanup failure preservation.

## 31.3 CLI Protocol Tests

Verify:

- Failed response envelopes.
- Request correlation.
- Unsupported versions.
- Malformed messages.
- No ordinary logs on protocol stdout.
- Terminal response invariants.

## 31.4 Logging Tests

Verify:

- Log levels.
- Structured formatting.
- Timestamp formatting.
- Sink selection.
- Log rotation.
- Queue capacity.
- Shutdown flushing.

## 31.5 Redaction Tests

Verify:

- Authentication headers.
- Secret configuration fields.
- Nested sensitive values.
- Exception text.
- Diagnostic exports.
- Application-defined sensitive fields.

## 31.6 Correlation Tests

Verify:

- Request correlation.
- Async task propagation.
- Thread context propagation where supported.
- Job correlation.
- Execution-attempt identifiers.
- Connector operation correlation.
- Process execution identifiers.

## 31.7 Failure Injection

Simulate:

- HTTP service unavailable.
- External executable crash.
- SQLite transaction error.
- Logging sink unavailable.
- Queue overflow.
- Python process crash.
- Invalid configuration.
- Cleanup failure.
- Event delivery failure.

## 31.8 Health Tests

Verify:

- Runtime readiness.
- Connector health.
- Optional dependency degradation.
- Health-check timeout.
- Stale health information.

## 31.9 Performance Tests

Verify that logging and diagnostic instrumentation do not violate approved resource and latency requirements.

---

# 32. Architecture Verification Rules

The architecture verifier should enforce relevant error-handling and observability conventions.

| Rule ID | Description |
|---|---|
| EO-VER-001 | Application uses approved framework error contracts at integration boundaries |
| EO-VER-002 | Framework errors use registered error codes |
| EO-VER-003 | Domain code does not depend on CLI error serialization |
| EO-VER-004 | Connector implementations map technical failures consistently |
| EO-VER-005 | CLI failures use standard error envelopes |
| EO-VER-006 | Protocol stdout is not used for ordinary diagnostic logging |
| EO-VER-007 | Framework modules use approved logging facilities |
| EO-VER-008 | Sensitive configuration fields are excluded from unrestricted logs |
| EO-VER-009 | Request and job correlation is supported |
| EO-VER-010 | Unexpected action exceptions are handled at framework boundaries |
| EO-VER-011 | Cleanup failures preserve original failure information |
| EO-VER-012 | Optional telemetry dependencies do not leak into the core runtime |
| EO-VER-013 | Log retention and resource limits are configured where required |
| EO-VER-014 | Framework health and readiness semantics remain distinct |
| EO-VER-015 | Diagnostics distinguish checked and unchecked conditions |
| EO-VER-016 | Error-handling test coverage meets applicable requirements |
| EO-VER-017 | Raw exception details are not exposed through public error serialization |
| EO-VER-018 | Production diagnostic configuration follows security policy |
| EO-VER-019 | Error and observability modules follow approved dependency boundaries |
| EO-VER-020 | Architecture exceptions are documented |

## 32.1 Verification Limitations

Static analysis cannot prove that secrets are never emitted by arbitrary third-party libraries.

It also cannot prove that all failure paths produce correct cleanup.

Runtime tests and controlled integration tests are required.

## 32.2 Verification Outcomes

Supported outcomes:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

---

# 33. Migration from Existing Applications

## 33.1 Purpose

Existing applications may contain:

- Custom exception classes.
- Inconsistent error codes.
- Direct `print()` debugging.
- Separate logging configurations.
- Application-specific error response formats.
- Custom crash handlers.
- Incomplete progress diagnostics.
- Missing correlation identifiers.

AdharaSutra should support incremental migration.

## 33.2 Migration Pipeline

```text
Existing Application
        │
        ▼
Discover Error and Logging Patterns
        │
        ▼
Record Existing Behavior
        │
        ▼
Map Errors to Shared Taxonomy
        │
        ▼
Introduce Framework Logging
        │
        ▼
Add Correlation
        │
        ▼
Migrate CLI Error Serialization
        │
        ▼
Verify Compatibility
        │
        ▼
Remove Duplicated Infrastructure
```

## 33.3 Error Compatibility

Migration must consider errors relied upon by:

- Electron frontend logic.
- Existing CLI consumers.
- Automation scripts.
- Tests.
- External integrations.

## 33.4 Adapter-First Migration

Existing exception classes may be mapped through compatibility adapters rather than rewritten immediately.

## 33.5 Logging Migration

Existing loggers may initially be routed into the framework logging configuration.

## 33.6 stdout Migration

Applications that previously wrote plain-text output to stdout must be adapted to avoid corrupting structured CLI protocol messages.

## 33.7 Verification

Migration must include behavioral tests verifying error codes, result semantics, and relevant diagnostic behavior.

---

# 34. End-to-End Validation Scenarios

## EO-S01 — Invalid Action Payload

**Given** an application action has a registered payload schema,

**When** Electron submits invalid input,

**Then** AdharaSutra shall reject the request before executing the handler.

**And** return a standardized validation error.

## EO-S02 — External HTTP Service Unavailable

**Given** an application uses a managed HTTP connector,

**When** the external service is unavailable,

**Then** the connector shall report a classified technical error.

**And** the application shall remain available for unrelated operations where supported.

## EO-S03 — External Process Failure

**Given** an external executable is running,

**When** it exits unsuccessfully,

**Then** the Process Connector shall capture relevant exit information.

**And** the Job Manager shall record the appropriate outcome.

## EO-S04 — Unexpected Application Exception

**Given** an action handler raises an unexpected exception,

**When** the framework execution boundary catches it,

**Then** the runtime shall return a safe internal error when communication remains functional.

**And** retain controlled diagnostic information.

## EO-S05 — Concurrent Request Correlation

**Given** several requests execute concurrently,

**When** their logs and responses are generated,

**Then** each operation shall retain its relevant request identifier.

## EO-S06 — Job Failure Correlation

**Given** a job launches an external subprocess,

**When** the subprocess fails,

**Then** diagnostics shall associate the request, job, execution attempt, and managed process where available.

## EO-S07 — Sensitive Error

**Given** an underlying exception contains a credential,

**When** the framework serializes the failure,

**Then** the frontend error shall not expose the credential.

## EO-S08 — Diagnostic stdout Isolation

**Given** a persistent CLI session is active,

**When** framework and application logs are produced,

**Then** stdout shall remain valid NDJSON protocol output.

## EO-S09 — Optional Logging Sink Failure

**Given** an optional file logging sink becomes unavailable,

**When** diagnostic logging continues,

**Then** the framework shall apply its documented fallback or failure policy.

**And** avoid unnecessary runtime termination.

## EO-S10 — Python Crash During Action

**Given** an action has been submitted,

**When** the Python process terminates before returning a result,

**Then** the Electron bridge shall report a transport failure.

**And** preserve uncertainty about possible business side effects.

## EO-S11 — Optional Connector Degradation

**Given** an optional integration is unavailable,

**When** health diagnostics are requested,

**Then** the affected connector shall report its actual health status.

**And** unrelated capabilities shall not automatically be reported unavailable.

## EO-S12 — Logging Queue Overload

**Given** diagnostic messages are produced faster than a logging sink can consume,

**When** the configured queue limit is reached,

**Then** the logging subsystem shall apply its bounded overload policy.

**And** expose diagnostic evidence of dropped or aggregated records where supported.

## EO-S13 — Startup and Cleanup Failure

**Given** application initialization fails after some components have started,

**When** cleanup also encounters a failure,

**Then** diagnostics shall preserve the primary initialization failure.

**And** separately record cleanup failures.

## EO-S14 — Renderer Reload

**Given** the renderer reloads,

**When** the Python runtime remains active,

**Then** framework logs and correlation shall continue according to the persistent runtime lifecycle.

## EO-S15 — Existing Application Migration

**Given** an application uses custom error and logging infrastructure,

**When** it migrates to AdharaSutra,

**Then** its required error behavior shall remain testable.

**And** common technical diagnostics shall use framework-managed facilities.

---

# 35. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| EO-D01 | Error taxonomy | Framework-wide stable categories |
| EO-D02 | Error identifiers | Stable machine-readable codes |
| EO-D03 | Business errors | Application-owned |
| EO-D04 | Technical errors | Framework-owned |
| EO-D05 | Error mapping | Explicit boundary translation |
| EO-D06 | Original cause | Preserved internally |
| EO-D07 | Public errors | Safe structured envelopes |
| EO-D08 | Retryability | True, false, or unknown |
| EO-D09 | Unknown outcomes | Explicitly represented |
| EO-D10 | Logging foundation | Python standard logging |
| EO-D11 | Structured logging | JSON-capable |
| EO-D12 | Default diagnostic channel | stderr |
| EO-D13 | CLI stdout | Protocol messages only |
| EO-D14 | Log file support | Optional rotating files |
| EO-D15 | Correlation | Request, job, attempt, process |
| EO-D16 | Async correlation | Context propagation |
| EO-D17 | Sensitive data | Schema-aware redaction |
| EO-D18 | Health | Separate from readiness |
| EO-D19 | Metrics | Lightweight optional capability |
| EO-D20 | Tracing | Optional extensible capability |
| EO-D21 | External telemetry | Optional adapters |
| EO-D22 | Log retention | Configurable and bounded |
| EO-D23 | Diagnostic exports | Redacted and controlled |
| EO-D24 | Architecture verification | Deterministic-first |
| EO-D25 | Existing migration | Adapter-first, incremental |

All decisions remain proposed until reviewed and validated.

---

# 36. Outstanding Questions

## EO-OQ-001 — Error Class Structure

Should the framework expose one base exception with registered codes, or multiple typed exception subclasses?

**Recommendation:** Use a stable base error contract with a small number of meaningful specialized classes. Avoid creating a subclass for every error code.

## EO-OQ-002 — Error Registry

Should error codes be registered dynamically or defined through a versioned catalog?

**Recommendation:** Maintain a versioned framework catalog and support validated application-specific namespaces.

## EO-OQ-003 — Application Error Mapping

Should applications register error mappers explicitly?

**Recommendation:** Yes. Explicit mapping makes boundary behavior more predictable and testable.

## EO-OQ-004 — Logging Foundation

Should AdharaSutra use Python's standard logging module or adopt a third-party structured logging system?

**Recommendation:** Use standard logging initially and provide structured formatters and adapters.

## EO-OQ-005 — Structured Log Format

Should all environments use JSON logs?

**Recommendation:** Use machine-readable JSON for production diagnostics while allowing a readable development formatter.

## EO-OQ-006 — Log Correlation

Should correlation identifiers be automatically injected into logs?

**Recommendation:** Yes, using execution-context propagation where supported.

## EO-OQ-007 — Exception Stack Traces

When should stack traces be included in diagnostic output?

**Recommendation:** Retain them for unexpected internal failures in controlled logs, never expose them automatically through frontend error responses.

## EO-OQ-008 — Error Detail Exposure

Should applications be able to add arbitrary detail fields to public errors?

**Recommendation:** Require schema-based or allowlisted detail serialization.

## EO-OQ-009 — Log Retention

What default retention should persistent applications use?

**Recommendation:** Establish bounded defaults after representative desktop storage and diagnostic requirements are validated.

## EO-OQ-010 — OpenTelemetry Integration

Should OpenTelemetry support be included in the first release?

**Recommendation:** Keep it optional and defer implementation until the core error, logging, and correlation contracts are stable.

## EO-OQ-011 — Health Polling

Should the framework periodically check connector health?

**Recommendation:** Default to on-demand checks, with optional periodic checks for applications that need them.

## EO-OQ-012 — Diagnostic Export

Should AdharaSutra provide a built-in support bundle generator?

**Recommendation:** Include a small redacted diagnostic-export capability after core logging and health reporting are implemented.

## EO-OQ-013 — Log Sink Failure

Should a failed logging sink ever trigger application shutdown?

**Recommendation:** Not for ordinary optional diagnostic logs. Stronger policies may apply to explicitly configured mandatory audit requirements.

## EO-OQ-014 — Runtime Log-Level Changes

Should Electron be able to enable detailed backend logging dynamically?

**Recommendation:** Support this only through an authorized diagnostic interface, with restrictions on sensitive output.

## EO-OQ-015 — Error Localization

Should the framework generate localized user-facing error messages?

**Recommendation:** Keep stable error codes and safe default English messages. Consuming applications should own localization and UI presentation.

---

# 37. Functional Requirement Traceability

| Functional requirement group | Error/observability responsibility |
|---|---|
| FR-ERR | Error taxonomy and propagation |
| FR-LOG | Logging and diagnostics |
| FR-RUN | Runtime failure handling |
| FR-CLI | Protocol error serialization |
| FR-ELC | Electron error mapping |
| FR-CON | Connector error classification |
| FR-HTTP | HTTP error mapping |
| FR-EXT | Process execution diagnostics |
| FR-DB | Persistence failure reporting |
| FR-STATE | State mutation and storage errors |
| FR-JOB | Job failures and correlation |
| FR-CFG | Configuration diagnostics |
| FR-SEC | Sensitive information protection |
| FR-TEST | Error and logging tests |
| FR-ARCH | Observability architecture verification |
| FR-MIG | Legacy error/logging migration |
| FR-DEV | Developer diagnostics |

---

# 38. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-REL | Explicit classification and failure isolation |
| NFR-OBS | Structured logging and correlation |
| NFR-SEC | Redaction and safe serialization |
| NFR-PERF | Lightweight optional instrumentation |
| NFR-RES | Bounded logging and retention |
| NFR-AVAIL | Health and readiness diagnostics |
| NFR-MAINT | Centralized error contracts |
| NFR-EXT | Optional logging and telemetry adapters |
| NFR-TEST | Deterministic error and redaction tests |
| NFR-COMP | Stable codes and versioned schemas |
| NFR-ARCH | Enforceable error/logging conventions |
| NFR-MIG | Incremental legacy adoption |
| NFR-DOC | Error catalog and diagnostic reference |
| NFR-DX | Actionable troubleshooting information |
| NFR-OPS | Production diagnostics and support exports |

---

# 39. Acceptance Criteria

The Error Handling and Observability Architecture may be approved when:

- [ ] A framework-wide error taxonomy is defined.
- [ ] Technical and domain error ownership is separated.
- [ ] Stable error-code conventions are established.
- [ ] Existing error codes are reconciled into one catalog.
- [ ] Error propagation boundaries are documented.
- [ ] Original exception causes are preserved internally.
- [ ] Public error serialization is safe and consistent.
- [ ] Retryability and unknown outcomes are represented accurately.
- [ ] Request failures are isolated where possible.
- [ ] Fatal runtime failure semantics are defined.
- [ ] Centralized logging ownership is established.
- [ ] Structured logging fields are defined.
- [ ] stdout is reserved for machine-readable protocol output.
- [ ] stderr and log-file behavior is defined.
- [ ] Log retention and resource limits are specified.
- [ ] Request, job, attempt, and process correlation is supported.
- [ ] Async and subprocess correlation limitations are documented.
- [ ] Sensitive-data redaction is defined.
- [ ] Diagnostic exports are sanitized.
- [ ] Health and readiness remain distinct.
- [ ] Optional metrics and tracing remain isolated from core dependencies.
- [ ] Electron error mapping is defined.
- [ ] Connector, job, state, and lifecycle integrations are consistent.
- [ ] Failure-injection tests are identified.
- [ ] Architecture verification rules are defined.
- [ ] Existing applications have a feasible migration path.
- [ ] Critical outstanding decisions are resolved or explicitly deferred.

---

# 40. Final Architecture Summary

AdharaSutra provides a centralized error-handling and observability foundation for independent Python applications.

The Error Infrastructure owns:

- Technical error categories.
- Stable error codes.
- Common exception contracts.
- Cause preservation.
- Error mapping.
- Safe serialization.
- Failure-boundary conventions.

The Observability Infrastructure owns:

- Structured logging.
- Diagnostic sinks.
- Correlation metadata.
- Runtime diagnostics.
- Health information.
- Optional metrics.
- Optional tracing.
- Sensitive-data redaction.
- Log retention.

Consuming applications own:

- Domain error definitions.
- Business failure interpretation.
- User-facing error presentation.
- Application-specific diagnostic context.
- Business retry eligibility.

The framework's error infrastructure shall remain lightweight and independent of optional external services.

The logging system shall preserve a strict separation between diagnostic output and CLI protocol output.

Request, job, and process correlation shall make it possible to follow technical execution across component boundaries.

Advanced telemetry remains optional, ensuring that minimal CLI applications do not incur unnecessary dependencies.

The framework must consistently distinguish actual failure, cancellation, timeout, recovery, and unknown execution outcomes.

**The central guarantee is: Every failure is classified, every operation is traceable, and every diagnostic respects the application's security and communication boundaries.**

---

# 41. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architecture review

**Next Document:** `docs/design/project-scaffolding.md`

The next document should define how AdharaSutra generates new applications using approved architecture profiles, including project templates, application bootstrap, dependency selection, configuration generation, testing foundations, documentation, package metadata, and automatic architecture validation.

---

**AdharaSutra — Build once. Standardize everywhere.**
