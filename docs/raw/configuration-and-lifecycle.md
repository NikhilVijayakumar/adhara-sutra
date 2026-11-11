# AdharaSutra — Configuration and Lifecycle Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/configuration-and-lifecycle.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Core Runtime Architecture  
**Architecture Style:** Declarative Configuration, Explicit Composition, Dependency-Aware Lifecycle  
**Primary Language:** Python 3.12+  
**Runtime Models:** One-Shot CLI and Persistent CLI

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

---

# 1. Purpose

This document defines the architecture of the AdharaSutra Configuration and Lifecycle subsystems.

These subsystems establish the conditions under which an application can be initialized, configured, executed, monitored, and terminated.

The Configuration subsystem manages how framework and application settings are declared, loaded, merged, validated, resolved, and provided to registered components.

The Lifecycle subsystem manages the initialization, readiness, execution, failure handling, and cleanup of those components.

Together, they provide a consistent foundation for applications using AdharaSutra.

## 1.1 Objectives

The architecture shall:

1. Centralize framework configuration.
2. Support application-defined configuration schemas.
3. Provide deterministic configuration precedence.
4. Support development, test, and production environments.
5. Keep secrets separate from ordinary application settings.
6. Validate configuration before dependent services initialize.
7. Support optional and required modules.
8. Compose application services and connectors predictably.
9. Resolve component startup dependencies.
10. Manage application and component lifecycles.
11. Provide explicit readiness and health semantics.
12. Handle partial initialization failures.
13. Coordinate graceful shutdown.
14. Manage jobs, processes, connectors, and state during termination.
15. Prevent resource leakage.
16. Support one-shot and persistent CLI applications.
17. Integrate with Electron process lifecycle.
18. Provide diagnostic information and actionable configuration errors.
19. Support deterministic verification.
20. Enable incremental migration of existing applications.

## 1.2 Central Principle

**Configuration defines the application’s required capabilities and operational policies. Lifecycle management ensures those capabilities are initialized, operated, and released safely.**

Consuming applications declare what they require.

AdharaSutra coordinates how those requirements are initialized and managed.

## 1.3 Non-Goals

The initial architecture does not require:

- A distributed configuration service.
- Kubernetes-style orchestration.
- A service discovery cluster.
- Runtime dependency installation.
- Automatic secret synchronization.
- Mandatory live configuration reloading.
- A general-purpose workflow orchestration engine.
- A complex dependency-injection container.
- Mandatory startup of all available connectors.
- Automatic recovery from every fatal application failure.

These may be considered later when supported by concrete application requirements.

---

# 2. Architectural Principles

## CL-001 — Framework-Owned Configuration Infrastructure

AdharaSutra shall own configuration loading, merging, validation, resolution, and diagnostics.

Applications own their domain-specific configuration definitions.

## CL-002 — Explicit Configuration Sources

Every effective setting shall originate from a documented configuration source or default.

## CL-003 — Deterministic Precedence

Configuration overrides shall follow one documented precedence policy.

## CL-004 — Validation Before Use

Required configuration shall be validated before dependent runtime components initialize.

## CL-005 — Explicit Capability Declaration

Applications shall declare required and optional runtime capabilities.

## CL-006 — Dependency-Aware Initialization

Components shall initialize according to their declared dependencies.

## CL-007 — Explicit Lifecycle Ownership

Every managed component shall have a defined lifecycle owner.

## CL-008 — Safe Partial Failure

Initialization failures shall trigger cleanup of successfully initialized components as appropriate.

## CL-009 — Accurate Readiness

An application shall report readiness only when required initialization and readiness conditions are satisfied.

## CL-010 — Optional Dependency Isolation

Unused optional modules shall not be installed or initialized merely because they are supported by the framework.

## CL-011 — Reverse-Dependency Shutdown

Components shall be released in an order that respects their dependencies and active resource ownership.

## CL-012 — Idempotent Shutdown

Repeated shutdown requests shall not cause unsafe repeated cleanup.

## CL-013 — Environment Isolation

Development, test, and production configurations shall not be mixed unintentionally.

## CL-014 — Sensitive Configuration Protection

Secrets shall be handled through explicit protected configuration mechanisms.

## CL-015 — No Hidden Runtime Initialization

Application modules shall not initialize framework-managed infrastructure merely because they are imported.

## CL-016 — Minimal Core Dependency

The configuration and lifecycle foundation shall remain usable without optional HTTP, WebSocket, SQLite, or job-management dependencies.

## CL-017 — Explicit Failure Semantics

Component failures shall be classified according to their effect on runtime integrity and application availability.

## CL-018 — Observable Lifecycle

Relevant state transitions and failures shall be available through framework diagnostics and events.

---

# 3. High-Level Architecture

## 3.1 Component Diagram

```text
┌─────────────────────────────────────────────────────┐
│                 CONSUMING APPLICATION               │
│                                                     │
│  Application Definition                             │
│  Configuration Schemas                              │
│  Service Registrations                              │
│  Connector Declarations                             │
│  Action Registrations                               │
│  Lifecycle Policies                                 │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  ADHARASUTRA CORE                   │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │             CONFIGURATION ENGINE              │  │
│  │                                               │  │
│  │ Source Loading                                │  │
│  │ Precedence and Merging                        │  │
│  │ Schema Validation                             │  │
│  │ Environment Resolution                        │  │
│  │ Secret References                             │  │
│  │ Configuration Diagnostics                     │  │
│  └───────────────────────┬───────────────────────┘  │
│                          │                          │
│                          ▼                          │
│  ┌───────────────────────────────────────────────┐  │
│  │             COMPOSITION ENGINE                │  │
│  │                                               │  │
│  │ Service Registry                              │  │
│  │ Capability Resolution                         │  │
│  │ Dependency Graph                              │  │
│  │ Resource Ownership                            │  │
│  └───────────────────────┬───────────────────────┘  │
│                          │                          │
│                          ▼                          │
│  ┌───────────────────────────────────────────────┐  │
│  │              LIFECYCLE ENGINE                 │  │
│  │                                               │  │
│  │ Initialization                                │  │
│  │ Dependency-Aware Startup                      │  │
│  │ Readiness                                     │  │
│  │ Runtime Operation                             │  │
│  │ Failure Handling                              │  │
│  │ Graceful Shutdown                             │  │
│  │ Resource Cleanup                              │  │
│  └───────────────────────┬───────────────────────┘  │
│                          │                          │
│              ┌───────────┼────────────┐             │
│              ▼           ▼            ▼             │
│          Connectors    State        Jobs            │
│              │           │            │             │
│              └───────────┼────────────┘             │
│                          ▼                          │
│                Application READY                    │
└─────────────────────────────────────────────────────┘
```

The configuration and composition stages determine what must be initialized.

The lifecycle engine determines when and how initialization occurs.

The diagram is conceptual and does not prescribe a mandatory sequential startup for unrelated components.

---

# 4. Proposed Module Structure

```text
src/adharasutra/
│
├── core/
│   ├── application.py
│   ├── bootstrap.py
│   │
│   ├── configuration/
│   │   ├── contracts.py
│   │   ├── definitions.py
│   │   ├── registry.py
│   │   ├── sources.py
│   │   ├── loaders.py
│   │   ├── merging.py
│   │   ├── precedence.py
│   │   ├── validation.py
│   │   ├── environment.py
│   │   ├── secrets.py
│   │   ├── snapshot.py
│   │   └── diagnostics.py
│   │
│   ├── composition/
│   │   ├── contracts.py
│   │   ├── registry.py
│   │   ├── descriptors.py
│   │   ├── resolver.py
│   │   ├── dependency_graph.py
│   │   └── scopes.py
│   │
│   └── lifecycle/
│       ├── contracts.py
│       ├── states.py
│       ├── manager.py
│       ├── initialization.py
│       ├── readiness.py
│       ├── shutdown.py
│       ├── cleanup.py
│       ├── ownership.py
│       └── failures.py
│
└── observability/
    ├── logging.py
    ├── health.py
    └── diagnostics.py
```

This is a proposed logical structure.

Individual files may be combined or separated during implementation.

The mandatory architectural boundary is between:

- Configuration definition and resolution.
- Dependency composition.
- Lifecycle coordination.
- Individual component implementations.

---

# 5. Configuration Architecture

## 5.1 Purpose

The Configuration Engine provides one authoritative mechanism for loading and validating framework and application configuration.

It shall support both simple applications and applications with multiple connectors, state stores, workers, and runtime policies.

## 5.2 Configuration Categories

Configuration is divided into:

| Category | Examples | Primary owner |
|---|---|---|
| Framework | Logging defaults, protocol limits | AdharaSutra |
| Application | Name, version, domain settings | Application |
| Runtime | Execution mode, concurrency | AdharaSutra runtime |
| Connector | HTTP endpoints, executable paths | Connector definitions |
| State | Persistence adapters, retention | State subsystem |
| Jobs | Queue capacity, executor limits | Job subsystem |
| Security | Allowed paths, credential references | Shared responsibility |
| Environment | Development/test/production settings | Deployment configuration |
| Development tooling | Architecture profiles, verification | Development tooling |

## 5.3 Configuration Ownership

AdharaSutra defines the configuration infrastructure and standard framework schemas.

Applications define extension schemas for their own business settings.

Applications must not modify framework configuration semantics through undocumented internal mechanisms.

## 5.4 Typed Configuration

Configuration should be represented through validated typed models.

The public contract should not force application domain code to depend on a particular configuration-library implementation.

## 5.5 Configuration Namespaces

Configuration keys should be organized by responsibility.

Examples:

```text
application.*
runtime.*
cli.*
connectors.*
state.*
jobs.*
logging.*
security.*
tooling.*
```

Framework-owned namespaces shall follow documented extension and override rules.

---

# 6. Configuration Sources

## 6.1 Supported Sources

The framework shall support documented configuration sources.

Proposed sources:

1. Framework defaults.
2. Application defaults.
3. Base application configuration file.
4. Environment-specific configuration file.
5. Environment variables.
6. Explicit runtime or CLI overrides.

Secrets may be resolved through protected sources after nonsecret configuration is validated sufficiently to identify the required secret references.

## 6.2 Proposed Precedence

From lowest to highest:

```text
Framework Defaults
        │
        ▼
Application Defaults
        │
        ▼
Base Configuration File
        │
        ▼
Environment-Specific File
        │
        ▼
Environment Variables
        │
        ▼
Explicit Runtime / CLI Overrides
        │
        ▼
Effective Configuration
```

Higher-precedence sources override lower-precedence values according to the approved merge policy.

This precedence is proposed and must be reviewed.

## 6.3 Framework Defaults

Framework defaults should be conservative, predictable, and documented.

Examples:

- Logging level.
- Message limits.
- Connector initialization behavior.
- Shutdown policies.
- Resource limits.

Defaults must not silently enable expensive optional infrastructure.

## 6.4 Application Defaults

Applications may define default values for domain settings.

For example:

- Preferred output format.
- Default project directory.
- Default processing options.

## 6.5 Configuration Files

Proposed primary format: YAML.

JSON and TOML may be supported through explicit loaders.

The initial implementation should avoid maintaining multiple unnecessarily complex configuration syntaxes.

The final default format remains a design decision.

## 6.6 Environment Variables

Environment variables may override supported configuration fields.

A deterministic namespace convention is required.

Illustrative example:

```text
ADHARA_RUNTIME_MODE=persistent-cli
ADHARA_LOGGING_LEVEL=INFO
ADHARA_JOBS_MAX_CONCURRENT=2
```

The exact environment-variable mapping will be finalized in the configuration contract.

## 6.7 CLI Overrides

Explicit overrides may be supplied by trusted startup configuration or developer commands.

They must not become an unrestricted mechanism for untrusted Electron renderer code to alter security-sensitive runtime settings.

## 6.8 Unknown Configuration Keys

The framework should reject unknown keys in strict production validation unless an extension namespace has explicitly declared support for additional fields.

Compatibility behavior must be documented.

---

# 7. Configuration Merge Semantics

## 7.1 Purpose

The framework must define exactly how configuration sources are combined.

## 7.2 Mapping Values

Nested mapping values may be recursively merged when permitted by schema.

## 7.3 Scalar Values

Higher-precedence scalar values replace lower-precedence values.

## 7.4 List Values

**Proposed policy:** Lists are replaced, not implicitly concatenated.

Implicit list concatenation can produce unexpected duplicated connectors, permissions, or execution policies.

## 7.5 Null and Missing Values

The configuration system must distinguish:

- Field not provided.
- Field explicitly set to null.
- Field has a default.
- Field is required but missing.

An explicit null value must not automatically be treated as an instruction to remove a setting.

Removal or reset semantics require documented rules.

## 7.6 Invalid Overrides

Invalid higher-precedence values must not be silently replaced with lower-precedence values.

The framework should report validation failure.

## 7.7 Merge Traceability

Diagnostics should identify which source supplied the effective value of a setting, without revealing sensitive values.

---

# 8. Configuration Schema and Validation

## 8.1 Schema Ownership

The framework defines schemas for its own configuration namespaces.

Applications register schemas for their domain-specific settings.

Connector modules register the schemas required for their capabilities.

## 8.2 Validation Stages

Configuration validation should occur in stages.

```text
Load Sources
      │
      ▼
Parse Source Syntax
      │
      ▼
Merge Values
      │
      ▼
Validate Types and Required Fields
      │
      ▼
Validate Cross-Field Constraints
      │
      ▼
Resolve Paths and Secret References
      │
      ▼
Validate Capability Dependencies
      │
      ▼
Create Configuration Snapshot
```

## 8.3 Structural Validation

Examples:

- Required fields are present.
- Values have valid types.
- Enum values are supported.
- Numeric limits are within allowed ranges.

## 8.4 Cross-Field Validation

Examples:

- Persistent state requires a persistence adapter.
- External-process execution requires an executable configuration.
- Persistent CLI mode requires compatible protocol settings.
- An enabled connector requires its dependencies.
- Durable job recovery requires a supported execution owner.

## 8.5 Environment-Specific Validation

Production configuration may require stricter validation than development configuration.

For example, production must not silently depend on a development virtual environment.

## 8.6 Validation Errors

A validation error should identify:

- Configuration key.
- Failure category.
- Expected constraint.
- Source location where available.
- Safe remediation guidance.

## 8.7 Early Validation

Invalid configuration must be detected before side-effecting component initialization whenever possible.

---

# 9. Configuration Snapshot Architecture

## 9.1 Purpose

The application runtime shall use a resolved configuration snapshot.

The snapshot represents the effective validated configuration at a particular point in the runtime lifecycle.

## 9.2 Proposed Policy

The initial framework should use an immutable configuration snapshot for each runtime instance.

This avoids unexpected mutations while jobs and connectors are running.

## 9.3 Snapshot Metadata

A configuration snapshot may include:

- Schema version.
- Environment.
- Effective settings.
- Source metadata.
- Creation timestamp.
- Redacted diagnostic representation.
- Nonsecret configuration fingerprint.

## 9.4 Snapshot Access

Components should receive their required typed configuration rather than unrestricted access to all application secrets and settings.

## 9.5 Runtime Mutation

Ordinary application business actions shall not directly mutate the active configuration snapshot.

Supported runtime changes must use an explicit reconfiguration mechanism.

## 9.6 Configuration Freshness

The framework shall distinguish startup configuration from files that may have changed afterward.

A changed configuration file does not imply the running application adopted those changes.

---

# 10. Environment Management

## 10.1 Supported Environments

The framework should support named environments.

Recommended baseline:

- Development.
- Test.
- Production.

Custom environments may be supported when declared.

## 10.2 Environment Selection

The effective environment shall be selected explicitly through trusted startup configuration.

## 10.3 Environment Isolation

Applications must not unintentionally mix:

- Development database paths.
- Production credentials.
- Test-only dependencies.
- Debug logging policies.
- Production artifact directories.

## 10.4 Test Configuration

Test environments should support:

- Temporary directories.
- In-memory state.
- Mock connectors.
- Controlled executable fixtures.
- Isolated SQLite databases.

## 10.5 Production Configuration

Production configuration must account for:

- Packaged runtime locations.
- Credential references.
- Writable application directories.
- Safe logging.
- Resource limits.
- Startup and shutdown deadlines.

## 10.6 Illustrative Configuration

```yaml
application:
  name: example-app
  version: 1.0.0
  environment: development

runtime:
  mode: persistent-cli

logging:
  level: INFO

connectors:
  http:
    enabled: false

  sqlite:
    enabled: false

jobs:
  enabled: false
```

This example illustrates configuration ownership and optional capabilities.

It is not the finalized schema.

---

# 11. Secret Management

## 11.1 Purpose

Applications frequently require credentials for external services.

The framework shall support secure configuration references without forcing secrets into ordinary committed files.

## 11.2 Supported Secret Sources

Potential sources include:

- Environment variables.
- Operating-system credential stores.
- Approved application-specific secret providers.
- Explicitly configured protected files.

Not all secret sources must be implemented in the first release.

## 11.3 Secret References

Configuration may declare references to protected values.

Illustrative example:

```yaml
connectors:
  http:
    service_api:
      base_url: https://example.invalid/api
      authentication:
        token_secret: SERVICE_API_TOKEN
```

The configuration file identifies the secret reference, not the secret value.

## 11.4 Secret Resolution

Secrets should be resolved only when required by authorized components.

## 11.5 Secret Exposure

The framework must avoid exposing secrets through:

- Logs.
- Configuration dumps.
- Error envelopes.
- Architecture reports.
- Electron events.
- Diagnostic exports.

## 11.6 Secret Rotation

Secret rotation must define whether the affected connector requires reinitialization.

Automatic rotation is not required initially.

## 11.7 Security Limitations

The framework cannot guarantee secrecy against arbitrary malicious code executing inside the same Python process with equivalent privileges.

Its controls are intended to prevent accidental exposure and enforce supported application boundaries.

---

# 12. Application Composition Architecture

## 12.1 Purpose

The Composition Engine assembles application capabilities from registered services and connector implementations.

## 12.2 Composition Root

Every application shall have one clearly identified composition root.

The composition root is responsible for registering:

- Application metadata.
- Configuration schemas.
- Application services.
- Actions.
- Required connectors.
- State definitions.
- Job definitions.
- Lifecycle hooks.

## 12.3 Composition Versus Initialization

Registration defines what components exist.

Initialization creates or starts resources when required.

These operations must remain distinguishable.

## 12.4 Component Descriptor

A managed component descriptor should include:

- Unique identifier.
- Component type.
- Factory or implementation reference.
- Dependencies.
- Lifecycle scope.
- Required or optional status.
- Initialization policy.
- Readiness policy.
- Shutdown policy.

## 12.5 Conceptual Registration

```python
app.register_service(
    name="voice_generation",
    factory=create_voice_generation_service,
    dependencies=["audiocpp"],
)
```

This is an illustrative proposed interface.

The exact public API will be finalized separately.

## 12.6 Composition Validation

The framework must detect:

- Duplicate registrations.
- Missing dependencies.
- Circular dependencies.
- Invalid lifecycle relationships.
- Unsupported capabilities.
- Invalid configuration.

---

# 13. Dependency Graph Architecture

## 13.1 Purpose

The framework shall represent startup dependencies explicitly.

## 13.2 Dependency Graph Example

```text
Application Runtime
       │
       ▼
Configuration
       │
       ▼
Connector Registry
       │
       ├── SQLite Connector
       │         │
       │         ▼
       │    Persistent State
       │         │
       │         ▼
       │      Job Store
       │
       └── Process Connector
                 │
                 ▼
            Audio Adapter
                 │
                 ▼
        Audio Generation Service
                 │
                 ▼
          Action Registration
```

This is one possible dependency graph.

A connector not required by an application must not appear as an obligatory startup dependency.

## 13.3 Topological Initialization

Components shall initialize in an order that respects their dependencies.

## 13.4 Parallel Initialization

Independent components may initialize concurrently when safe.

The framework must not introduce unnecessary startup serialization.

## 13.5 Circular Dependencies

Circular dependency declarations must produce a structured configuration or composition error.

## 13.6 Optional Dependencies

Optional components must not force application failure unless they are required by an enabled capability or declared readiness condition.

## 13.7 Lifecycle Scope Validation

A longer-lived service must not retain unsafe references to shorter-lived services.

For example, an application-scoped singleton must not permanently retain a request-scoped execution context.

Such relationships should be detected where possible.

---

# 14. Component Lifecycle Contracts

## 14.1 Purpose

Managed components shall follow consistent lifecycle semantics.

## 14.2 Proposed Interface

```python
from typing import Protocol


class ManagedComponent(Protocol):
    async def start(self) -> None:
        ...

    async def close(self) -> None:
        ...
```

This is conceptual.

Lightweight components without external resources should not be forced to implement unnecessary startup and shutdown operations.

## 14.3 Optional Capabilities

Components may additionally provide:

- Readiness checks.
- Health checks.
- Reconfiguration support.
- Failure notifications.
- Shutdown preparation.

## 14.4 Lifecycle Ownership

The application lifecycle manager coordinates component lifecycle operations.

Component implementations retain responsibility for releasing their own resources.

## 14.5 Idempotency

Lifecycle operations must define behavior when called repeatedly.

Shutdown must be safe to request more than once.

## 14.6 Cleanup Guarantee

The framework shall make a best effort to clean up managed resources, including after partial startup failure.

It cannot guarantee cleanup after abrupt operating-system termination or unrecoverable process failure.

---

# 15. Application Lifecycle State Machine

## 15.1 Proposed States

```text
CREATED
   │
   ▼
CONFIGURING
   │
   ▼
INITIALIZING
   │
   ▼
READY
   │
   ▼
RUNNING
   │
   ▼
STOPPING
   │
   ▼
STOPPED
```

Failure may occur during configuration, initialization, or runtime operation.

A failure may trigger cleanup before the application reaches its final stopped or failed state.

## 15.2 State Definitions

| State | Meaning |
|---|---|
| Created | Application definition exists |
| Configuring | Configuration sources are being resolved |
| Initializing | Required runtime components are starting |
| Ready | Required initialization and readiness conditions are satisfied |
| Running | Runtime is accepting or executing supported operations |
| Stopping | New work is restricted and cleanup is underway |
| Stopped | Normal shutdown completed |
| Failed | Fatal application lifecycle failure occurred |

## 15.3 State Transition Rules

- Invalid transitions shall be rejected.
- Readiness shall not be reported before required initialization completes.
- Once stopping begins, ordinary new work shall not be admitted.
- Fatal failures shall not be hidden by later nonfatal events.
- Lifecycle transitions shall be observable.

## 15.4 Failure State

A fatal failure should preserve diagnostic context even if the lifecycle manager subsequently performs cleanup.

The implementation must define whether `FAILED` is an intermediate or final externally visible state.

**Proposed policy:** Preserve fatal-failure information separately from cleanup state so failure evidence is not lost.

---

# 16. Application Bootstrap

## 16.1 Purpose

Bootstrap creates the runtime environment for a consuming application.

## 16.2 Bootstrap Sequence

```text
Application Entry Point
        │
        ▼
Create Application Definition
        │
        ▼
Load Configuration Sources
        │
        ▼
Merge and Validate Configuration
        │
        ▼
Resolve Environment and Secrets
        │
        ▼
Register Capabilities
        │
        ▼
Build Dependency Graph
        │
        ▼
Validate Composition
        │
        ▼
Initialize Required Components
        │
        ▼
Restore Required Persistent State
        │
        ▼
Initialize Registered Application Services
        │
        ▼
Initialize CLI Runtime
        │
        ▼
Evaluate Readiness
        │
        ▼
Application READY
```

The actual order of state restoration, services, and connectors shall follow the validated dependency graph.

## 16.3 Bootstrap Constraints

Application bootstrap must not:

- Execute unrelated business actions.
- Start optional connectors without a declared need.
- Ignore invalid configuration.
- Suppress required initialization failures.
- Bypass lifecycle ownership.
- Depend on Electron for standalone CLI operation.

## 16.4 One-Shot Bootstrap

One-shot mode should initialize only the resources required for the requested action, subject to mandatory application initialization rules.

## 16.5 Persistent Bootstrap

Persistent mode may initialize reusable resources once and retain them across requests.

## 16.6 Bootstrap Diagnostics

Startup diagnostics should identify:

- Current initialization phase.
- Failed component.
- Dependency chain.
- Failure category.
- Cleanup status.
- Safe remediation guidance.

---

# 17. Component Initialization Policies

## 17.1 Eager Initialization

A component starts during application bootstrap.

Suitable for:

- Required configuration-dependent services.
- Critical persistence stores.
- Mandatory runtime components.

## 17.2 Lazy Initialization

A component starts when first required.

Suitable for:

- Optional HTTP clients.
- Rarely used external integrations.
- Expensive optional resources.

## 17.3 Conditional Initialization

A component starts only when its declared capability or application profile requires it.

## 17.4 Initialization Policy Validation

The framework must reject invalid combinations.

For example, a required eagerly initialized service must not depend on an unavailable component that cannot be initialized before its use.

## 17.5 Dependency Initialization

Lazy dependencies must be initialized safely under concurrent first-use conditions.

The framework must avoid creating duplicate application-scoped instances unintentionally.

## 17.6 Initialization Failure

A lazy component failure should normally affect only operations requiring that component, unless it is configured as critical to overall application availability.

---

# 18. Readiness Architecture

## 18.1 Purpose

Readiness determines whether the application can accept its supported workload.

## 18.2 Readiness Versus Health

**Readiness** answers:

Can this application accept the relevant operation?

**Health** answers:

Is this runtime or component functioning according to its defined health checks?

These are related but distinct.

## 18.3 Application Readiness

The framework may report overall readiness when:

- Required configuration is valid.
- Required services are initialized.
- Mandatory dependencies satisfy their readiness policies.
- CLI transport can process supported requests.
- The application is not shutting down.

## 18.4 Optional Connector Failure

An application may remain ready when an optional connector is unavailable.

## 18.5 Capability Readiness

The framework should support capability-level readiness where meaningful.

For example:

```text
Application: READY

Capabilities:
  voice_generation: READY
  image_generation: DEGRADED
  project_management: READY
```

This avoids treating every optional external dependency failure as a total application failure.

## 18.6 Readiness and Handshake

The Electron bridge shall establish session readiness through the compatible CLI handshake.

The Python runtime must not return successful session readiness before mandatory initialization is complete.

## 18.7 Readiness Changes

Readiness may change after startup.

The runtime should expose relevant changes through diagnostics and approved events.

## 18.8 Readiness Limits

A successful readiness check does not guarantee that every future operation will succeed.

---

# 19. Runtime Operation

## 19.1 Purpose

Once ready, the runtime accepts and executes registered application actions.

## 19.2 Runtime Responsibilities

During normal operation, the framework coordinates:

- Request admission.
- Action execution.
- Connector access.
- State access.
- Job submission.
- Events.
- Diagnostics.
- Error boundaries.
- Resource cleanup.

## 19.3 Runtime Resource Ownership

Application-scoped components remain managed for the lifetime of the runtime.

Request-scoped resources are cleaned up when their execution context completes.

Job-scoped resources are managed by the Job Manager.

## 19.4 Runtime Failure Classification

Failures shall be classified by impact.

| Classification | Example | Typical effect |
|---|---|---|
| Request failure | Invalid action payload | Request fails |
| Component failure | Optional HTTP service unavailable | Affected capability degrades |
| Required service failure | Critical persistence unavailable | Relevant operations unavailable; runtime may become unready |
| Fatal runtime failure | Protocol engine integrity compromised | Controlled shutdown |
| Process termination | Python crash | External bridge detects loss |

The exact mapping is configuration- and capability-dependent.

## 19.5 Fault Isolation

Expected operation failures should not terminate unrelated healthy operations.

Fatal infrastructure failures may require runtime shutdown when safe continuation cannot be guaranteed.

---

# 20. Lifecycle Hooks

## 20.1 Purpose

Applications and managed components may register lifecycle hooks.

## 20.2 Proposed Hook Categories

```text
before_start
after_configuration
before_ready
after_ready
before_shutdown
after_shutdown
on_failure
```

The final hook names and execution contract remain open.

## 20.3 Hook Requirements

Hooks shall have:

- Explicit registration.
- Defined execution phase.
- Ordering rules.
- Timeout or cancellation policy where needed.
- Error-handling policy.
- Access to appropriate lifecycle context.

## 20.4 Hook Ownership

The framework owns hook execution.

The application owns hook behavior.

## 20.5 Restrictions

Hooks must not be used to bypass the normal service composition system.

A hook that starts an unmanaged subprocess or persistent resource may violate framework ownership requirements.

## 20.6 Failure Handling

Failures in critical hooks may abort startup or alter shutdown outcome.

Failures in optional notification hooks should not unnecessarily destabilize the runtime.

---

# 21. Partial Initialization Failure

## 21.1 Problem

Startup can fail after some components have already initialized.

For example:

1. Configuration loads successfully.
2. SQLite initializes.
3. Persistent state restores.
4. An application service fails.
5. Startup cannot complete.

The framework must avoid leaving successfully initialized resources unmanaged.

## 21.2 Cleanup Sequence

```text
Initialization Begins
         │
         ▼
Component A Starts
         │
         ▼
Component B Starts
         │
         ▼
Component C Fails
         │
         ▼
Stop Initialization
         │
         ▼
Close Component B
         │
         ▼
Close Component A
         │
         ▼
Record Failure
         │
         ▼
Report Startup Failure
```

Cleanup follows reverse dependency order where applicable.

## 21.3 Cleanup Failure

A cleanup failure must not overwrite the original initialization failure.

Both failures should be retained in controlled diagnostics.

## 21.4 Retry Policy

The framework must not automatically retry initialization indefinitely.

Retries, if supported, require bounded policies and consideration of side effects.

## 21.5 Readiness

Application readiness must remain false after failed required initialization.

## 21.6 External Side Effects

Cleanup cannot guarantee reversal of all external effects.

Application-specific compensation is required for operations that create durable side effects during initialization.

---

# 22. Graceful Shutdown

## 22.1 Purpose

Graceful shutdown releases managed resources while preserving valid application and persistence outcomes.

## 22.2 Shutdown Triggers

Possible triggers include:

- Normal one-shot completion.
- Electron shutdown.
- Authorized `system.shutdown`.
- Operating-system termination signal.
- Fatal runtime failure.
- Explicit application lifecycle request.

## 22.3 Shutdown Sequence

```text
Shutdown Requested
        │
        ▼
Mark Runtime STOPPING
        │
        ▼
Stop New Request Admission
        │
        ▼
Apply Active Request Policy
        │
        ▼
Apply Job Shutdown Policy
        │
        ▼
Wait Within Defined Deadlines
        │
        ▼
Release Job and Request Resources
        │
        ▼
Close Application Services
        │
        ▼
Close Connectors and State Stores
        │
        ▼
Flush Diagnostics
        │
        ▼
Close Protocol Transport
        │
        ▼
Mark Runtime STOPPED
```

The exact cleanup order shall be derived from dependencies and resource ownership.

## 22.4 Shutdown Policies

Supported policies may include:

- Wait for completion.
- Request cooperative cancellation.
- Cancel within a deadline.
- Mark interrupted work appropriately.
- Transfer eligible work to a durable executor where supported.

## 22.5 Active Requests

The framework must define whether active requests:

- Complete.
- Are cancelled.
- Are failed with a shutdown error.

The selected policy may vary by execution mode and operation type.

## 22.6 Active Jobs

Job shutdown follows `job-and-process-management.md`.

Persisted job metadata does not guarantee continued execution.

## 22.7 Connector Shutdown

Connectors shall not be closed before their active dependent operations are appropriately completed, cancelled, or released.

## 22.8 Persistent State

Committed persistent state shall not be deleted during ordinary shutdown.

## 22.9 Shutdown Deadlines

Shutdown shall have configurable limits.

If graceful shutdown cannot complete, the owner may escalate to platform-supported termination behavior.

## 22.10 Idempotent Shutdown

Repeated shutdown requests must not run unsafe duplicate cleanup sequences.

---

# 23. Shutdown Failure Handling

## 23.1 Failure Categories

Shutdown may encounter:

- Job cancellation failure.
- External process termination failure.
- Connector close failure.
- Persistence flush failure.
- Log flush failure.
- Hook failure.
- Shutdown timeout.

## 23.2 Error Aggregation

The lifecycle manager should collect cleanup failures without stopping all remaining cleanup unnecessarily.

## 23.3 Failure Reporting

The final process outcome must reflect relevant fatal shutdown failures according to the approved exit-code policy.

## 23.4 Unknown Outcomes

If a process is forcibly terminated, some operations may have unknown final outcomes.

The framework must not claim successful completion merely because termination was requested.

## 23.5 Cleanup Diagnostics

The framework should retain:

- Original shutdown trigger.
- Components closed.
- Components that failed cleanup.
- Outstanding jobs or processes.
- Forced termination actions.
- Final termination status.

---

# 24. One-Shot CLI Lifecycle

## 24.1 Purpose

One-shot execution initializes the required runtime, executes one command, and terminates.

## 24.2 Lifecycle

```text
Process Starts
      │
      ▼
Load Configuration
      │
      ▼
Compose Required Components
      │
      ▼
Initialize Required Services
      │
      ▼
Execute Action
      │
      ▼
Return Terminal Response
      │
      ▼
Release Resources
      │
      ▼
Process Exits
```

## 24.3 Initialization Optimization

Only required optional capabilities should be initialized.

## 24.4 State Behavior

Request and process state are volatile.

Any state requiring survival across invocations must be explicitly persisted.

## 24.5 Job Restrictions

A one-shot process must not acknowledge a background job as independently continuing unless an actual separate execution owner exists.

## 24.6 Exit Status

Process exit codes must follow the approved CLI protocol policy.

---

# 25. Persistent CLI Lifecycle

## 25.1 Purpose

Persistent CLI mode supports long-lived Electron-backed applications.

## 25.2 Lifecycle

```text
Electron Launches Python
        │
        ▼
AdharaSutra Bootstrap
        │
        ▼
Required Services READY
        │
        ▼
Protocol Handshake
        │
        ▼
Persistent Session ACTIVE
        │
        ├── Execute Requests
        ├── Publish Events
        ├── Manage Jobs
        └── Maintain Resources
        │
        ▼
Shutdown / Fatal Failure
        │
        ▼
Managed Cleanup
        │
        ▼
Process Exit
```

## 25.3 Long-Lived Resources

Application-scoped connectors and services may remain initialized across multiple requests.

## 25.4 Session Lifecycle

The persistent session follows its own lifecycle.

Session termination does not necessarily imply all process-level state is durable or recoverable.

## 25.5 Concurrent Requests

The runtime must maintain request isolation and enforce supported concurrency limits.

## 25.6 Restart Behavior

A restarted Python process creates a new runtime instance.

Its in-memory state must be rebuilt or restored according to explicit policies.

---

# 26. Electron Lifecycle Integration

## 26.1 Process Ownership

The Electron main process owns the standard AdharaSutra Python backend process in a desktop deployment.

## 26.2 Readiness

Electron shall not treat the Python backend as ready until required startup and protocol handshake succeed.

## 26.3 Backend Failure

If Python terminates unexpectedly, the Electron bridge shall invalidate pending requests and report transport-level failure.

## 26.4 Restart

The bridge may follow a bounded configured restart policy.

It must not automatically replay non-idempotent business actions.

## 26.5 Shutdown

Electron requests backend shutdown through the approved CLI protocol mechanism.

The backend lifecycle manager coordinates cleanup.

## 26.6 Renderer Reload

A renderer reload must not automatically restart the Python runtime unless the application explicitly requires it.

## 26.7 Multiple Windows

Application runtime ownership is associated with Electron main, not an arbitrary renderer window.

## 26.8 Packaging

Runtime configuration must resolve production executable paths and application data directories independently of development assumptions.

---

# 27. Configuration Reloading

## 27.1 Purpose

Some applications may need settings changes while running.

## 27.2 Initial Policy

**Proposed decision:** Configuration is immutable during a runtime session by default.

Live reloading is optional and deferred until its consistency guarantees are established.

## 27.3 Reconfiguration Categories

Settings may be classified as:

- Immutable after startup.
- Restart required.
- Component restart required.
- Dynamically reconfigurable.

## 27.4 Safe Reconfiguration

A reconfiguration operation must define:

1. New configuration validation.
2. Affected components.
3. Dependent services.
4. In-flight operations.
5. Transition ordering.
6. Failure handling.
7. Rollback or recovery behavior.

## 27.5 Secret Rotation

Rotated credentials may require connector reinitialization.

## 27.6 Concurrency

Configuration changes must not produce inconsistent component state during concurrent execution.

## 27.7 Scope

Automatic file watching and hot reload are not mandatory for the initial framework.

---

# 28. Runtime Diagnostics

## 28.1 Configuration Diagnostics

The framework should expose safe diagnostics for:

- Effective environment.
- Loaded configuration sources.
- Missing required values.
- Invalid settings.
- Capability activation.
- Disabled optional modules.
- Redacted configuration summary.

## 28.2 Lifecycle Diagnostics

The framework should expose:

- Runtime state.
- Initialization phase.
- Component readiness.
- Component health.
- Active dependency failures.
- Shutdown progress.
- Cleanup failures.

## 28.3 Framework Actions

Relevant reserved actions may include:

```text
system.health
system.version
system.capabilities
system.shutdown
```

These operations must remain consistent with `cli-protocol.md`.

## 28.4 Diagnostic Safety

Framework diagnostics must not expose secrets or sensitive application configuration values.

## 28.5 Reporting Boundaries

Development tooling may analyze source configuration files.

Production runtime diagnostics shall report active runtime state rather than claim static source inspection proves operational correctness.

---

# 29. Error Architecture

## 29.1 Configuration Errors

Proposed codes:

```text
CONFIG_SOURCE_NOT_FOUND
CONFIG_PARSE_FAILED
CONFIG_VALIDATION_FAILED
CONFIG_REQUIRED_VALUE_MISSING
CONFIG_UNKNOWN_KEY
CONFIG_OVERRIDE_INVALID
CONFIG_SECRET_UNAVAILABLE
CONFIG_ENVIRONMENT_INVALID
CONFIG_INCOMPATIBLE_OPTIONS
```

## 29.2 Composition Errors

Proposed codes:

```text
SERVICE_NOT_REGISTERED
SERVICE_DUPLICATE_REGISTRATION
SERVICE_DEPENDENCY_MISSING
SERVICE_DEPENDENCY_CYCLE
SERVICE_SCOPE_INVALID
CAPABILITY_UNAVAILABLE
```

## 29.3 Lifecycle Errors

Proposed codes:

```text
LIFECYCLE_INVALID_TRANSITION
LIFECYCLE_INITIALIZATION_FAILED
LIFECYCLE_NOT_READY
LIFECYCLE_SHUTTING_DOWN
LIFECYCLE_SHUTDOWN_FAILED
LIFECYCLE_CLEANUP_FAILED
LIFECYCLE_TIMEOUT
```

These identifiers must be reconciled with the framework-wide error catalog.

## 29.4 Error Propagation

Errors shall preserve:

- Stable error category.
- Affected component.
- Lifecycle phase.
- Correlation metadata where applicable.
- Safe human-readable explanation.
- Internal cause for diagnostics.

## 29.5 Primary and Secondary Failures

When initialization fails and subsequent cleanup also fails, the original initialization failure must remain identifiable.

---

# 30. Security Architecture

## 30.1 Configuration Trust

Not all configuration sources have equal trust.

The runtime shall restrict which settings can be overridden by untrusted requests.

## 30.2 Secret Handling

Secrets shall be redacted from ordinary logs and diagnostics.

## 30.3 Configuration File Safety

Configuration files shall be parsed as data.

Loading configuration must not require executing arbitrary source code.

## 30.4 Path Safety

Configured executable and storage paths must follow the framework's path-validation policies.

## 30.5 Production Restrictions

Production configuration should reject or explicitly warn about unsafe settings such as unrestricted debug capabilities.

## 30.6 Lifecycle Authorization

Runtime shutdown and reconfiguration actions must be restricted to authorized callers.

## 30.7 Dependency Initialization

Component factories must come from trusted application or plugin registration.

The framework must not dynamically import arbitrary renderer-provided module paths.

## 30.8 Diagnostic Access

Sensitive runtime diagnostics should be accessible only through approved interfaces.

---

# 31. Resource Efficiency

## 31.1 Startup Efficiency

The framework must avoid initializing unused optional capabilities.

## 31.2 Lazy Initialization

Lazy components should initialize once per declared scope, with safe concurrent initialization.

## 31.3 Configuration Parsing

Configuration should not be repeatedly parsed for every ordinary request.

## 31.4 Reusable Resources

Persistent applications may reuse HTTP clients, database facilities, and other managed resources.

## 31.5 Shutdown Efficiency

Cleanup must have bounded waiting behavior.

## 31.6 Memory Ownership

Component scope and retention must avoid keeping request-specific objects alive indefinitely.

## 31.7 Benchmarking

Performance evaluation should measure:

- Configuration parsing.
- Configuration validation.
- Dependency graph resolution.
- Minimal startup.
- Full startup with selected connectors.
- Lazy first-use initialization.
- Graceful shutdown.
- Partial failure cleanup.

Numeric thresholds shall follow approved non-functional requirements.

---

# 32. Testing Strategy

## 32.1 Configuration Unit Tests

Verify:

- Default values.
- Source precedence.
- Nested mapping merge.
- List replacement.
- Missing versus null.
- Environment-variable mapping.
- Schema validation.
- Unknown keys.
- Invalid overrides.
- Source traceability.

## 32.2 Secret Handling Tests

Verify:

- Secret references.
- Missing secrets.
- Redaction.
- Unauthorized exposure prevention.
- Connector initialization with protected credentials.

## 32.3 Composition Tests

Verify:

- Service registration.
- Duplicate detection.
- Missing dependencies.
- Cyclic dependencies.
- Scope violations.
- Optional components.
- Test overrides.

## 32.4 Lifecycle Tests

Verify:

- Valid transitions.
- Invalid transitions.
- Startup ordering.
- Readiness.
- Graceful shutdown.
- Repeated shutdown.
- Hook failures.
- Resource cleanup.

## 32.5 Partial Failure Tests

Verify:

- Failure during connector initialization.
- Failure during state restoration.
- Failure during service startup.
- Cleanup after partial initialization.
- Preservation of primary failure evidence.

## 32.6 One-Shot Tests

Verify:

- Required-only initialization.
- Action execution.
- Response delivery.
- Cleanup.
- Exit status.
- Volatile state lifetime.

## 32.7 Persistent CLI Tests

Verify:

- Startup and handshake.
- Multiple requests.
- Lazy connector activation.
- Failure isolation.
- Session termination.
- Shutdown.

## 32.8 Electron Integration Tests

Verify:

- Runtime startup configuration.
- Readiness signaling.
- Python crash handling.
- Renderer reload behavior.
- Controlled shutdown.
- Production executable discovery.

## 32.9 Cross-Platform Tests

Validate relevant lifecycle and configuration behavior on:

- Windows.
- Linux.
- macOS.

## 32.10 Failure Injection

Simulate:

- Invalid configuration.
- Missing secret.
- Circular dependency.
- Unavailable connector.
- Startup timeout.
- Job shutdown timeout.
- Process termination failure.
- Database restoration failure.
- Logging failure.
- Repeated shutdown requests.

---

# 33. Architecture Verification Rules

The architecture verifier should enforce applicable configuration and lifecycle rules.

| Rule ID | Description |
|---|---|
| CL-VER-001 | Application defines a valid AdharaSutra bootstrap |
| CL-VER-002 | Configuration follows the approved schema |
| CL-VER-003 | Configuration sources use supported mechanisms |
| CL-VER-004 | Environment configuration has defined selection rules |
| CL-VER-005 | Required configuration fields are validated |
| CL-VER-006 | Secret values are not embedded in prohibited locations |
| CL-VER-007 | Components use approved registration mechanisms |
| CL-VER-008 | Service dependencies are resolvable |
| CL-VER-009 | Service dependency cycles are prohibited |
| CL-VER-010 | Lifecycle scope relationships are valid |
| CL-VER-011 | Optional capabilities are not initialized without need |
| CL-VER-012 | Managed resources declare appropriate cleanup behavior |
| CL-VER-013 | Application readiness follows required initialization |
| CL-VER-014 | Shutdown uses the framework lifecycle mechanism |
| CL-VER-015 | Application does not implement a competing runtime lifecycle |
| CL-VER-016 | Core configuration does not depend on optional connectors |
| CL-VER-017 | Runtime does not require development tooling |
| CL-VER-018 | Production configuration avoids unsupported development paths |
| CL-VER-019 | Configuration and lifecycle exceptions are documented |
| CL-VER-020 | Required lifecycle and configuration tests are present |

Not every rule can be proven statically.

Runtime behavior such as cleanup, readiness, and shutdown requires executable tests.

---

# 34. Existing Application Migration

## 34.1 Purpose

Existing applications may implement custom:

- Configuration loaders.
- Environment-variable parsing.
- Global settings.
- Service registries.
- Initialization sequences.
- Shutdown hooks.
- Connector startup.
- Process cleanup.
- Runtime readiness.
- Logging initialization.

AdharaSutra should support incremental migration.

## 34.2 Discovery

The migration engine should identify:

- Configuration files.
- Configuration precedence.
- Environment selection.
- Secret storage patterns.
- Application entry points.
- Service initialization.
- Resource ownership.
- Shutdown logic.
- Existing readiness mechanisms.

## 34.3 Migration Pipeline

```text
Existing Application
        │
        ▼
Discover Configuration and Lifecycle
        │
        ▼
Record Current Behavior
        │
        ▼
Map Configuration Schemas
        │
        ▼
Introduce AdharaSutra Bootstrap
        │
        ▼
Register Existing Services
        │
        ▼
Migrate Configuration Loading
        │
        ▼
Migrate Startup and Shutdown
        │
        ▼
Verify Behavioral Compatibility
        │
        ▼
Remove Duplicated Infrastructure
```

## 34.4 Compatibility

Migration must preserve:

- Required application settings.
- Environment selection.
- External dependency configuration.
- Startup behavior where relied upon.
- Shutdown behavior.
- Existing business functionality.
- Persistent data compatibility.

## 34.5 Transitional Adapters

Legacy configuration or service-management mechanisms may be wrapped temporarily.

## 34.6 Migration Verification

Architecture conformance alone is not sufficient.

Startup, shutdown, and business regression tests must pass.

---

# 35. Representative End-to-End Scenarios

## CL-S01 — Minimal CLI Application

**Given** an application uses only the minimal CLI profile,

**When** it starts,

**Then** AdharaSutra shall validate configuration and initialize required core services.

**And** optional HTTP, WebSocket, SQLite, and job components shall not initialize without a declared need.

## CL-S02 — Persistent Electron Application

**Given** Electron starts the Python runtime,

**When** configuration and required initialization succeed,

**Then** the runtime shall become ready.

**And** the bridge shall establish a compatible CLI session.

## CL-S03 — Invalid Configuration

**Given** a required configuration field is invalid,

**When** startup begins,

**Then** the framework shall report a structured validation error.

**And** dependent services shall not initialize.

## CL-S04 — Missing Secret

**Given** a required connector references an unavailable secret,

**When** initialization occurs,

**Then** the framework shall report a safe secret-resolution failure.

**And** shall not expose secret values.

## CL-S05 — Optional Connector Failure

**Given** an optional external service is unavailable,

**When** the application starts,

**Then** unrelated capabilities may remain ready according to configuration.

**And** the affected capability shall report its actual availability.

## CL-S06 — Circular Dependency

**Given** two services declare a dependency cycle,

**When** composition validation runs,

**Then** initialization shall fail before affected services start.

**And** the diagnostic shall identify the cycle.

## CL-S07 — Lazy Initialization

**Given** an optional connector is configured for lazy initialization,

**When** the application starts without using it,

**Then** the connector shall not acquire unnecessary external resources.

**When** the connector is first requested,

**Then** it shall initialize according to its lifecycle policy.

## CL-S08 — Partial Initialization Failure

**Given** two components initialize and a third fails,

**When** startup aborts,

**Then** the framework shall clean up successfully initialized resources in a safe dependency order.

**And** preserve evidence of the original failure.

## CL-S09 — Active Job During Shutdown

**Given** jobs are running,

**When** application shutdown begins,

**Then** the Job Manager shall apply the configured shutdown policy.

**And** connector cleanup shall respect remaining execution ownership.

## CL-S10 — Repeated Shutdown

**Given** shutdown has already started,

**When** another shutdown request arrives,

**Then** the framework shall not perform unsafe duplicate cleanup.

## CL-S11 — Renderer Reload

**Given** the Electron renderer reloads,

**When** Electron main retains the Python runtime,

**Then** the Python application shall not restart solely because the renderer was recreated.

## CL-S12 — Production Packaging

**Given** a packaged Electron application,

**When** its backend initializes,

**Then** configuration and runtime paths shall resolve according to approved production packaging rules.

## CL-S13 — Configuration Source Precedence

**Given** the same setting is defined in multiple sources,

**When** configuration is resolved,

**Then** the effective value shall follow the documented precedence rules.

**And** diagnostics shall identify the winning source without exposing sensitive values.

## CL-S14 — Persistent State Restoration Failure

**Given** required persistent state is incompatible or unavailable,

**When** startup attempts restoration,

**Then** the application shall not report full readiness.

**And** the framework shall provide a classified restoration failure.

## CL-S15 — Existing Application Migration

**Given** an application has a custom configuration loader and startup sequence,

**When** it adopts AdharaSutra,

**Then** equivalent configuration and lifecycle behavior shall remain testable.

**And** duplicated infrastructure may be removed after verification.

---

# 36. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| CL-D01 | Configuration ownership | Framework-managed |
| CL-D02 | Application settings | Application-defined schemas |
| CL-D03 | Default file format | YAML proposed |
| CL-D04 | Configuration precedence | Defaults → files → environment → explicit overrides |
| CL-D05 | Merge semantics | Mapping merge, scalar/list replacement |
| CL-D06 | Unknown keys | Strict validation by default |
| CL-D07 | Effective configuration | Validated immutable snapshot |
| CL-D08 | Secret handling | Protected references and providers |
| CL-D09 | Environment selection | Explicit trusted startup configuration |
| CL-D10 | Composition | Registration and factories |
| CL-D11 | Dependency management | Validated acyclic dependency graph |
| CL-D12 | Initialization order | Dependency-aware |
| CL-D13 | Independent initialization | Concurrent where safe |
| CL-D14 | Optional capabilities | Lazy or conditional |
| CL-D15 | Application lifecycle | Explicit state machine |
| CL-D16 | Readiness | Required components and policies |
| CL-D17 | Health | Separate from readiness |
| CL-D18 | Partial startup failure | Reverse-dependency cleanup |
| CL-D19 | Shutdown | Coordinated and idempotent |
| CL-D20 | Configuration reload | Deferred optional capability |
| CL-D21 | One-shot lifecycle | Required-only initialization and cleanup |
| CL-D22 | Persistent lifecycle | Reusable managed resources |
| CL-D23 | Electron ownership | Main process manages Python lifetime |
| CL-D24 | Verification | Deterministic-first |
| CL-D25 | Existing migration | Incremental with compatibility adapters |

These decisions remain proposed until reviewed and validated.

---

# 37. Outstanding Questions

## CL-OQ-001 — Configuration Format

Should YAML be the default, or should TOML be preferred for Python-centric applications?

**Recommendation:** Select one primary format and keep optional loaders separate.

## CL-OQ-002 — Configuration Schema Technology

Should the framework use Pydantic, dataclasses, or an abstraction supporting multiple validation technologies?

**Recommendation:** Define a stable public validation contract and evaluate implementation overhead before selecting the underlying technology.

## CL-OQ-003 — Dependency Injection

Should the framework implement a custom dependency-injection container?

**Recommendation:** Begin with explicit service registration, factories, and dependency resolution rather than a complex container.

## CL-OQ-004 — Lifecycle Async Model

Should all managed components expose asynchronous lifecycle hooks?

**Recommendation:** Support async lifecycle coordination while allowing simple synchronous components through appropriate adapters.

## CL-OQ-005 — Readiness Granularity

Should the runtime report only overall readiness or capability-level readiness?

**Recommendation:** Support overall and capability-level status, with the latter available through diagnostics.

## CL-OQ-006 — Live Configuration Reloading

Should configuration files be watched automatically?

**Recommendation:** Defer automatic file watching until reconfiguration safety is fully defined.

## CL-OQ-007 — Service Initialization Concurrency

Should independent components initialize concurrently by default?

**Recommendation:** Permit bounded concurrency where dependencies and component safety allow it.

## CL-OQ-008 — Shutdown Deadline Defaults

What deadlines should apply to requests, jobs, connectors, and overall shutdown?

**Recommendation:** Define separate configurable limits using representative application tests.

## CL-OQ-009 — Lifecycle Hook Ordering

Should lifecycle hooks use explicit priorities or dependency declarations?

**Recommendation:** Prefer dependency-aware ordering for resource-owning components and simple ordered hooks for notifications.

## CL-OQ-010 — Configuration Error Recovery

Should the runtime permit corrected configuration to be reloaded after a failed startup without restarting the process?

**Recommendation:** Do not require this initially; restarting with corrected configuration is simpler and more predictable.

## CL-OQ-011 — Multiple Runtime Instances

Should one Python process host multiple AdharaSutra applications?

**Recommendation:** Treat one application per runtime instance as the initial model, with explicitly scoped multiple-instance support only if required.

## CL-OQ-012 — Secret Provider Interface

Which credential providers should be included initially?

**Recommendation:** Begin with environment-variable references and extensible provider contracts, adding platform credential stores when needed.

## CL-OQ-013 — Runtime Diagnostics Exposure

Should Electron be allowed to retrieve the effective configuration?

**Recommendation:** Expose only a controlled redacted diagnostic representation, not unrestricted configuration data.

## CL-OQ-014 — Failure Recovery

Should critical components support automatic reinitialization after runtime failure?

**Recommendation:** Support explicit failure policies and avoid universal automatic restarts that may repeat side effects.

---

# 38. Functional Requirement Traceability

| Requirement group | Configuration/lifecycle responsibility |
|---|---|
| FR-RUN | Runtime initialization and lifecycle |
| FR-CFG | Configuration sources, merging, validation |
| FR-DI | Service composition and dependencies |
| FR-CON | Connector initialization and cleanup |
| FR-CLI | CLI startup and shutdown |
| FR-ELC | Electron readiness and process lifecycle |
| FR-STATE | State restoration and cleanup |
| FR-JOB | Job initialization and shutdown |
| FR-ERR | Configuration and lifecycle error classification |
| FR-LOG | Startup and shutdown diagnostics |
| FR-SEC | Secrets, configuration trust, authorization |
| FR-TEST | Configuration and lifecycle testing |
| FR-ARCH | Architecture conformance |
| FR-MIG | Existing application migration |
| FR-PKG | Production runtime configuration |

---

# 39. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-PERF | Efficient configuration and dependency-aware startup |
| NFR-RES | Optional initialization and resource cleanup |
| NFR-REL | Validated configuration and lifecycle control |
| NFR-AVAIL | Accurate readiness and controlled degradation |
| NFR-SCALE | Bounded concurrent initialization |
| NFR-SEC | Protected secrets and trusted configuration |
| NFR-PORT | Platform-aware configuration paths |
| NFR-MAINT | Explicit module and lifecycle ownership |
| NFR-EXT | Configurable services and extension schemas |
| NFR-TEST | Testable configuration and lifecycle components |
| NFR-COMP | Versioned configuration and public contracts |
| NFR-ARCH | Enforceable composition and dependency rules |
| NFR-MIG | Incremental adoption |
| NFR-OBS | Lifecycle diagnostics and correlation |
| NFR-OPS | Safe startup, shutdown, and packaging |

---

# 40. Acceptance Criteria

The Configuration and Lifecycle architecture may be approved when:

- [ ] Configuration ownership is defined.
- [ ] Supported configuration sources are identified.
- [ ] Precedence and merge semantics are unambiguous.
- [ ] Null, missing, and default values are distinguishable.
- [ ] Framework and application schemas are separated.
- [ ] Configuration validation occurs before dependent initialization.
- [ ] Cross-field configuration constraints are supported.
- [ ] Environment isolation is defined.
- [ ] Secret references and redaction policies are defined.
- [ ] Effective configuration snapshots are supported conceptually.
- [ ] Application composition root ownership is clear.
- [ ] Service registration and dependency validation are defined.
- [ ] Component lifecycle scopes are defined.
- [ ] Optional capabilities do not initialize unnecessarily.
- [ ] Startup ordering follows dependencies.
- [ ] Readiness and health are distinguished.
- [ ] Application lifecycle transitions are defined.
- [ ] Partial initialization cleanup is specified.
- [ ] Lifecycle hook behavior is documented.
- [ ] Graceful shutdown is dependency-aware.
- [ ] Shutdown is safe to request repeatedly.
- [ ] Jobs and processes follow their ownership policies.
- [ ] One-shot execution has defined cleanup semantics.
- [ ] Persistent CLI execution retains resources appropriately.
- [ ] Electron startup and shutdown integrate with the lifecycle manager.
- [ ] Configuration reloading limitations are explicit.
- [ ] Errors and diagnostics are standardized.
- [ ] Production packaging assumptions are documented.
- [ ] Architecture verification rules are identifiable.
- [ ] Existing application migration is feasible.
- [ ] Critical unresolved decisions are approved or deferred.

---

# 41. Final Architecture Summary

AdharaSutra provides one centralized configuration and lifecycle foundation for independent Python applications.

The Configuration Engine manages:

- Configuration sources.
- Precedence.
- Merging.
- Schema validation.
- Environment selection.
- Secret references.
- Effective configuration snapshots.
- Configuration diagnostics.

The Composition Engine manages:

- Component registration.
- Service factories.
- Dependency resolution.
- Capability declarations.
- Lifecycle scopes.
- Component ownership.

The Lifecycle Engine manages:

- Application bootstrap.
- Dependency-aware initialization.
- Readiness.
- Runtime state.
- Failure handling.
- Partial failure cleanup.
- Graceful shutdown.
- Resource release.

Consuming applications define their settings, services, capabilities, and business behavior through approved extension points.

A minimal CLI application can initialize only its required core capabilities.

A complex Electron-backed application can initialize and coordinate persistent state, jobs, HTTP clients, external processes, and application services using the same foundational mechanisms.

The architecture favors validated immutable configuration snapshots, explicit service composition, optional capabilities, and dependency-aware lifecycle management.

The central guarantee is:

**Every component has an explicit configuration, dependency relationship, lifecycle owner, and cleanup policy.**

---

# 42. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architecture review

**Next Document:** `docs/design/error-handling-and-observability.md`

The next design document should define the framework-wide error taxonomy, domain-to-technical error mapping, structured logging, request/job correlation, health diagnostics, metrics, sensitive-data redaction, and the separation between application results and diagnostic output.

---

**AdharaSutra — Build once. Standardize everywhere.**
