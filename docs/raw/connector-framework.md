# AdharaSutra — Connector Framework Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/connector-framework.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Infrastructure Architecture  
**Architecture Style:** Modular, Ports and Adapters, Capability-Oriented Connectors  
**Primary Language:** Python 3.12+

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`
- `docs/design/electron-integration.md`

---

# 1. Purpose

This document defines the architecture of the AdharaSutra Connector Framework.

The Connector Framework provides standardized infrastructure for applications that communicate with external services, execute external programs, access databases, and interact with local files.

Its primary objectives are to:

1. Eliminate duplicated connection and resource-management infrastructure.
2. Provide consistent connector registration, configuration, lifecycle, and diagnostics.
3. Support specialized interfaces appropriate to each underlying technology.
4. Isolate application business logic from infrastructure implementations.
5. Support optional connectors without loading unnecessary dependencies.
6. Standardize technical error handling, timeouts, and cancellation.
7. Support testing through replaceable connectors and controlled fixtures.
8. Allow reusable service-specific adapters to be developed independently.
9. Maintain compatibility with AdharaSutra's unified CLI protocol.
10. Support incremental migration from custom infrastructure implementations.

The framework owns the technical mechanisms for connecting to external systems.

Consuming applications own the business meaning of operations performed through those connections.

## 1.1 Central Principle

**AdharaSutra standardizes how external dependencies are accessed and managed, while applications define what those dependencies are used for.**

For example:

- AdharaSutra manages HTTP connections; an application defines ComfyUI workflow operations.
- AdharaSutra manages subprocesses; an application defines audio.cpp commands.
- AdharaSutra manages SQLite connections and transactions; an application defines its database schema and repositories.
- AdharaSutra manages WebSocket connections; an application defines the meaning of received messages.

---

# 2. Scope

## 2.1 In Scope

This architecture defines:

- Connector contracts.
- Connector registration.
- Connector identity.
- Configuration and dependency injection.
- Connector lifecycle.
- Resource ownership.
- Connection health and readiness.
- Error classification.
- Timeouts.
- Retries.
- Cancellation.
- Concurrency.
- Resource cleanup.
- HTTP clients.
- WebSocket clients.
- External CLI execution.
- SQLite persistence facilities.
- Filesystem infrastructure.
- Service-specific integration adapters.
- Connector testing.
- Connector diagnostics.
- Optional connector packaging.
- Connector migration.
- Architecture verification rules.

## 2.2 Out of Scope

The Connector Framework does not own:

- Application business rules.
- AI model prompts.
- ComfyUI workflow definitions.
- audio.cpp command semantics.
- LM Studio model selection policies.
- Domain database schemas.
- Business-level transaction policies.
- Application-specific file organization.
- Electron communication transport.
- Application job scheduling.
- Domain-specific retry decisions.

These responsibilities belong to consuming applications or other AdharaSutra subsystems.

---

# 3. Connector Design Principles

## CF-001 — Framework-Managed Infrastructure

Applications shall use framework-provided connector facilities for supported infrastructure categories according to their architecture profile.

## CF-002 — Specialized Capabilities

Connectors shall expose interfaces appropriate to their technology.

A SQLite connector must not be forced into an HTTP-like request interface.

## CF-003 — Common Lifecycle

Managed connectors shall follow consistent registration, initialization, readiness, failure, and cleanup conventions.

## CF-004 — Dependency Isolation

Unused connectors shall not impose their optional dependencies on the core runtime.

## CF-005 — Application Independence

The framework shall not contain consuming application business logic.

## CF-006 — Configuration-Driven Integration

Connector behavior shall be configured through validated framework configuration and explicit registration.

## CF-007 — Explicit Ownership

Every connector instance and resource shall have a defined lifecycle owner.

## CF-008 — Consistent Technical Errors

Connector implementations shall translate infrastructure failures into standardized technical error categories.

## CF-009 — Safe Defaults

Connectors shall use conservative security, timeout, retry, and resource-management defaults.

## CF-010 — Testability

Connector implementations shall support controlled test substitutes and integration fixtures.

## CF-011 — Observable Operations

Connector operations shall support structured diagnostics, correlation, and health reporting.

## CF-012 — Transport Independence

Changing the underlying external connector shall not require changing the standard Electron-to-Python protocol.

## CF-013 — Explicit Retry Semantics

The framework shall not automatically repeat operations that may produce unsafe duplicate side effects.

## CF-014 — Controlled Extensibility

Applications and optional integration packages shall be able to extend connector capabilities through documented interfaces.

## CF-015 — Deterministic Architecture Enforcement

Connector usage conventions shall be verifiable through deterministic analysis wherever technically feasible.

---

# 4. High-Level Connector Architecture

## 4.1 Architecture Diagram

```text
┌─────────────────────────────────────────────┐
│                 ELECTRON                    │
│                                             │
│          AdharaSutra CLI Protocol           │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│             ADHARASUTRA RUNTIME             │
│                                             │
│            Action Registration              │
│                    │                        │
│                    ▼                        │
│          Application Use Cases              │
│                    │                        │
│                    ▼                        │
│         Application-Defined Ports           │
│                    │                        │
│                    ▼                        │
│       Service-Specific Integration Adapters │
│                    │                        │
│                    ▼                        │
│  ┌───────────────────────────────────────┐  │
│  │         CONNECTOR FRAMEWORK           │  │
│  │                                       │  │
│  │  Connector Registry                   │  │
│  │  Connector Lifecycle                  │  │
│  │  Configuration                        │  │
│  │  Health & Diagnostics                 │  │
│  │  Errors & Resource Management         │  │
│  │                  │                    │  │
│  │  ┌───────────────┼─────────────────┐  │  │
│  │  ▼               ▼                 ▼  │  │
│  │ HTTP / WS      External CLI     SQLite │  │
│  │                                    │  │  │
│  │             Filesystem Services    │  │  │
│  └──────────────────┬────────────────────┘  │
└─────────────────────┼───────────────────────┘
                      │
          ┌───────────┼─────────────┐
          ▼           ▼             ▼
      ComfyUI     audio.cpp       SQLite
      LM Studio   Other CLIs      Files
      Other APIs
```

## 4.2 Architecture Boundary

The Connector Framework resides below application-specific integration adapters.

It may be used directly by application infrastructure modules when no service-specific adapter is necessary.

Application domain layers shall depend on application-defined ports rather than concrete framework connector implementations.

## 4.3 Infrastructure Versus Business Responsibility

| Responsibility | Owner |
|---|---|
| Connection creation | Framework |
| Connection cleanup | Framework |
| HTTP request execution | Framework |
| External API endpoint mapping | Application/plugin |
| Executable launching | Framework |
| Executable argument semantics | Application/plugin |
| SQLite connection management | Framework |
| SQL queries for domain entities | Application |
| Technical timeout enforcement | Framework |
| Business deadline policies | Application |
| Low-level retry mechanism | Framework |
| Retry safety and business policy | Application |
| Technical failure mapping | Framework |
| Business failure interpretation | Application |
| Connector health reporting | Framework |
| Business readiness rules | Application |

---

# 5. Connector Classification

AdharaSutra defines the following connector categories.

| Connector | Type | Initial priority | External dependency |
|---|---|---|---|
| HTTP | Network | P0 | HTTPX proposed |
| External CLI | Process | P0 | Python standard library |
| SQLite | Persistence | P0 | Python sqlite3 or approved adapter |
| Filesystem | Storage | P0 | Python standard library |
| WebSocket | Network streaming | P1 | Optional WebSocket client |
| Custom | Extensibility | P1 | Adapter-specific |

The priority classifications indicate the proposed importance of each connector to the full framework design.

They do not mean all connectors must initialize in a minimal application.

## 5.1 Connector Capabilities

Connector implementations may support different capabilities.

Examples:

- Lifecycle management.
- Health checking.
- Request execution.
- Streaming.
- Cancellation.
- Transaction support.
- Persistent sessions.
- File operations.

Capabilities shall be declared explicitly.

The framework must not assume that every connector supports every capability.

---

# 6. Proposed Package Structure

```text
src/adharasutra/connectors/
│
├── __init__.py
├── contracts.py
├── registry.py
├── lifecycle.py
├── capabilities.py
├── configuration.py
├── errors.py
├── health.py
│
├── http/
│   ├── __init__.py
│   ├── client.py
│   ├── configuration.py
│   ├── requests.py
│   ├── responses.py
│   ├── retry.py
│   └── streaming.py
│
├── websocket/
│   ├── __init__.py
│   ├── client.py
│   ├── configuration.py
│   ├── sessions.py
│   └── reconnection.py
│
├── process/
│   ├── __init__.py
│   ├── runner.py
│   ├── executable.py
│   ├── arguments.py
│   ├── environment.py
│   ├── streaming.py
│   ├── cancellation.py
│   └── termination.py
│
├── sqlite/
│   ├── __init__.py
│   ├── database.py
│   ├── connections.py
│   ├── transactions.py
│   ├── migrations.py
│   ├── backup.py
│   └── health.py
│
└── filesystem/
    ├── __init__.py
    ├── paths.py
    ├── directories.py
    ├── temporary.py
    ├── artifacts.py
    └── safety.py
```

This is a proposed logical organization.

Individual files may be combined or separated during implementation without changing the approved module boundaries.

---

# 7. Common Connector Contracts

## 7.1 Purpose

The common connector contracts define how connectors are registered, initialized, managed, and inspected.

They shall not force unrelated operations into one universal method.

## 7.2 Connector Identity

Every connector instance shall have:

- A unique application-scoped identifier.
- A connector category.
- A configuration reference.
- A defined owner.
- A lifecycle state.
- Declared capabilities.

Example configuration:

```yaml
connectors:
  http:
    comfyui:
      base_url: http://127.0.0.1:8188

    lmstudio:
      base_url: http://127.0.0.1:1234

  process:
    audiocpp:
      executable: ./tools/audio-cli

  sqlite:
    application_db:
      path: ./data/application.db
```

The format is illustrative.

The final configuration schema will be defined separately.

## 7.3 Lifecycle Contract

Conceptual Python interface:

```python
from typing import Protocol


class ManagedConnector(Protocol):
    async def start(self) -> None:
        ...

    async def close(self) -> None:
        ...
```

Not all connectors must establish a connection at startup.

For example, an external CLI connector may validate executable configuration and launch a process only when requested.

The lifecycle contract shall distinguish initialization from actual external resource acquisition.

## 7.4 Health Contract

```python
from typing import Protocol


class HealthCheckable(Protocol):
    async def health(self):
        ...
```

Health checks are optional capabilities.

The framework shall not assume a connector without a health-check implementation is unhealthy.

## 7.5 Capability-Oriented Contracts

A connector may implement one or more specialized interfaces.

Examples:

```text
ManagedConnector
       │
       ├── HttpClientCapability
       ├── WebSocketClientCapability
       ├── ProcessExecutionCapability
       ├── TransactionCapability
       └── FileOperationCapability
```

These are separate capability contracts.

They are not required to share a universal `execute()` method.

## 7.6 Synchronous and Asynchronous Operations

The framework shall support appropriate execution styles.

HTTP and WebSocket connectors may expose asynchronous APIs.

SQLite may use synchronous operations internally through a controlled execution strategy.

Filesystem utilities may support synchronous or asynchronous access depending on workload requirements.

The architecture must not introduce asynchronous wrappers that block the event loop while appearing nonblocking.

---

# 8. Connector Registry

**Module:** `adharasutra.connectors.registry`

## 8.1 Purpose

The Connector Registry manages connector definitions and instances within an application.

## 8.2 Responsibilities

- Register connector definitions.
- Validate identifiers.
- Validate configuration.
- Resolve connector dependencies.
- Instantiate connectors.
- Manage lifecycle ownership.
- Expose connector capabilities.
- Detect duplicate registrations.
- Provide connector lookup.
- Coordinate connector cleanup.

## 8.3 Registration Model

Conceptual API:

```python
app.register_connector(
    name="comfyui",
    connector_type="http",
    configuration={
        "base_url": "http://127.0.0.1:8188"
    },
)
```

This is a proposed API shape.

The final interface may use typed connector descriptors rather than dictionaries.

## 8.4 Connector Lookup

Conceptual usage:

```python
http_client = context.connectors.http(
    "comfyui"
)
```

A missing connector shall produce a documented framework error.

## 8.5 Registry Scope

The default registry is application-scoped.

Independent AdharaSutra applications must not unintentionally share connector instances.

## 8.6 Duplicate Registration

Duplicate identifiers within the same registry namespace shall be detected.

An application must not silently replace an existing connector definition.

Explicit override mechanisms may be permitted in test environments.

## 8.7 Connector Dependencies

The registry shall support declared dependencies where needed.

For example, a service-specific adapter may depend on an HTTP connector.

The registry must detect missing dependencies and avoid cyclic initialization.

---

# 9. Connector Lifecycle Architecture

## 9.1 Lifecycle States

Proposed lifecycle:

```text
REGISTERED
    │
    ▼
INITIALIZING
    │
    ▼
READY
    │
    ├────────► DEGRADED
    │
    ├────────► FAILED
    │
    ▼
CLOSING
    │
    ▼
CLOSED
```

## 9.2 State Definitions

| State | Meaning |
|---|---|
| Registered | Definition is known but not initialized |
| Initializing | Initialization is in progress |
| Ready | Connector is initialized and available for supported operations |
| Degraded | Some operations or dependencies are impaired |
| Failed | Connector cannot currently provide required capabilities |
| Closing | Resource cleanup is in progress |
| Closed | Connector lifecycle has ended |

**Important:** `READY` does not necessarily mean that a remote dependency is reachable.

A configured HTTP client may be initialized while ComfyUI is offline.

Connector readiness and external dependency health must be represented separately.

## 9.3 Initialization Strategies

Connectors may use:

### Eager initialization

Initialize before the application becomes ready.

Appropriate for required infrastructure.

### Lazy initialization

Initialize when first used.

Appropriate for optional or expensive resources.

### Conditional initialization

Initialize only when a feature or profile requires the connector.

The strategy must be explicit.

## 9.4 Initialization Ordering

The application runtime shall initialize connectors in dependency order.

Unrelated connectors should not be forced to initialize sequentially unless required.

## 9.5 Partial Startup Failure

If a required connector fails during startup:

1. Record the failure.
2. Prevent application readiness when the dependency is mandatory.
3. Clean up already initialized resources.
4. Report a structured initialization error.

If an optional connector fails, the application may continue in a degraded state according to configuration.

## 9.6 Shutdown Ordering

Connector cleanup should occur in reverse dependency order.

No connector should be closed while a framework-managed operation still legitimately owns its resources unless the shutdown policy requires cancellation.

---

# 10. Connector Resource Ownership

## 10.1 Ownership Principle

Every managed resource must have one clearly defined lifecycle owner.

Examples:

- HTTP client instance.
- WebSocket connection.
- External process.
- SQLite connection.
- Database transaction.
- Temporary file.
- Open file handle.

## 10.2 Resource Scope

Possible scopes:

| Scope | Example |
|---|---|
| Application | HTTP client pool |
| Session | Persistent WebSocket session |
| Request | Temporary request context |
| Job | External process |
| Transaction | SQLite transaction |
| Operation | Temporary file handle |

## 10.3 Application-Owned Connectors

Applications may provide custom connector implementations.

When registered as framework-managed connectors, their lifecycle shall follow AdharaSutra's resource ownership conventions.

## 10.4 Unmanaged Resources

If an application explicitly uses a library outside the connector framework under an approved exception, it must document ownership and cleanup.

The architecture verifier should identify unsupported unmanaged infrastructure patterns where possible.

---

# 11. Connector Configuration

## 11.1 Centralized Configuration

Connector settings shall use the framework configuration system.

## 11.2 Configuration Categories

Typical settings include:

- Connector identifier.
- Enabled state.
- Initialization strategy.
- Endpoint or executable location.
- Timeout settings.
- Retry settings.
- Authentication references.
- Concurrency limits.
- Resource limits.
- Health-check policy.
- Shutdown behavior.

## 11.3 Configuration Validation

Required connector configuration must be validated before initialization.

Invalid configuration must produce actionable errors.

## 11.4 Configuration Isolation

Different applications must not accidentally share connector configuration.

## 11.5 Secret Handling

Credentials shall not be embedded in ordinary committed configuration files.

Connectors should receive credentials through approved protected configuration facilities.

## 11.6 Runtime Reconfiguration

Runtime reconfiguration may be supported, but must define:

- Which settings can change.
- Whether active operations are affected.
- Whether reinitialization is required.
- How configuration changes are validated.
- How failed updates are rolled back.

Automatic runtime reconfiguration is not required for the initial implementation.

---

# 12. Connector Health and Readiness

## 12.1 Health Categories

Connector health should distinguish:

- Healthy.
- Degraded.
- Unavailable.
- Unknown.
- Not checked.

## 12.2 Health Versus Initialization

Initialization state and external dependency health are separate concepts.

For example:

```text
Connector: comfyui
Initialization: READY
Remote Health: UNAVAILABLE
```

This means the framework's HTTP connector is configured and initialized, but the external ComfyUI service cannot be reached.

## 12.3 Health-Check Policies

Health checks may be:

- On demand.
- During startup.
- Periodic.
- Before selected operations.

Periodic health checks must be optional and have controlled resource usage.

## 12.4 Health Results

Health results should contain:

- Connector identifier.
- Health status.
- Check timestamp.
- Check method.
- Failure category where applicable.
- Safe diagnostic details.

## 12.5 Health Limitations

A successful network connection does not guarantee that every service operation will succeed.

The framework must not present a superficial health check as proof of complete service functionality.

---

# 13. Connector Error Architecture

## 13.1 Technical Error Categories

The framework shall define stable technical error categories.

Examples:

```text
CONNECTOR_NOT_FOUND
CONNECTOR_NOT_INITIALIZED
CONNECTOR_UNAVAILABLE
CONNECTOR_CONFIGURATION_INVALID
CONNECTOR_TIMEOUT
CONNECTOR_AUTHENTICATION_FAILED
CONNECTOR_PERMISSION_DENIED
CONNECTOR_RESOURCE_EXHAUSTED
CONNECTOR_EXECUTION_FAILED
CONNECTOR_CANCELLED
CONNECTOR_CLOSED
```

Names are proposed and will be reconciled with `cli-protocol.md`.

## 13.2 Error Mapping

Underlying library exceptions shall be translated into framework connector errors at appropriate boundaries.

## 13.3 Error Information

A connector error should include:

- Error category.
- Safe message.
- Connector identifier.
- Operation context.
- Correlation identifier.
- Retryability when known.
- Original cause for controlled internal diagnostics.

## 13.4 Application-Level Interpretation

Application adapters may translate technical connector errors into domain-specific errors.

For example:

```text
HTTP Connection Failure
        │
        ▼
CONNECTOR_UNAVAILABLE
        │
        ▼
Application Adapter
        │
        ▼
IMAGE_SERVICE_UNAVAILABLE
        │
        ▼
AdharaSutra Error Envelope
```

## 13.5 Error Security

Secrets, authentication tokens, and unnecessary sensitive request data must not be exposed through frontend-facing connector errors.

---

# 14. Timeout Architecture

## 14.1 Timeout Ownership

Timeouts exist at different levels.

| Timeout | Owner |
|---|---|
| Electron request timeout | Electron bridge |
| Framework action deadline | Runtime execution layer |
| HTTP connection timeout | HTTP connector |
| HTTP read timeout | HTTP connector |
| External process timeout | Process connector |
| WebSocket connection timeout | WebSocket connector |
| Database busy timeout | SQLite connector |
| Job deadline | Job manager |

## 14.2 Deadline Propagation

Where supported, an execution deadline should propagate from the application operation into connector operations.

Connector-specific timeouts must not silently exceed an explicitly enforced remaining operation deadline.

## 14.3 Timeout Semantics

A timeout does not prove that an external operation had no effect.

The framework shall preserve unknown outcomes when necessary.

## 14.4 Default Values

Actual timeout values shall be configurable and chosen according to connector type.

Global defaults must not assume that every operation is short-running.

---

# 15. Retry Architecture

## 15.1 Retry Principle

Retries are technical mechanisms with potential business consequences.

The framework may execute a configured retry policy, but the application must determine whether repeating an operation is safe.

## 15.2 Retry Configuration

Potential settings:

- Maximum attempts.
- Delay.
- Backoff strategy.
- Maximum delay.
- Eligible failures.
- Overall deadline.
- Idempotency constraints.

## 15.3 Automatic Retry Restrictions

The framework must not automatically retry potentially non-idempotent operations unless a safe retry policy is explicitly declared.

Examples requiring special care:

- HTTP POST requests.
- External CLI commands that modify files.
- Database writes.
- Operations that start external processing jobs.

## 15.4 Retry Observability

Retry attempts should be traceable without exposing sensitive operation payloads.

## 15.5 Retry Exhaustion

After exhausting permitted retries, the connector shall return the final failure with relevant attempt metadata.

---

# 16. Cancellation Architecture

## 16.1 Cancellation Ownership

Application or job execution may request cancellation.

Connectors implement their supported cancellation mechanisms.

## 16.2 Cancellation Behavior

Different connector types require different approaches.

| Connector | Typical behavior |
|---|---|
| HTTP | Cancel local pending request |
| WebSocket | Stop receiving or close session |
| External CLI | Request process termination |
| SQLite | Interrupt supported operations or roll back transaction |
| Filesystem | Stop cancellable operations where possible |

## 16.3 Cancellation Accuracy

Cancelling the local operation does not necessarily cancel an already accepted operation on the remote service.

For example, stopping an HTTP request does not automatically terminate image generation already started inside ComfyUI.

The application-specific adapter must implement any supported remote cancellation operation.

## 16.4 Cancellation Outcomes

The framework should distinguish:

- Requested.
- Acknowledged.
- Completed.
- Unsupported.
- Failed.
- Already completed.

## 16.5 Cleanup

Cancelled operations shall release framework-owned resources according to their lifecycle contract.

---

# 17. HTTP Connector Architecture

**Module:** `adharasutra.connectors.http`

**Priority:** P0

## 17.1 Purpose

Provide reusable outbound HTTP communication.

## 17.2 Recommended Implementation

HTTPX is the proposed underlying HTTP library.

The public connector contract should not expose unnecessary dependencies on HTTPX-specific implementation details.

## 17.3 Responsibilities

- HTTP client creation.
- Connection pooling.
- Base URL management.
- Request execution.
- Headers.
- Query parameters.
- Request bodies.
- Authentication configuration.
- Timeouts.
- Controlled retries.
- Response handling.
- Streaming.
- Error mapping.
- Resource cleanup.

## 17.4 Conceptual API

```python
client = context.connectors.http("comfyui")

response = await client.post(
    "/prompt",
    json={"prompt": workflow},
)
```

This is illustrative and does not finalize the connector API.

## 17.5 HTTP Client Lifetime

The default HTTP client should be reusable within its configured lifecycle scope.

A new client instance should not be created for every operation unless explicitly required.

## 17.6 Request Methods

The connector should support standard HTTP request methods and appropriate request bodies.

## 17.7 Streaming

The connector shall support streaming response bodies without requiring the entire response in memory.

## 17.8 Authentication

Supported authentication behavior may include:

- Static headers.
- Bearer tokens.
- Basic authentication where explicitly configured.
- Custom authentication providers.

Credential storage belongs to the configuration and secret-handling facilities.

## 17.9 HTTP Response Ownership

The connector returns technical response information.

Application adapters interpret endpoint-specific response structures.

## 17.10 HTTP Error Handling

Transport errors must be distinguishable from valid HTTP responses with non-success status codes.

The framework should not automatically interpret every application-specific HTTP status as a framework error.

## 17.11 Example Integration

```text
Application Image Use Case
          │
          ▼
ComfyUI Adapter
          │
          ▼
AdharaSutra HTTP Connector
          │
          ▼
ComfyUI HTTP API
```

The application or optional plugin owns the ComfyUI API mapping.

---

# 18. WebSocket Connector Architecture

**Module:** `adharasutra.connectors.websocket`

**Priority:** P1

## 18.1 Purpose

Provide managed outbound WebSocket connections.

## 18.2 Responsibilities

- Connection creation.
- Connection lifecycle.
- Message sending.
- Message reception.
- Connection timeouts.
- Close handling.
- Failure detection.
- Optional reconnection.
- Event subscription.
- Resource cleanup.

## 18.3 Conceptual API

```python
socket = context.connectors.websocket("comfyui")

async for message in socket.messages():
    handle_message(message)
```

This is illustrative.

## 18.4 Message Interpretation

The connector owns WebSocket transport behavior.

Applications interpret service-specific message structures.

## 18.5 Reconnection

Reconnection must be configurable.

Reconnecting a WebSocket connection must not automatically replay messages or business actions without an explicit policy.

## 18.6 Backpressure

Incoming messages must use bounded buffering or another controlled flow-management strategy.

## 18.7 Session Ownership

The connector must explicitly define whether a WebSocket connection is:

- Application-scoped.
- Session-scoped.
- Job-scoped.

## 18.8 Example Integration

```text
Application Job
       │
       ▼
ComfyUI Adapter
       │
       ▼
WebSocket Connector
       │
       ▼
ComfyUI Progress Events
       │
       ▼
Application Progress Mapping
       │
       ▼
AdharaSutra Job Events
```

---

# 19. External CLI Connector Architecture

**Module:** `adharasutra.connectors.process`

**Priority:** P0

## 19.1 Purpose

Provide safe and reusable execution of external programs.

This module is a foundational capability for applications using audio.cpp and similar external tools.

## 19.2 Responsibilities

- Executable discovery.
- Executable validation.
- Argument construction.
- Environment configuration.
- Working directory management.
- Process creation.
- stdin handling.
- stdout capture.
- stderr capture.
- Streaming output.
- Exit-code interpretation.
- Timeout enforcement.
- Cancellation.
- Process-tree cleanup.
- Resource ownership.

## 19.3 Component Architecture

```text
External CLI Connector
│
├── Executable Resolver
├── Execution Configuration
├── Argument Validation
├── Environment Builder
├── Process Runner
├── stdin Writer
├── stdout Reader
├── stderr Reader
├── Streaming Dispatcher
├── Timeout Controller
├── Cancellation Controller
└── Process Cleanup
```

## 19.4 Conceptual API

```python
runner = context.connectors.process("audiocpp")

result = await runner.run(
    executable="audio-cli",
    args=[
        "--input", input_path,
        "--output", output_path,
    ],
)
```

The executable name and arguments are illustrative.

They are not verified audio.cpp commands.

## 19.5 Executable Resolution

The connector shall support controlled executable discovery.

Possible sources:

- Explicit configuration.
- Application-managed tool directories.
- Bundled executable manifests.
- Approved system executable paths.

## 19.6 Argument Safety

Arguments shall be represented as structured sequences.

Shell execution shall be disabled by default.

## 19.7 Environment Variables

The connector shall support explicit environment configuration.

Sensitive variables should not be logged.

## 19.8 Streaming

The connector shall support incremental stdout and stderr processing.

Streams must be drained appropriately to avoid subprocess deadlocks caused by full operating-system pipe buffers.

## 19.9 Exit Codes

The connector reports raw exit status and technical execution metadata.

Service-specific adapters interpret executable-specific exit-code semantics.

## 19.10 Cancellation

The connector shall support controlled termination.

Platform-specific termination behavior must be isolated.

## 19.11 Process Trees

The connector must document whether child-process termination includes descendant processes.

Windows, Linux, and macOS may require different mechanisms.

## 19.12 Interactive Processes

Persistent interactive external processes may be supported through an additional capability interface.

This must not be confused with the AdharaSutra Electron-to-Python CLI session.

## 19.13 Example Integration

```text
Application Audio Use Case
          │
          ▼
AudioCpp Adapter
          │
          ▼
AdharaSutra Process Connector
          │
          ▼
audio.cpp Executable
          │
          ▼
Exit Status / Output
          │
          ▼
Application Result
```

---

# 20. SQLite Connector Architecture

**Module:** `adharasutra.connectors.sqlite`

**Priority:** P0

## 20.1 Purpose

Provide reusable SQLite connection, transaction, and persistence infrastructure.

## 20.2 Responsibilities

- Database location resolution.
- Connection lifecycle.
- Connection configuration.
- Transaction handling.
- Concurrency management.
- Schema migration support.
- Backup and integrity facilities.
- Error mapping.
- Resource cleanup.

## 20.3 Application Ownership

Applications own:

- Database schema definitions.
- Domain repositories.
- SQL queries.
- Domain data mapping.
- Business transaction boundaries.
- Migration content.

AdharaSutra owns the generic execution mechanisms.

## 20.4 Conceptual API

```python
database = context.connectors.sqlite(
    "application_db"
)

with database.transaction() as tx:
    tx.execute(
        "INSERT INTO items(name) VALUES (?)",
        ("example",),
    )
```

This is illustrative synchronous pseudocode.

The final design must explicitly define synchronous and asynchronous execution models.

## 20.5 Connection Ownership

The SQLite connector must define how connections are scoped.

SQLite connections must not be shared unsafely across threads or concurrent execution contexts.

## 20.6 Transaction Semantics

Transactions shall have explicit ownership.

The framework must define:

- Commit behavior.
- Rollback behavior.
- Nested transaction policy.
- Exception handling.
- Connection cleanup.

## 20.7 Concurrency

The connector must account for SQLite's concurrency characteristics.

Potential mechanisms include:

- Controlled connection ownership.
- Configurable busy timeout.
- Serialized writes where appropriate.
- Explicit transaction scopes.
- Optional WAL configuration.

No universal concurrency configuration should be imposed without evaluating consuming application workloads.

## 20.8 Schema Migrations

The connector shall provide or integrate with a schema migration mechanism.

Application-specific migration scripts remain application-owned.

## 20.9 Backups

Backup facilities must support consistent database snapshots through an appropriate SQLite backup mechanism.

Raw file copying while the database is active must not be assumed safe for every configuration.

## 20.10 Example Integration

```text
Application Use Case
        │
        ▼
Repository Port
        │
        ▼
SQLite Repository Adapter
        │
        ▼
AdharaSutra SQLite Connector
        │
        ▼
Application Database
```

---

# 21. Filesystem Connector Architecture

**Module:** `adharasutra.connectors.filesystem`

**Priority:** P0

## 21.1 Purpose

Provide reusable local filesystem facilities.

## 21.2 Responsibilities

- Application data directory resolution.
- Configuration directory resolution.
- Cache directory resolution.
- Temporary directory management.
- Path validation.
- File operations.
- Artifact references.
- Resource cleanup.
- Cross-platform path handling.

## 21.3 Application Directories

The framework shall support logical directories such as:

```text
application_data
application_config
application_cache
application_logs
application_temp
application_outputs
```

Actual filesystem paths are platform- and application-specific.

## 21.4 Path Safety

The connector shall validate paths against configured access boundaries.

Validation must account for:

- Relative paths.
- Absolute paths.
- Path traversal.
- Symbolic links.
- Resolved targets.
- Platform-specific path behavior.

Where operations are security-sensitive, the implementation must account for race conditions between path validation and file access.

## 21.5 Temporary Resources

Temporary files and directories shall have explicit ownership and cleanup policies.

## 21.6 Artifact Management

Generated files may be represented through managed artifact descriptors.

Example:

```json
{
  "artifact_id": "artifact-001",
  "type": "file",
  "path": "outputs/generated.wav",
  "media_type": "audio/wav"
}
```

Artifact access must not grant unrestricted filesystem capabilities to Electron renderer code.

## 21.7 Large File Operations

Large file operations should support streaming or chunked processing where practical.

The connector must not unnecessarily load entire large files into memory.

## 21.8 Application-Specific File Operations

The application owns domain-specific file organization.

For example:

- Audio segments.
- Generated comic-panel assets.
- Model output directories.
- Project files.

The framework provides generic file-management mechanisms.

---

# 22. Service-Specific Integration Adapters

## 22.1 Purpose

Service-specific adapters translate application operations into connector operations.

## 22.2 Adapter Ownership

Adapters may be:

- Application-owned.
- Distributed as optional AdharaSutra integration plugins.

They must not introduce a competing framework runtime.

## 22.3 ComfyUI Adapter

Potential responsibilities:

- Workflow submission.
- Workflow-specific request mapping.
- Workflow identifiers.
- Progress interpretation.
- Result retrieval.
- Remote cancellation where supported.

Uses:

- HTTP connector.
- WebSocket connector.

## 22.4 LM Studio Adapter

Potential responsibilities:

- Model listing.
- Inference endpoint mapping.
- Prompt submission.
- Streaming token handling.
- Model-related result interpretation.

Uses:

- HTTP connector.
- Optional streaming capabilities.

## 22.5 audio.cpp Adapter

Potential responsibilities:

- Command selection.
- Argument mapping.
- Output-file conventions.
- Exit-code interpretation.
- Progress parsing.
- Tool-specific cancellation behavior.

Uses:

- External CLI connector.
- Filesystem facilities.

## 22.6 Adapter Interface Example

```python
from typing import Protocol


class ImageGenerationPort(Protocol):
    async def generate(self, request):
        ...
```

An application-specific adapter implements the port using framework connectors.

## 22.7 Adapter Replacement

Changing the implementation of a port should not require modifying:

- Domain entities.
- Electron transport.
- CLI request framing.
- Framework action routing.

Business contract changes remain subject to application compatibility rules.

---

# 23. Connector Dependency Injection

## 23.1 Composition Principle

Connector instances are created and managed by the framework.

Application services receive connector capabilities through the application composition root.

## 23.2 Preferred Dependency Flow

```text
Application Composition Root
          │
          ▼
Framework Connector Registry
          │
          ▼
Concrete Connector
          │
          ▼
Application Adapter
          │
          ▼
Application Use Case
```

## 23.3 Explicit Dependencies

Application use cases should depend on declared ports rather than performing arbitrary connector registry lookups.

## 23.4 Test Substitution

Connector dependencies must be replaceable with fakes or mocks.

## 23.5 Avoiding Service Locator Coupling

The global application context should not become the primary dependency mechanism inside domain services.

Connector lookup belongs primarily at composition and infrastructure boundaries.

---

# 24. Connector Concurrency and Backpressure

## 24.1 Concurrency Limits

Connectors may declare limits for:

- Active HTTP requests.
- WebSocket sessions.
- External processes.
- SQLite operations.
- Filesystem transfers.

## 24.2 Queue Management

Queued connector operations must use bounded buffering or explicit admission control.

## 24.3 Resource Exhaustion

The framework shall report resource exhaustion rather than allowing unlimited resource growth.

## 24.4 Backpressure

Streaming connectors must support backpressure or bounded-buffer behavior appropriate to their transport.

## 24.5 Cancellation Under Load

Cancellation requests should remain serviceable when possible, even under high operation load.

## 24.6 Independent Limits

An HTTP connector's concurrency limit should not automatically restrict unrelated SQLite or process operations.

---

# 25. Connector Observability

## 25.1 Diagnostic Metadata

Connector operations should support:

- Connector ID.
- Operation category.
- Request ID.
- Job ID.
- Start time.
- Duration.
- Outcome.
- Error category.

## 25.2 Logging

The framework should provide structured connector diagnostics.

## 25.3 Sensitive Data

Logs must avoid exposing:

- Authentication tokens.
- Passwords.
- Secret configuration values.
- Sensitive request bodies by default.

## 25.4 Metrics

Optional metrics may include:

- Active connections.
- Request counts.
- Error counts.
- Process execution durations.
- Retry attempts.
- Queue sizes.

Advanced telemetry must remain optional.

## 25.5 Health Reporting

The connector registry should provide a consolidated health report without forcing every connector to perform expensive live checks.

---

# 26. Connector Testing Strategy

## 26.1 Testing Levels

Connectors shall support:

- Unit tests.
- Contract tests.
- Integration tests.
- Failure tests.
- Cancellation tests.
- Resource cleanup tests.
- Cross-platform tests where applicable.

## 26.2 Common Connector Contract Tests

Verify:

- Registration.
- Configuration validation.
- Initialization.
- Lifecycle transitions.
- Error classification.
- Cleanup.
- Health capability behavior.
- Dependency isolation.

## 26.3 HTTP Connector Tests

Verify:

- Supported request methods.
- Request timeout.
- Connection failure.
- Authentication configuration.
- Retry eligibility.
- Streaming.
- Cleanup.

Use controlled mock or local HTTP services.

## 26.4 WebSocket Connector Tests

Verify:

- Connection establishment.
- Message delivery.
- Connection closure.
- Reconnection behavior.
- Invalid messages.
- Backpressure.

## 26.5 External CLI Connector Tests

Verify:

- Executable discovery.
- Argument safety.
- stdout/stderr capture.
- Streaming.
- Exit codes.
- Timeouts.
- Cancellation.
- Process cleanup.
- Paths containing spaces.
- Platform-specific termination.

Use controlled test executables rather than requiring audio.cpp in every test run.

## 26.6 SQLite Connector Tests

Verify:

- Transactions.
- Rollback.
- Connection ownership.
- Busy handling.
- Concurrency behavior.
- Schema migrations.
- Backup and recovery.

## 26.7 Filesystem Tests

Verify:

- Path validation.
- Temporary cleanup.
- Symbolic links.
- Traversal prevention.
- Large file handling.
- Artifact lifetime.

## 26.8 Adapter Tests

Application-specific adapters should be tested against connector test doubles.

Live ComfyUI, LM Studio, or audio.cpp tests should be separate optional integration suites.

---

# 27. Connector Architecture Verification

## 27.1 Purpose

The architecture verifier shall detect supported patterns that violate connector conventions.

## 27.2 Proposed Rules

| Rule ID | Rule |
|---|---|
| CF-VER-001 | Core runtime must not import optional connector implementations |
| CF-VER-002 | Application domain must not import concrete connector implementations |
| CF-VER-003 | Connector implementations must not import application business modules |
| CF-VER-004 | External HTTP operations follow approved framework connector policy |
| CF-VER-005 | External CLI execution follows framework process policy |
| CF-VER-006 | SQLite connection lifecycle follows framework persistence policy |
| CF-VER-007 | Connector registrations have valid identifiers |
| CF-VER-008 | Connector configuration satisfies declared schemas |
| CF-VER-009 | Optional dependencies do not leak into unrelated imports |
| CF-VER-010 | Connector lifecycle ownership is declared |
| CF-VER-011 | Service-specific adapters use approved connector interfaces |
| CF-VER-012 | Unapproved shell execution is detected |
| CF-VER-013 | Relevant connector resources have cleanup mechanisms |
| CF-VER-014 | Connector exceptions and baselines are documented |
| CF-VER-015 | Connector test coverage requirements are satisfied |
| CF-VER-016 | Connector configuration does not contain prohibited embedded secrets |

## 27.3 Verification Limitations

Static verification cannot prove every runtime behavior.

For example, the existence of a `close()` method does not prove that cleanup occurs correctly.

Runtime tests are required for lifecycle, cancellation, and concurrency guarantees.

## 27.4 Verification Status

Applicable checks shall report:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

---

# 28. Existing Application Connector Migration

## 28.1 Migration Goal

Existing applications should be able to replace duplicated infrastructure without changing domain behavior unnecessarily.

## 28.2 Discovery

The migration engine should identify:

- Direct HTTPX usage.
- Direct subprocess usage.
- Direct SQLite connections.
- Custom WebSocket clients.
- Custom filesystem utilities.
- Custom retry logic.
- Custom connector error handling.
- Custom lifecycle management.

## 28.3 Migration Sequence

```text
Existing Application
         │
         ▼
Discover Infrastructure
         │
         ▼
Identify Connector Responsibilities
         │
         ▼
Record Existing Behavior
         │
         ▼
Introduce Framework Connector
         │
         ▼
Adapt Existing Integration
         │
         ▼
Verify Compatibility
         │
         ▼
Remove Duplicated Infrastructure
```

## 28.4 Migration Principles

- Preserve existing behavior.
- Preserve configuration compatibility where required.
- Preserve database integrity.
- Preserve external command argument semantics.
- Preserve output formats.
- Preserve cancellation behavior.
- Preserve error behavior where relied upon by consumers.

## 28.5 Compatibility Adapters

Existing infrastructure may be wrapped temporarily rather than replaced immediately.

## 28.6 Migration Verification

The migration must include relevant regression and integration tests.

Architecture compliance alone is not sufficient to prove migration correctness.

---

# 29. Optional Dependency and Distribution Strategy

## 29.1 Initial Strategy

Use a modular Python distribution with optional dependencies.

## 29.2 Proposed Installation Patterns

```bash
pip install adharasutra
```

HTTP capability:

```bash
pip install "adharasutra[http]"
```

WebSocket capability:

```bash
pip install "adharasutra[websocket]"
```

Development tooling:

```bash
pip install "adharasutra[devtools]"
```

These are proposed installation interfaces, not published package claims.

## 29.3 Core Dependency Isolation

A minimal AdharaSutra application must not require HTTPX, WebSocket libraries, or development analyzers unless it uses features that need them.

## 29.4 Independent Integration Packages

Service-specific adapters may eventually be distributed separately.

Examples:

```text
adharasutra-comfyui
adharasutra-lmstudio
adharasutra-audiocpp
```

These names are proposed.

## 29.5 Version Compatibility

Plugins and optional adapters must declare their compatible AdharaSutra public API versions.

---

# 30. Connector Configuration Example

The following illustrates a possible application configuration.

```yaml
application:
  name: example-app
  version: 1.0.0

connectors:

  http:
    comfyui:
      enabled: true
      base_url: http://127.0.0.1:8188
      timeout_seconds: 30
      initialization: lazy

    lmstudio:
      enabled: true
      base_url: http://127.0.0.1:1234
      timeout_seconds: 60
      initialization: lazy

  websocket:
    comfyui_events:
      enabled: true
      url: ws://127.0.0.1:8188/ws
      initialization: lazy

  process:
    audiocpp:
      enabled: true
      executable: ./tools/audio-cli
      timeout_seconds: 600
      initialization: lazy

  sqlite:
    application_db:
      enabled: true
      path: ./data/application.db

  filesystem:
    outputs:
      root: ./outputs
```

All endpoints, paths, executable names, and settings are illustrative.

The final connector configuration schema will be specified separately.

---

# 31. End-to-End Connector Scenarios

## Scenario CF-S01 — HTTP-Based Image Generation

**Given** an application has registered a ComfyUI HTTP adapter,

**When** an image-generation use case invokes the adapter,

**Then** the adapter shall use AdharaSutra's managed HTTP connector.

**And** the application shall receive a technical result or classified failure.

**And** Electron shall continue using the standard CLI protocol.

## Scenario CF-S02 — WebSocket Progress

**Given** an application uses a WebSocket-based progress source,

**When** the external service publishes progress,

**Then** the connector shall deliver received messages to the application adapter.

**And** the application shall interpret those messages.

**And** relevant progress may be published through AdharaSutra's job event facilities.

## Scenario CF-S03 — External CLI Execution

**Given** an application uses an audio.cpp-style executable,

**When** an audio use case runs,

**Then** the framework shall manage subprocess creation, output capture, and cleanup.

**And** the application adapter shall interpret tool-specific output.

## Scenario CF-S04 — SQLite Transaction

**Given** a repository needs to persist domain data,

**When** a transaction executes,

**Then** AdharaSutra shall manage connection and transaction infrastructure.

**And** the application repository shall implement domain-specific SQL operations.

## Scenario CF-S05 — Optional Connector Unavailable

**Given** an optional ComfyUI connector is unavailable,

**When** the application initializes,

**Then** unrelated application capabilities may remain available according to configuration.

**And** the connector health state shall report the dependency's unavailability.

## Scenario CF-S06 — Connector Cancellation

**Given** a managed external process is running,

**When** cancellation is requested,

**Then** the process connector shall attempt the configured termination procedure.

**And** report the actual cancellation outcome.

## Scenario CF-S07 — Retry Safety

**Given** a potentially non-idempotent external operation,

**When** a timeout occurs,

**Then** the framework shall not automatically retry without an explicitly approved safe retry policy.

## Scenario CF-S08 — Connector Replacement

**Given** a use case depends on an application-defined port,

**When** the application replaces its adapter implementation,

**Then** domain use cases shall not need to change merely because the external transport changes.

## Scenario CF-S09 — Resource Cleanup

**Given** an application is shutting down,

**When** connector cleanup begins,

**Then** framework-owned resources shall be released in an appropriate dependency order.

## Scenario CF-S10 — Minimal Application

**Given** an application uses only the core CLI runtime,

**When** it starts,

**Then** it shall not initialize unused HTTP, WebSocket, SQLite, or external process facilities.

## Scenario CF-S11 — Connector Failure Isolation

**Given** one optional connector fails,

**When** another unrelated connector is used,

**Then** the unrelated connector should remain usable when its dependencies and application runtime remain healthy.

## Scenario CF-S12 — Existing Application Migration

**Given** an existing application has custom HTTP, subprocess, and SQLite infrastructure,

**When** AdharaSutra connectors are introduced incrementally,

**Then** existing business behavior shall remain verifiable.

**And** duplicated infrastructure may be removed after successful regression testing.

---

# 32. Connector Performance Requirements

Connector infrastructure must follow the approved non-functional requirements.

Proposed goals include:

| Metric | Expected behavior |
|---|---|
| Initialization | Avoid unnecessary startup overhead |
| HTTP | Reuse connections where appropriate |
| External CLI | Avoid unnecessary intermediate processes |
| WebSocket | Use bounded message buffering |
| SQLite | Avoid unsafe concurrent connection sharing |
| Filesystem | Support large-file streaming |
| Memory | Release unused resources |
| Cancellation | Avoid indefinite blocking |
| Diagnostics | Minimize runtime overhead |
| Optional dependencies | Remain unloaded unless required |

Numerical performance targets must be benchmarked separately for each connector category.

---

# 33. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| CF-D01 | Connector model | Capability-oriented |
| CF-D02 | Shared connector behavior | Registration, lifecycle, health, errors |
| CF-D03 | Connector registry | Application-scoped |
| CF-D04 | Initialization | Eager/lazy/conditional |
| CF-D05 | HTTP implementation | HTTPX |
| CF-D06 | WebSocket implementation | Optional client adapter |
| CF-D07 | External CLI implementation | Managed Python subprocess |
| CF-D08 | SQLite implementation | Standard SQLite with controlled execution strategy |
| CF-D09 | Filesystem implementation | Python standard library and platform-aware utilities |
| CF-D10 | Connector dependency policy | Optional dependencies |
| CF-D11 | Service-specific APIs | Application or integration plugins |
| CF-D12 | Error model | Shared technical errors |
| CF-D13 | Retry policy | Explicit and safety-aware |
| CF-D14 | Cancellation | Capability-specific |
| CF-D15 | Health checking | Optional, independent of readiness |
| CF-D16 | Testability | Replaceable connector implementations |
| CF-D17 | Architecture verification | Deterministic-first |
| CF-D18 | Distribution | Modular monolith initially |
| CF-D19 | Resource ownership | Explicit lifecycle scopes |
| CF-D20 | Remote operation cancellation | Application adapter responsibility |

These decisions remain proposed until reviewed and validated.

---

# 34. Outstanding Questions

## CF-OQ-001 — Connector Registration API

Should the public API use typed connector descriptors, declarative configuration, or both?

**Recommendation:** Support typed registration with configuration-file integration.

## CF-OQ-002 — Connector Initialization

Should all connectors default to lazy initialization?

**Recommendation:** Default optional connectors to lazy initialization and allow required connectors to use eager initialization.

## CF-OQ-003 — SQLite Execution Model

Should SQLite operations be synchronous, asynchronous through an adapter, or both?

**Recommendation:** Define the supported concurrency model after testing representative workloads. Avoid pretending synchronous operations are nonblocking.

## CF-OQ-004 — HTTP Retry Defaults

Should common HTTP requests retry automatically?

**Recommendation:** Default to conservative behavior and require explicit eligibility for retries that may repeat side effects.

## CF-OQ-005 — Connector Health

Should health checks run periodically by default?

**Recommendation:** Prefer on-demand checks initially, with optional scheduled checks.

## CF-OQ-006 — External CLI Sessions

Should the process connector support persistent interactive subprocesses in the initial release?

**Recommendation:** Implement ordinary subprocess execution first and add persistent sessions when required by a concrete application.

## CF-OQ-007 — Filesystem Ownership

Should filesystem operations be represented as a connector or as a separate framework service?

**Recommendation:** Retain them as a framework infrastructure capability, but review whether a connector lifecycle adds meaningful value to ordinary file utilities.

## CF-OQ-008 — Connector Plugins

Should service-specific integrations ship with the framework or separately?

**Recommendation:** Keep the core generic and distribute service-specific adapters separately when reuse justifies it.

## CF-OQ-009 — Connector Configuration Changes

Should connectors support live reconfiguration?

**Recommendation:** Defer automatic hot reconfiguration until lifecycle and concurrency semantics are validated.

## CF-OQ-010 — Artifact Management

Should generated artifacts be managed inside filesystem services or through a dedicated artifact-management module?

**Recommendation:** Begin with lightweight artifact facilities and split them out if retention, indexing, sharing, or lifecycle complexity grows.

## CF-OQ-011 — Transaction Integration

Should the application runtime provide a higher-level unit-of-work abstraction above the SQLite connector?

**Recommendation:** Evaluate based on actual repository and transaction requirements rather than imposing an ORM-like abstraction prematurely.

## CF-OQ-012 — Cross-Connector Transactions

Should AdharaSutra coordinate transactions involving SQLite, files, and external HTTP services?

**Recommendation:** Do not promise distributed atomic transactions. Applications should coordinate compensating operations or recovery workflows where necessary.

---

# 35. Functional Requirements Traceability

| Requirement group | Connector responsibility |
|---|---|
| FR-CON | Connector contracts, registry, lifecycle |
| FR-HTTP | HTTP connector |
| FR-EXT | External process connector |
| FR-DB | SQLite connector |
| FR-WS | WebSocket connector |
| FR-FS | Filesystem facilities |
| FR-CFG | Connector configuration |
| FR-ERR | Technical error mapping |
| FR-LOG | Connector diagnostics |
| FR-DI | Connector composition |
| FR-STATE | Persistence adapters |
| FR-JOB | Job execution integrations |
| FR-SEC | Connector security controls |
| FR-TEST | Connector contract testing |
| FR-DISC | Connector usage discovery |
| FR-ARCH | Connector architecture verification |
| FR-MIG | Existing connector migration |

---

# 36. Non-Functional Requirements Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-PERF | Connection reuse and efficient execution |
| NFR-RES | Lifecycle ownership and bounded resources |
| NFR-REL | Failure isolation and classified errors |
| NFR-AVAIL | Health checks and optional degradation |
| NFR-SCALE | Configurable concurrency and backpressure |
| NFR-SEC | Safe process and filesystem operations |
| NFR-PORT | Platform-aware connector implementations |
| NFR-MAINT | Specialized interfaces and clear ownership |
| NFR-EXT | Custom connector extension points |
| NFR-TEST | Test doubles and controlled fixtures |
| NFR-COMP | Stable public capability interfaces |
| NFR-ARCH | Deterministic connector usage rules |
| NFR-MIG | Incremental infrastructure replacement |
| NFR-OBS | Structured diagnostics and correlation |

---

# 37. Connector Framework Acceptance Criteria

The connector architecture may be approved when:

- [ ] Common connector contracts are defined.
- [ ] Connector identity and registration rules are defined.
- [ ] Lifecycle states are consistent.
- [ ] Initialization and remote health are distinguished.
- [ ] Connector ownership and cleanup are explicit.
- [ ] Optional dependencies remain isolated.
- [ ] HTTP capabilities are clearly defined.
- [ ] WebSocket capabilities are clearly defined.
- [ ] External process execution is safely managed.
- [ ] SQLite ownership and transaction semantics are defined.
- [ ] Filesystem security boundaries are addressed.
- [ ] Connector-specific cancellation is supported where feasible.
- [ ] Retry behavior accounts for side effects.
- [ ] Timeout ownership is clear.
- [ ] Configuration is validated.
- [ ] Technical error categories are standardized.
- [ ] Application-specific adapters remain separate.
- [ ] Domain layers remain infrastructure-independent.
- [ ] Connector testing strategies are defined.
- [ ] Architecture verification rules are identifiable.
- [ ] Existing applications have a feasible migration path.
- [ ] Connector health reporting is meaningful.
- [ ] Cross-platform behavior is considered.
- [ ] Major architectural risks are documented.
- [ ] Critical unresolved decisions are approved or explicitly deferred.

---

# 38. Final Architecture Summary

AdharaSutra's Connector Framework provides a common infrastructure foundation for external communication, process execution, database access, and filesystem management.

It establishes consistent mechanisms for:

- Registration.
- Configuration.
- Lifecycle.
- Resource ownership.
- Health reporting.
- Technical errors.
- Timeouts.
- Cancellation.
- Retry policies.
- Diagnostics.
- Testing.
- Architecture verification.

Connectors retain specialized interfaces appropriate to their technology.

HTTP, WebSocket, external CLI, SQLite, and filesystem operations are not forced into an artificial universal execution API.

Applications and optional integration plugins define service-specific behavior through adapters built on top of these connector facilities.

The Connector Framework does not change the standard Electron-to-Python protocol.

Applications use the same AdharaSutra runtime and action-routing system regardless of how their external dependencies operate.

The fundamental architectural principle is:

**One managed infrastructure foundation. Specialized connector capabilities. Application-owned business behavior.**

---

# 39. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending connector architecture review

**Next Document:** `docs/design/state-management.md`

The next document should define state scopes, state ownership, concurrent updates, subscriptions, persistence adapters, state restoration, lifecycle integration, and how application business state remains separate from framework runtime state.

---

**AdharaSutra — Build once. Standardize everywhere.**
