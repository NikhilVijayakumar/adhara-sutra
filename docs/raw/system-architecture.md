# AdharaSutra — System Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/system-architecture.md`  
**Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** High-Level System Architecture  
**Architecture Style:** Framework-First, Modular, CLI-Native, Ports and Adapters

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`

---

# 1. Purpose

This document defines the proposed high-level system architecture of AdharaSutra.

It establishes how the framework provides a standardized architectural and runtime foundation for independent Python applications.

The architecture must enable consuming applications to focus on business functionality while AdharaSutra manages common infrastructure responsibilities.

It also defines how new applications are constructed, how existing applications adopt the framework, and how architecture compliance can be verified.

This document focuses on system structure and interactions.

Detailed internal component designs, public APIs, schemas, configuration formats, and implementation algorithms will be specified separately.

## 1.1 Architectural Objectives

The architecture shall:

1. Establish AdharaSutra as the foundational application runtime.
2. Keep application business logic independent of framework internals.
3. Standardize Electron-to-Python communication through a CLI protocol.
4. Provide common infrastructure for external HTTP, CLI, WebSocket, SQLite, and filesystem operations.
5. Centralize application lifecycle, configuration, state, jobs, and error handling.
6. Support both short-lived and persistent CLI execution.
7. Allow applications to extend framework capabilities through documented interfaces.
8. Avoid unnecessary dependencies and infrastructure duplication.
9. Provide a consistent architecture for newly generated applications.
10. Enable existing applications to migrate incrementally.
11. Support deterministic architecture verification.
12. Produce structured implementation and migration reports for developers and coding agents.
13. Maintain clear boundaries between production runtime and development tooling.

## 1.2 Architecture Scope

The architecture covers:

- Python application runtime.
- Application registration and bootstrap.
- CLI protocol and action routing.
- Electron communication bridge.
- Service and dependency composition.
- State and job orchestration.
- Connector infrastructure.
- Configuration, logging, and diagnostics.
- Application architectural conventions.
- Project scaffolding.
- Architecture discovery.
- Architecture verification.
- Migration analysis and execution support.
- Development and production deployment models.

---

# 2. Fundamental Architectural Decision

## 2.1 AdharaSutra Is the Application Foundation

AdharaSutra is not a helper library that application code occasionally invokes.

It is the foundational framework upon which applications operate.

The framework manages the overall execution environment.

Applications register their domain-specific capabilities through framework-defined extension points.

**Framework responsibilities:**

- Initialize application infrastructure.
- Load and validate configuration.
- Register services and connectors.
- Manage application lifecycle.
- Receive and validate CLI requests.
- Route requests to application handlers.
- Manage shared technical state.
- Execute and monitor jobs.
- Provide external communication infrastructure.
- Handle technical errors and diagnostics.
- Serialize responses and events.
- Coordinate resource cleanup.

**Application responsibilities:**

- Define business entities.
- Implement business rules.
- Define use cases.
- Implement action handlers.
- Configure required framework capabilities.
- Define domain-specific persistence operations.
- Define integration-specific business workflows.
- Register required application services.

### Architectural Rule SA-001

Applications MUST use AdharaSutra as their configured application runtime.

Applications MUST NOT independently recreate the framework's communication, lifecycle, or infrastructure orchestration mechanisms.

### Architectural Rule SA-002

AdharaSutra MUST NOT contain business functionality belonging to individual consuming applications.

### Architectural Rule SA-003

The framework MAY invoke application-provided handlers through registered interfaces, but framework source modules MUST NOT import consuming application implementations.

---

# 3. Overall System Architecture

## 3.1 High-Level Component Diagram

```text
┌──────────────────────────────────────────────────────────┐
│                      ELECTRON                            │
│                                                          │
│  ┌─────────────┐    ┌──────────────┐                     │
│  │ Renderer UI │───►│ Electron IPC │                     │
│  └─────────────┘    └──────┬───────┘                     │
│                            │                             │
│                     ┌──────▼────────┐                   │
│                     │ Electron Main │                   │
│                     │    Process    │                   │
│                     └──────┬────────┘                   │
│                            │                             │
│                     ┌──────▼───────────┐                │
│                     │ AdharaSutra      │                │
│                     │ Electron Bridge  │                │
│                     └──────┬───────────┘                │
└────────────────────────────┼─────────────────────────────┘
                             │
                             │ Versioned CLI Protocol
                             │ stdin / stdout / stderr
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  ADHARASUTRA RUNTIME                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │              CLI COMMUNICATION LAYER             │  │
│  │ Protocol | Validation | Routing | Serialization   │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │              APPLICATION CORE                    │  │
│  │ Bootstrap | Registry | Lifecycle | Execution      │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │               RUNTIME SERVICES                   │  │
│  │                                                    │  │
│  │ Configuration  State  Jobs  Events  Logging        │  │
│  │ Dependency Composition  Errors  Health            │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │            APPLICATION EXTENSION BOUNDARY         │  │
│  │ Registered Actions | Services | Ports | Models    │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │                BUSINESS LOGIC                     │  │
│  │ Application Use Cases | Domain Rules | Workflows   │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────▼────────────────────────────┐  │
│  │               CONNECTOR SERVICES                 │  │
│  │ HTTP | WebSocket | CLI | SQLite | Filesystem       │  │
│  └───────────────────────┬────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           │
             ┌─────────────┼──────────────┐
             │             │              │
             ▼             ▼              ▼
        HTTP/WS API     Executables     Storage
             │             │              │
        ComfyUI          audio.cpp       SQLite
        LM Studio        Other CLI       Files
        Other APIs
```

This diagram represents runtime execution and communication.

It does not mean that application domain modules are physically part of the framework distribution.

Application business logic remains inside the consuming application's package and is composed into the runtime at startup.

---

# 4. Architectural Subsystems

AdharaSutra is divided into five logical subsystems.

## 4.1 Core Runtime

The core runtime manages application execution.

Components:

- Application definition.
- Bootstrap manager.
- Lifecycle manager.
- Service registry.
- Dependency composition.
- Runtime context.
- Error infrastructure.
- Configuration initialization.

## 4.2 Communication Runtime

The communication subsystem provides the standard Electron-facing interface.

Components:

- CLI transport.
- Protocol parser.
- Request validator.
- Action router.
- Response serializer.
- Event dispatcher.
- Session manager.
- Cancellation handler.
- Protocol compatibility manager.

## 4.3 Infrastructure Runtime

The infrastructure subsystem provides reusable technical facilities.

Components:

- HTTP connector.
- WebSocket connector.
- External CLI connector.
- SQLite connector.
- Filesystem services.
- State stores.
- Job engine.
- Process manager.
- Logging.
- Health monitoring.

## 4.4 Architecture Tooling

This subsystem provides development-time architecture capabilities.

Components:

- Architecture profiles.
- Source discovery.
- Module dependency analysis.
- Architecture rule engine.
- Conformance verifier.
- Report generator.
- Baseline comparison.
- Exception validation.

## 4.5 Application Development and Migration Tooling

This subsystem supports creating and adopting applications.

Components:

- Project scaffolder.
- Architecture templates.
- Existing-project analyzer.
- Gap analysis.
- Migration planner.
- Compatibility mapping.
- Safe source transformations.
- Migration status reporting.
- Verification orchestration.

### Architectural Rule SA-004

Development tooling MUST NOT be required merely to execute an already packaged application.

The production runtime must remain usable without architecture analyzers, migration utilities, and scaffolding dependencies.

---

# 5. Repository and Package Architecture

## 5.1 Recommended Logical Structure

```text
adhara-sutra/
│
├── packages/
│   │
│   ├── adharasutra-core/
│   │   ├── application/
│   │   ├── bootstrap/
│   │   ├── lifecycle/
│   │   ├── registry/
│   │   ├── configuration/
│   │   └── errors/
│   │
│   ├── adharasutra-cli/
│   │   ├── protocol/
│   │   ├── transport/
│   │   ├── router/
│   │   ├── sessions/
│   │   └── serialization/
│   │
│   ├── adharasutra-connectors/
│   │   ├── http/
│   │   ├── websocket/
│   │   ├── external_cli/
│   │   ├── sqlite/
│   │   └── filesystem/
│   │
│   ├── adharasutra-state/
│   │   ├── stores/
│   │   ├── scopes/
│   │   ├── subscriptions/
│   │   └── persistence/
│   │
│   ├── adharasutra-jobs/
│   │   ├── scheduler/
│   │   ├── execution/
│   │   ├── progress/
│   │   ├── cancellation/
│   │   └── recovery/
│   │
│   ├── adharasutra-architecture/
│   │   ├── discovery/
│   │   ├── analyzers/
│   │   ├── rules/
│   │   ├── verification/
│   │   └── reporting/
│   │
│   ├── adharasutra-migration/
│   │   ├── analysis/
│   │   ├── planning/
│   │   ├── compatibility/
│   │   ├── transformations/
│   │   └── verification/
│   │
│   └── adharasutra-scaffold/
│       ├── generator/
│       ├── templates/
│       └── profiles/
│
├── electron/
│   └── electron-bridge/
│
├── contracts/
├── examples/
├── tests/
└── docs/
```

This represents logical module ownership.

## 5.2 Initial Distribution Strategy

**Proposed decision:**

Begin with one Python distribution, using internal modular package boundaries.

Use optional dependency groups for connector and tooling capabilities.

Avoid independently versioning many Python packages before their public interfaces stabilize.

Independent packages may be extracted when justified by:

- Dependency isolation.
- Independent release cadence.
- Significant optional dependencies.
- Reuse outside the core framework.
- Public API stability.

The Electron bridge remains a separate TypeScript package because it targets a different runtime.

**Decision status:** Proposed — Requires packaging design review.

---

# 6. Core Runtime Architecture

## 6.1 Application Definition

Every consuming application declares an AdharaSutra application instance.

The instance represents the registered application configuration and capabilities.

Conceptual example:

```python
from adharasutra import Application

app = Application(
    name="vani",
    version="1.0.0",
)

app.run()
```

This is an intended public API shape, not a finalized implementation.

## 6.2 Runtime Initialization

The bootstrap manager is responsible for initializing the application.

```text
Application Definition
          │
          ▼
Load Configuration
          │
          ▼
Validate Configuration
          │
          ▼
Register Application Services
          │
          ▼
Resolve Dependencies
          │
          ▼
Initialize Connectors
          │
          ▼
Initialize State and Jobs
          │
          ▼
Register Action Handlers
          │
          ▼
Initialize CLI Transport
          │
          ▼
Application READY
```

Initialization order must respect actual dependency relationships.

If initialization fails, previously initialized resources must be released.

## 6.3 Runtime Composition

The framework must define composition rules for:

- Singleton application services.
- Session-scoped services.
- Request-scoped services.
- Connector instances.
- State stores.
- Job execution contexts.

The framework should use explicit registration and composition.

A large, opaque dependency injection container is not required by this high-level architecture.

## 6.4 Application Context

Handlers receive access to authorized framework services through an execution context.

The context may expose:

```text
ApplicationContext
├── application
├── configuration
├── services
├── connectors
├── state
├── jobs
├── events
├── logger
└── execution_metadata
```

The context must not become an unrestricted mechanism for bypassing architecture boundaries.

Domain modules should receive their required dependencies through defined interfaces rather than directly depending on the entire framework context.

---

# 7. CLI Communication Architecture

## 7.1 Primary Communication Boundary

Electron communicates with Python through a standardized process-based CLI transport.

No HTTP server is required between Electron and the Python application.

The CLI communication subsystem is responsible for receiving, validating, dispatching, and responding to requests.

## 7.2 Communication Pipeline

```text
Electron Action
      │
      ▼
Electron Bridge
      │
      ▼
CLI Request Transport
      │
      ▼
Protocol Parser
      │
      ▼
Envelope Validation
      │
      ▼
Action Registry
      │
      ▼
Payload Validation
      │
      ▼
Application Handler
      │
      ▼
Result / Failure
      │
      ▼
Response Serializer
      │
      ▼
CLI Response Transport
      │
      ▼
Electron Bridge
      │
      ▼
Electron UI
```

## 7.3 Unified Protocol

The protocol defines common envelopes for:

- Requests.
- Responses.
- Events.
- Errors.
- Cancellation.
- Session control.

The specific action and payload belong to the consuming application.

The envelope structure belongs to AdharaSutra.

Example:

```json
{
  "protocol_version": "1.0",
  "request_id": "req-001",
  "action": "voice.generate",
  "payload": {
    "text": "Hello"
  }
}
```

## 7.4 Transport Framing

**Proposed decision:**

Use UTF-8 newline-delimited JSON for persistent communication.

Each logical protocol message occupies one complete line.

- stdin carries incoming messages.
- stdout carries outgoing protocol messages.
- stderr carries diagnostic logs.

The protocol shall define:

- Message-size limits.
- Invalid message handling.
- Correlation identifiers.
- Response ordering.
- Terminal message semantics.
- Protocol negotiation.
- Backpressure.
- Cancellation behavior.

## 7.5 CLI Execution Modes

AdharaSutra supports two execution models.

### Mode A — One-Shot CLI

A process is launched for a command and terminates after returning its result.

Characteristics:

- Simple lifecycle.
- Suitable for independent operations.
- No persistent in-memory state between invocations.
- Process startup overhead applies to each request.

### Mode B — Persistent CLI

Electron launches a Python process that remains active.

Characteristics:

- Multiple requests per process.
- Shared process-managed resources.
- Event streaming.
- Concurrent asynchronous actions where supported.
- Persistent connections to external services.
- Centralized state and job coordination.

### Proposed default

Use persistent CLI communication for Electron-backed applications where repeated actions, shared state, and long-running operations justify it.

Keep one-shot CLI execution available for standalone commands, diagnostics, automation, and simpler workloads.

**Decision status:** Proposed.

---

# 8. Electron Integration Architecture

## 8.1 Responsibility Boundary

AdharaSutra includes a companion Electron bridge package.

The bridge provides consistent communication between the Electron main process and the Python application runtime.

## 8.2 Electron Component Responsibilities

### Renderer

Responsible for:

- User interface.
- User interactions.
- Presenting results.
- Displaying progress.
- Requesting supported actions.

The renderer must not directly spawn arbitrary processes.

### Preload Layer

Responsible for:

- Exposing an allowlisted API.
- Mediating communication with Electron main.
- Preventing unrestricted operating-system access.

### Electron Main Process

Responsible for:

- Python runtime discovery.
- Python process creation.
- Process ownership.
- Application shutdown coordination.
- IPC authorization.
- Bridge lifecycle.

### AdharaSutra Electron Bridge

Responsible for:

- Protocol serialization.
- Request correlation.
- Response handling.
- Progress-event dispatch.
- Timeouts.
- Cancellation messages.
- Process failure reporting.
- Compatibility negotiation.

## 8.3 Process Ownership

The Electron main process owns the Python application process in the standard desktop deployment model.

The bridge must define behavior for:

- Electron startup.
- Python readiness.
- Python crash.
- Electron shutdown.
- Unexpected renderer termination.
- Restart.
- Pending request invalidation.

The standard model should not create an additional Python process for every UI action when persistent mode is configured.

---

# 9. Application Extension Architecture

## 9.1 Application Registration

Applications extend AdharaSutra through registration rather than modifying framework internals.

Supported extension categories include:

- Business actions.
- Application services.
- Domain interfaces.
- Integration adapters.
- State schemas.
- Job handlers.
- Lifecycle hooks.

## 9.2 Action Handler Execution

Conceptual example:

```python
@app.action("audio.generate")
async def generate_audio(payload, context):
    service = context.services.get(
        "audio_generation"
    )

    return await service.generate(payload)
```

The framework owns:

- Request parsing.
- Validation.
- Action lookup.
- Execution context.
- Error translation.
- Result serialization.
- Progress delivery.

The application owns:

- Audio-generation behavior.
- Business validation.
- Domain rules.
- Workflow decisions.

## 9.3 Business Logic Isolation

Application business modules should not directly depend on:

- Typer.
- Electron IPC.
- Framework protocol framing.
- HTTPX implementation details.
- Raw subprocess execution.
- SQLite connection setup.

Infrastructure adapters may depend on framework-provided connector APIs.

Application services may depend on application-defined ports.

The domain layer should remain independent of both.

---

# 10. Framework Connector Architecture

## 10.1 Connector Design

The connector subsystem provides standardized infrastructure facilities.

It does not require all external technologies to expose identical operations.

A generic connector lifecycle may include:

```text
REGISTERED
     │
     ▼
INITIALIZING
     │
     ▼
READY
     │
     ├────► DEGRADED
     │
     ├────► FAILED
     │
     ▼
CLOSING
     │
     ▼
CLOSED
```

Individual connector types expose specialized capabilities.

## 10.2 Connector Registry

The registry manages:

- Connector identifiers.
- Configuration.
- Initialization.
- Dependency resolution.
- Health.
- Resource ownership.
- Shutdown.

## 10.3 HTTP Connector

Provides outbound HTTP communication.

Typical features:

- Client lifecycle.
- Connection reuse.
- Base URL configuration.
- Request methods.
- Timeouts.
- Authentication support.
- Controlled retries.
- Error mapping.
- Response streaming.

Recommended underlying implementation: HTTPX.

The connector owns technical HTTP behavior.

The consuming application or integration plugin defines service-specific operations.

## 10.4 External CLI Connector

Provides managed execution of external programs.

Features:

- Executable discovery.
- Structured arguments.
- Environment management.
- Process creation.
- Output capture.
- Streaming.
- Exit status.
- Timeout.
- Cancellation.
- Process cleanup.

This connector provides the technical mechanism required for audio.cpp-style tools.

External command specifications and output mappings remain integration-specific.

## 10.5 SQLite Connector

Provides managed SQLite facilities.

Responsibilities:

- Database path configuration.
- Connection lifecycle.
- Transaction handling.
- Concurrency policy.
- Schema migration infrastructure.
- Backup and recovery facilities.
- Error classification.

Applications define their own database schemas and repository operations.

## 10.6 WebSocket Connector

Provides managed outbound WebSocket communication.

Responsibilities:

- Connection creation.
- Message streaming.
- Connection lifecycle.
- Failure detection.
- Reconnection where configured.
- Message processing interfaces.

## 10.7 Filesystem Services

Provide:

- Application directory resolution.
- Managed temporary files.
- Path validation.
- File operation utilities.
- Artifact references.
- Cleanup support.

## 10.8 Service-Specific Adapters

Examples:

```text
Connector Infrastructure
         │
         ├── HTTP Connector
         │       ├── ComfyUI Adapter
         │       └── LM Studio Adapter
         │
         ├── External CLI Connector
         │       └── audio.cpp Adapter
         │
         └── SQLite Connector
                 └── Application Repositories
```

These adapters translate service-specific operations into the underlying connector facilities.

Service-specific adapters may be distributed as optional plugins or implemented within consuming applications.

---

# 11. State Management Architecture

## 11.1 State Ownership

The framework provides state infrastructure.

Applications define their own state models.

State is divided into explicit scopes.

| Scope | Ownership | Lifetime |
|---|---|---|
| Request | Execution context | One request |
| Session | CLI session | Session lifetime |
| Process | Python runtime | Process lifetime |
| Job | Job manager | Job execution and retention policy |
| Persistent | Storage backend | Across process restarts |

## 11.2 State Stores

State stores provide:

- Typed access.
- Controlled mutation.
- Subscription mechanisms.
- Concurrency guarantees.
- Optional persistence.
- Cleanup policies.

## 11.3 Persistent State

Persistent state is implemented through storage adapters.

SQLite is the proposed default local persistence option, but should not be mandatory for stateless applications.

## 11.4 Concurrency

The framework must define:

- Atomic update semantics.
- Concurrent readers and writers.
- State consistency boundaries.
- Event notification ordering.
- Recovery after failed mutations.

## 11.5 Architecture Constraint

In-memory state must never be treated as durable across process termination.

Persistent state restoration must use an explicitly configured backend.

---

# 12. Job Execution Architecture

## 12.1 Purpose

The job subsystem manages long-running and asynchronous application operations.

Typical consuming workloads include:

- Audio processing.
- Image generation.
- Model inference.
- Large file processing.
- External CLI execution.

The framework provides execution management.

The application provides job behavior.

## 12.2 Job Lifecycle

```text
CREATED
   │
   ▼
PENDING
   │
   ▼
RUNNING
   │
   ├────────► COMPLETED
   │
   ├────────► FAILED
   │
   └────────► CANCELLED
```

Cancellation requests may have an intermediate state while termination is pending.

## 12.3 Job Manager Responsibilities

- Generate job identifiers.
- Maintain lifecycle records.
- Schedule supported execution.
- Enforce concurrency limits.
- Publish progress.
- Handle cancellation.
- Manage timeouts.
- Store result metadata.
- Track failure causes.
- Coordinate cleanup.

## 12.4 Execution Ownership

The initial architecture should distinguish:

### In-Process Jobs

Executed within the active Python runtime.

They do not survive process termination.

### External Process Jobs

Executed using managed child processes.

Their lifetime follows the configured process-ownership policy.

### Durable Jobs

Require persistent metadata and a defined worker process or execution service.

Durable execution should not be implied merely because a job record exists in SQLite.

## 12.5 Proposed Initial Design

Support in-process and managed external-process jobs first.

Design a compatible extension point for durable workers without requiring a separate worker system for every application.

**Decision status:** Proposed.

---

# 13. Configuration Architecture

## 13.1 Central Configuration

All common configuration facilities are owned by AdharaSutra.

Applications define additional configuration fields where necessary.

## 13.2 Configuration Sources

Supported sources may include:

- Framework defaults.
- Application configuration files.
- Environment variables.
- Explicit CLI overrides.
- Runtime-provided settings.

Precedence must be deterministic and documented.

## 13.3 Configuration Validation

Configuration is validated before dependent resources are initialized.

Invalid configuration must produce actionable errors.

## 13.4 Configuration Isolation

Independent applications must not accidentally share configuration or state.

Each application should have independently resolved paths for:

- Application data.
- Cache.
- Logs.
- Temporary files.
- Databases.

---

# 14. Logging, Error Handling, and Diagnostics

## 14.1 Error Architecture

The framework defines a standardized technical error model.

Categories include:

- Protocol errors.
- Validation errors.
- Configuration errors.
- Connector errors.
- Process errors.
- Persistence errors.
- Timeouts.
- Cancellation.
- Internal runtime failures.

Applications may define domain-specific errors and map them through documented interfaces.

## 14.2 Error Boundaries

Errors are handled at explicit boundaries:

```text
External Dependency
        │
        ▼
Connector Error Mapping
        │
        ▼
Application Handler
        │
        ▼
Framework Execution Boundary
        │
        ▼
Standard Protocol Error
        │
        ▼
Electron
```

Expected business errors must not automatically become fatal framework errors.

## 14.3 Logging

The framework provides:

- Structured logging.
- Configurable severity.
- Request correlation.
- Job correlation.
- Connector identification.
- Sensitive-data redaction.

Logs must not interfere with protocol output.

## 14.4 Diagnostics

The runtime should expose:

- Application readiness.
- Connector availability.
- Configuration problems.
- Active job information.
- Runtime version.
- Protocol version.
- Platform-specific dependency status.

---

# 15. Development Tooling Architecture

AdharaSutra includes development tools that operate on application repositories.

These tools are distinct from the production runtime.

```text
                   Developer CLI
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Scaffold       Inspect       Verify
          │             │             │
          │             ▼             │
          │       Discovery Engine    │
          │             │             │
          │             ▼             │
          │       Architecture Model ◄┘
          │             │
          │             ▼
          │       Findings & Evidence
          │             │
          │             ▼
          └────────► Migration Planner
                        │
                        ▼
                  Migration Tasks
                        │
                        ▼
                  Apply / Review
                        │
                        ▼
                    Reverify
```

## 15.1 Shared Architecture Model

The discovery engine should produce a structured intermediate representation of the application.

The architecture verifier and migration planner consume this representation.

This avoids implementing separate and inconsistent project analyzers for every tool.

## 15.2 Development Tooling Constraints

- Analysis must be read-only by default.
- Reports must record source revision information.
- Modifications require explicit operations.
- Generated changes must be reviewable.
- Tooling must not be required in the packaged application runtime.

---

# 16. Architecture Discovery Engine

## 16.1 Responsibilities

The discovery engine analyzes supported application source files and metadata.

It identifies:

- Project structure.
- Python packages.
- Module relationships.
- Entry points.
- CLI registrations.
- Electron process invocations.
- Connector implementations.
- SQLite usage.
- State management.
- Jobs and subprocesses.
- Configuration.
- Relevant tests.

## 16.2 Intermediate Architecture Model

Conceptual structure:

```text
ApplicationArchitecture
├── project_metadata
├── source_revision
├── entry_points
├── modules
├── dependencies
├── actions
├── electron_interfaces
├── connectors
├── state_stores
├── job_handlers
├── persistence
├── configuration
└── evidence
```

Each discovered item should carry sufficient evidence to explain how it was identified.

## 16.3 Discovery Limitations

Static discovery cannot guarantee complete understanding of:

- Dynamic imports.
- Reflection.
- Runtime-generated commands.
- Hidden external behavior.
- Complex dependency injection.
- Dynamically constructed subprocess arguments.

The discovery engine must explicitly report analysis limitations.

---

# 17. Architecture Verification Engine

## 17.1 Purpose

The verifier evaluates whether a project conforms to an architecture profile.

## 17.2 Verification Pipeline

```text
Source Repository
       │
       ▼
Architecture Discovery
       │
       ▼
Intermediate Architecture Model
       │
       ▼
Load Architecture Profile
       │
       ▼
Execute Verification Rules
       │
       ▼
Collect Evidence
       │
       ▼
Normalize Findings
       │
       ▼
Generate Compliance Report
```

## 17.3 Rule Categories

- Project structure.
- Dependency direction.
- Framework adoption.
- CLI protocol.
- Electron integration.
- Connector usage.
- State ownership.
- Job management.
- Configuration.
- Security.
- Testing.
- Documentation references.

## 17.4 Deterministic Verification

Machine-verifiable rules must use deterministic analysis and tests where feasible.

LLM-based analysis may supplement the findings but cannot override deterministic results.

## 17.5 Verification Outcomes

Supported outcomes:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

The verifier must not treat unexecuted checks as passing.

## 17.6 Architecture Profiles

Profiles define requirements applicable to an application type.

Examples:

- Minimal CLI.
- Standard CLI.
- DDD.
- Electron CLI.
- AI Worker.

Profiles may compose shared rules while enabling capability-specific checks.

---

# 18. Migration Architecture

## 18.1 Migration Principles

Migration must preserve application behavior wherever possible.

The framework should replace duplicated technical infrastructure without unnecessarily rewriting domain logic.

## 18.2 Migration Pipeline

```text
Existing Application
        │
        ▼
Discovery
        │
        ▼
Current Implementation Report
        │
        ▼
Architecture Verification
        │
        ▼
Gap Analysis
        │
        ▼
Migration Plan
        │
        ▼
Incremental Changes
        │
        ▼
Architecture Verification
        │
        ▼
Behavioral Regression Tests
        │
        ▼
Migration Completion Report
```

## 18.3 Migration Strategies

### Adapter-First

Introduce compatibility adapters around existing implementations.

Best when minimal changes are required.

### Incremental Refactoring

Replace infrastructure component by component.

Recommended default strategy.

### Controlled Rebuild

Reconstruct selected components where incremental separation is impractical.

Business behavior must still be verified against existing expectations.

## 18.4 Migration Boundaries

Migration may modify:

- Application bootstrap.
- CLI registration.
- Infrastructure initialization.
- Connector wiring.
- State infrastructure.
- Technical utilities.
- Configuration.
- Project structure.
- Electron bridge integration.

Business algorithms and domain rules must not be silently modified.

## 18.5 Migration Reporting

Reports must identify:

- Current implementation.
- Target architecture.
- Architectural gaps.
- Affected files.
- Dependencies between changes.
- Risks.
- Compatibility constraints.
- Acceptance criteria.
- Verification requirements.

## 18.6 Agent Assistance

Coding agents may use generated reports to:

- Understand the existing application.
- Plan refactoring.
- Implement migration tasks.
- Explain architectural decisions.
- Investigate uncertain behavior.

Deterministic verification and regression tests remain the authoritative completion evidence.

---

# 19. Project Scaffolding Architecture

## 19.1 Purpose

The scaffolder creates new applications conforming to supported architecture profiles.

## 19.2 Generator Inputs

Potential inputs include:

- Application name.
- Python package name.
- Architecture profile.
- Runtime mode.
- Required connectors.
- State requirements.
- Job requirements.
- Electron integration.
- Testing preferences.

## 19.3 Generator Outputs

Generated projects should include:

- Package metadata.
- Framework bootstrap.
- Application registration.
- Standard action registration.
- Configuration.
- Project folders.
- Test setup.
- Architecture profile.
- Development commands.
- Minimal documentation.

## 19.4 Generation Verification

The scaffolder must run or expose baseline validation to ensure generated applications conform to the selected architecture.

## 19.5 Template Ownership

Templates are framework-owned.

Generated application business code is application-owned.

Generated files must not be overwritten during framework upgrades without explicit migration procedures.

---

# 20. Deployment Architecture

## 20.1 Standalone CLI Application

```text
Operating System
       │
       ▼
Application CLI
       │
       ▼
AdharaSutra Runtime
       │
       ▼
Application Actions
       │
       ▼
External Dependencies
```

This model is appropriate for terminal applications, scripts, and automation.

## 20.2 Electron with Bundled Python Runtime

```text
Desktop Application Package
│
├── Electron Runtime
│   ├── Renderer
│   ├── Main
│   └── AdharaSutra Bridge
│
├── Python Runtime / Executable
│   ├── AdharaSutra
│   ├── Application Business Logic
│   └── Selected Connectors
│
└── Application Resources
    ├── Configuration
    ├── Data Directory
    └── Optional External Executables
```

The Python runtime may be bundled as an environment or frozen executable.

The exact packaging mechanism remains a detailed design decision.

## 20.3 Electron with Externally Installed Dependencies

Some applications may depend on separately installed services or executables.

Examples:

- ComfyUI.
- LM Studio.
- audio.cpp.

AdharaSutra must support locating, configuring, and diagnosing these dependencies.

The framework must not assume every external dependency is bundled with the application.

## 20.4 Platform Support

Target operating systems:

- Windows.
- Linux.
- macOS.

Platform-specific process management and packaging behavior must be isolated behind framework infrastructure interfaces.

---

# 21. End-to-End Runtime Scenarios

## 21.1 Scenario A — HTTP-Based Integration

**Example:** Electron invokes an application action that communicates with ComfyUI.

```text
Electron UI
    │
    ▼
Shared Electron Bridge
    │
    ▼
AdharaSutra CLI
    │
    ▼
Action Router
    │
    ▼
Application Image Handler
    │
    ▼
Application ComfyUI Adapter
    │
    ▼
AdharaSutra HTTP Connector
    │
    ▼
ComfyUI API
    │
    ▼
Result / Progress / Error
    │
    ▼
AdharaSutra Protocol
    │
    ▼
Electron UI
```

The framework is responsible for transport, execution, and communication infrastructure.

The application is responsible for image-generation workflow behavior.

## 21.2 Scenario B — External CLI Integration

**Example:** Electron invokes audio processing using audio.cpp.

```text
Electron UI
    │
    ▼
Shared Electron Bridge
    │
    ▼
AdharaSutra CLI
    │
    ▼
Action Router
    │
    ▼
Application Audio Handler
    │
    ▼
audio.cpp Adapter
    │
    ▼
AdharaSutra Process Connector
    │
    ▼
audio.cpp Executable
    │
    ▼
Output / Status / Error
    │
    ▼
AdharaSutra Protocol
    │
    ▼
Electron UI
```

The same Electron protocol is used in both scenarios.

## 21.3 Scenario C — SQLite Persistence

```text
Electron Request
       │
       ▼
AdharaSutra CLI
       │
       ▼
Application Use Case
       │
       ▼
Application Repository Port
       │
       ▼
Repository Implementation
       │
       ▼
AdharaSutra SQLite Facilities
       │
       ▼
SQLite Database
       │
       ▼
Application Result
       │
       ▼
AdharaSutra CLI Response
```

## 21.4 Scenario D — Long-Running Job

```text
Electron Starts Action
       │
       ▼
Framework Action Router
       │
       ▼
Application Job Handler
       │
       ▼
Job Manager
       │
       ├── Job Identifier
       │
       ├── Execution
       │      │
       │      ├── Progress
       │      ├── Cancellation
       │      └── Result
       │
       ▼
Framework Event Dispatcher
       │
       ▼
Electron Bridge
       │
       ▼
Electron UI
```

For persistent or detached execution, the job manager must communicate with a real execution owner.

Job metadata alone does not guarantee background execution.

---

# 22. Cross-Cutting Architectural Concerns

## 22.1 Security

Security is enforced at:

- Electron IPC boundary.
- CLI protocol validation.
- Action registration.
- External process execution.
- Network connector configuration.
- Filesystem access.
- Secret management.
- Logging and diagnostics.

## 22.2 Observability

Requests, jobs, connectors, and lifecycle transitions should carry correlation metadata.

Diagnostic details must be accessible without corrupting application protocol output.

## 22.3 Resource Management

Framework-managed resources must have explicit ownership and cleanup behavior.

## 22.4 Concurrency

The framework must define safe handling of concurrent requests, state mutations, job execution, and connector operations.

## 22.5 Compatibility

The architecture must distinguish versions of:

- Python framework.
- Electron bridge.
- CLI protocol.
- Public application interfaces.
- Configuration schemas.
- Architecture profiles.
- Report schemas.

## 22.6 Testability

Framework components must be testable without live Electron applications or external AI services.

## 22.7 Documentation

The framework must maintain clear architectural documentation and machine-readable contracts for public interfaces.

---

# 23. Architectural Constraints

The following constraints apply to all detailed designs.

| ID | Constraint |
|---|---|
| SA-001 | Applications use AdharaSutra as their runtime |
| SA-002 | Framework contains no application business logic |
| SA-003 | Framework invokes applications only through registration boundaries |
| SA-004 | Development tooling is not mandatory at runtime |
| SA-005 | Electron-to-Python communication uses the unified CLI contract |
| SA-006 | External connector technologies do not change the Electron protocol |
| SA-007 | Domain logic remains independent of infrastructure implementations |
| SA-008 | Connector lifecycles are framework-managed |
| SA-009 | State ownership and persistence scope are explicit |
| SA-010 | Jobs have explicit execution owners |
| SA-011 | Architecture verification is deterministic-first |
| SA-012 | Migration preserves behavior and data unless explicitly authorized |
| SA-013 | New application generation and migration converge on common architecture profiles |
| SA-014 | Public protocols and schemas are versioned |
| SA-015 | Optional integrations do not impose unnecessary runtime dependencies |

These constraints will later inform architecture verification rules.

Not every constraint can be proven through static source analysis alone.

---

# 24. Architectural Alternatives and Tradeoffs

## 24.1 Framework Inheritance vs Composition

**Option A:** Applications subclass a framework base application.

**Option B:** Applications register their capabilities with a framework runtime.

**Proposed approach:** Composition and registration.

Reasons:

- Clear extension points.
- Less inheritance coupling.
- Easier testing.
- Better compatibility with independently developed applications.

## 24.2 CLI vs HTTP Between Electron and Python

**Option A:** FastAPI or another local HTTP server.

**Option B:** Standard CLI process communication.

**Selected direction:** CLI process communication.

Reasons:

- Consistent with existing application workflows.
- No additional local HTTP server requirement.
- Supports terminal and automation usage.
- Enables one common bridge across applications.

## 24.3 Persistent vs One-Shot CLI

**Proposed approach:** Support both.

Persistent sessions are preferred for repeated interactive desktop operations.

One-shot execution remains useful for automation and independent tasks.

## 24.4 Unified Connector Interface vs Specialized Interfaces

**Proposed approach:** Shared lifecycle and management conventions with connector-specific capability interfaces.

A generic connector must not hide database transactions or process-streaming behavior behind an unsuitable abstraction.

## 24.5 One Package vs Multiple Packages

**Proposed approach:** One initial Python distribution with optional dependency groups and clear internal module boundaries.

Extract packages only when independent distribution becomes justified.

## 24.6 In-Process Jobs vs External Workers

**Proposed approach:** Support in-process and managed external-process execution initially.

Provide extension points for durable workers without imposing them on every application.

---

# 25. Architecture Validation Strategy

The architecture shall be validated against the approved functional and non-functional requirements.

Validation occurs at multiple levels.

## 25.1 Structural Validation

Confirm:

- Clear subsystem ownership.
- Valid dependency directions.
- No framework-to-application implementation coupling.
- Runtime/tooling separation.
- Optional dependency isolation.

## 25.2 Protocol Validation

Confirm:

- Consistent request and response envelopes.
- Correct correlation.
- Event streaming.
- Cancellation.
- Protocol version rejection.
- Error handling.

## 25.3 Integration Validation

Confirm:

- HTTP integration.
- External CLI execution.
- SQLite persistence.
- Connector health and failure behavior.
- Resource cleanup.

## 25.4 Runtime Validation

Confirm:

- Application startup.
- Persistent execution.
- One-shot execution.
- State scopes.
- Job execution ownership.
- Process termination handling.

## 25.5 Migration Validation

Confirm:

- Existing code can be inspected.
- Current architecture can be documented.
- Violations can be identified.
- Migration tasks can be generated.
- Infrastructure can be replaced incrementally.
- Business behavior remains testable.

---

# 26. Architecture Validation Matrix

| Scenario | Primary components | Expected outcome |
|---|---|---|
| Minimal CLI application | Core, CLI | Successful action execution |
| Electron request | Bridge, protocol, router | Correlated response |
| ComfyUI request | HTTP connector | External result through standard CLI |
| audio.cpp execution | CLI connector | Managed subprocess result |
| SQLite operation | Persistence facilities | Transactionally correct result |
| Long-running operation | Jobs, events | Progress and terminal status |
| Job cancellation | Jobs, process manager | Accurate cancellation outcome |
| Python process crash | Electron bridge | Failure detection |
| Concurrent state updates | State engine | Consistent updates |
| New application generation | Scaffolder | Architecture-compliant project |
| Existing application analysis | Discovery | Evidence-backed report |
| Architecture violation | Verifier | Reproducible finding |
| Existing application migration | Migration engine | Incremental adoption |
| Framework version mismatch | Compatibility layer | Explicit incompatibility handling |

---

# 27. Outstanding Architectural Decisions

These decisions require detailed review before the final architecture baseline is approved.

| ID | Decision | Current direction |
|---|---|---|
| AD-001 | Runtime composition model | Registration and composition |
| AD-002 | Default Electron execution mode | Persistent CLI |
| AD-003 | Protocol message framing | UTF-8 NDJSON |
| AD-004 | CLI concurrency model | Async-capable execution |
| AD-005 | State persistence default | Optional SQLite |
| AD-006 | Job execution ownership | In-process and managed subprocess |
| AD-007 | Durable job support | Future compatible extension |
| AD-008 | Connector abstraction | Shared lifecycle, specialized operations |
| AD-009 | Python distribution | Modular monolith initially |
| AD-010 | Electron runtime packaging | Evaluate bundled Python vs frozen executable |
| AD-011 | Architecture profile format | Versioned declarative rules |
| AD-012 | Migration automation | Safe codemods with reviewed refactoring |
| AD-013 | Compatibility policy | Independently versioned protocol and schemas |
| AD-014 | Report storage and freshness | Revision-aware generated artifacts |

These decisions are proposals unless explicitly selected in the foundational architecture constraints.

---

# 28. Risks and Mitigations

## Risk R-001 — Framework Complexity

A framework that attempts to own too many capabilities may become difficult to maintain.

**Mitigation:** Keep modules independent, use optional capabilities, and implement incrementally.

## Risk R-002 — CLI Protocol Complexity

Persistent bidirectional communication introduces concurrency, ordering, buffering, and cancellation concerns.

**Mitigation:** Define an explicit protocol specification and validate it through executable contract tests.

## Risk R-003 — State Ownership Confusion

Different CLI execution modes may lead to incorrect assumptions about in-memory state.

**Mitigation:** Make state scopes and ownership explicit.

## Risk R-004 — Job Durability Assumptions

Applications may incorrectly assume that returning a job ID guarantees continued execution.

**Mitigation:** Require explicit job execution ownership and recovery semantics.

## Risk R-005 — Architecture Verification False Positives

Static analysis may incorrectly classify legitimate integration code.

**Mitigation:** Support evidence, scoped exceptions, and NEEDS_REVIEW outcomes.

## Risk R-006 — Unsafe Migration

Automated changes may inadvertently affect application behavior.

**Mitigation:** Non-destructive analysis, reviewable diffs, regression tests, and incremental migration.

## Risk R-007 — Cross-Platform Process Behavior

Process termination and executable packaging differ across operating systems.

**Mitigation:** Platform-specific infrastructure adapters and production smoke tests.

## Risk R-008 — Framework Upgrade Breakage

Changes to core interfaces may disrupt multiple consuming applications.

**Mitigation:** Stable public interfaces, compatibility testing, deprecation policies, and versioned contracts.

---

# 29. Architecture Completion Criteria

The high-level system architecture may be approved when:

- [ ] All major framework subsystems have defined responsibilities.
- [ ] Framework and application boundaries are unambiguous.
- [ ] The Electron communication architecture is consistent.
- [ ] CLI execution models are documented.
- [ ] Connector categories and lifecycle responsibilities are defined.
- [ ] State ownership and persistence boundaries are identified.
- [ ] Job execution and cancellation ownership are defined.
- [ ] Development tooling is separate from production runtime.
- [ ] Architecture discovery and verification use a shared analysis model.
- [ ] Migration uses evidence-based incremental planning.
- [ ] Deployment models are documented.
- [ ] Cross-platform considerations are understood.
- [ ] Major tradeoffs and alternatives are recorded.
- [ ] Critical open decisions are resolved or explicitly deferred.
- [ ] Representative end-to-end scenarios have been reviewed.
- [ ] Functional requirements are traceable to architecture components.
- [ ] Non-functional requirements have credible validation approaches.

---

# 30. Next Design Documents

After approving this high-level architecture, detailed design should proceed through the following documents.

### 30.1 Module Architecture

`docs/design/module-architecture.md`

Defines:

- Internal framework modules.
- Public interfaces.
- Module dependencies.
- Runtime versus tooling boundaries.
- Extension mechanisms.
- Package ownership.

### 30.2 Application Architecture

`docs/design/application-architecture.md`

Defines:

- Generated application structure.
- DDD conventions.
- Domain and application layers.
- Framework integration.
- Business-action registration.
- Dependency rules.

### 30.3 CLI Protocol

`docs/design/cli-protocol.md`

Defines:

- Exact message schemas.
- Protocol framing.
- Execution modes.
- Request correlation.
- Events.
- Errors.
- Cancellation.
- Compatibility.

### 30.4 Electron Integration

`docs/design/electron-integration.md`

Defines:

- Electron bridge internals.
- IPC boundaries.
- Process lifecycle.
- Python startup.
- Streaming.
- Packaging.

### 30.5 Connector Framework

`docs/design/connector-framework.md`

Defines:

- Connector interfaces.
- Registration and lifecycle.
- HTTP and WebSocket facilities.
- External process execution.
- SQLite facilities.
- Connector testing.

### 30.6 State and Job Management

Separate detailed documents define state stores, job execution, persistence, concurrency, cancellation, and recovery.

### 30.7 Architecture Verification and Migration

Detailed documents define source analysis, rule evaluation, evidence models, reports, migration planning, compatibility, and safe transformation mechanisms.

---

# 31. Architecture Summary

AdharaSutra is designed as a modular, CLI-native Python application framework.

The framework owns the common application runtime, communication protocol, state management, jobs, external connectors, lifecycle, configuration, errors, diagnostics, and architecture conventions.

Electron communicates with consuming applications through a standardized CLI protocol.

Applications register business capabilities through defined extension points.

External systems such as ComfyUI, LM Studio, audio.cpp, and SQLite are accessed through framework-managed technical infrastructure.

Architecture discovery, verification, scaffolding, and migration tooling operate as development-time capabilities using the same architectural standards.

The resulting ecosystem should allow applications to share a consistent foundation while retaining independently developed business functionality.

---

# 32. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architectural review  
**Next Document:** `docs/design/module-architecture.md`

**AdharaSutra — Build once. Standardize everywhere.**
