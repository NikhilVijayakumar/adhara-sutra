# AdharaSutra — Functional Requirements

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/functional-requirements.md`  
**Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Functional Requirements Specification  
**Related Document:** `docs/design/vision.md`

---

# 1. Purpose

This document defines the functional requirements of AdharaSutra, a CLI-first Python application framework intended to provide a common architectural and runtime foundation for multiple independent applications.

AdharaSutra must standardize application infrastructure while allowing consuming applications to implement their own business logic.

The requirements cover:

- Application runtime and bootstrap.
- CLI command routing and execution.
- Unified Electron-to-Python communication.
- External HTTP, WebSocket, CLI, SQLite, and filesystem integrations.
- Application state management.
- Job and process lifecycle management.
- Configuration and dependency management.
- Logging, errors, and diagnostics.
- Project scaffolding.
- Architecture discovery and verification.
- Existing application migration.
- Architecture and implementation reporting.
- Testing and developer tooling.
- Packaging and compatibility support.

This document establishes functional expectations without prescribing complete implementation designs.

Specific technologies, interfaces, folder layouts, and architectural decisions will be finalized in subsequent design documents.

---

# 2. Scope

## 2.1 In Scope

AdharaSutra shall provide a reusable application framework that defines, manages, and standardizes common infrastructure capabilities.

It shall be usable as the foundational runtime for new applications and as an adoptable framework for existing applications.

The framework shall support applications whose frontend is Electron and whose backend is implemented in Python.

It shall also support standalone Python CLI applications that do not use Electron.

## 2.2 Out of Scope

AdharaSutra shall not:

1. Implement application-specific business logic.
2. Determine domain-specific workflows.
3. Require an Electron frontend for all applications.
4. Require HTTP communication between Electron and Python.
5. Implement specialized AI inference, audio generation, or image-generation algorithms.
6. Force every application to use every connector or subsystem.
7. Automatically modify business logic without review.
8. Depend on an LLM for its core runtime.
9. Replace mature third-party libraries without a documented requirement.
10. Treat static architecture compliance as proof of complete application correctness.

---

# 3. Requirement Classification

## 3.1 Requirement Identifiers

All functional requirements shall have stable identifiers.

Format:

`FR-<MODULE>-<NUMBER>`

Example:

`FR-CLI-001`

Identifiers should not be reassigned to unrelated requirements after approval.

## 3.2 Priorities

| Priority | Meaning |
|---|---|
| P0 — Critical | Essential for the foundational framework |
| P1 — High | Required for the intended full framework |
| P2 — Medium | Important supporting capability |
| P3 — Optional | Future or advanced enhancement |

Priority does not automatically determine implementation order. Dependencies and risk may require some higher-priority infrastructure to be developed earlier.

## 3.3 Requirement Status

Each requirement may have one of the following statuses:

- Proposed
- Under Review
- Approved
- Deferred
- Rejected
- Implemented
- Verified

All requirements in this initial document are **Proposed** unless explicitly approved later.

## 3.4 Verification Methods

Requirements may be verified through:

- Automated unit tests.
- Integration tests.
- CLI protocol contract tests.
- Architecture conformance checks.
- Generated-project validation.
- Migration regression tests.
- End-to-end Electron tests.
- Manual technical review where automation is insufficient.

---

# 4. Application Runtime Requirements

**Requirement group:** `FR-RUN`

The application runtime is the foundation of AdharaSutra.

It must provide consistent initialization, execution, and shutdown behavior for consuming applications.

### FR-RUN-001 — Framework-Based Application Creation

**Priority:** P0

The framework shall provide a standard mechanism for defining and initializing an application.

**Acceptance criteria:**

- An application can be registered using the public framework API.
- An application has a unique name and defined version.
- Applications do not need to implement their own runtime initialization infrastructure.
- Invalid application definitions produce structured errors.

### FR-RUN-002 — Application Bootstrap

**Priority:** P0

The framework shall initialize required application services using a standardized bootstrap process.

**Acceptance criteria:**

- Configuration is validated before dependent services start.
- Registered services and connectors are initialized according to declared dependencies.
- Initialization failures prevent entry into the ready state.
- Successfully initialized resources are cleaned up following partial startup failures.

### FR-RUN-003 — Application Lifecycle

**Priority:** P0

The framework shall manage application lifecycle states.

Required lifecycle states include:

- Created
- Initializing
- Ready
- Running
- Stopping
- Stopped
- Failed

**Acceptance criteria:**

- Lifecycle transitions follow defined rules.
- Invalid transitions are rejected or handled according to documented policy.
- Applications can observe relevant lifecycle events.
- Shutdown releases framework-managed resources.

### FR-RUN-004 — Application Extension Points

**Priority:** P0

Applications shall register their own business handlers, services, models, and supported integrations through documented extension points.

**Acceptance criteria:**

- Business actions can be registered without modifying framework source code.
- Application services can use framework-provided facilities.
- Framework components do not directly depend on consuming application modules.
- Application code can be tested independently of the CLI transport.

### FR-RUN-005 — Application Context

**Priority:** P0

The framework shall provide a controlled application context containing access to registered runtime facilities.

The context may expose:

- Configuration.
- Logging.
- State.
- Connectors.
- Job services.
- Registered application services.
- Execution metadata.

**Acceptance criteria:**

- Handlers can access required registered services.
- Unregistered capabilities produce clear errors.
- Request-scoped metadata is isolated appropriately.
- Context access does not bypass defined security restrictions.

### FR-RUN-006 — Runtime Execution Modes

**Priority:** P0

The framework shall support short-lived and persistent application execution modes.

**Acceptance criteria:**

- A short-lived process can execute an action and terminate.
- A persistent process can execute multiple requests.
- Both modes use consistent application action semantics.
- Resource and state ownership are defined for each mode.

### FR-RUN-007 — Graceful Shutdown

**Priority:** P1

The framework shall provide coordinated shutdown behavior.

**Acceptance criteria:**

- Active jobs are cancelled, completed, or handed off according to policy.
- Managed subprocesses are terminated or detached only according to explicit rules.
- Connectors release resources.
- Shutdown failures are reported.
- Forced termination is handled as a distinct failure condition.

---

# 5. CLI Framework Requirements

**Requirement group:** `FR-CLI`

AdharaSutra shall own the CLI infrastructure used by consuming applications.

Applications shall not need to independently implement command routing, protocol serialization, or process communication infrastructure.

### FR-CLI-001 — Centralized CLI Routing

**Priority:** P0

The framework shall provide a centralized action and command router.

**Acceptance criteria:**

- Registered actions can be invoked by identifier.
- Unknown actions produce standardized errors.
- Duplicate action registrations are detected.
- Routing does not contain application-specific business logic.

### FR-CLI-002 — Action Registration

**Priority:** P0

Applications shall register action handlers through a documented API.

**Acceptance criteria:**

- Action identifiers are validated.
- Handlers can define input and output schemas.
- Synchronous and asynchronous handlers are supported through documented execution semantics.
- Registered actions can be discovered for diagnostics and documentation.

### FR-CLI-003 — Input Validation

**Priority:** P0

The framework shall validate request envelopes and application-defined payload schemas.

**Acceptance criteria:**

- Invalid protocol envelopes are rejected.
- Invalid business-action payloads produce structured validation errors.
- Validation occurs before the handler executes.
- Validation errors identify the affected fields without exposing sensitive values.

### FR-CLI-004 — Structured Output

**Priority:** P0

The framework shall serialize action results using standardized response envelopes.

**Acceptance criteria:**

- Successful requests produce valid protocol responses.
- Failed requests produce valid error responses whenever communication remains possible.
- Application results are represented as response data.
- Diagnostic logs do not corrupt protocol output.

### FR-CLI-005 — One-Shot CLI Execution

**Priority:** P0

The framework shall support executing a single request through a CLI process.

**Acceptance criteria:**

- The process accepts the request through a documented input mechanism.
- The requested action is dispatched.
- A structured result is returned.
- The process exits with a documented status.

### FR-CLI-006 — Persistent CLI Execution

**Priority:** P0

The framework shall support persistent bidirectional communication over a CLI process.

**Acceptance criteria:**

- Multiple requests can be processed within one process lifetime.
- Requests and responses are correlated.
- Events can be emitted during processing.
- Process shutdown and disconnection are handled.
- Shared process resources follow defined lifecycle rules.

### FR-CLI-007 — Standard Exit Codes

**Priority:** P1

The framework shall define consistent process exit-code semantics.

Exit categories shall distinguish:

- Success.
- Input errors.
- Configuration errors.
- Dependency failures.
- Execution failures.
- Timeouts.
- Cancellation.

Exact numeric values will be finalized in the CLI protocol design.

### FR-CLI-008 — CLI Help and Discovery

**Priority:** P1

The framework shall support discovering registered commands and their usage.

**Acceptance criteria:**

- Users can list available commands.
- Commands expose their documented arguments.
- Invalid invocations provide meaningful guidance.
- Machine-readable action metadata can be generated.

### FR-CLI-009 — CLI Version Information

**Priority:** P1

Applications shall expose application, framework, and supported protocol versions.

### FR-CLI-010 — Standard Input Support

**Priority:** P1

The framework shall support structured requests and large-input references without requiring all data to be embedded in command-line arguments.

---

# 6. Electron Communication Requirements

**Requirement group:** `FR-ELC`

The framework shall establish a unified communication contract between Electron and Python.

### FR-ELC-001 — Unified Electron Protocol

**Priority:** P0

Electron applications shall communicate with AdharaSutra applications through one versioned CLI protocol.

**Acceptance criteria:**

- The same request envelope is supported across applications.
- The same response and error envelope structures are supported.
- External integration transport choices do not change the frontend protocol.

### FR-ELC-002 — CLI-Based Communication

**Priority:** P0

Electron-to-Python communication shall use process communication rather than requiring an HTTP server.

Supported communication channels shall include stdin, stdout, and stderr according to the protocol design.

### FR-ELC-003 — Standard Request Envelope

**Priority:** P0

Requests shall support:

- Protocol version.
- Request identifier.
- Action identifier.
- Action payload.

Additional metadata may be supported through versioned optional fields.

### FR-ELC-004 — Standard Response Envelope

**Priority:** P0

Responses shall support:

- Protocol version.
- Request identifier.
- Success or failure.
- Result data.
- Structured error information.

### FR-ELC-005 — Event Streaming

**Priority:** P0

The framework shall support structured events during request execution.

**Acceptance criteria:**

- Events can be correlated with requests or jobs.
- Events follow a documented schema.
- Malformed events are detectable.
- Electron can distinguish events from terminal results.

### FR-ELC-006 — Cancellation

**Priority:** P0

Electron shall be able to request cancellation of supported active operations.

**Acceptance criteria:**

- Cancellation requests identify their target.
- Cancellation produces an explicit outcome.
- Unsupported cancellation is reported.
- Cancellation does not automatically imply that an external dependency successfully stopped.

### FR-ELC-007 — Connection and Process Failure Handling

**Priority:** P0

The framework and Electron bridge shall detect and report unexpected process termination and communication failures.

### FR-ELC-008 — Correlation and Ordering

**Priority:** P0

The protocol shall define request correlation and message-ordering guarantees.

### FR-ELC-009 — Protocol Compatibility

**Priority:** P0

The framework shall identify unsupported protocol versions and prevent unsafe interpretation of incompatible messages.

### FR-ELC-010 — Shared Electron Bridge

**Priority:** P1

AdharaSutra shall provide or specify a reusable TypeScript bridge for Electron applications.

The bridge shall manage:

- Python process startup.
- Request submission.
- Response parsing.
- Event subscriptions.
- Cancellation.
- Timeouts.
- Process lifecycle.
- Error propagation.

### FR-ELC-011 — Electron Security Boundary

**Priority:** P0

The bridge shall ensure that renderer-provided input cannot directly invoke arbitrary system commands through the framework.

---

# 7. Connector Framework Requirements

**Requirement group:** `FR-CON`

AdharaSutra shall provide reusable connector infrastructure for external dependencies.

### FR-CON-001 — Connector Registry

**Priority:** P0

The framework shall provide a mechanism to register and resolve external connectors.

**Acceptance criteria:**

- Connectors have stable identifiers.
- Applications can declare required connectors.
- Duplicate registrations are detected.
- Connector dependencies can be validated.

### FR-CON-002 — Connector Lifecycle

**Priority:** P0

Connectors shall follow documented initialization, readiness, health, and shutdown conventions.

### FR-CON-003 — Connector Configuration

**Priority:** P0

Connectors shall receive validated configuration through framework-managed facilities.

### FR-CON-004 — Standard Error Mapping

**Priority:** P0

Connector failures shall be translated into consistent framework-level error categories while preserving useful diagnostic information.

### FR-CON-005 — Connector Isolation

**Priority:** P0

Applications shall be able to use one connector without installing unrelated integration dependencies.

### FR-CON-006 — Connector Health Reporting

**Priority:** P1

Connectors shall expose health or availability information where the underlying technology supports meaningful checks.

### FR-CON-007 — Connector Test Doubles

**Priority:** P1

The framework shall support replacing live connectors with test doubles.

### FR-CON-008 — Custom Connector Registration

**Priority:** P1

Applications and optional packages shall be able to register custom connector implementations without modifying core framework code.

---

# 8. HTTP Connector Requirements

**Requirement group:** `FR-HTTP`

### FR-HTTP-001 — Outbound HTTP Requests

**Priority:** P0

The framework shall provide reusable facilities for outbound HTTP communication.

Supported operations shall include commonly required HTTP methods.

### FR-HTTP-002 — Connection Management

**Priority:** P0

The framework shall manage HTTP client initialization, reuse, and cleanup.

### FR-HTTP-003 — Timeout Policies

**Priority:** P0

HTTP operations shall support configurable timeouts.

### FR-HTTP-004 — Retry Policies

**Priority:** P1

The framework shall support configurable retry behavior for eligible failures.

Retries must account for request idempotency and must not automatically repeat unsafe operations.

### FR-HTTP-005 — Authentication Support

**Priority:** P1

The framework shall support common authentication configuration patterns without requiring credentials to be embedded in source code.

### FR-HTTP-006 — Response Processing

**Priority:** P0

The HTTP connector shall expose response status, headers, body, and failure information through documented interfaces.

### FR-HTTP-007 — Streaming Support

**Priority:** P1

The framework shall support streaming HTTP responses where required by external services.

---

# 9. External CLI Connector Requirements

**Requirement group:** `FR-EXT`

### FR-EXT-001 — External Executable Invocation

**Priority:** P0

The framework shall support safely executing external CLI programs.

### FR-EXT-002 — Executable Discovery

**Priority:** P0

The framework shall support locating executables through configured paths and approved discovery mechanisms.

### FR-EXT-003 — Argument Management

**Priority:** P0

The framework shall pass structured argument arrays to external processes.

Unsafe shell interpretation must not be required for ordinary execution.

### FR-EXT-004 — Process Output Capture

**Priority:** P0

The framework shall capture stdout, stderr, and exit status.

### FR-EXT-005 — Streaming Output

**Priority:** P0

The framework shall support processing output incrementally while an external process executes.

### FR-EXT-006 — Timeout and Cancellation

**Priority:** P0

The framework shall support timeouts and cancellation policies for external processes.

### FR-EXT-007 — Process Cleanup

**Priority:** P0

The framework shall manage child-process cleanup according to defined platform and ownership policies.

### FR-EXT-008 — Output Parsing Extensions

**Priority:** P1

Applications or integration plugins shall be able to register parsers for external command outputs.

### FR-EXT-009 — External CLI Compatibility

**Priority:** P1

The framework shall support external executables with different argument conventions, exit codes, and output formats without changing the Electron protocol.

### FR-EXT-010 — Interactive External Processes

**Priority:** P2

The framework should support managed interactive or persistent external CLI sessions where necessary.

---

# 10. SQLite and Persistence Requirements

**Requirement group:** `FR-DB`

### FR-DB-001 — SQLite Connection Management

**Priority:** P0

The framework shall provide managed SQLite connection facilities.

### FR-DB-002 — Transaction Management

**Priority:** P0

The framework shall support explicit transaction boundaries.

### FR-DB-003 — Database Configuration

**Priority:** P0

Applications shall configure database locations and connection policies through framework configuration.

### FR-DB-004 — Schema Migration Infrastructure

**Priority:** P1

The framework shall provide or integrate with a database schema migration mechanism.

Applications remain responsible for their domain schemas.

### FR-DB-005 — Persistence Abstraction

**Priority:** P1

Applications shall be able to implement domain repositories using framework-managed database facilities.

### FR-DB-006 — Database Concurrency Policy

**Priority:** P0

The framework shall define and enforce supported concurrency and connection-ownership semantics.

### FR-DB-007 — Backup and Recovery Support

**Priority:** P1

The framework shall provide facilities or approved procedures for SQLite backup, integrity checking, and recovery.

### FR-DB-008 — Persistent State Support

**Priority:** P1

The state-management subsystem shall be able to use SQLite-backed persistence through a documented adapter.

---

# 11. WebSocket Connector Requirements

**Requirement group:** `FR-WS`

### FR-WS-001 — WebSocket Client Connections

**Priority:** P1

The framework shall support outbound WebSocket client connections.

### FR-WS-002 — Event Reception

**Priority:** P1

WebSocket messages shall be consumable through a documented event or stream interface.

### FR-WS-003 — Connection Lifecycle

**Priority:** P1

The connector shall support connection setup, close, failure detection, and cleanup.

### FR-WS-004 — Reconnection Policies

**Priority:** P2

The framework should support controlled reconnection policies where appropriate.

### FR-WS-005 — Message Validation

**Priority:** P1

Applications shall be able to validate received messages using registered schemas or parsers.

---

# 12. Filesystem Requirements

**Requirement group:** `FR-FS`

### FR-FS-001 — Application Data Directories

**Priority:** P0

The framework shall provide standardized resolution of application data, configuration, cache, temporary, and log directories.

### FR-FS-002 — Path Validation

**Priority:** P0

The framework shall support controlled path validation and access boundaries.

### FR-FS-003 — Temporary File Management

**Priority:** P1

Temporary files and directories shall have defined creation and cleanup behavior.

### FR-FS-004 — File Operation Utilities

**Priority:** P1

The framework shall provide reusable filesystem operations where these materially reduce duplication.

### FR-FS-005 — Large Artifact Handling

**Priority:** P1

The framework shall support passing large generated artifacts through managed file references rather than requiring binary payloads in CLI responses.

---

# 13. State Management Requirements

**Requirement group:** `FR-STATE`

### FR-STATE-001 — Central State Facilities

**Priority:** P0

The framework shall provide reusable state-management facilities.

### FR-STATE-002 — Application-Defined State

**Priority:** P0

Applications shall define their own state schemas and values.

The framework shall not define business-specific state.

### FR-STATE-003 — State Access

**Priority:** P0

The framework shall expose documented mechanisms to read and update state.

### FR-STATE-004 — State Change Notifications

**Priority:** P1

Applications shall be able to subscribe to relevant state changes.

### FR-STATE-005 — State Scope

**Priority:** P0

The framework shall distinguish:

- Request-scoped state.
- Session-scoped state.
- Process-scoped state.
- Persistent state.

### FR-STATE-006 — State Persistence

**Priority:** P1

Applications shall be able to configure persistent state storage where required.

### FR-STATE-007 — State Concurrency

**Priority:** P0

The framework shall define safe concurrent access and update behavior.

### FR-STATE-008 — State Restoration

**Priority:** P1

Persistent state shall be recoverable following application restart, subject to the selected persistence policy.

### FR-STATE-009 — State Cleanup

**Priority:** P1

Expired or terminated session state shall be cleaned up according to defined policies.

---

# 14. Job Management Requirements

**Requirement group:** `FR-JOB`

### FR-JOB-001 — Job Registration and Execution

**Priority:** P0

The framework shall provide reusable job execution facilities.

Applications shall define job behavior.

### FR-JOB-002 — Job Identifiers

**Priority:** P0

Every managed job shall have an identifiable execution record.

### FR-JOB-003 — Job Lifecycle

**Priority:** P0

Jobs shall support defined states, including pending, running, completed, failed, and cancelled.

### FR-JOB-004 — Progress Reporting

**Priority:** P0

Jobs shall be able to emit structured progress updates.

### FR-JOB-005 — Cancellation

**Priority:** P0

Jobs shall support cancellation where the underlying operation can be cancelled.

### FR-JOB-006 — Timeout Management

**Priority:** P0

Job execution shall support configured deadlines or timeouts.

### FR-JOB-007 — Concurrency Management

**Priority:** P1

The framework shall support limits on concurrently executing jobs.

### FR-JOB-008 — Job Results

**Priority:** P0

Completed jobs shall expose results or managed artifact references.

### FR-JOB-009 — Job Persistence

**Priority:** P1

The framework shall support durable job metadata when configured.

### FR-JOB-010 — Worker Ownership

**Priority:** P0

The framework shall define which process or worker owns active jobs.

A job shall not be represented as continuing after its owning process terminates unless a persistent execution mechanism actually exists.

### FR-JOB-011 — Recovery Policy

**Priority:** P1

The framework shall support documented behavior for recovering, retrying, or marking interrupted jobs following unexpected termination.

---

# 15. Configuration Requirements

**Requirement group:** `FR-CFG`

### FR-CFG-001 — Central Configuration

**Priority:** P0

The framework shall provide a centralized configuration system.

### FR-CFG-002 — Multiple Configuration Sources

**Priority:** P0

The framework shall support configuration from documented sources, including environment variables and application configuration files.

### FR-CFG-003 — Configuration Validation

**Priority:** P0

Configuration shall be validated before dependent services initialize.

### FR-CFG-004 — Configuration Precedence

**Priority:** P0

The framework shall define deterministic configuration precedence.

### FR-CFG-005 — Application-Specific Settings

**Priority:** P0

Applications shall be able to define additional configuration schemas.

### FR-CFG-006 — Secret Handling

**Priority:** P0

The framework shall support configuration mechanisms that avoid storing secrets directly in ordinary committed source files.

### FR-CFG-007 — Runtime Overrides

**Priority:** P1

Supported settings may be overridden using documented runtime mechanisms.

### FR-CFG-008 — Configuration Diagnostics

**Priority:** P1

The framework shall report invalid or missing configuration with actionable error messages.

---

# 16. Error Handling Requirements

**Requirement group:** `FR-ERR`

### FR-ERR-001 — Standard Error Model

**Priority:** P0

The framework shall define a common structured error model.

### FR-ERR-002 — Error Classification

**Priority:** P0

Errors shall distinguish categories such as:

- Validation.
- Configuration.
- Protocol.
- Connector.
- Process.
- Timeout.
- Cancellation.
- Persistence.
- Internal execution.

### FR-ERR-003 — Error Propagation

**Priority:** P0

Errors shall propagate through defined framework boundaries without losing important diagnostic information.

### FR-ERR-004 — Error Serialization

**Priority:** P0

Frontend-facing errors shall follow the common CLI protocol.

### FR-ERR-005 — Sensitive Information Protection

**Priority:** P0

Errors returned to Electron shall not expose secrets or unnecessary internal details.

### FR-ERR-006 — Application-Specific Error Mapping

**Priority:** P1

Applications shall be able to map domain errors into supported framework error categories.

---

# 17. Logging and Diagnostics Requirements

**Requirement group:** `FR-LOG`

### FR-LOG-001 — Central Logging

**Priority:** P0

The framework shall provide common logging facilities.

### FR-LOG-002 — Structured Logs

**Priority:** P1

The framework shall support structured log output.

### FR-LOG-003 — Request Correlation

**Priority:** P0

Diagnostic information shall support correlation with requests and jobs.

### FR-LOG-004 — Log Destination Separation

**Priority:** P0

Logging shall not corrupt machine-readable CLI protocol streams.

### FR-LOG-005 — Configurable Log Levels

**Priority:** P1

Log verbosity shall be configurable.

### FR-LOG-006 — Runtime Diagnostics

**Priority:** P1

The framework shall expose diagnostics for configuration, dependencies, connectors, and runtime readiness.

### FR-LOG-007 — Diagnostic Export

**Priority:** P2

The framework should support exporting sanitized diagnostic reports.

---

# 18. Dependency and Service Management Requirements

**Requirement group:** `FR-DI`

### FR-DI-001 — Service Registration

**Priority:** P0

Applications shall register services and implementations using framework-defined mechanisms.

### FR-DI-002 — Dependency Resolution

**Priority:** P0

The framework shall resolve registered dependencies according to defined rules.

### FR-DI-003 — Service Lifecycle

**Priority:** P0

Service instances shall follow documented lifetime and cleanup policies.

### FR-DI-004 — Dependency Validation

**Priority:** P0

Missing or circular dependencies shall produce detectable initialization errors.

### FR-DI-005 — Test Replacement

**Priority:** P1

Registered services shall be replaceable with test implementations.

### FR-DI-006 — Optional Dependencies

**Priority:** P1

Applications shall not be required to initialize unused framework capabilities.

---

# 19. Project Scaffolding Requirements

**Requirement group:** `FR-SCAF`

### FR-SCAF-001 — New Project Generation

**Priority:** P1

AdharaSutra shall provide a mechanism to generate new applications.

### FR-SCAF-002 — Architecture Profiles

**Priority:** P1

The generator shall support predefined architecture profiles.

Potential profiles include:

- Minimal.
- CLI.
- DDD.
- Electron CLI.
- AI worker.

### FR-SCAF-003 — Standard Folder Structure

**Priority:** P1

Generated applications shall follow the selected architecture profile.

### FR-SCAF-004 — Framework Bootstrap Generation

**Priority:** P1

Generated applications shall include a working AdharaSutra bootstrap and entry point.

### FR-SCAF-005 — Connector Selection

**Priority:** P1

Project generation shall allow selection of required connectors.

### FR-SCAF-006 — Testing Boilerplate

**Priority:** P1

Generated applications shall include appropriate test configuration and example tests.

### FR-SCAF-007 — Documentation Generation

**Priority:** P1

Generated applications shall include a minimal documentation structure appropriate to their profile.

### FR-SCAF-008 — Architecture Verification Readiness

**Priority:** P1

A newly generated application shall pass applicable architecture checks without requiring structural corrections.

### FR-SCAF-009 — Safe Generation

**Priority:** P0

Project generation shall not overwrite existing user files without explicit authorization.

---

# 20. Architecture Discovery Requirements

**Requirement group:** `FR-DISC`

### FR-DISC-001 — Project Inspection

**Priority:** P1

The framework shall analyze existing Python application structures.

### FR-DISC-002 — Entry Point Discovery

**Priority:** P1

The inspection engine shall identify known application and CLI entry points.

### FR-DISC-003 — Module and Dependency Discovery

**Priority:** P1

The engine shall identify Python modules and statically discoverable dependencies.

### FR-DISC-004 — CLI Command Discovery

**Priority:** P1

The engine shall identify supported CLI registration and routing patterns.

### FR-DISC-005 — Electron Integration Discovery

**Priority:** P1

The engine shall inspect Electron process invocation and IPC patterns where supported source files are available.

### FR-DISC-006 — External Integration Discovery

**Priority:** P1

The engine shall identify recognizable HTTP, WebSocket, external CLI, SQLite, and filesystem integration patterns.

### FR-DISC-007 — State and Job Discovery

**Priority:** P1

The engine shall identify known application state and job-execution patterns.

### FR-DISC-008 — Current Implementation Report

**Priority:** P1

The engine shall generate a report explaining the current implementation.

### FR-DISC-009 — Source Evidence

**Priority:** P0

Reported findings shall contain source references where available.

### FR-DISC-010 — Uncertainty Reporting

**Priority:** P0

The engine shall distinguish observed implementation facts from inferred or unverified behavior.

### FR-DISC-011 — Incremental Analysis

**Priority:** P2

The engine should support updating reports after relevant source files change without unnecessarily reanalyzing unrelated files.

---

# 21. Architecture Verification Requirements

**Requirement group:** `FR-ARCH`

### FR-ARCH-001 — Architecture Profiles

**Priority:** P1

The framework shall define versioned architecture profiles.

### FR-ARCH-002 — Rule Catalog

**Priority:** P1

The framework shall provide a catalog of architecture conformance rules.

### FR-ARCH-003 — Project Structure Verification

**Priority:** P1

The verifier shall validate required folders, files, and project metadata.

### FR-ARCH-004 — Dependency Boundary Verification

**Priority:** P1

The verifier shall detect forbidden dependencies and module-layer violations within supported analysis boundaries.

### FR-ARCH-005 — Framework Adoption Verification

**Priority:** P1

The verifier shall detect whether required framework entry points and registered infrastructure conventions are present.

### FR-ARCH-006 — CLI Protocol Verification

**Priority:** P1

The verifier shall evaluate the application's compatibility with required CLI protocol contracts.

### FR-ARCH-007 — Connector Policy Verification

**Priority:** P1

The verifier shall detect supported patterns that bypass required framework connector facilities.

### FR-ARCH-008 — State and Job Verification

**Priority:** P1

The verifier shall evaluate applicable state and job-management requirements using static analysis and executable tests.

### FR-ARCH-009 — Deterministic Results

**Priority:** P0

Deterministically verifiable rules shall produce reproducible results for the same inputs, configuration, and analyzer versions.

### FR-ARCH-010 — Verification Status

**Priority:** P0

The verifier shall distinguish:

- Pass.
- Fail.
- Needs review.
- Not checked.

### FR-ARCH-011 — Machine-Readable Reports

**Priority:** P1

Verification results shall be exportable in a versioned structured format.

### FR-ARCH-012 — Evidence and Remediation

**Priority:** P1

Violations shall provide rule identifiers, evidence, severity, and recommended remediation where possible.

### FR-ARCH-013 — Baseline Support

**Priority:** P1

Existing projects shall be able to track acknowledged violations while blocking newly introduced violations according to policy.

### FR-ARCH-014 — Approved Exceptions

**Priority:** P1

The verifier shall support explicitly documented, scoped, reviewable exceptions.

### FR-ARCH-015 — CI Enforcement

**Priority:** P1

Architecture verification shall support noninteractive execution and meaningful exit statuses.

### FR-ARCH-016 — Optional LLM Review

**Priority:** P2

The framework may support optional advisory architecture analysis using external coding agents or LLM services.

LLM review shall not override deterministic results.

---

# 22. Existing Application Migration Requirements

**Requirement group:** `FR-MIG`

### FR-MIG-001 — Existing Project Migration

**Priority:** P1

AdharaSutra shall support adopting the framework in existing applications.

### FR-MIG-002 — Migration Analysis

**Priority:** P1

Migration analysis shall use discovered implementation information and architecture verification results.

### FR-MIG-003 — Gap Analysis

**Priority:** P1

The migration engine shall identify differences between the existing implementation and target architecture.

### FR-MIG-004 — Migration Strategies

**Priority:** P1

The framework shall support planning migration using:

- Adapter-first adoption.
- Incremental refactoring.
- Controlled rebuild.

### FR-MIG-005 — Migration Plan Generation

**Priority:** P1

The framework shall generate a structured migration plan.

### FR-MIG-006 — Business Behavior Preservation

**Priority:** P0

Migration operations shall not intentionally alter application business behavior unless explicitly authorized.

### FR-MIG-007 — CLI Compatibility Preservation

**Priority:** P0

Migration planning shall account for existing CLI commands and Electron-facing contracts.

### FR-MIG-008 — Persistence Preservation

**Priority:** P0

Migration shall account for existing data, schema compatibility, backups, and recovery.

### FR-MIG-009 — Incremental Migration

**Priority:** P1

Migration shall support independently verifiable migration units.

### FR-MIG-010 — Migration Status Tracking

**Priority:** P1

The framework shall track migration progress against planned tasks and findings.

### FR-MIG-011 — Safe Automated Transformations

**Priority:** P2

The framework may provide deterministic automated transformations for explicitly supported source patterns.

### FR-MIG-012 — Reviewable Changes

**Priority:** P0

Automated transformations shall produce inspectable changes and shall not silently modify unrelated application logic.

### FR-MIG-013 — Migration Verification

**Priority:** P1

Migration completion shall be evaluated through architecture verification and required regression tests.

### FR-MIG-014 — Rollback Planning

**Priority:** P1

Migration plans shall document rollback or recovery strategies appropriate to affected code and data.

### FR-MIG-015 — Migration Completion Report

**Priority:** P1

The framework shall generate a report of completed, deferred, and unresolved migration requirements.

---

# 23. Architecture and Migration Reporting Requirements

**Requirement group:** `FR-REP`

### FR-REP-001 — Implementation Report

**Priority:** P1

The framework shall generate a report describing the current application implementation.

### FR-REP-002 — Verification Report

**Priority:** P1

The framework shall generate architecture conformance reports.

### FR-REP-003 — Migration Report

**Priority:** P1

The framework shall generate actionable migration findings and tasks.

### FR-REP-004 — Markdown Output

**Priority:** P1

Reports shall support human-readable Markdown output.

### FR-REP-005 — JSON Output

**Priority:** P1

Reports shall support machine-readable JSON output.

### FR-REP-006 — Report Versioning

**Priority:** P0

Structured reports shall identify their schema version.

### FR-REP-007 — Source Revision Tracking

**Priority:** P1

Reports shall include sufficient revision information to detect stale analysis.

### FR-REP-008 — Finding Traceability

**Priority:** P1

Findings shall reference relevant architecture rules and source evidence.

### FR-REP-009 — Actionable Recommendations

**Priority:** P1

Migration findings shall provide enough context for a developer or coding agent to investigate and implement a correction.

### FR-REP-010 — Report Refresh

**Priority:** P1

The framework shall support regenerating reports after source changes.

---

# 24. Testing Infrastructure Requirements

**Requirement group:** `FR-TEST`

### FR-TEST-001 — Framework Testing Utilities

**Priority:** P1

The framework shall provide reusable testing facilities for applications and framework modules.

### FR-TEST-002 — CLI Contract Tests

**Priority:** P0

The framework shall provide executable tests for the unified CLI protocol.

### FR-TEST-003 — Action Handler Tests

**Priority:** P1

Applications shall be able to test registered action handlers without launching Electron.

### FR-TEST-004 — Connector Test Doubles

**Priority:** P1

The framework shall provide mechanisms for replacing external dependencies during tests.

### FR-TEST-005 — Process Execution Tests

**Priority:** P1

The framework shall support testing external CLI behavior using controlled executable fixtures.

### FR-TEST-006 — State and Job Tests

**Priority:** P1

The framework shall support validating state, concurrency, lifecycle, cancellation, and failure behavior.

### FR-TEST-007 — Architecture Tests

**Priority:** P1

The framework shall support executing applicable architecture checks as automated tests.

### FR-TEST-008 — Migration Regression Tests

**Priority:** P1

Migration plans shall identify behavioral tests needed to preserve existing application functionality.

### FR-TEST-009 — Electron Integration Tests

**Priority:** P1

The shared Electron bridge shall be testable against representative Python runtime fixtures.

---

# 25. Developer Experience Requirements

**Requirement group:** `FR-DEV`

### FR-DEV-001 — Standard Developer Commands

**Priority:** P1

The framework shall provide a consistent developer CLI for supported project operations.

Proposed command categories:

- Create.
- Inspect.
- Verify.
- Migrate.
- Diagnose.
- Report.
- Version.

### FR-DEV-002 — Local Diagnostics

**Priority:** P1

Developers shall be able to diagnose common configuration, runtime, connector, and protocol problems.

### FR-DEV-003 — Examples

**Priority:** P1

The framework shall provide representative working examples of common integration patterns.

### FR-DEV-004 — Documentation Discovery

**Priority:** P1

Developers shall be able to locate documentation relevant to supported framework capabilities.

### FR-DEV-005 — Agent-Friendly Reports

**Priority:** P1

Architecture and migration reports shall provide structured context suitable for multiple coding agents.

### FR-DEV-006 — Framework Capability Discovery

**Priority:** P2

The framework should expose registered runtime capabilities, connectors, and supported integration information through diagnostics.

---

# 26. Packaging and Distribution Requirements

**Requirement group:** `FR-PKG`

### FR-PKG-001 — Python Package Distribution

**Priority:** P1

The framework shall support installation as a versioned Python distribution.

### FR-PKG-002 — Command-Line Entry Point

**Priority:** P1

The framework shall provide an executable developer command.

Proposed executable: `adhara`.

### FR-PKG-003 — Optional Dependencies

**Priority:** P1

Applications shall be able to install only required connector and integration dependencies.

### FR-PKG-004 — Electron Bridge Distribution

**Priority:** P1

The shared Electron bridge shall be distributable as a versioned TypeScript/JavaScript package.

### FR-PKG-005 — Supported Platform Packaging

**Priority:** P1

The framework shall define packaging and runtime-discovery mechanisms for supported desktop operating systems.

### FR-PKG-006 — Production Runtime Support

**Priority:** P1

Packaged Electron applications shall be able to locate and execute their Python backend without relying on an undeclared development environment.

### FR-PKG-007 — External Executable Packaging

**Priority:** P1

The framework shall support configuration and diagnostics for bundled or separately installed external executables.

### FR-PKG-008 — Version Compatibility

**Priority:** P0

Framework and bridge releases shall identify compatible CLI protocol versions.

### FR-PKG-009 — Upgrade and Migration Guidance

**Priority:** P1

Breaking framework changes shall have documented compatibility and upgrade guidance.

---

# 27. Documentation Requirements

**Requirement group:** `FR-DOC`

### FR-DOC-001 — Framework Documentation

**Priority:** P1

The framework shall provide documentation for public capabilities, architecture, and supported development workflows.

### FR-DOC-002 — Application Documentation Templates

**Priority:** P1

Project scaffolding shall generate appropriate initial documentation for consuming applications.

### FR-DOC-003 — Protocol Reference

**Priority:** P0

The unified CLI protocol shall have a maintained reference describing messages, events, errors, and version compatibility.

### FR-DOC-004 — Connector Reference

**Priority:** P1

Every public connector category shall have documented configuration, lifecycle, and error behavior.

### FR-DOC-005 — Architecture Rule Reference

**Priority:** P1

Every enforceable architecture rule shall have a stable identifier and documented purpose.

### FR-DOC-006 — Migration Documentation

**Priority:** P1

The framework shall document supported migration workflows, limitations, compatibility requirements, and recovery procedures.

### FR-DOC-007 — Documentation Validation

**Priority:** P2

The framework should support validating required documentation structures and machine-verifiable references.

---

# 28. Security-Related Functional Requirements

**Requirement group:** `FR-SEC`

### FR-SEC-001 — Request Validation

**Priority:** P0

The framework shall validate protocol messages before dispatch.

### FR-SEC-002 — Action Allowlisting

**Priority:** P0

Only registered and authorized application actions shall be executable through the framework router.

### FR-SEC-003 — Safe Process Execution

**Priority:** P0

External command execution shall use controlled executable and argument handling.

### FR-SEC-004 — Sensitive Data Redaction

**Priority:** P0

Framework error and logging facilities shall support redacting sensitive information.

### FR-SEC-005 — Controlled Filesystem Access

**Priority:** P0

Framework-managed file operations shall support configured access boundaries.

### FR-SEC-006 — Connector Credential Handling

**Priority:** P0

External connector credentials shall be handled through supported secure configuration mechanisms.

### FR-SEC-007 — Electron IPC Boundary

**Priority:** P0

The Electron bridge shall avoid exposing arbitrary operating-system execution capabilities to renderer code.

### FR-SEC-008 — Diagnostic Data Protection

**Priority:** P1

Generated diagnostics and reports shall avoid exposing secrets or unnecessary sensitive runtime data.

---

# 29. Representative End-to-End Functional Scenarios

The following scenarios represent major use cases that the framework must support.

## Scenario 1 — New CLI Application

**Given** a developer wants to create a Python application,

**When** a new application is generated using AdharaSutra,

**Then** the generated application shall have a valid project structure, framework bootstrap, registered example action, and executable CLI entry point.

**And** it shall pass applicable baseline architecture checks.

## Scenario 2 — Electron Invokes Python Business Logic

**Given** an Electron application uses the standard bridge,

**When** Electron submits a valid action request,

**Then** AdharaSutra shall validate and route the request to the registered application handler.

**And** return the result using the standard response protocol.

## Scenario 3 — HTTP-Based External Dependency

**Given** an application action requires ComfyUI or LM Studio,

**When** the action invokes its configured integration,

**Then** the framework-managed HTTP infrastructure shall handle the outbound communication.

**And** Electron shall continue using the same CLI communication protocol.

## Scenario 4 — External CLI Dependency

**Given** an application action requires an audio.cpp-style executable,

**When** the action invokes the registered external CLI adapter,

**Then** the framework shall manage process execution, output, timeout, and cleanup.

**And** return standardized results or errors to Electron.

## Scenario 5 — Long-Running Job

**Given** a registered action starts a long-running operation,

**When** the operation executes,

**Then** AdharaSutra shall expose progress and lifecycle events through the configured execution mode.

**And** support cancellation according to the job's capabilities.

## Scenario 6 — Persistent State

**Given** an application defines state that must survive process termination,

**When** the application restarts,

**Then** the framework shall restore the state through the configured persistent storage mechanism, subject to application-defined restoration rules.

## Scenario 7 — Existing Application Inspection

**Given** an existing Python/Electron application,

**When** architecture discovery is executed,

**Then** the framework shall report identifiable modules, entry points, connectors, communication patterns, and state-management mechanisms.

**And** distinguish observed findings from uncertain conclusions.

## Scenario 8 — Architecture Violation

**Given** an application uses a prohibited infrastructure pattern,

**When** architecture verification is executed,

**Then** the verifier shall report the applicable rule violation with source evidence.

**And** return the appropriate verification status.

## Scenario 9 — Existing Application Migration

**Given** a working application with custom CLI and infrastructure code,

**When** a migration plan is generated,

**Then** AdharaSutra shall identify the required adoption changes, affected components, and compatibility requirements.

**And** provide verifiable migration tasks.

## Scenario 10 — Agent-Assisted Migration

**Given** a migration report and current implementation report,

**When** a coding agent consumes those reports,

**Then** the reports shall contain structured findings, source evidence, relevant requirements, and verification instructions sufficient to guide investigation and implementation.

The coding agent remains responsible for examining the actual source code before modifying it.

## Scenario 11 — Failure During External Processing

**Given** an external HTTP service or CLI executable fails,

**When** the failure reaches the framework,

**Then** AdharaSutra shall classify and report the failure using the standard error protocol.

**And** release resources according to the applicable lifecycle policy.

## Scenario 12 — Framework Upgrade

**Given** a consuming application depends on a prior framework version,

**When** the framework is upgraded,

**Then** compatibility checks shall identify incompatible protocol or public interface changes where supported.

**And** relevant upgrade guidance shall be available.

---

# 30. Functional Dependencies

The major framework capabilities have the following logical dependencies.

| Capability | Primary dependencies |
|---|---|
| CLI Runtime | Core runtime, configuration, action registry |
| Electron Bridge | CLI protocol, process lifecycle |
| HTTP Connector | Configuration, lifecycle, error handling |
| External CLI Connector | Process management, lifecycle, errors |
| SQLite Connector | Configuration, persistence lifecycle |
| State Engine | Runtime, concurrency, optional persistence |
| Job Engine | Runtime, state, events, process ownership |
| Architecture Discovery | Source analyzers, project metadata |
| Architecture Verification | Architecture profiles, rule engine, discovery |
| Migration Planning | Discovery, verification, compatibility analysis |
| Scaffolding | Architecture profiles, application templates |
| Reports | Discovery, verification, migration findings |

These dependencies are conceptual. Detailed module dependencies will be finalized during architecture design.

---

# 31. Functional Acceptance Gates

## Gate A — Core Runtime

The framework must demonstrate:

- Application initialization.
- Action registration.
- CLI routing.
- Structured responses.
- Error handling.
- Lifecycle management.

## Gate B — External Integration

The framework must demonstrate:

- HTTP integration.
- External CLI integration.
- SQLite access.
- Connector lifecycle and error handling.

## Gate C — Electron Integration

The framework must demonstrate:

- Standard Electron-to-Python requests.
- Responses and events.
- Process management.
- Cancellation and failure handling.

## Gate D — State and Jobs

The framework must demonstrate:

- Scoped state management.
- Persistent state.
- Job lifecycle.
- Progress reporting.
- Concurrency and cancellation semantics.

## Gate E — Application Generation

The framework must demonstrate:

- New-project scaffolding.
- Valid bootstrap.
- Architecture-compliant project generation.
- Baseline test execution.

## Gate F — Architecture Verification

The framework must demonstrate:

- Architecture profile loading.
- Rule evaluation.
- Evidence-backed findings.
- Machine-readable reports.
- Deterministic verification behavior.

## Gate G — Migration

The framework must demonstrate:

- Existing-project discovery.
- Gap analysis.
- Migration planning.
- Incremental adoption.
- Compatibility preservation.
- Regression and architecture verification.

---

# 32. Functional Requirements Summary

| Group | Requirement area | Count |
|---|---|---:|
| FR-RUN | Application Runtime | 7 |
| FR-CLI | CLI Framework | 10 |
| FR-ELC | Electron Communication | 11 |
| FR-CON | Connector Framework | 8 |
| FR-HTTP | HTTP Connector | 7 |
| FR-EXT | External CLI Connector | 10 |
| FR-DB | SQLite and Persistence | 8 |
| FR-WS | WebSocket Connector | 5 |
| FR-FS | Filesystem | 5 |
| FR-STATE | State Management | 9 |
| FR-JOB | Job Management | 11 |
| FR-CFG | Configuration | 8 |
| FR-ERR | Error Handling | 6 |
| FR-LOG | Logging and Diagnostics | 7 |
| FR-DI | Dependency Management | 6 |
| FR-SCAF | Project Scaffolding | 9 |
| FR-DISC | Architecture Discovery | 11 |
| FR-ARCH | Architecture Verification | 16 |
| FR-MIG | Application Migration | 15 |
| FR-REP | Reporting | 10 |
| FR-TEST | Testing Infrastructure | 9 |
| FR-DEV | Developer Experience | 6 |
| FR-PKG | Packaging and Distribution | 9 |
| FR-DOC | Documentation | 7 |
| FR-SEC | Security Functions | 8 |
| **Total** | **25 requirement groups** | **207** |

These requirements define the proposed full framework scope, not a commitment to implement all capabilities in the first release.

---

# 33. Review and Finalization Requirements

Before this document is approved, the following must be completed:

1. Review all requirements against the framework vision.
2. Identify overlapping or redundant requirements.
3. Identify missing functional capabilities.
4. Validate requirement ownership and scope.
5. Confirm requirement priorities.
6. Distinguish foundational capabilities from future enhancements.
7. Review cross-module dependencies.
8. Ensure requirements are observable and testable.
9. Validate representative Electron, HTTP, CLI, SQLite, state, and migration scenarios.
10. Record unresolved design decisions.
11. Confirm compatibility with existing application adoption.
12. Approve the functional requirements baseline.

Requirements may be refined during subsequent architecture design, but approved changes should remain traceable.

---

# 34. Document Status

**Current status:** Draft  
**Approval status:** Pending review  
**Source document:** `docs/design/vision.md`

**Next recommended document:** `docs/design/non-functional-requirements.md`

The next phase should define measurable quality attributes, including performance, latency, scalability, reliability, portability, memory usage, concurrency, recoverability, security, and maintainability.

---

# 35. Final Principle

AdharaSutra must provide the **common foundation for applications without becoming the owner of their business logic**.

Its functional capabilities must be designed to make application infrastructure standardized, reusable, verifiable, replaceable, and independently maintainable.

The framework's ultimate value is not the number of features it provides, but the extent to which applications can rely on those features instead of repeatedly building and maintaining their own implementations.

**AdharaSutra — Build once. Standardize everywhere.**
