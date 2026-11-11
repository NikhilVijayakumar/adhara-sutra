# AdharaSutra — Module Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/module-architecture.md`  
**Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Module Architecture  
**Architecture Style:** Framework-First, Modular Monolith, Ports and Adapters  
**Primary Language:** Python 3.12+  
**Frontend Integration:** Electron through a shared CLI protocol

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`

---

# 1. Purpose

This document defines the internal module architecture of AdharaSutra.

It establishes:

1. Module boundaries and responsibilities.
2. Public and internal interfaces.
3. Module dependencies and dependency direction.
4. Runtime composition and ownership.
5. Mandatory and optional modules.
6. Application extension mechanisms.
7. Communication between framework components.
8. State, job, and connector ownership.
9. Separation between production and development tooling.
10. Module testing and verification requirements.
11. Packaging and dependency isolation.
12. Module-level acceptance criteria.

The primary goal is to ensure that AdharaSutra provides a complete common application foundation without becoming tightly coupled to consuming applications or individual external dependencies.

## 1.1 Scope

This document defines the logical module architecture.

It does not finalize:

- Every public method signature.
- Every configuration field.
- Every CLI protocol schema.
- Every database table.
- Specific implementation algorithms.
- Complete package publishing strategies.

Those details belong in the corresponding detailed design documents.

However, module ownership and dependency boundaries established here are intended to become enforceable architectural rules.

---

# 2. Module Architecture Principles

## MA-001 — Framework Ownership

AdharaSutra owns the application runtime and shared infrastructure.

Applications register their business capabilities through framework-defined extension points.

The framework must not depend on application-specific business implementations.

## MA-002 — Single Responsibility

Every framework module must have a clearly defined responsibility.

A module should not become responsible for unrelated infrastructure simply because those capabilities are frequently used together.

## MA-003 — Explicit Dependency Direction

Dependencies between modules must be documented and enforced.

Circular dependencies between framework modules are prohibited.

## MA-004 — Interface-Based Extension

Consuming applications and optional plugins should extend the framework through documented public interfaces rather than importing internal implementation modules.

## MA-005 — Optional Infrastructure

Applications must not be required to initialize or install infrastructure that they do not use.

Examples:

- A minimal CLI application should not require SQLite.
- An audio.cpp application should not require ComfyUI.
- An HTTP-only integration should not require an external process adapter.

## MA-006 — Shared Infrastructure, Specialized Capabilities

Common infrastructure operations should be centralized.

However, different infrastructure categories may expose different interfaces.

HTTP communication, SQLite transactions, and subprocess execution must not be forced into an unsuitable universal operation interface.

## MA-007 — Runtime and Tooling Separation

Architecture discovery, verification, migration, and scaffolding are development-time capabilities.

They must not be required for ordinary application execution.

## MA-008 — Deterministic Verification

Module boundaries and dependency restrictions must be verifiable through deterministic analysis wherever technically feasible.

## MA-009 — Business Logic Independence

The framework provides extension points, runtime services, and infrastructure abstractions.

Business rules remain inside consuming applications.

## MA-010 — Incremental Evolution

The initial framework should favor stable module boundaries over premature distribution into many independent packages.

---

# 3. Module Classification

AdharaSutra modules are divided into four categories.

| Category | Purpose | Runtime dependency |
|---|---|---|
| Core | Mandatory application framework capabilities | Required |
| Infrastructure | Reusable technical services | Optional where applicable |
| Development tooling | Scaffolding, verification, migration | Development only |
| Platform integration | Electron and platform-specific adapters | Optional |

## 3.1 Core Modules

The initial core consists of:

- Application Kernel
- Configuration
- Lifecycle
- Service Registry and Composition
- Error Model
- CLI Transport and Protocol
- Action Registry and Execution
- Serialization and Validation
- Minimal Diagnostics

These capabilities form the minimum functional application framework.

## 3.2 Optional Infrastructure Modules

- HTTP Client
- WebSocket Client
- External Process/CLI Connector
- SQLite Persistence
- Filesystem Facilities
- State Management
- Job Management
- Event Management
- Advanced Observability

Some capabilities may become required by a selected architecture profile even though they remain optional for the overall framework.

## 3.3 Development Tooling Modules

- Project Scaffolding
- Architecture Discovery
- Architecture Verification
- Migration Planning and Execution Support
- Report Generation
- Documentation Validation

## 3.4 Platform Integration Modules

- Electron Bridge
- Windows Process Support
- Linux Process Support
- macOS Process Support
- Production Packaging Support

---

# 4. High-Level Module Architecture

```text
                       CONSUMING APPLICATION
                  ┌────────────────────────────┐
                  │ Domain / Business Actions  │
                  │ Application Services       │
                  │ Integration Adapters       │
                  └──────────────┬─────────────┘
                                 │
                                 │ Registration / Public APIs
                                 ▼
┌───────────────────────────────────────────────────────────┐
│                       ADHARASUTRA                         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  APPLICATION CORE                   │  │
│  │                                                     │  │
│  │ Kernel | Lifecycle | Configuration | Composition    │  │
│  │ Errors | Validation | Registry                      │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐  │
│  │                   CLI RUNTIME                       │  │
│  │                                                     │  │
│  │ Protocol | Transport | Router | Execution           │  │
│  │ Sessions | Responses | Cancellation                 │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐  │
│  │               RUNTIME SERVICES                      │  │
│  │                                                     │  │
│  │ State | Jobs | Events | Logging | Diagnostics        │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐  │
│  │                 INFRASTRUCTURE                      │  │
│  │                                                     │  │
│  │ HTTP | WebSocket | CLI Process | SQLite | Files      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘

                    DEVELOPMENT TOOLING
                  ┌───────────────────────┐
                  │ Scaffold              │
                  │ Discover              │
                  │ Verify                │
                  │ Migrate               │
                  │ Report                │
                  └───────────────────────┘
```

**Important:** This diagram groups responsibilities, not import dependencies. It must not be interpreted as requiring every module in an upper row to import modules in the lower row.

The runtime composes these capabilities through public interfaces.

---

# 5. Proposed Python Package Structure

The initial implementation should use one Python distribution with separate internal modules.

```text
adhara-sutra/
│
├── pyproject.toml
├── README.md
├── LICENSE
│
├── src/
│   └── adharasutra/
│       │
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── application.py
│       │   ├── context.py
│       │   ├── bootstrap.py
│       │   ├── lifecycle.py
│       │   ├── registry.py
│       │   ├── composition.py
│       │   ├── configuration.py
│       │   ├── errors.py
│       │   └── types.py
│       │
│       ├── cli/
│       │   ├── protocol/
│       │   │   ├── models.py
│       │   │   ├── validation.py
│       │   │   ├── serialization.py
│       │   │   └── compatibility.py
│       │   │
│       │   ├── transport/
│       │   │   ├── base.py
│       │   │   ├── oneshot.py
│       │   │   └── persistent.py
│       │   │
│       │   ├── routing/
│       │   │   ├── actions.py
│       │   │   ├── dispatcher.py
│       │   │   └── execution.py
│       │   │
│       │   ├── sessions/
│       │   │   ├── manager.py
│       │   │   └── correlation.py
│       │   │
│       │   └── entrypoint.py
│       │
│       ├── connectors/
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── health.py
│       │   │
│       │   ├── http/
│       │   │   ├── client.py
│       │   │   ├── config.py
│       │   │   └── errors.py
│       │   │
│       │   ├── websocket/
│       │   │   ├── client.py
│       │   │   └── config.py
│       │   │
│       │   ├── process/
│       │   │   ├── runner.py
│       │   │   ├── discovery.py
│       │   │   ├── streaming.py
│       │   │   └── termination.py
│       │   │
│       │   ├── sqlite/
│       │   │   ├── database.py
│       │   │   ├── transactions.py
│       │   │   └── migrations.py
│       │   │
│       │   └── filesystem/
│       │       ├── paths.py
│       │       ├── temporary.py
│       │       └── artifacts.py
│       │
│       ├── state/
│       │   ├── stores.py
│       │   ├── scopes.py
│       │   ├── subscriptions.py
│       │   ├── concurrency.py
│       │   └── persistence.py
│       │
│       ├── jobs/
│       │   ├── manager.py
│       │   ├── scheduler.py
│       │   ├── lifecycle.py
│       │   ├── progress.py
│       │   ├── cancellation.py
│       │   └── recovery.py
│       │
│       ├── events/
│       │   ├── dispatcher.py
│       │   ├── models.py
│       │   └── subscriptions.py
│       │
│       ├── observability/
│       │   ├── logging.py
│       │   ├── diagnostics.py
│       │   └── correlation.py
│       │
│       ├── tooling/
│       │   ├── scaffold/
│       │   ├── discovery/
│       │   ├── verification/
│       │   ├── migration/
│       │   └── reporting/
│       │
│       └── developer_cli/
│           ├── main.py
│           └── commands/
│
├── electron/
│   └── bridge/
│       ├── src/
│       ├── tests/
│       └── package.json
│
├── contracts/
│   ├── protocol/
│   ├── architecture/
│   └── reports/
│
├── templates/
├── examples/
├── tests/
└── docs/
```

This structure is provisional.

Detailed designs may split, merge, or rename individual files without changing the approved module responsibilities.

The development tooling may later become a separate Python distribution to prevent unnecessary runtime dependencies.

---

# 6. Module Dependency Architecture

## 6.1 Dependency Principle

High-level contracts must not depend on low-level implementations.

Optional infrastructure modules may depend on core abstractions.

Core runtime abstractions must not depend on optional connector implementations.

## 6.2 Permitted Dependency Relationships

```text
                 Application / Bootstrap
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      CLI Runtime      Runtime Services   Connectors
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                     Core Contracts
```

The application bootstrap composes concrete implementations.

Individual business domain modules remain outside this dependency graph.

## 6.3 Module Dependency Matrix

The matrix below describes intended **direct compile-time/import dependencies**, not runtime calls through registered interfaces.

| Module | Permitted dependencies |
|---|---|
| Core contracts | Python standard library; approved minimal typing/validation dependencies |
| Configuration | Core contracts |
| Lifecycle | Core contracts |
| Composition | Core contracts, lifecycle |
| CLI protocol | Core contracts, protocol schemas |
| CLI transport | Core contracts, CLI protocol |
| Action execution | Core contracts, CLI protocol, routing abstractions |
| Connector base | Core contracts |
| HTTP connector | Connector base, configuration |
| Process connector | Connector base, configuration |
| SQLite connector | Connector base, configuration |
| State | Core contracts; persistence ports |
| Jobs | Core contracts, state/event interfaces |
| Events | Core contracts |
| Observability | Core contracts |
| Architecture discovery | Shared analysis models; development-only dependencies |
| Verification | Discovery models, rule contracts |
| Migration | Discovery, verification, reporting |
| Scaffolding | Templates, architecture profile definitions |
| Electron bridge | Versioned protocol contracts; TypeScript runtime libraries |

Concrete adapter registration and lifecycle coordination occur in the composition layer.

## 6.4 Prohibited Dependencies

The following relationships are prohibited:

1. `core` importing application business modules.
2. `core` importing optional connector implementations.
3. `core` importing architecture discovery or migration tooling.
4. CLI protocol models importing application action handlers.
5. Connector implementations importing consuming application domain modules.
6. Domain modules importing Electron or CLI transport implementations.
7. Production runtime requiring development tooling.
8. Runtime modules directly importing project-specific adapters such as audio.cpp.
9. Architecture verifier importing arbitrary application modules for execution during static analysis.
10. Unapproved circular imports between framework modules.

---

# 7. Core Contracts Module

**Module:** `adharasutra.core`

**Classification:** Mandatory.

## 7.1 Purpose

The Core Contracts module defines the stable abstractions shared by framework components.

It should remain lightweight and independent of optional external integrations.

## 7.2 Responsibilities

- Shared types.
- Framework identifiers.
- Error categories.
- Application metadata contracts.
- Lifecycle abstractions.
- Service registration contracts.
- Execution-context interfaces.
- Common validation contracts.

## 7.3 Public Concepts

Proposed public abstractions include:

```text
Application
ApplicationContext
ApplicationMetadata
LifecycleState
ServiceRegistry
ServiceDescriptor
FrameworkError
ExecutionContext
```

Exact types will be finalized in the Core Runtime design.

## 7.4 Constraints

The core must not depend on:

- Electron.
- HTTPX.
- WebSocket clients.
- SQLite implementations.
- External executable integrations.
- Architecture analyzers.
- Migration tooling.
- Consuming application packages.

## 7.5 Acceptance Criteria

- Core contracts can be imported without installing optional connectors.
- No application business code is present.
- All core dependencies are documented.
- Public interfaces have independent unit tests.
- Dependency verification detects prohibited imports.

---

# 8. Application Kernel Module

**Module:** `adharasutra.core.application`

**Classification:** Mandatory.

## 8.1 Purpose

The Application Kernel is the central framework runtime responsible for coordinating application initialization and execution.

It is the main entry point for consuming applications.

## 8.2 Responsibilities

- Application identity.
- Application registration.
- Runtime configuration.
- Subsystem composition.
- Application readiness.
- Startup.
- Shutdown.
- Framework service access.

## 8.3 Application Definition

Conceptual interface:

```python
from adharasutra import Application

app = Application(
    name="my-application",
    version="1.0.0",
)
```

Applications register actions, services, and connectors using public extension points.

## 8.4 Kernel Constraints

The kernel must not implement:

- Domain-specific workflows.
- HTTP service-specific API methods.
- Audio processing logic.
- Image-generation logic.
- Database domain repositories.

## 8.5 Lifecycle Ownership

The kernel coordinates startup and shutdown across registered modules.

It must know which resources are framework-managed and which are application-managed.

Cleanup is performed according to explicit ownership rules.

---

# 9. Configuration Module

**Module:** `adharasutra.core.configuration`

**Classification:** Mandatory.

## 9.1 Purpose

Provide centralized, typed, validated application configuration.

## 9.2 Responsibilities

- Configuration source loading.
- Configuration precedence.
- Framework defaults.
- Application-defined settings.
- Environment overrides.
- Configuration validation.
- Secret redaction.
- Configuration diagnostics.

## 9.3 Configuration Scopes

Configuration is divided into:

- Framework configuration.
- Application configuration.
- Connector configuration.
- Runtime execution configuration.
- Development tooling configuration.

## 9.4 Initialization Behavior

Configuration must be validated before dependent resources initialize.

Invalid required settings must prevent readiness.

## 9.5 Constraints

Configuration loading must not initialize unrelated connectors.

Core configuration should not require optional infrastructure packages.

---

# 10. Lifecycle Module

**Module:** `adharasutra.core.lifecycle`

**Classification:** Mandatory.

## 10.1 Purpose

Define and enforce application, service, and resource lifecycle behavior.

## 10.2 Responsibilities

- Lifecycle state transitions.
- Startup hooks.
- Shutdown hooks.
- Dependency-aware initialization.
- Partial-failure cleanup.
- Graceful termination.
- Resource ownership tracking.

## 10.3 Lifecycle Contracts

Framework-managed services may implement lifecycle interfaces appropriate to their capabilities.

Conceptual example:

```python
class ManagedResource:
    async def start(self) -> None:
        ...

    async def close(self) -> None:
        ...
```

This is a proposed interface shape, not a requirement that every simple service be asynchronous.

## 10.4 Failure Behavior

If startup fails:

1. Initialization stops.
2. The runtime records the failure.
3. Successfully started resources are released.
4. Readiness is not reported.
5. The failure is exposed through the standard error and diagnostic mechanisms.

---

# 11. Service Registry and Composition Module

**Module:** `adharasutra.core.registry`

**Classification:** Mandatory.

## 11.1 Purpose

Manage service definitions and dependency wiring across applications.

## 11.2 Responsibilities

- Service registration.
- Dependency resolution.
- Lifecycle scope.
- Duplicate detection.
- Dependency validation.
- Test substitutions.
- Application-level composition.

## 11.3 Supported Service Lifetimes

Proposed lifetimes:

| Lifetime | Ownership |
|---|---|
| Application | One application runtime |
| Session | One persistent CLI session |
| Request | One action execution |
| Job | One managed job |

The exact lifecycle rules require further design.

## 11.4 Design Principle

Use explicit registration and composition first.

Avoid implementing a complex general-purpose dependency-injection container unless demonstrated requirements justify it.

## 11.5 Dependency Validation

The composition module must detect:

- Missing dependencies.
- Duplicate registrations.
- Invalid lifecycle dependencies.
- Circular dependency definitions where statically or dynamically detectable.

---

# 12. CLI Protocol Module

**Module:** `adharasutra.cli.protocol`

**Classification:** Mandatory for CLI applications.

## 12.1 Purpose

Define the stable communication contract used by Electron and the Python runtime.

## 12.2 Responsibilities

- Request models.
- Response models.
- Event models.
- Error envelopes.
- Protocol version validation.
- Serialization.
- Deserialization.
- Message validation.
- Compatibility checks.

## 12.3 Protocol Independence

Protocol models must not depend on:

- Electron-specific renderer implementation.
- Application business actions.
- HTTP connector implementations.
- External CLI connectors.
- SQLite.

## 12.4 Common Message Categories

```text
Request
Response
Event
Error
CancellationRequest
SessionControl
```

These are conceptual message categories.

Exact schemas will be finalized in `cli-protocol.md`.

## 12.5 Protocol Contract Ownership

The Python runtime and Electron bridge must use compatible definitions of the protocol.

Machine-readable schemas should be maintained as authoritative contract artifacts.

---

# 13. CLI Transport Module

**Module:** `adharasutra.cli.transport`

**Classification:** Mandatory for CLI applications.

## 13.1 Purpose

Manage communication between the process boundary and the protocol engine.

## 13.2 Supported Transports

### One-Shot Transport

- Accept a request.
- Execute the action.
- Return the result.
- Terminate according to execution outcome.

### Persistent Transport

- Maintain process communication.
- Receive multiple requests.
- Send responses and events.
- Handle cancellation.
- Detect disconnection.
- Coordinate shutdown.

## 13.3 Standard Communication Channels

| Channel | Purpose |
|---|---|
| stdin | Incoming structured protocol messages |
| stdout | Outgoing structured protocol messages |
| stderr | Diagnostic logs |

## 13.4 Transport Responsibilities

- Message framing.
- Buffer management.
- Message-size limits.
- Read and write failures.
- Backpressure.
- Protocol transport errors.
- Graceful termination.

## 13.5 Constraints

The transport must not:

- Execute business rules.
- Construct HTTP requests to external services.
- Directly manage domain database operations.
- Interpret application-specific payload meaning.

---

# 14. Action Registry and Router Module

**Module:** `adharasutra.cli.routing`

**Classification:** Mandatory.

## 14.1 Purpose

Map action identifiers to registered application handlers.

## 14.2 Responsibilities

- Action registration.
- Action lookup.
- Action metadata.
- Input schema association.
- Handler dispatch.
- Handler availability.
- Duplicate detection.

## 14.3 Conceptual Action Definition

```python
@app.action("voice.generate")
async def generate_voice(payload, context):
    ...
```

## 14.4 Execution Sequence

```text
Receive Request
      │
      ▼
Validate Envelope
      │
      ▼
Resolve Action
      │
      ▼
Validate Payload
      │
      ▼
Create Execution Context
      │
      ▼
Invoke Handler
      │
      ▼
Normalize Result or Error
      │
      ▼
Serialize Response
```

## 14.5 Business Logic Boundary

Action handlers are application-owned.

The router is framework-owned.

The router must not know what a voice, image, model, character, or other domain concept means.

---

# 15. Session Management Module

**Module:** `adharasutra.cli.sessions`

**Classification:** Optional for one-shot applications; required for persistent CLI mode.

## 15.1 Purpose

Manage persistent CLI communication sessions.

## 15.2 Responsibilities

- Session identifiers.
- Session lifecycle.
- Request correlation.
- Active request tracking.
- Cancellation routing.
- Session cleanup.
- Connection failure handling.

## 15.3 Session State

Session state is process-scoped unless an explicit persistence mechanism is configured.

Terminating a persistent CLI process invalidates its in-memory sessions.

## 15.4 Concurrency

The module must define behavior for:

- Concurrent requests.
- Out-of-order completion.
- Event ordering.
- Reused request identifiers.
- Session termination during execution.

Detailed semantics will be specified in the CLI protocol document.

---

# 16. Connector Foundation Module

**Module:** `adharasutra.connectors`

**Classification:** Core interfaces mandatory; concrete connectors optional.

## 16.1 Purpose

Provide common infrastructure integration conventions.

## 16.2 Shared Responsibilities

- Connector registration.
- Connector identity.
- Configuration.
- Lifecycle.
- Health.
- Error mapping.
- Resource ownership.
- Test substitutions.

## 16.3 Connector Interface Design

A shared lifecycle interface is appropriate.

However, connector capabilities must remain specialized.

```text
Connector Lifecycle
        │
        ├── HTTP Capabilities
        ├── WebSocket Capabilities
        ├── Process Capabilities
        ├── Database Capabilities
        └── Filesystem Capabilities
```

## 16.4 Connector Registry

The registry manages connector registration and retrieval.

The registry must support independent connector instances and application-specific configuration.

## 16.5 Error Boundaries

Connectors translate underlying technical failures into framework-level technical error categories.

Application-specific interpretation belongs in service adapters or business handlers.

---

# 17. HTTP Connector Module

**Module:** `adharasutra.connectors.http`

**Classification:** Optional.

## 17.1 Purpose

Provide reusable outbound HTTP communication.

## 17.2 Responsibilities

- HTTP client lifecycle.
- Connection reuse.
- Request execution.
- Timeouts.
- Authentication configuration.
- Controlled retries.
- Streaming responses.
- Technical error mapping.
- Diagnostics.

## 17.3 Recommended Implementation

HTTPX is the proposed underlying HTTP client.

This is an implementation recommendation, not a dependency of the framework core.

## 17.4 External Integration Boundary

The HTTP connector does not directly implement:

- ComfyUI workflow semantics.
- LM Studio prompting behavior.
- Domain request construction.
- Business result interpretation.

Those operations belong to optional integration plugins or consuming applications.

## 17.5 Testing Requirements

The module must be testable with controlled local HTTP fixtures or mock transports.

External internet access must not be required for core tests.

---

# 18. WebSocket Connector Module

**Module:** `adharasutra.connectors.websocket`

**Classification:** Optional.

## 18.1 Purpose

Provide managed outbound WebSocket communication.

## 18.2 Responsibilities

- Connection lifecycle.
- Message sending.
- Message reception.
- Subscription handling.
- Timeouts.
- Failure detection.
- Optional reconnection.
- Cleanup.

## 18.3 Integration Scope

Applications remain responsible for interpreting service-specific WebSocket messages.

The connector handles transport-level concerns.

---

# 19. External Process Connector Module

**Module:** `adharasutra.connectors.process`

**Classification:** Optional, but required when applications execute external CLI tools through the framework.

## 19.1 Purpose

Provide safe, reusable execution of external programs.

This module is especially important for applications integrating audio.cpp and similar tools.

## 19.2 Responsibilities

- Executable discovery.
- Executable path validation.
- Structured argument construction.
- Process creation.
- Environment configuration.
- Standard input.
- Standard output.
- Standard error.
- Streaming output.
- Exit status.
- Timeout.
- Cancellation.
- Process-tree cleanup.

## 19.3 Connector Design

```text
External Process Connector
├── Executable Resolver
├── Argument Builder
├── Environment Builder
├── Process Runner
├── Output Reader
├── Stream Parser Hooks
├── Timeout Controller
├── Cancellation Controller
└── Process Cleanup
```

## 19.4 Service-Specific Integrations

An audio.cpp adapter defines:

- Executable-specific commands.
- Supported arguments.
- Expected output.
- Output parsing.
- Exit-code interpretation.
- Service-specific failure meaning.

AdharaSutra manages the actual subprocess execution.

## 19.5 Process Ownership

Every managed process must have a defined owner.

The module must distinguish:

- Short-lived processes.
- Persistent interactive processes.
- Jobs using external processes.
- Explicitly detached processes, if supported.

## 19.6 Security

Shell interpretation must be disabled by default.

Arbitrary renderer-provided executable paths must not be executed without validation and authorization.

---

# 20. SQLite Connector Module

**Module:** `adharasutra.connectors.sqlite`

**Classification:** Optional.

## 20.1 Purpose

Provide reusable SQLite infrastructure.

## 20.2 Responsibilities

- Database configuration.
- Connection creation.
- Connection lifecycle.
- Transactions.
- Concurrency policies.
- Migration infrastructure.
- Backup support.
- Error mapping.
- Database health checks.

## 20.3 Ownership Boundary

Framework-owned:

- SQLite connection infrastructure.
- Transactions.
- Lifecycle.
- Error handling.
- Generic migration mechanisms.

Application-owned:

- Domain schema.
- Repositories.
- Queries.
- Domain mapping.
- Business transactions and invariants.

## 20.4 Design Constraint

The framework should not initially implement a custom ORM.

Applications may use documented repository patterns and supported database utilities.

## 20.5 Concurrency

Connection sharing and transaction ownership must be explicit.

The SQLite connector must define whether operations are synchronous, asynchronous through an adapter, or executed through controlled workers.

This decision will be resolved during the connector design.

---

# 21. Filesystem Module

**Module:** `adharasutra.connectors.filesystem`

**Classification:** Optional facilities, with minimal application-directory resolution available to core configuration where needed.

## 21.1 Purpose

Provide consistent local filesystem infrastructure.

## 21.2 Responsibilities

- Application-specific directories.
- Path resolution.
- Path validation.
- Temporary files.
- Managed artifacts.
- Cleanup.
- Cross-platform behavior.

## 21.3 Artifact References

Large generated outputs should be exchanged through controlled file references rather than embedding large binary payloads in the CLI protocol.

## 21.4 Security

Path validation must account for:

- Relative paths.
- Absolute paths.
- Symbolic links.
- Path traversal.
- Allowed storage roots.
- Platform-specific filesystem behavior.

---

# 22. State Management Module

**Module:** `adharasutra.state`

**Classification:** Optional infrastructure module.

## 22.1 Purpose

Provide reusable state stores and state lifecycle management.

## 22.2 Responsibilities

- State registration.
- State scopes.
- Typed access.
- Controlled mutation.
- Subscriptions.
- Concurrency.
- Optional persistence.
- Cleanup.

## 22.3 Supported State Scopes

```text
State
├── Request
├── Session
├── Process
├── Job
└── Persistent
```

## 22.4 Framework and Application Boundaries

The framework defines the mechanism.

The application defines:

- State values.
- State schemas.
- Domain state transitions.
- Business invariants.

## 22.5 Persistence Abstraction

The state module depends on a storage port rather than a concrete SQLite implementation.

SQLite may implement that port.

This avoids making SQLite mandatory for every application using state management.

## 22.6 Event Integration

State changes may publish notifications through the event subsystem.

State management must not depend directly on Electron.

---

# 23. Event Management Module

**Module:** `adharasutra.events`

**Classification:** Lightweight internal event contracts may be core; advanced event services optional.

## 23.1 Purpose

Provide common event publication and subscription mechanisms.

## 23.2 Responsibilities

- Event definitions.
- Event publication.
- Subscriptions.
- Event delivery.
- Subscriber cleanup.
- Error handling.
- Event correlation.

## 23.3 Event Categories

- Runtime lifecycle events.
- Connector events.
- State change events.
- Job progress events.
- Application-defined events.

## 23.4 Event Boundaries

Internal events do not automatically become Electron protocol events.

The CLI event adapter determines which events are exposed externally.

## 23.5 Design Constraint

The initial framework does not require a distributed event broker.

An in-process event dispatcher is sufficient for the initial local runtime.

Durability and cross-process delivery require explicit extensions.

---

# 24. Job Management Module

**Module:** `adharasutra.jobs`

**Classification:** Optional.

## 24.1 Purpose

Provide managed execution of long-running and asynchronous application tasks.

## 24.2 Responsibilities

- Job creation.
- Job identifiers.
- Job lifecycle.
- Scheduling.
- Concurrency limits.
- Progress.
- Cancellation.
- Timeouts.
- Results.
- Recovery metadata.
- Cleanup.

## 24.3 Job Components

```text
Job Management
├── Job Registry
├── Job Scheduler
├── Job Executor
├── Job State
├── Progress Publisher
├── Cancellation Controller
├── Timeout Controller
├── Result Store
└── Recovery Policy
```

## 24.4 Job Execution Models

### In-Process Jobs

Executed in the current runtime.

Lifetime is limited by process ownership.

### Managed External Process Jobs

Executed through the process connector.

The job engine owns the execution record, while the process connector manages the external process.

### Durable Jobs

Require persistent metadata and an explicit execution owner.

Durable workers are a future extension unless required by a validated initial use case.

## 24.5 Dependency Boundaries

The job engine should depend on execution abstractions rather than a particular external CLI or HTTP service.

## 24.6 Progress Events

Job progress is published through the event subsystem and may be forwarded through the CLI protocol.

---

# 25. Observability Module

**Module:** `adharasutra.observability`

**Classification:** Minimal logging mandatory; advanced features optional.

## 25.1 Purpose

Provide consistent runtime diagnostics.

## 25.2 Responsibilities

- Logging.
- Request correlation.
- Job correlation.
- Connector diagnostics.
- Runtime health reporting.
- Error tracing.
- Sensitive-data redaction.

## 25.3 Logging Boundary

Structured CLI messages belong on stdout.

Diagnostic logging belongs on stderr or configured logging destinations.

## 25.4 Optional Capabilities

Advanced metrics and tracing should be optional.

They must not become mandatory dependencies of minimal CLI applications.

---

# 26. Electron Bridge Module

**Module:** `@adharasutra/electron-bridge`

**Classification:** Optional companion TypeScript package.

## 26.1 Purpose

Provide the standardized Electron-to-Python communication implementation.

## 26.2 Responsibilities

- Python executable discovery.
- Process startup.
- Process readiness.
- Protocol serialization.
- Request tracking.
- Response parsing.
- Event subscriptions.
- Cancellation.
- Timeouts.
- Process shutdown.
- Crash detection.
- Protocol compatibility.

## 26.3 Architecture

```text
Electron Renderer
        │
        ▼
Restricted Preload API
        │
        ▼
Electron Main Process
        │
        ▼
AdharaSutra Electron Bridge
        │
        ▼
Python Process
        │
        ▼
AdharaSutra CLI Runtime
```

## 26.4 Boundary Rules

The renderer must not directly execute arbitrary Python commands.

The main process owns process lifecycle.

The bridge uses the versioned protocol.

The bridge must not implement application business logic.

## 26.5 Compatibility

The bridge and Python runtime must validate protocol compatibility before normal action execution.

---

# 27. Architecture Discovery Module

**Module:** `adharasutra.tooling.discovery`

**Classification:** Development only.

## 27.1 Purpose

Analyze the structure and implementation patterns of Python applications.

## 27.2 Responsibilities

- Project discovery.
- Source inventory.
- Module dependency analysis.
- Entry point detection.
- CLI implementation analysis.
- Electron invocation analysis.
- Connector usage discovery.
- State and job pattern discovery.
- Source evidence collection.

## 27.3 Shared Architecture Model

The discovery module produces a structured intermediate architecture representation.

```text
ApplicationArchitecture
├── Metadata
├── SourceRevision
├── Modules
├── Dependencies
├── EntryPoints
├── CliActions
├── ElectronIntegrations
├── Connectors
├── StateStores
├── Jobs
├── Persistence
├── Configuration
└── Evidence
```

## 27.4 Source Safety

Source inspection must be read-only by default.

Static analysis must not execute arbitrary application source code.

Dynamic discovery must be an explicit, isolated operation where supported.

## 27.5 Consumers

The shared architecture model is used by:

- Architecture verification.
- Migration planning.
- Implementation reports.
- Agent-facing architecture summaries.

---

# 28. Architecture Verification Module

**Module:** `adharasutra.tooling.verification`

**Classification:** Development only.

## 28.1 Purpose

Verify that applications follow defined architecture profiles and rules.

## 28.2 Responsibilities

- Architecture profile loading.
- Rule registration.
- Rule execution.
- Dependency validation.
- Structural checks.
- Protocol contract validation.
- Connector policy checks.
- Finding classification.
- Evidence generation.
- Baseline comparison.
- Exception handling.

## 28.3 Verification Engine

```text
Architecture Model
        │
        ▼
Architecture Profile
        │
        ▼
Rule Registry
        │
        ▼
Deterministic Rule Execution
        │
        ▼
Finding Normalization
        │
        ▼
Verification Report
```

## 28.4 Finding Status

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

## 28.5 Rule Ownership

Each rule must define:

- Rule identifier.
- Description.
- Applicable architecture profiles.
- Severity.
- Required evidence.
- Verification method.
- Known limitations.
- Remediation guidance.

## 28.6 Deterministic Requirements

Mandatory rule evaluation must remain functional without an LLM.

## 28.7 CI Integration

The verifier must support noninteractive execution and predictable exit statuses.

---

# 29. Migration Module

**Module:** `adharasutra.tooling.migration`

**Classification:** Development only.

## 29.1 Purpose

Support incremental adoption of AdharaSutra by existing applications.

## 29.2 Responsibilities

- Migration analysis.
- Architecture gap identification.
- Compatibility assessment.
- Migration plan generation.
- Task dependency ordering.
- Safe transformations.
- Migration tracking.
- Verification orchestration.
- Completion reporting.

## 29.3 Migration Dependencies

The migration module uses:

- Architecture discovery.
- Architecture verification.
- Shared architecture models.
- Reporting.
- Approved architecture profiles.

## 29.4 Migration Boundaries

The migration engine must not silently alter business logic.

Automated changes must be reviewable.

Migration must preserve existing behavior and persistent data according to the approved migration plan.

## 29.5 Agent Integration

Migration reports must be usable by Claude Code, Codex, OpenCode, and other coding agents without requiring an agent-specific report format.

## 29.6 Migration Planning Outputs

```text
MigrationPlan
├── CurrentArchitecture
├── TargetArchitecture
├── Findings
├── CompatibilityRequirements
├── MigrationTasks
├── Dependencies
├── Risks
├── AcceptanceCriteria
└── VerificationPlan
```

---

# 30. Project Scaffolding Module

**Module:** `adharasutra.tooling.scaffold`

**Classification:** Development only.

## 30.1 Purpose

Generate new applications using approved architecture profiles.

## 30.2 Responsibilities

- Application templates.
- Project structure.
- Framework bootstrap generation.
- Configuration generation.
- Connector selection.
- Test scaffolding.
- Documentation templates.
- Architecture profile selection.
- Initial project verification.

## 30.3 Generator Inputs

- Project name.
- Python package name.
- Architecture profile.
- Runtime mode.
- Connector selection.
- State options.
- Job options.
- Electron integration.

## 30.4 Generator Ownership

The scaffolder creates source files that become owned by the consuming application.

The framework must not overwrite application-owned files during upgrades without explicit migration operations.

## 30.5 Architecture Alignment

Generated applications must conform to the same architecture profiles used by the verifier.

This prevents scaffolding and verification from implementing different architectural standards.

---

# 31. Reporting Module

**Module:** `adharasutra.tooling.reporting`

**Classification:** Development only.

## 31.1 Purpose

Provide consistent report generation for architecture discovery, verification, and migration.

## 31.2 Report Types

### Current Implementation Report

Explains how the project currently works.

### Architecture Verification Report

Lists compliance results and violations.

### Migration Report

Describes required architectural changes and migration tasks.

### Migration Completion Report

Summarizes completed work, remaining issues, and verification evidence.

## 31.3 Supported Formats

- Markdown.
- JSON.

Additional formats may be supported through extensions.

## 31.4 Report Metadata

Reports should include:

- Schema version.
- Project identity.
- Source revision.
- Analyzer version.
- Architecture profile.
- Generation timestamp.
- Verification status.
- Evidence references.

## 31.5 Reporting Constraints

The reporting module must not independently reinterpret architecture rules.

It renders findings produced by the appropriate analysis engines.

---

# 32. Developer CLI Module

**Module:** `adharasutra.developer_cli`

**Classification:** Development only.

## 32.1 Purpose

Provide a consistent command-line interface for framework development and application maintenance.

## 32.2 Proposed Commands

```bash
adhara new my-app

adhara inspect ./my-app

adhara verify ./my-app

adhara migrate analyze ./my-app

adhara migrate plan ./my-app

adhara migrate status ./my-app

adhara doctor ./my-app

adhara version
```

These are proposed commands, not existing implemented functionality.

## 32.3 Separation from Application CLI

The developer CLI and an application's runtime CLI are separate interfaces.

**Developer CLI:**

- Creates applications.
- Inspects architecture.
- Verifies implementation.
- Plans migrations.
- Runs diagnostics.

**Application Runtime CLI:**

- Receives Electron requests.
- Executes registered application actions.
- Returns application responses.
- Publishes runtime events.

The `adhara` developer command must not become a mandatory launcher dependency for packaged applications.

---

# 33. Cross-Module Communication

## 33.1 Allowed Communication Mechanisms

Modules may communicate through:

1. Direct calls to approved public interfaces.
2. Registered service interfaces.
3. Dependency injection/composition.
4. Defined in-process events.
5. Explicit transport protocols where required.

## 33.2 Discouraged Communication Patterns

Avoid:

- Arbitrary global mutable state.
- Runtime monkey-patching.
- Hidden service locators inside domain code.
- Circular imports.
- Direct access to another module's private implementation.
- Undocumented cross-module callbacks.
- Duplicated event or error contracts.

## 33.3 Error Propagation

Technical failures should use framework error categories.

Domain failures should remain application-defined until mapped at an appropriate boundary.

## 33.4 Cancellation Propagation

Cancellation must flow through explicit execution contexts or cancellation interfaces.

The framework must not assume that all external integrations support immediate cancellation.

---

# 34. Mandatory and Optional Module Matrix

| Module | Minimal CLI | Electron CLI | AI Worker |
|---|---|---|---|
| Core runtime | Required | Required | Required |
| Configuration | Required | Required | Required |
| Lifecycle | Required | Required | Required |
| CLI protocol | Required | Required | Required |
| Action router | Required | Required | Required |
| Basic logging | Required | Required | Required |
| Persistent sessions | Optional | Recommended | Optional |
| Electron bridge | Not required | Required | Not required |
| HTTP connector | Optional | Optional | Optional |
| WebSocket connector | Optional | Optional | Optional |
| Process connector | Optional | Optional | Optional |
| SQLite | Optional | Optional | Optional |
| State engine | Optional | Optional | Optional |
| Job engine | Optional | Optional | Recommended |
| Event services | Optional | Recommended | Recommended |
| Architecture verifier | Development only | Development only | Development only |
| Migration tooling | Development only | Development only | Development only |
| Scaffolding | Development only | Development only | Development only |

The actual required capabilities are determined by an application's selected profile and declared dependencies.

---

# 35. Application Extension Example

A consuming application might define:

```python
from adharasutra import Application

app = Application(
    name="vani",
    version="1.0.0",
)

@app.action("voice.generate")
async def generate_voice(payload, context):
    service = context.services.get(
        "voice_generation"
    )

    return await service.generate(payload)

app.run()
```

The application is responsible for defining and registering `voice_generation`.

The framework provides:

- Runtime initialization.
- Service resolution.
- CLI routing.
- Protocol validation.
- Execution context.
- Result serialization.
- Error handling.
- Lifecycle management.

The application's business logic remains outside the framework.

This example is illustrative. The final API will be specified in the Application Architecture and Core Runtime design documents.

---

# 36. Module-Level Architecture Verification

The architecture verifier should enforce relevant module dependency rules.

## 36.1 Example Rules

| Rule ID | Description |
|---|---|
| MOD-001 | Core must not import optional connectors |
| MOD-002 | Core must not import development tooling |
| MOD-003 | CLI protocol must not import application handlers |
| MOD-004 | Connectors must not import consuming application domains |
| MOD-005 | Domain modules must not import CLI transport |
| MOD-006 | State must not depend directly on SQLite implementation |
| MOD-007 | Jobs must use approved execution interfaces |
| MOD-008 | Electron bridge must use versioned protocol contracts |
| MOD-009 | Migration must consume shared discovery findings |
| MOD-010 | Scaffolding must use approved architecture profiles |
| MOD-011 | No prohibited circular dependencies |
| MOD-012 | Optional dependencies must not be loaded by unrelated modules |

## 36.2 Verification Methods

Use:

- Import graph analysis.
- Python AST.
- Static rule evaluation.
- Schema validation.
- Contract tests.
- Runtime integration tests where necessary.

Static analysis alone cannot prove every runtime ownership or lifecycle requirement.

## 36.3 CI Requirements

Architectural violations shall be reported with:

- Rule ID.
- Severity.
- Source location.
- Evidence.
- Explanation.
- Recommended correction.

---

# 37. Module Testing Strategy

Each module must have appropriate independent tests.

| Module | Primary tests |
|---|---|
| Core | Initialization, registration, lifecycle |
| Configuration | Loading, precedence, validation |
| Composition | Service resolution, dependency errors |
| CLI protocol | Schemas, serialization, compatibility |
| CLI transport | Framing, timeouts, disconnection |
| Router | Registration, dispatch, validation |
| Sessions | Correlation, cancellation, concurrency |
| HTTP | Request behavior, retry, timeout |
| Process | Execution, streaming, termination |
| SQLite | Transactions, concurrency, rollback |
| State | Scopes, mutation, persistence |
| Events | Publication, subscription, cleanup |
| Jobs | Lifecycle, progress, cancellation |
| Electron bridge | Process IPC, errors, compatibility |
| Discovery | Source analysis, evidence |
| Verification | Rule correctness, deterministic results |
| Migration | Plans, transformations, regressions |
| Scaffolding | Generated-project validity |
| Reporting | Schema validity, source references |

Integration tests should verify that the modules work together without requiring real AI services for every test run.

---

# 38. Public API and Internal API Policy

## 38.1 Public APIs

Public APIs are the supported extension and usage interfaces.

Examples:

- Application creation.
- Action registration.
- Service registration.
- Connector registration.
- State access.
- Job submission.
- Lifecycle hooks.
- Architecture verification entry points.

## 38.2 Internal APIs

Internal implementation details are not guaranteed stable across compatible releases unless explicitly documented.

## 38.3 Import Policy

Applications should import from documented package entry points.

For example:

```python
from adharasutra import Application
```

Avoid depending on internal framework implementation paths unless the relevant interface is explicitly public.

## 38.4 Compatibility

Changes to public APIs must follow the framework's compatibility and deprecation policy.

Protocol compatibility is managed separately from Python API compatibility.

---

# 39. Module Evolution and Extraction

The initial modular-monolith structure may evolve.

A module should be considered for independent distribution when:

1. It has stable public interfaces.
2. It has substantial optional dependencies.
3. It has an independent release cadence.
4. It is useful outside the main framework.
5. It can be tested independently.
6. Extraction reduces rather than increases maintenance complexity.

Potential future distributions:

```text
adharasutra
adharasutra-http
adharasutra-process
adharasutra-sqlite
adharasutra-architecture
adharasutra-migration
adharasutra-scaffold
```

These are potential package names, not approved distribution names.

The Electron bridge remains a separate package because of its TypeScript/Electron runtime.

---

# 40. Architectural Risks

## R-MOD-001 — Excessive Module Fragmentation

Creating too many independently released packages may introduce dependency and version-management complexity.

**Mitigation:** Start with a modular monolith.

## R-MOD-002 — Core Dependency Growth

Optional infrastructure may accidentally become mandatory through import chains.

**Mitigation:** Enforce core import boundaries and test minimal installation.

## R-MOD-003 — Circular Module Dependencies

State, jobs, events, and lifecycle services may become mutually dependent.

**Mitigation:** Define shared contracts and use composition at the application boundary.

## R-MOD-004 — Service Registry Becoming a Service Locator

Excessive runtime lookup may obscure dependencies.

**Mitigation:** Prefer explicit service injection and restrict registry use within application composition and framework boundaries.

## R-MOD-005 — Over-Generalized Connectors

A universal connector API may hide important transport-specific behavior.

**Mitigation:** Share lifecycle conventions while retaining specialized capability interfaces.

## R-MOD-006 — Development Tooling Leakage

Architecture analyzers may increase production installation size.

**Mitigation:** Isolate development dependencies and modules.

## R-MOD-007 — Inconsistent Module Extension

Different applications may bypass approved extension interfaces.

**Mitigation:** Document public APIs and enforce detectable violations.

## R-MOD-008 — Premature Public API Stabilization

Finalizing interfaces before validating representative applications may create unnecessary long-term compatibility obligations.

**Mitigation:** Validate APIs with multiple application scenarios before declaring stability.

---

# 41. Detailed Design Decisions Requiring Review

| ID | Decision | Proposed direction |
|---|---|---|
| MD-001 | Python distribution model | Modular monolith |
| MD-002 | Core dependency policy | Minimal dependencies |
| MD-003 | Service composition | Explicit registration |
| MD-004 | Public API exposure | Stable facade modules |
| MD-005 | CLI transport | One-shot and persistent |
| MD-006 | Connector contracts | Shared lifecycle, specialized capabilities |
| MD-007 | State persistence | Port-based, optional SQLite |
| MD-008 | Job execution | Executor abstractions |
| MD-009 | Event management | Lightweight in-process dispatcher |
| MD-010 | Electron bridge | Separate TypeScript package |
| MD-011 | Development tooling | Optional tooling dependencies |
| MD-012 | Architecture discovery | Shared intermediate model |
| MD-013 | Migration and verification | Shared evidence and rule results |
| MD-014 | Package extraction | Only after demonstrated need |

These remain proposed decisions until reviewed and approved.

---

# 42. Module Architecture Acceptance Criteria

The module architecture may be finalized when:

- [ ] Every core module has a defined responsibility.
- [ ] Mandatory and optional modules are identified.
- [ ] Module dependencies are documented.
- [ ] Circular dependencies are prohibited.
- [ ] Framework and application ownership are clearly separated.
- [ ] The core runtime is independent of optional connectors.
- [ ] CLI protocol and application actions are separated.
- [ ] Electron bridge and Python runtime responsibilities are defined.
- [ ] Connector categories have appropriate boundaries.
- [ ] State and job ownership are clear.
- [ ] Runtime and tooling dependencies are isolated.
- [ ] Architecture discovery, verification, and migration share consistent models.
- [ ] Public interfaces are distinguished from internal interfaces.
- [ ] Minimal applications do not require unrelated integrations.
- [ ] Representative consuming applications can use the proposed extension mechanisms.
- [ ] Module architecture can be verified through deterministic checks.
- [ ] Major risks and unresolved decisions are documented.

---

# 43. Relationship to Functional Requirements

| Functional requirement group | Primary module ownership |
|---|---|
| FR-RUN | Core, Kernel, Lifecycle |
| FR-CLI | CLI Protocol, Transport, Router |
| FR-ELC | Electron Bridge, CLI |
| FR-CON | Connector Foundation |
| FR-HTTP | HTTP Connector |
| FR-EXT | Process Connector |
| FR-DB | SQLite Connector |
| FR-WS | WebSocket Connector |
| FR-FS | Filesystem |
| FR-STATE | State |
| FR-JOB | Jobs |
| FR-CFG | Configuration |
| FR-ERR | Core Errors |
| FR-LOG | Observability |
| FR-DI | Service Composition |
| FR-SCAF | Scaffolding |
| FR-DISC | Discovery |
| FR-ARCH | Verification |
| FR-MIG | Migration |
| FR-REP | Reporting |
| FR-TEST | Framework Testing Facilities |
| FR-DEV | Developer CLI |
| FR-PKG | Packaging Infrastructure |
| FR-DOC | Documentation Tooling and Templates |
| FR-SEC | Cross-cutting responsibility |

---

# 44. Relationship to Non-Functional Requirements

The module architecture supports the following quality attributes:

| Quality attribute | Architectural mechanism |
|---|---|
| Performance | Lightweight core and reusable resources |
| Resource efficiency | Optional loading and controlled lifecycle |
| Reliability | Explicit ownership and failure boundaries |
| Security | Validated actions and safe process connectors |
| Maintainability | Modular responsibilities and dependency rules |
| Extensibility | Public interfaces and registered capabilities |
| Testability | Ports, test doubles, independent modules |
| Portability | Platform-specific adapters behind common interfaces |
| Compatibility | Stable public APIs and versioned contracts |
| Architecture conformance | Deterministic import and structural verification |
| Migration safety | Shared analysis and evidence-backed planning |
| Developer experience | Consistent application structure and tooling |

---

# 45. Final Architecture Summary

AdharaSutra is designed as a modular Python application framework whose production runtime provides the foundation for consuming applications.

Its core manages application creation, configuration, lifecycle, composition, CLI communication, validation, and error handling.

Optional infrastructure modules provide HTTP, WebSocket, subprocess, SQLite, filesystem, state, jobs, and advanced observability capabilities.

The Electron bridge provides a standardized TypeScript interface to the Python CLI runtime.

Applications register business actions and services without implementing their own communication and infrastructure foundations.

Development-time modules provide architecture discovery, verification, migration, reporting, and project scaffolding.

All modules follow explicitly defined responsibilities and dependency rules.

The initial implementation favors a modular monolith, with optional dependencies and stable internal boundaries, to avoid premature complexity while supporting future independent distribution.

The central architectural principle remains:

**The framework owns application infrastructure and execution conventions. Consuming applications own business behavior.**

---

# 46. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending module architecture review

**Next Document:** `docs/design/application-architecture.md`

The next document will define how consuming applications are structured on top of AdharaSutra, including DDD layers, application services, business actions, repositories, workflows, integration adapters, configuration, testing, and architecture enforcement.

---

**AdharaSutra — Build once. Standardize everywhere.**
