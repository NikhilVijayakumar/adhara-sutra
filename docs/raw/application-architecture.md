# AdharaSutra — Application Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/application-architecture.md`  
**Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Consuming Application Architecture  
**Architecture Style:** Framework-First, DDD-Compatible, Hexagonal Architecture  
**Primary Interface:** CLI  
**Electron Communication:** Unified AdharaSutra CLI Protocol

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`

---

# 1. Purpose

This document defines how consuming Python applications must be structured, initialized, extended, tested, verified, and maintained when using AdharaSutra.

AdharaSutra is the foundational application framework.

Consuming applications implement domain-specific business capabilities on top of the framework without independently recreating common infrastructure.

The architecture must support:

1. New applications generated using AdharaSutra.
2. Existing applications migrating to AdharaSutra.
3. Standalone Python CLI applications.
4. Electron applications communicating with Python through CLI.
5. Applications integrating external HTTP services.
6. Applications integrating external CLI executables.
7. Applications using SQLite persistence.
8. Long-running workloads and application-managed business state.
9. Deterministic architecture verification.
10. Consistent development across different coding agents and repositories.

The primary architectural objective is to ensure that applications inherit the framework's capabilities through explicit composition and registration while retaining independent business logic.

---

# 2. Fundamental Application Architecture Principle

## AA-001 — Framework-First Application Development

Every consuming application shall use AdharaSutra as its configured runtime.

The application shall register its capabilities through framework-defined extension points.

The framework shall manage the execution of registered actions.

The application shall not recreate infrastructure already provided by the framework.

### Framework-owned responsibilities

- Application initialization.
- CLI transport and parsing.
- Request routing.
- Protocol validation.
- Response serialization.
- Error normalization.
- Logging infrastructure.
- State storage mechanisms.
- Job execution infrastructure.
- External process management.
- HTTP communication infrastructure.
- SQLite connection and transaction facilities.
- Connector lifecycle.
- Service composition.
- Application shutdown.
- Architecture verification integration.

### Application-owned responsibilities

- Business entities.
- Domain models.
- Domain services.
- Business policies.
- Use cases.
- Application actions.
- Business workflows.
- Domain validation.
- Application-specific state schemas.
- Domain repositories.
- External service-specific adapters.
- Business error definitions.

### Principle

> An application extends AdharaSutra by registering business capabilities. It does not create another application framework around AdharaSutra.

---

# 3. Application Architecture Overview

## 3.1 High-Level Architecture

```text
┌────────────────────────────────────────────────────┐
│                   ELECTRON UI                      │
│                                                    │
│  User Interaction                                  │
│        │                                           │
│        ▼                                           │
│  Electron Preload / Main                           │
│        │                                           │
│        ▼                                           │
│  AdharaSutra Electron Bridge                       │
└──────────────────────┬─────────────────────────────┘
                       │
                       │ Unified CLI Protocol
                       ▼
┌────────────────────────────────────────────────────┐
│                  ADHARASUTRA                       │
│                                                    │
│  Application Runtime                               │
│        │                                           │
│        ▼                                           │
│  CLI Protocol / Action Router                      │
│        │                                           │
│        ▼                                           │
│  Registered Application Action                     │
│        │                                           │
│        ▼                                           │
│  APPLICATION LAYER                                 │
│        │                                           │
│        ├── Use Cases                               │
│        ├── Application Services                    │
│        ├── Commands / Queries                      │
│        └── Business Workflows                      │
│                 │                                  │
│                 ▼                                  │
│  DOMAIN LAYER                                      │
│        │                                           │
│        ├── Entities                                │
│        ├── Value Objects                           │
│        ├── Domain Services                         │
│        └── Business Policies                       │
│                                                    │
│  INFRASTRUCTURE ADAPTERS                           │
│        │                                           │
│        ├── ComfyUI Adapter                          │
│        ├── LM Studio Adapter                        │
│        ├── audio.cpp Adapter                        │
│        └── Domain Repositories                     │
│                 │                                  │
│                 ▼                                  │
│  FRAMEWORK CONNECTOR FACILITIES                    │
│        │                                           │
│        ├── HTTP                                    │
│        ├── WebSocket                               │
│        ├── External CLI                            │
│        ├── SQLite                                  │
│        └── Filesystem                              │
└──────────────────────┬─────────────────────────────┘
                       │
                       ▼
               External Dependencies
```

The application layers are loaded into the AdharaSutra runtime, but their source code remains part of the consuming application.

The diagram illustrates execution flow. Compile-time dependencies follow the architectural dependency rules defined later in this document.

---

# 4. Application Architecture Profiles

AdharaSutra shall support multiple application profiles.

The selected profile determines required application structure and applicable architecture rules.

## 4.1 Minimal Profile

**Profile:** `minimal`

Intended for:

- Small Python utilities.
- Simple command-line tools.
- Applications with limited domain complexity.

Required structure:

```text
my-app/
├── pyproject.toml
├── src/my_app/
│   ├── app.py
│   └── actions/
└── tests/
```

A minimal application must still use AdharaSutra's runtime and CLI conventions.

It should not be forced to create empty DDD layers.

## 4.2 Standard CLI Profile

**Profile:** `cli`

Intended for applications with multiple commands, services, and integrations.

Required concepts:

- Application registration.
- Action handlers.
- Application services.
- Configuration.
- Framework-managed connectors.
- Tests.

## 4.3 DDD Profile

**Profile:** `ddd`

Intended for applications with complex business rules and multiple domain concepts.

Required concepts:

- Domain.
- Application.
- Infrastructure.
- Interfaces.
- Application composition.

## 4.4 Electron CLI Profile

**Profile:** `electron-cli`

Intended for applications with an Electron frontend and Python backend.

Adds:

- Unified Electron CLI protocol.
- Shared Electron bridge.
- Python runtime lifecycle.
- Structured request/response contracts.
- Event streaming.
- Cancellation.
- Packaged application integration tests.

## 4.5 AI Worker Profile

**Profile:** `ai-worker`

Intended for long-running local AI workflows.

Adds recommended facilities for:

- Jobs.
- Progress events.
- External process management.
- HTTP/WebSocket integrations.
- Artifact handling.
- Cancellation.
- Optional persistent state.

## 4.6 Profile Composition

Architecture profiles should support controlled composition.

For example:

```yaml
application:
  architecture: ddd
  interfaces:
    - electron-cli
  capabilities:
    - jobs
    - state
    - http
    - external-cli
    - sqlite
```

This avoids creating a separate architecture profile for every combination of capabilities.

The configuration example is conceptual. Its final schema will be defined in the configuration and scaffolding design documents.

---

# 5. Default Application Project Structure

The proposed default structure for a complex Electron-backed application is:

```text
my-application/
│
├── README.md
├── pyproject.toml
├── architecture.yaml
│
├── config/
│   ├── application.yaml
│   ├── development.yaml
│   └── production.yaml
│
├── src/
│   └── my_application/
│       │
│       ├── __init__.py
│       ├── app.py
│       ├── bootstrap.py
│       │
│       ├── domain/
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── aggregates/
│       │   ├── services/
│       │   ├── policies/
│       │   ├── events/
│       │   └── exceptions/
│       │
│       ├── application/
│       │   ├── actions/
│       │   ├── commands/
│       │   ├── queries/
│       │   ├── handlers/
│       │   ├── services/
│       │   ├── workflows/
│       │   ├── ports/
│       │   └── dto/
│       │
│       ├── infrastructure/
│       │   ├── adapters/
│       │   │   ├── http/
│       │   │   ├── external_cli/
│       │   │   └── websocket/
│       │   │
│       │   ├── persistence/
│       │   │   ├── repositories/
│       │   │   └── migrations/
│       │   │
│       │   └── integration/
│       │
│       ├── interfaces/
│       │   └── cli/
│       │       ├── registration.py
│       │       ├── requests/
│       │       └── responses/
│       │
│       └── composition/
│           ├── services.py
│           ├── connectors.py
│           ├── state.py
│           └── jobs.py
│
├── electron/
│   ├── src/
│   │   ├── main/
│   │   ├── preload/
│   │   └── renderer/
│   └── package.json
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contracts/
│   ├── architecture/
│   └── electron/
│
└── docs/
    ├── architecture.md
    ├── actions.md
    ├── integrations.md
    └── development.md
```

This is a target template, not a requirement for every project.

Only selected capabilities should be generated.

For example, an application without SQLite should not need persistence migration folders.

---

# 6. Application Layering

## 6.1 Dependency Direction

The default DDD architecture uses four major layers.

```text
          INTERFACES
              │
              ▼
         APPLICATION
              │
              ▼
            DOMAIN
              ▲
              │
        INFRASTRUCTURE
```

The infrastructure layer implements contracts defined by the application or domain layers.

Composition occurs at the outer application boundary.

### Allowed dependencies

| Source layer | Permitted project-layer dependencies |
|---|---|
| Domain | Domain |
| Application | Domain, application-defined ports |
| Infrastructure | Application ports, domain models where necessary |
| Interfaces | Application services and request/response models |
| Composition | All application layers and approved framework APIs |

Framework public interfaces may be used at approved outer boundaries.

### Prohibited dependencies

- Domain importing infrastructure.
- Domain importing Electron.
- Domain importing AdharaSutra CLI transport.
- Domain importing HTTPX or raw subprocess management.
- Application importing concrete infrastructure implementations.
- Infrastructure importing interface-layer command handlers.
- Application actions directly implementing CLI protocol framing.

The composition root is an intentional exception to ordinary dependency restrictions because its responsibility is wiring implementations together.

---

# 7. Domain Layer

**Directory:** `domain/`

## 7.1 Purpose

The domain layer represents the application's business concepts and rules.

It is independent of transport and infrastructure implementations.

## 7.2 Responsibilities

- Business entities.
- Value objects.
- Aggregates.
- Domain services.
- Business policies.
- Domain events.
- Domain-specific exceptions.
- Domain invariants.

## 7.3 Example

A hypothetical audio application might define:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceRequest:
    text: str
    voice_id: str

    def __post_init__(self):
        if not self.text.strip():
            raise ValueError(
                "Text cannot be empty"
            )
```

This model contains a business rule.

It does not know:

- How Electron communicates.
- How CLI requests are parsed.
- How audio.cpp is executed.
- How SQLite is configured.
- How framework jobs are scheduled.

## 7.4 Domain Independence

Domain code should be testable using ordinary Python unit tests.

It must not require:

- Electron.
- HTTP services.
- SQLite databases.
- External command-line tools.
- Running AdharaSutra application instances.

## 7.5 Domain Complexity

Not every application needs aggregates, repositories, or rich domain services.

Simple applications may use a smaller architecture profile.

The framework should enforce the declared profile rather than force unnecessary domain abstractions.

---

# 8. Application Layer

**Directory:** `application/`

## 8.1 Purpose

The application layer coordinates business use cases.

It defines what an application does in response to a request without owning the transport through which that request arrived.

## 8.2 Responsibilities

- Use cases.
- Commands.
- Queries.
- Application services.
- Business workflow orchestration.
- Transaction boundaries.
- Domain service coordination.
- Application ports.
- Application-level validation.
- Data transfer objects.

## 8.3 Commands and Queries

A command requests a state-changing operation.

A query retrieves information without intentionally changing application business state.

Examples:

```text
Commands
├── GenerateVoice
├── SaveVoiceProfile
├── GenerateImage
└── CancelProcessing

Queries
├── ListVoiceProfiles
├── GetGenerationStatus
└── GetAvailableModels
```

Command/query separation is a design convention.

The framework does not require a separate CQRS message bus or event-sourcing system.

## 8.4 Use Case Example

```python
class GenerateVoice:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine

    async def execute(self, request):
        return await self.audio_engine.generate(
            text=request.text,
            voice_id=request.voice_id,
        )
```

The use case knows that it needs an audio-generation capability.

It does not know whether the implementation uses:

- An external CLI executable.
- HTTP.
- A native Python library.
- Another supported transport.

## 8.5 Application Ports

Ports define the capabilities required by application use cases.

Example:

```python
from typing import Protocol


class AudioEnginePort(Protocol):
    async def generate(
        self,
        text: str,
        voice_id: str,
    ) -> str:
        ...
```

The consuming application's infrastructure implements this port.

## 8.6 Application Service Boundaries

Application services may coordinate multiple domain operations and infrastructure ports.

They should not:

- Parse raw CLI protocol messages.
- Create framework runtimes.
- Manage Electron IPC.
- Initialize unmanaged HTTP clients.
- Construct arbitrary shell commands.
- Open unmanaged database connections.

---

# 9. Infrastructure Layer

**Directory:** `infrastructure/`

## 9.1 Purpose

The infrastructure layer implements application-defined ports using AdharaSutra-provided technical facilities.

## 9.2 Responsibilities

- Service-specific external adapters.
- Repository implementations.
- Domain data mapping.
- External request construction.
- External output interpretation.
- Application-specific integration configuration.
- Persistence implementation.

## 9.3 Framework Infrastructure Versus Application Infrastructure

This distinction is central to AdharaSutra.

| Technical responsibility | Owner |
|---|---|
| HTTP connection lifecycle | AdharaSutra |
| HTTP timeouts and common retries | AdharaSutra |
| ComfyUI workflow API mapping | Application or optional plugin |
| External process creation | AdharaSutra |
| Process cancellation and cleanup | AdharaSutra |
| audio.cpp argument mapping | Application or optional plugin |
| SQLite connection lifecycle | AdharaSutra |
| SQLite transaction infrastructure | AdharaSutra |
| Voice-profile database queries | Application |
| Filesystem path safety | AdharaSutra facilities |
| Domain-specific file organization | Application |

## 9.4 External CLI Adapter Example

A hypothetical audio.cpp adapter might look like:

```python
class AudioCppAdapter:
    def __init__(self, process_runner):
        self.process_runner = process_runner

    async def generate(
        self,
        text: str,
        voice_id: str,
    ) -> str:
        result = await self.process_runner.run(
            executable="audio-cli",
            args=[
                "--text", text,
                "--voice", voice_id,
            ],
        )

        return result.stdout
```

This is illustrative pseudocode, not a verified audio.cpp command or finalized framework API.

The application adapter knows which arguments its external tool expects.

The framework process runner manages how the executable is launched, monitored, and terminated.

## 9.5 HTTP Adapter Example

```python
class ModelCatalogAdapter:
    def __init__(self, http_client):
        self.http_client = http_client

    async def list_models(self):
        return await self.http_client.get(
            "/v1/models"
        )
```

The application adapter knows the endpoint and expected meaning of its response.

The framework manages HTTP connections and transport behavior.

## 9.6 Infrastructure Dependency Rule

Infrastructure adapters should use public framework connector APIs.

Applications must not independently reproduce the framework's transport lifecycle or common technical error-handling mechanisms.

---

# 10. Interface Layer

**Directory:** `interfaces/cli/`

## 10.1 Purpose

The interface layer connects AdharaSutra action registration with application use cases.

It does not implement a custom CLI communication engine.

## 10.2 Responsibilities

- Register application actions.
- Define request schemas.
- Define response schemas.
- Convert payloads into application commands.
- Invoke application use cases.
- Map domain errors where appropriate.

## 10.3 Conceptual Example

```python
from adharasutra import Application

app = Application(
    name="vani",
    version="1.0.0",
)


@app.action("voice.generate")
async def generate_voice(payload, context):
    use_case = context.services.get(
        "generate_voice"
    )

    return await use_case.execute(payload)
```

The final public registration API will be defined in the CLI and runtime design documents.

## 10.4 Interface Constraints

The interface layer shall not:

- Parse stdin directly.
- Write protocol envelopes manually.
- Manage stdout framing.
- Spawn application runtime processes.
- Reimplement request correlation.
- Implement framework cancellation protocols.
- Own business workflow decisions.

All these responsibilities belong to AdharaSutra or the relevant application use case.

---

# 11. Composition Root and Bootstrap

**Directories:** `composition/` and `bootstrap.py`

## 11.1 Purpose

The composition root assembles the consuming application using AdharaSutra services and application-defined implementations.

This is the only ordinary application boundary allowed to know concrete implementations from all application layers.

## 11.2 Responsibilities

- Create the AdharaSutra application definition.
- Register application services.
- Select connector implementations.
- Wire application ports to adapters.
- Register actions.
- Register state schemas.
- Configure jobs.
- Register lifecycle hooks.

## 11.3 Bootstrap Sequence

```text
Application Entry Point
        │
        ▼
Create AdharaSutra Application
        │
        ▼
Register Configuration Schema
        │
        ▼
Declare Required Connectors
        │
        ▼
Register Application Services
        │
        ▼
Wire Ports to Implementations
        │
        ▼
Register Actions
        │
        ▼
Register State and Jobs
        │
        ▼
AdharaSutra Starts Runtime
```

The framework controls actual initialization ordering and resource lifecycle.

## 11.4 Conceptual Composition Example

```python
from adharasutra import Application

from my_application.application.services import (
    GenerateVoice,
)
from my_application.infrastructure.adapters import (
    AudioCppAdapter,
)


app = Application(
    name="vani",
    version="1.0.0",
)

# Illustrative proposed registration API
app.register_service(
    "audio_engine",
    factory=lambda ctx: AudioCppAdapter(
        ctx.connectors.process("audiocpp")
    ),
)

app.register_service(
    "generate_voice",
    factory=lambda ctx: GenerateVoice(
        ctx.services.get("audio_engine")
    ),
)

app.run()
```

These APIs are conceptual.

They demonstrate dependency ownership, not finalized implementation syntax.

## 11.5 Bootstrap Invariants

- An application must have one clearly defined composition root.
- Services must not be initialized through unrelated import side effects.
- Dependency resolution must be explicit.
- Missing dependencies must be detectable.
- Connector lifecycle remains framework-managed.
- Application startup must not bypass framework initialization.

---

# 12. Application Action Architecture

## 12.1 Action Definition

An action is an externally invocable application capability.

Examples:

```text
voice.generate
voice.list
audio.separate
model.status
image.generate
project.load
project.save
```

Action identifiers belong to the consuming application.

The action registration and execution infrastructure belongs to AdharaSutra.

## 12.2 Action Metadata

Every registered action should expose:

- Identifier.
- Description.
- Input schema.
- Output schema.
- Execution characteristics.
- Cancellation support.
- Authorization policy, if applicable.
- Version or compatibility metadata.

## 12.3 Action Execution Pipeline

```text
Electron / CLI Request
        │
        ▼
AdharaSutra Protocol Validation
        │
        ▼
Action Lookup
        │
        ▼
Application Payload Validation
        │
        ▼
Execution Context Creation
        │
        ▼
Registered Application Action
        │
        ▼
Application Use Case
        │
        ▼
Domain / Infrastructure Ports
        │
        ▼
Application Result
        │
        ▼
AdharaSutra Serialization
        │
        ▼
Electron / CLI Response
```

## 12.4 Action Ownership

The framework owns:

- Registration mechanics.
- Routing.
- Validation invocation.
- Error normalization.
- Response serialization.
- Execution lifecycle.

The application owns:

- Action meaning.
- Business validation.
- Workflow behavior.
- Result semantics.

## 12.5 Action Compatibility

Changes to action schemas must consider existing Electron consumers.

The framework shall provide mechanisms for versioning and compatibility checking.

The application remains responsible for deciding whether a business action change is backward compatible.

---

# 13. Application State Architecture

## 13.1 State Definition

AdharaSutra supplies state storage and lifecycle facilities.

Applications define their own state models.

Examples:

- Selected model.
- Active workspace.
- Voice profile selection.
- Current project metadata.
- Processing options.
- Persistent user preferences.

## 13.2 State Ownership

| State | Owner | Managed through |
|---|---|---|
| Runtime readiness | Framework | Runtime lifecycle |
| Connector health | Framework | Connector registry |
| Request metadata | Framework | Execution context |
| Job status | Framework | Job manager |
| Business state model | Application | Framework state facilities |
| Business state transitions | Application | Application services |
| Persistent state storage | Framework infrastructure | Configured adapter |

## 13.3 State Rules

1. State scopes must be explicit.
2. Business invariants belong to the application.
3. Persistent state must use a configured durable backend.
4. In-memory state must not be assumed to survive process termination.
5. Concurrent updates must follow documented consistency rules.
6. State changes exposed to Electron must use framework-managed events or responses.

## 13.4 UI State Versus Backend State

Not all Electron UI state belongs in Python.

Purely visual state such as temporary panel selection, hover state, or local form display state may remain in Electron.

Python should own authoritative application state that must be shared with use cases, persisted, or coordinated with backend jobs.

The design should avoid unnecessary synchronization of purely presentational state.

---

# 14. Application Job Architecture

## 14.1 Purpose

Applications may define long-running workloads.

Examples:

- Audio generation.
- Source separation.
- Image generation.
- Large file processing.
- Model inference.
- Data indexing.

AdharaSutra owns common job orchestration infrastructure.

## 14.2 Application Responsibilities

The consuming application defines:

- Job work.
- Business inputs.
- Expected outputs.
- Domain progress stages.
- Domain-specific retry eligibility.
- Business cancellation behavior.

## 14.3 Framework Responsibilities

AdharaSutra provides:

- Job identifiers.
- Execution ownership.
- Scheduling facilities.
- Concurrency limits.
- Progress publication.
- Cancellation coordination.
- Timeout management.
- Status tracking.
- Result metadata.
- Cleanup.

## 14.4 Execution Models

Applications may use:

- Synchronous actions.
- Asynchronous actions.
- Managed in-process jobs.
- Managed external-process jobs.
- Durable workers where explicitly supported.

A job must have an identifiable execution owner.

Returning a job identifier is not sufficient to guarantee background execution.

## 14.5 Progress Reporting

The application reports meaningful business progress.

The framework translates that progress into standardized events.

For example:

```json
{
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": 60,
    "stage": "audio-generation"
  }
}
```

The framework owns the event envelope.

The application owns the meaning of `audio-generation`.

---

# 15. Application Persistence Architecture

## 15.1 Persistence Principles

Applications define their persistence needs.

AdharaSutra manages generic database infrastructure.

The persistence design should separate:

- Database connection management.
- Transaction boundaries.
- Domain repositories.
- Business mapping.
- Schema migrations.

## 15.2 Repository Ports

Application use cases should depend on repository interfaces.

Example:

```python
from typing import Protocol


class VoiceRepositoryPort(Protocol):
    async def save(self, voice):
        ...

    async def find(self, voice_id):
        ...
```

## 15.3 Repository Implementations

Repository implementations use framework-managed SQLite facilities.

They own:

- Domain-specific queries.
- Data mapping.
- Schema assumptions.
- Repository semantics.

They do not own raw connection lifecycle policy.

## 15.4 Transaction Boundaries

Business transactions should be coordinated by application services or use cases through framework-provided transaction facilities.

Domain layers must not depend on SQLite transaction implementations.

## 15.5 Data Ownership

Each application owns its domain database schema and data.

AdharaSutra owns reusable database mechanisms.

Framework upgrades must not silently modify consuming application schemas.

---

# 16. Application Connector Architecture

## 16.1 Connector Selection

Applications declare required connector capabilities.

For example:

```yaml
connectors:
  http:
    enabled: true

  process:
    enabled: true

  sqlite:
    enabled: true
```

Only declared capabilities should be activated.

## 16.2 Connector Configuration

Applications provide external dependency configuration.

Examples:

- ComfyUI service URL.
- LM Studio service URL.
- audio.cpp executable path.
- SQLite database location.

The framework validates and manages the technical configuration.

## 16.3 Connector Adapters

Adapters map application operations to external dependency operations.

```text
Application Use Case
         │
         ▼
Application Port
         │
         ▼
Service-Specific Adapter
         │
         ▼
AdharaSutra Connector
         │
         ▼
External Dependency
```

## 16.4 Connector Replacement

Applications should be able to change adapter implementations without modifying:

- Electron protocol handling.
- CLI action routing.
- Domain entities.
- Application use-case contracts.

For example, an audio-generation port might initially use audio.cpp and later use a different backend.

The framework integration remains consistent.

## 16.5 Service-Specific Plugins

Applications may consume reusable AdharaSutra integration plugins.

Potential examples:

- ComfyUI integration plugin.
- LM Studio integration plugin.
- audio.cpp integration plugin.

These plugins should provide service-specific adapters and mappings while using framework connector infrastructure.

They should not replace the framework runtime or introduce competing Electron protocols.

---

# 17. Electron Application Architecture

## 17.1 Principle

Electron remains responsible for user-interface behavior.

AdharaSutra remains responsible for Python application execution and infrastructure.

All communication uses the unified CLI contract.

## 17.2 Electron Layer Structure

```text
electron/
└── src/
    ├── main/
    │   ├── index.ts
    │   └── python-runtime.ts
    │
    ├── preload/
    │   └── index.ts
    │
    └── renderer/
        ├── components/
        ├── pages/
        ├── hooks/
        └── services/
```

## 17.3 Electron Main Process

The main process:

- Initializes the shared bridge.
- Starts the Python runtime.
- Manages process lifecycle.
- Handles shutdown.
- Controls supported IPC operations.
- Reports backend readiness.

## 17.4 Preload Layer

The preload layer exposes restricted APIs to the renderer.

It must not expose arbitrary process execution.

## 17.5 Renderer

The renderer:

- Submits application actions.
- Displays results.
- Subscribes to progress.
- Requests supported cancellation.
- Manages UI-only state.

## 17.6 Shared Bridge Example

```typescript
const result = await pythonBridge.execute(
  "voice.generate",
  {
    text: "Hello",
    voice_id: "voice-1"
  }
);
```

The bridge implementation is shared across consuming applications.

The action identifier and payload are application-specific.

## 17.7 External Transport Independence

Electron must not know whether an action uses:

- HTTP.
- WebSocket.
- External CLI.
- SQLite.
- Local Python code.
- Filesystem operations.

It interacts with application actions through the same protocol.

---

# 18. Application Configuration

## 18.1 Configuration Ownership

AdharaSutra provides:

- Configuration loading.
- Validation.
- Environment overrides.
- Configuration precedence.
- Secret handling facilities.
- Configuration diagnostics.

Applications define:

- Domain settings.
- Required connectors.
- External dependency locations.
- Business defaults.
- Resource limits.

## 18.2 Example Configuration

```yaml
application:
  name: vani
  version: 1.0.0

runtime:
  mode: persistent-cli

connectors:
  process:
    audiocpp:
      executable: audio-cli

  sqlite:
    database: data/vani.db

jobs:
  max_concurrent: 2
```

The structure above is illustrative.

The exact schema will be finalized in the configuration design.

## 18.3 Environment Isolation

Development, test, and production configurations must remain distinguishable.

Configuration must not require hardcoded user-specific filesystem paths.

## 18.4 Secret Management

Applications must not store sensitive credentials directly in committed configuration files.

---

# 19. Application Error Architecture

## 19.1 Error Categories

Applications may define domain-specific errors.

The framework defines technical error categories.

Examples:

- Validation error.
- Business rule violation.
- External dependency unavailable.
- Process execution failure.
- Database failure.
- Timeout.
- Cancellation.
- Internal execution failure.

## 19.2 Domain Error Mapping

An application may map a domain error into an exposed application error contract.

For example:

```text
Domain Error
     │
     ▼
Application Error Mapper
     │
     ▼
Framework Error Envelope
     │
     ▼
Electron
```

## 19.3 Error Isolation

A failed business operation should not automatically terminate the entire Python runtime.

Unexpected technical failures must be handled according to the runtime's error and shutdown policies.

## 19.4 Error Information

Frontend responses should expose:

- Stable error code.
- Safe error message.
- Retryability where known.
- Relevant request correlation.

Sensitive diagnostics remain in controlled logs.

---

# 20. Application Testing Architecture

## 20.1 Testing Principle

Applications must be testable independently of Electron and external production services.

## 20.2 Testing Structure

```text
tests/
├── unit/
│   ├── domain/
│   └── application/
│
├── integration/
│   ├── connectors/
│   └── persistence/
│
├── contracts/
│   ├── cli/
│   └── actions/
│
├── architecture/
│
└── electron/
```

## 20.3 Domain Unit Tests

Verify business rules without framework runtime initialization.

## 20.4 Application Use-Case Tests

Verify workflows using fake ports or adapters.

## 20.5 Infrastructure Integration Tests

Verify service-specific adapters and repositories.

Framework test utilities should provide controlled connectors or fixtures where appropriate.

## 20.6 CLI Contract Tests

Verify:

- Action registration.
- Request validation.
- Response envelopes.
- Error handling.
- Event streaming.
- Cancellation.
- Protocol compatibility.

## 20.7 Architecture Tests

Verify the application follows its selected architecture profile.

## 20.8 Electron Integration Tests

Verify the shared bridge can start and communicate with the Python runtime.

## 20.9 Packaged Application Tests

Production packaging must be tested separately from the development environment.

---

# 21. Application Architecture Verification

## 21.1 Purpose

AdharaSutra shall verify that consuming applications follow the framework's defined architectural conventions.

## 21.2 Verification Categories

| Category | Example rule |
|---|---|
| Framework adoption | Application uses the AdharaSutra runtime |
| Project structure | Required layers exist for selected profile |
| Domain isolation | Domain does not import CLI or connector implementations |
| Application boundaries | Use cases depend on ports, not infrastructure |
| Infrastructure usage | External operations use approved framework connectors |
| CLI registration | Actions use the framework router |
| Electron integration | Electron uses the shared bridge |
| State ownership | State scopes follow declared policies |
| Job execution | Framework-managed execution is used |
| Persistence | Database lifecycle uses approved facilities |
| Configuration | Framework configuration is used |
| Tests | Required contracts and architecture checks exist |

## 21.3 Verification Status

Each applicable rule should produce:

- PASS.
- FAIL.
- NEEDS_REVIEW.
- NOT_CHECKED.

## 21.4 Static and Runtime Verification

Static analysis can verify imports, folder structures, configuration patterns, and known API usage.

Runtime tests must verify execution behavior such as:

- Process cleanup.
- Cancellation.
- State persistence.
- Job lifecycle.
- Protocol interaction.

## 21.5 Approved Exceptions

Legitimate deviations must be explicitly documented.

Exceptions must not silently disable mandatory safety or communication requirements.

## 21.6 Proposed Command

```bash
adhara verify ./my-application
```

This command is a proposed developer tooling interface.

---

# 22. Existing Application Adoption

## 22.1 Principle

An existing application should not need to be rewritten from scratch to adopt AdharaSutra.

Migration should preserve functioning business logic.

## 22.2 Existing Application Example

An existing project may contain:

```text
legacy-app/
├── main.py
├── cli.py
├── services/
├── database.py
├── subprocess_runner.py
├── http_client.py
└── electron/
```

It may already work correctly but contain duplicated infrastructure.

## 22.3 Migration Target

The goal is to move toward:

```text
migrated-app/
├── src/migrated_app/
│   ├── app.py
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── interfaces/
│   └── composition/
├── electron/
└── tests/
```

The migration target must use the selected architecture profile and preserve application behavior.

## 22.4 Migration Stages

### Stage 1 — Discover

Identify current CLI commands, Electron integration, state, HTTP clients, process execution, persistence, and business logic.

### Stage 2 — Map

Map existing components to their proposed AdharaSutra responsibilities.

### Stage 3 — Introduce Runtime

Register existing business functions through AdharaSutra.

### Stage 4 — Migrate Communication

Replace custom CLI communication with the unified protocol while maintaining compatibility.

### Stage 5 — Migrate Infrastructure

Replace duplicated HTTP, subprocess, SQLite, logging, and configuration implementations.

### Stage 6 — Align Architecture

Move business logic into appropriate application and domain modules.

### Stage 7 — Verify

Run architecture checks and behavioral regression tests.

### Stage 8 — Clean Up

Remove obsolete infrastructure after compatibility is established.

## 22.5 Temporary Compatibility Adapters

Applications may temporarily retain legacy module structures while adapting their behavior into the framework.

The verifier should distinguish:

- Fully compliant implementations.
- Approved transitional implementations.
- Unresolved violations.
- Unsupported analysis.

---

# 23. Application Architecture Reporting

## 23.1 Current Implementation Report

Explains:

- Existing entry points.
- CLI commands.
- Application modules.
- Dependency relationships.
- External integrations.
- State ownership.
- Job behavior.
- Persistence mechanisms.

## 23.2 Conformance Report

Identifies:

- Applicable architecture rules.
- Passing checks.
- Violations.
- Source evidence.
- Exceptions.
- Unsupported checks.

## 23.3 Migration Report

Provides:

- Current implementation.
- Target architecture.
- Required changes.
- Affected files.
- Risks.
- Compatibility expectations.
- Acceptance criteria.
- Verification instructions.

## 23.4 Agent-Friendly Output

Reports must support Markdown and machine-readable JSON.

The same output format should work across coding agents without requiring separate reporting systems for each vendor.

---

# 24. Framework Versioning and Application Compatibility

## 24.1 Independent Version Boundaries

The architecture distinguishes:

- AdharaSutra Python runtime version.
- Electron bridge version.
- CLI protocol version.
- Application version.
- Action contract versions.
- Architecture profile version.

## 24.2 Framework Upgrades

Applications should be able to upgrade the framework independently from business logic.

Breaking framework changes must have documented migration guidance.

## 24.3 Action Compatibility

Applications own their action payload and result semantics.

Changing action schemas may require Electron frontend updates or compatibility adapters.

## 24.4 Protocol Compatibility

The bridge and runtime must detect unsupported protocol combinations.

A framework update must not silently reinterpret existing messages.

## 24.5 Architecture Profile Changes

Changes to architecture profiles should be versioned and verified.

Existing applications should be able to inspect new violations introduced by upgrading a profile.

---

# 25. Application Documentation Requirements

Each generated application should include minimal documentation appropriate to its profile.

## 25.1 Required Documentation

At minimum:

- Project overview.
- Application purpose.
- Framework version.
- Application startup instructions.
- Registered actions.
- External dependencies.
- Configuration.
- Testing instructions.
- Architecture profile.

## 25.2 Complex Application Documentation

DDD and Electron applications should additionally document:

- Domain boundaries.
- Application use cases.
- Connector adapters.
- State ownership.
- Job execution.
- Persistence schema.
- Electron communication.
- Packaging requirements.

## 25.3 Ownership

The application owns documentation describing its business capabilities.

AdharaSutra owns documentation describing generic framework behavior.

Applications should link to framework references instead of copying complete framework specifications.

---

# 26. Architecture Rules

The following rules are proposed for deterministic verification where technically feasible.

| ID | Rule |
|---|---|
| APP-001 | Application uses AdharaSutra as its configured runtime |
| APP-002 | Business logic remains application-owned |
| APP-003 | One explicit application composition root is defined |
| APP-004 | Domain does not import interface-layer implementations |
| APP-005 | Domain does not import infrastructure implementations |
| APP-006 | Application services do not depend on concrete infrastructure |
| APP-007 | External HTTP infrastructure uses approved framework facilities |
| APP-008 | External CLI execution uses framework process facilities |
| APP-009 | Database lifecycle uses framework persistence facilities |
| APP-010 | Electron uses the standardized bridge |
| APP-011 | CLI actions use framework registration and routing |
| APP-012 | Application handlers do not implement protocol framing |
| APP-013 | State follows declared ownership and persistence scopes |
| APP-014 | Jobs use documented framework execution facilities |
| APP-015 | Configuration is validated through the framework |
| APP-016 | Required action contracts are testable |
| APP-017 | No prohibited circular application-layer dependencies |
| APP-018 | Optional connectors are not required when unused |
| APP-019 | Architecture exceptions are documented |
| APP-020 | Migration preserves required behavioral compatibility |

Some rules require executable tests or review rather than static analysis alone.

---

# 27. Application Architecture Validation Scenarios

## Scenario AA-S01 — New DDD Application

**Given** a developer generates a DDD application,

**When** the project is inspected,

**Then** the required architecture layers must exist.

**And** its framework bootstrap must be valid.

**And** its applicable architecture checks must pass.

## Scenario AA-S02 — Business Action Execution

**Given** an application registers a business action,

**When** Electron invokes the action,

**Then** AdharaSutra must validate and route the request.

**And** the application use case must execute.

**And** the result must use the standard response protocol.

## Scenario AA-S03 — External HTTP Adapter

**Given** an application uses an HTTP-based external dependency,

**When** a business action invokes the dependency,

**Then** the application adapter must use framework-managed HTTP facilities.

**And** the Electron communication interface must remain unchanged.

## Scenario AA-S04 — External CLI Adapter

**Given** an application uses an external executable,

**When** an action invokes the executable,

**Then** AdharaSutra must manage process execution and lifecycle.

**And** the application adapter must interpret tool-specific behavior.

## Scenario AA-S05 — Domain Independence

**Given** a domain module,

**When** architecture verification inspects dependencies,

**Then** prohibited imports from CLI, Electron, or infrastructure implementations must be reported.

## Scenario AA-S06 — State Persistence

**Given** application state configured as persistent,

**When** the application restarts,

**Then** the framework must restore the state according to the configured persistence semantics.

## Scenario AA-S07 — Job Cancellation

**Given** an application job is running,

**When** Electron requests cancellation,

**Then** the framework must coordinate cancellation.

**And** report the actual cancellation outcome.

## Scenario AA-S08 — Existing Application Migration

**Given** an existing working application,

**When** migration adopts AdharaSutra,

**Then** existing business behavior must remain testable.

**And** infrastructure responsibilities must progressively move to the framework.

## Scenario AA-S09 — Framework Upgrade

**Given** a consuming application uses a supported framework version,

**When** it upgrades to a newer version,

**Then** compatibility verification must identify relevant breaking changes.

## Scenario AA-S10 — Minimal Application Isolation

**Given** a minimal CLI application,

**When** it starts,

**Then** it must not initialize unrelated SQLite, WebSocket, HTTP, or job infrastructure.

---

# 28. Architecture Tradeoffs

## 28.1 Strict Layering Versus Simplicity

DDD layering improves maintainability for complex applications but adds overhead for small utilities.

**Proposed resolution:** Multiple architecture profiles with a shared runtime.

## 28.2 Framework Context Versus Explicit Injection

A shared application context is convenient but can become an unrestricted service locator.

**Proposed resolution:** Use context primarily at framework boundaries and prefer explicit dependencies in business services.

## 28.3 Standard Infrastructure Versus Specialized Integration

Generic connectors reduce duplication but cannot fully understand external systems.

**Proposed resolution:** Framework-owned technical connectors with application-owned semantic adapters.

## 28.4 Application State Versus Electron UI State

Moving every UI value into Python increases synchronization complexity.

**Proposed resolution:** Keep presentation-only state in Electron and authoritative business state in the Python application where appropriate.

## 28.5 Migration Consistency Versus Legacy Compatibility

Strict architecture requirements can conflict with incremental adoption.

**Proposed resolution:** Support temporary compatibility adapters, migration baselines, and evidence-backed verification.

## 28.6 Framework Convenience Versus Domain Independence

Exposing framework services everywhere simplifies access but introduces coupling.

**Proposed resolution:** Domain independence is mandatory; use explicit ports for application-level dependencies.

---

# 29. Risks and Mitigations

## AA-R01 — Application Logic Leaks Into the Framework

**Risk:** Common application behavior may be mistaken for reusable framework infrastructure.

**Mitigation:** Require framework modules to remain independent of consuming application domains.

## AA-R02 — Excessive Framework Context Usage

**Risk:** Application services become tightly coupled to the global framework context.

**Mitigation:** Prefer explicit dependency injection through application ports.

## AA-R03 — Duplicated Infrastructure

**Risk:** Applications continue creating raw HTTP clients, process runners, and database managers.

**Mitigation:** Provide clear connector APIs, architecture checks, and migration guidance.

## AA-R04 — Overcomplicated Generated Projects

**Risk:** Simple utilities inherit unnecessary DDD folders and services.

**Mitigation:** Profile-based scaffolding.

## AA-R05 — Electron Business Logic Duplication

**Risk:** Business decisions are independently implemented in Electron and Python.

**Mitigation:** Define authoritative ownership of each business operation and state model.

## AA-R06 — Hidden Runtime State

**Risk:** Application behavior depends on process-global state that does not survive one-shot execution.

**Mitigation:** Explicit state scopes and persistent execution models.

## AA-R07 — Migration Breakage

**Risk:** Existing CLI commands, persistence, or workflows change unintentionally.

**Mitigation:** Baseline tests, compatibility adapters, incremental migration, and regression verification.

## AA-R08 — Framework Upgrade Coupling

**Risk:** Applications depend on undocumented internal framework APIs.

**Mitigation:** Public API boundaries, compatibility tests, and architecture verification.

---

# 30. Detailed Design Decisions Requiring Review

| ID | Decision | Proposed direction |
|---|---|---|
| AA-D01 | Default architecture for complex apps | DDD / Hexagonal |
| AA-D02 | Application integration model | Composition and registration |
| AA-D03 | Action identification | Namespaced string identifiers |
| AA-D04 | Business handler signatures | Typed requests and registered handlers |
| AA-D05 | Dependency injection | Explicit composition with lightweight registry |
| AA-D06 | External integration | Application ports + framework connectors |
| AA-D07 | Persistence | Domain repositories using framework SQLite |
| AA-D08 | State ownership | Explicit request/session/process/persistent scopes |
| AA-D09 | Job ownership | Framework lifecycle with application-defined work |
| AA-D10 | Electron integration | Shared bridge and CLI protocol |
| AA-D11 | Application structure | Profile-based scaffolding |
| AA-D12 | Architecture enforcement | Deterministic-first verification |
| AA-D13 | Existing application migration | Incremental adoption |
| AA-D14 | Business error mapping | Application errors normalized at framework boundary |
| AA-D15 | Configuration | Framework validation with application-defined schemas |

These are design proposals rather than finalized implementation decisions.

---

# 31. Functional Requirement Traceability

| Functional requirement group | Application architecture responsibility |
|---|---|
| FR-RUN | Application bootstrap and registration |
| FR-CLI | Action interface registration |
| FR-ELC | Shared Electron bridge |
| FR-CON | Application adapter composition |
| FR-HTTP | Service-specific HTTP adapters |
| FR-EXT | Service-specific CLI adapters |
| FR-DB | Domain repositories |
| FR-WS | WebSocket integration adapters |
| FR-FS | Domain-specific artifact operations |
| FR-STATE | Application state schemas |
| FR-JOB | Business job definitions |
| FR-CFG | Application configuration |
| FR-ERR | Business error mapping |
| FR-LOG | Application diagnostic context |
| FR-DI | Composition root |
| FR-SCAF | Generated application structure |
| FR-DISC | Application architecture discovery |
| FR-ARCH | Application conformance |
| FR-MIG | Existing application adoption |
| FR-REP | Implementation and migration reporting |
| FR-TEST | Application tests |
| FR-DEV | Application developer experience |
| FR-PKG | Application packaging |
| FR-DOC | Application documentation |
| FR-SEC | Application security boundaries |

---

# 32. Non-Functional Requirement Traceability

| Quality attribute | Application architecture mechanism |
|---|---|
| Performance | Lightweight action handlers and managed resources |
| Reliability | Framework lifecycle and failure boundaries |
| Security | Validated actions and approved infrastructure |
| Maintainability | Explicit layers and module responsibilities |
| Testability | Domain independence and mockable ports |
| Extensibility | Adapter implementations and service registration |
| Compatibility | Versioned action and protocol contracts |
| Portability | Framework-managed platform facilities |
| State consistency | Scoped framework state management |
| Resource efficiency | Optional infrastructure initialization |
| Migration safety | Compatibility adapters and regression tests |
| Architecture verification | Enforceable dependency rules |
| Developer experience | Standard templates and conventions |

---

# 33. Application Architecture Acceptance Criteria

The application architecture may be approved when:

- [ ] Framework and application responsibilities are unambiguous.
- [ ] The default application structure is defined.
- [ ] Architecture profiles are consistent with the system architecture.
- [ ] Domain and application layer boundaries are clear.
- [ ] Framework-specific dependencies are restricted to appropriate layers.
- [ ] The composition root has explicit ownership.
- [ ] Application action registration is well defined.
- [ ] Electron integration follows the unified CLI contract.
- [ ] External service adapters use framework connectors.
- [ ] State and job ownership are documented.
- [ ] Persistence responsibilities are clearly divided.
- [ ] Application error mapping is defined.
- [ ] Architecture conformance rules are identifiable.
- [ ] Existing applications have a feasible migration path.
- [ ] Unit, integration, contract, and packaging tests are accounted for.
- [ ] Major tradeoffs and open decisions are recorded.

---

# 34. Final Architecture Summary

AdharaSutra provides the common runtime and infrastructure foundation for independent Python applications.

Consuming applications are built through framework registration and composition.

The framework manages:

- Application initialization.
- CLI routing.
- Electron communication.
- External connectors.
- State infrastructure.
- Job execution.
- Configuration.
- Lifecycle.
- Logging.
- Technical errors.
- Architecture verification.

Applications implement:

- Domain models.
- Business rules.
- Application use cases.
- Business workflows.
- Action handlers.
- Domain repositories.
- Service-specific integration adapters.

The default architecture for complex applications follows DDD and Hexagonal Architecture.

Simpler applications may use smaller profiles without losing the common framework runtime.

Existing applications can progressively adopt the same architecture through discovery, verification, compatibility adapters, and incremental migration.

The most important invariant is:

**AdharaSutra owns the application foundation. Consuming applications own their business capabilities.**

---

# 35. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending application architecture review

**Next Document:** `docs/design/cli-protocol.md`

The next document will define the unified CLI communication protocol in detail, including exact request and response envelopes, message framing, one-shot and persistent execution, events, request correlation, cancellation, error handling, concurrency, and Electron compatibility.

---

**AdharaSutra — Build once. Standardize everywhere.**
