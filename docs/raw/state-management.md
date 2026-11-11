# AdharaSutra — State Management Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/state-management.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Runtime Infrastructure Architecture  
**Architecture Style:** Scoped State, Explicit Ownership, Port-Based Persistence  
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
- `docs/design/connector-framework.md`

---

# 1. Purpose

This document defines the proposed state-management architecture of AdharaSutra.

The state subsystem provides consistent mechanisms for storing, accessing, updating, observing, persisting, restoring, and cleaning up application and framework state.

The framework owns the state-management infrastructure.

Consuming applications own their domain state definitions, business invariants, and state transition policies.

The design must support:

1. One-shot CLI execution.
2. Persistent CLI sessions.
3. Concurrent action execution.
4. Long-running jobs.
5. Application-specific state models.
6. Framework runtime state.
7. Persistent state storage.
8. State subscriptions and notifications.
9. Controlled state restoration.
10. Electron frontend synchronization.
11. State lifecycle and cleanup.
12. Architecture verification.
13. Incremental migration of existing applications.

## 1.1 Central Principle

**State must have explicit ownership, scope, lifetime, and consistency guarantees.**

The framework must never imply that state survives process termination unless it is stored using an explicitly configured persistent mechanism.

## 1.2 Design Goals

The state subsystem shall:

- Reduce duplicated state infrastructure across applications.
- Support multiple state scopes.
- Provide predictable concurrent access.
- Separate business state from technical runtime state.
- Allow optional persistence.
- Support state-change notifications.
- Integrate with application lifecycle and jobs.
- Remain independent of Electron.
- Avoid requiring SQLite for applications that do not need persistence.
- Support test doubles and deterministic verification.

## 1.3 Non-Goals

The state subsystem is not intended to:

- Implement application business rules.
- Replace domain entities and aggregates.
- Become a universal database abstraction.
- Automatically persist all application variables.
- Synchronize every Electron UI variable with Python.
- Provide distributed consensus.
- Guarantee state durability without a persistent backend.
- Implement event sourcing by default.
- Provide a distributed cache.
- Guarantee atomic transactions across unrelated external systems.

---

# 2. State Architecture Principles

## SM-001 — Explicit State Scope

Every managed state definition shall declare its scope.

## SM-002 — Explicit State Ownership

Every state instance shall have a defined owner responsible for its lifetime.

## SM-003 — Business Logic Independence

AdharaSutra shall manage state infrastructure without implementing application business transitions.

## SM-004 — Persistence Is Explicit

In-memory state shall not automatically be treated as durable.

## SM-005 — Concurrency Safety

Concurrent state operations shall follow documented consistency rules.

## SM-006 — Controlled Mutation

State updates shall use supported APIs that enforce applicable validation, versioning, and concurrency policies.

## SM-007 — State Isolation

Unrelated applications, sessions, requests, and jobs shall not unintentionally share private state.

## SM-008 — Observable Changes

State changes may produce structured notifications through the framework event subsystem.

## SM-009 — Framework Independence from Electron

The state-management engine shall not import Electron-specific interfaces.

## SM-010 — Optional Persistence

Applications shall be able to use volatile state without installing or initializing SQLite.

## SM-011 — Port-Based Storage

Persistent state shall depend on storage contracts rather than directly coupling the state engine to SQLite.

## SM-012 — Lifecycle Integration

State creation, restoration, expiration, and cleanup shall follow application and execution lifecycle rules.

## SM-013 — Deterministic Verification

State configuration and supported ownership rules shall be verifiable wherever technically feasible.

## SM-014 — No Hidden Global State

The framework shall discourage uncontrolled mutable module-level state for application business data.

## SM-015 — Truthful Durability

The framework shall report actual persistence and recovery guarantees rather than treating successful in-memory mutation as durable storage.

---

# 3. State Classification

AdharaSutra distinguishes state by purpose and lifetime.

## 3.1 Framework State

Framework state describes technical runtime behavior.

Examples:

- Runtime lifecycle.
- Connector initialization status.
- Connector health.
- Active request metadata.
- Job lifecycle.
- Session metadata.
- Runtime diagnostic counters.

The framework owns these values and their technical transitions.

## 3.2 Application State

Application state represents business or application-level information.

Examples:

- Selected voice profile.
- Active workspace.
- Selected inference model.
- Project configuration.
- User preferences.
- Current processing options.
- Application-specific task metadata.

The application owns the meaning and validity of these values.

## 3.3 Derived State

Derived state is calculated from other state or authoritative data.

Examples:

- Whether a processing action is available.
- Number of active jobs.
- Aggregate processing progress.
- Whether required services are ready.

Derived state should not be persisted independently unless justified by performance or recovery requirements.

## 3.4 UI-Only State

Presentation-only state may remain inside Electron.

Examples:

- Hover state.
- Open or closed panels.
- Temporary selection.
- Scroll position.
- Unsaved visual layout controls.

AdharaSutra should not require backend synchronization for purely presentational state.

---

# 4. State Scopes

The framework defines five primary state scopes.

| Scope | Owner | Lifetime | Default durability |
|---|---|---|---|
| Request | Request execution context | One request | Volatile |
| Session | Persistent CLI session | Session lifetime | Volatile |
| Process | Python application runtime | Process lifetime | Volatile |
| Job | Job execution owner | Job lifecycle and retention | Volatile |
| Persistent | Application storage context | Across process restarts | Durable when committed |

These scopes describe ownership and lifetime.

They are not interchangeable storage backends.

---

# 5. High-Level State Architecture

```text
┌─────────────────────────────────────────────────────┐
│                  ADHARASUTRA RUNTIME                │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │             STATE REGISTRY                    │  │
│  │                                               │  │
│  │  State Definitions                            │  │
│  │  Schemas                                      │  │
│  │  Scope Rules                                  │  │
│  │  Ownership                                    │  │
│  │  Validation                                   │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                           │
│                         ▼                           │
│  ┌───────────────────────────────────────────────┐  │
│  │              STATE MANAGER                    │  │
│  │                                               │  │
│  │  Read / Update / Compare-and-Set              │  │
│  │  Isolation / Concurrency                      │  │
│  │  Versioning / Notifications                   │  │
│  └──────────────┬────────────────┬───────────────┘  │
│                 │                │                  │
│                 ▼                ▼                  │
│  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ VOLATILE STORES  │  │ PERSISTENT STATE PORT   │  │
│  │                  │  │                         │  │
│  │ Request          │  │ Load                    │  │
│  │ Session          │  │ Save                    │  │
│  │ Process          │  │ Delete                  │  │
│  │ Job              │  │ Transactions            │  │
│  └──────────────────┘  └────────────┬────────────┘  │
│                                    │                │
│                                    ▼                │
│                         ┌─────────────────────┐     │
│                         │ Storage Adapter     │     │
│                         │ SQLite / Other      │     │
│                         └─────────────────────┘     │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │             EVENT ADAPTER                     │  │
│  │  State Changes → Authorized Subscribers      │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

The diagram describes logical responsibilities.

It does not require every state operation to invoke every component.

---

# 6. Proposed Module Structure

```text
src/adharasutra/state/
│
├── __init__.py
├── contracts.py
├── definitions.py
├── registry.py
├── manager.py
├── scopes.py
├── ownership.py
├── validation.py
├── versioning.py
├── errors.py
│
├── stores/
│   ├── base.py
│   ├── memory.py
│   └── persistent.py
│
├── concurrency/
│   ├── locks.py
│   ├── compare_and_set.py
│   └── transactions.py
│
├── subscriptions/
│   ├── publisher.py
│   ├── subscriber.py
│   └── filtering.py
│
├── persistence/
│   ├── ports.py
│   ├── serializer.py
│   ├── restoration.py
│   └── migrations.py
│
└── lifecycle/
    ├── initialization.py
    ├── cleanup.py
    └── expiration.py
```

This is the proposed logical organization.

Implementation may consolidate files where a smaller structure is easier to maintain.

## 6.1 Dependency Direction

The state engine may depend on:

- Core contracts.
- Approved validation interfaces.
- Lifecycle abstractions.
- Event publication interfaces.
- Persistence ports.

The core state engine must not depend directly on:

- Electron.
- SQLite implementation details.
- HTTPX.
- External CLI implementations.
- Application domain modules.
- Architecture verification tooling.
- Migration tooling.

Concrete persistence adapters are registered through the application composition root.

---

# 7. State Definitions and Registry

## 7.1 Purpose

The State Registry stores the definitions of managed state.

It does not necessarily contain every state value.

## 7.2 State Definition Metadata

A state definition should identify:

- State key.
- Owner category.
- Scope.
- Value schema.
- Initial value or initializer.
- Mutability policy.
- Persistence configuration.
- Notification policy.
- Concurrency policy.
- Retention or expiration policy.
- Access restrictions.

## 7.3 Example Definition

Conceptual configuration:

```yaml
state:
  active_workspace:
    scope: process
    type: string
    nullable: true
    notify: true

  user_preferences:
    scope: persistent
    schema: UserPreferences
    storage: application_db

  request_context:
    scope: request
    schema: RequestContext
```

This is illustrative, not a finalized schema.

## 7.4 Registration Rules

The registry shall:

1. Validate state identifiers.
2. Detect duplicate definitions.
3. Validate supported scopes.
4. Validate schemas.
5. Validate persistence configuration.
6. Detect incompatible ownership settings.
7. Reject invalid combinations.

## 7.5 Namespace Rules

Applications should use namespaced state identifiers.

Examples:

```text
application.workspace.active
application.voice.selected
application.preferences
framework.runtime.status
framework.connector.comfyui.health
framework.jobs.active_count
```

Framework-owned namespaces must be protected from unrestricted application mutation.

## 7.6 Registration Lifecycle

State definitions should normally be registered during application composition.

Unexpected runtime registration must require an explicitly supported dynamic registration mechanism.

---

# 8. Request-Scoped State

## 8.1 Purpose

Request-scoped state contains information associated with one action execution.

Examples:

- Request correlation metadata.
- Request-specific temporary values.
- Execution deadlines.
- Request-specific validation context.
- Cancellation metadata.

## 8.2 Ownership

The framework execution context owns request-scoped state.

## 8.3 Lifetime

Request-scoped state is created when the request begins and released when the request execution context reaches its terminal state.

## 8.4 Isolation

Concurrent requests must not unintentionally share mutable request state.

## 8.5 Persistence

Request-scoped state is volatile by default.

If information must survive after request completion, it must be explicitly transferred to an appropriate longer-lived scope.

## 8.6 Constraints

Request state must not be stored in unrestricted module globals.

It must not be assumed available after the execution context is disposed.

---

# 9. Session-Scoped State

## 9.1 Purpose

Session state is associated with an active persistent CLI session.

Examples:

- Session preferences.
- Session-specific temporary configuration.
- Active workspace selection for one session.
- Session-level subscriptions.
- Session metadata.

## 9.2 Ownership

The persistent CLI session owns its state scope.

## 9.3 Lifetime

Session state is created after successful session initialization and removed when the session ends.

## 9.4 Session Isolation

Separate sessions must not share session-private state unless an explicit shared application state mechanism is used.

## 9.5 Session Termination

Session state is invalidated when:

- The session closes.
- The owning Python process terminates.
- A fatal communication failure ends the session.
- An explicit session shutdown occurs.

## 9.6 Reconnection

A new session must not automatically inherit the previous session's volatile state.

Restoration requires explicitly persisted information and documented application behavior.

## 9.7 Electron Considerations

An Electron renderer reload is not necessarily the end of the Python CLI session.

The bridge's session lifecycle is owned by Electron main and the Python runtime, not by individual renderer components.

---

# 10. Process-Scoped State

## 10.1 Purpose

Process state exists for the lifetime of one AdharaSutra application runtime.

Examples:

- Runtime readiness.
- Shared application configuration snapshot.
- Active connector metadata.
- Application-scoped caches.
- Shared application settings.
- Runtime counters.

## 10.2 Ownership

The AdharaSutra application runtime owns process-scoped state.

## 10.3 Lifetime

Process state is initialized during application startup and released during shutdown.

## 10.4 Concurrency

Multiple requests and jobs may access process state.

Therefore, mutations must use supported concurrency controls.

## 10.5 Process Restart

Process state does not survive Python process termination.

The state may be reconstructed from:

- Configuration.
- Registered initializers.
- Persistent storage.
- External services.

Restoration is not guaranteed unless explicitly designed.

## 10.6 Application Isolation

Independent Python application processes must not accidentally share process-scoped state.

---

# 11. Job-Scoped State

## 11.1 Purpose

Job state represents information associated with a managed execution.

Examples:

- Job status.
- Progress.
- Execution stage.
- Cancellation status.
- Result metadata.
- Error metadata.
- Temporary execution resources.

## 11.2 Ownership

The job manager owns framework job metadata.

The application owns business-specific job data and transition rules.

## 11.3 Lifetime

Job-scoped state may remain available for a configured retention period after execution completes.

## 11.4 Retention

Retention policies may determine:

- How long terminal job metadata remains available.
- Whether completed results are persisted.
- When temporary artifacts are cleaned up.
- When job-specific subscriptions are released.

## 11.5 Job State and Persistent State

Persisting job metadata does not guarantee continued execution.

A job requires an active execution owner to run.

The state subsystem must preserve the distinction between:

- Persisted job information.
- Current execution ownership.
- Actual execution status.

## 11.6 Integration

The job subsystem should use state contracts rather than directly manipulating state store internals.

The detailed job lifecycle will be defined in `job-management.md`.

---

# 12. Persistent State

## 12.1 Purpose

Persistent state survives process termination and may be restored by a later application runtime.

Examples:

- User preferences.
- Saved application settings.
- Workspace metadata.
- Recoverable job metadata.
- Application-level selections requiring persistence.

## 12.2 Persistence Requirement

Persistent state must be associated with a configured durable storage adapter.

## 12.3 Storage Port

The state module shall define a storage interface independent of SQLite.

Conceptual interface:

```python
from typing import Protocol


class StatePersistencePort(Protocol):
    async def load(
        self,
        key: str,
    ):
        ...

    async def save(
        self,
        key: str,
        value,
    ) -> None:
        ...

    async def delete(
        self,
        key: str,
    ) -> None:
        ...
```

This example illustrates responsibilities, not a finalized API.

The production contract must also define scope identity, revisions, serialization, transaction semantics, and error behavior.

## 12.4 SQLite Adapter

SQLite is the proposed default local persistent-state adapter when persistence is enabled.

The adapter shall use AdharaSutra's SQLite connector facilities.

## 12.5 Application Domain Persistence

The generic state subsystem must not replace domain repositories.

For example:

- Saving a selected voice profile identifier may use persistent state.
- Saving complete voice-profile entities should normally use the application's domain repository.

## 12.6 Durable Acknowledgment

A successful persistent-state write must correspond to the configured storage adapter's documented commit guarantee.

The framework must not acknowledge durable persistence before the required commit operation succeeds.

## 12.7 Corruption and Recovery

The persistence adapter must provide classified failures for:

- Storage unavailable.
- Invalid stored data.
- Schema incompatibility.
- Transaction failure.
- Integrity failure.
- Version conflict.

Recovery behavior must be explicit.

---

# 13. State Access API

## 13.1 Purpose

Applications shall access managed state through documented interfaces.

## 13.2 Conceptual API

```python
state = context.state

await state.set(
    "application.workspace.active",
    "workspace-001",
)

workspace = await state.get(
    "application.workspace.active"
)
```

This is illustrative.

The final API must enforce scope and authorization rules.

## 13.3 Typed State Access

The framework should support typed state definitions and validation.

State reads should return values consistent with their registered schema.

## 13.4 Mutation API

The framework should support:

- Read.
- Set.
- Delete.
- Compare-and-set.
- Controlled update operations.

## 13.5 Missing Values

The API must distinguish:

- An unregistered state key.
- A registered key without a current value.
- A valid stored null value.
- A failed state read.

These conditions must not be silently conflated.

## 13.6 Access Restrictions

Applications must not freely modify framework-owned state.

The state manager shall enforce the declared state ownership policy.

---

# 14. State Concurrency Architecture

## 14.1 Problem

Persistent CLI execution supports multiple active requests and jobs.

Multiple operations may read and update the same state.

Without concurrency controls, updates may be lost or state may become inconsistent.

## 14.2 Required Guarantees

The framework shall define:

- Atomic operations.
- Concurrent read behavior.
- Concurrent update behavior.
- Conflict detection.
- Versioning.
- Lock ownership.
- Persistence commit ordering.

## 14.3 Atomic Set

A single state update must appear atomic within its supported scope.

## 14.4 Compare-and-Set

The framework should support conditional updates.

Conceptual example:

```python
await state.compare_and_set(
    key="application.counter",
    expected_version=4,
    value=10,
)
```

The update succeeds only if the expected version matches the current version.

## 14.5 State Revision

Managed mutable state should support monotonically increasing revisions within its relevant ownership scope.

Revisions assist with:

- Conflict detection.
- Change subscriptions.
- Electron synchronization.
- Diagnostic tracing.

Revisions are not globally unique transaction identifiers.

## 14.6 Immutable Snapshots

State read operations should avoid exposing mutable internal references that bypass the state manager.

A returned value should be immutable, copied, or otherwise protected according to the value type and store policy.

## 14.7 Locking

The framework may use appropriate synchronization mechanisms.

The implementation must avoid holding locks across arbitrary long-running business operations.

## 14.8 Cross-Process Concurrency

In-memory concurrency controls do not coordinate separate Python processes.

Persistent adapters must provide the required cross-process guarantees, such as transactional conflict handling.

## 14.9 Deadlocks

The state subsystem must define lock-ordering or other strategies that avoid common deadlocks.

---

# 15. State Transactions

## 15.1 Purpose

Some operations require multiple related state mutations.

## 15.2 Transaction Scope

The framework may support atomic multi-key updates within one compatible state backend.

## 15.3 Conceptual API

```python
async with state.transaction() as tx:
    await tx.set("application.a", 1)
    await tx.set("application.b", 2)
```

This is illustrative and must not be assumed supported by every store.

## 15.4 Transaction Limitations

The framework must not promise atomic transactions across:

- Independent in-memory stores.
- Separate SQLite databases without explicit support.
- HTTP services.
- External CLI tools.
- Filesystem operations.

## 15.5 Failure Handling

If an atomic transaction fails, the backend must follow its documented rollback behavior.

## 15.6 State and Domain Transactions

Domain repositories may need their own transaction boundaries.

The framework must avoid introducing ambiguous nested transactions between generic state storage and domain repositories.

## 15.7 Proposed Initial Scope

Support atomic individual operations and compare-and-set first.

Support multi-key transactions only for backends where the implementation can guarantee the documented behavior.

---

# 16. State Validation

## 16.1 Schema-Based Validation

Managed state values shall be validated against their registered schemas.

## 16.2 Validation Timing

Validation should occur:

- At registration.
- During initialization.
- Before mutation.
- During persistent restoration.

## 16.3 Business Validation

The framework verifies structural state validity.

The application verifies domain invariants.

For example, the framework may validate that a selected model identifier is a string.

The application determines whether that model is available or permitted.

## 16.4 Invalid State

Invalid state must not be silently accepted.

The framework shall return a classified validation failure.

## 16.5 Schema Evolution

Persistent state may require schema versioning and migration.

Applications own migration logic for business-specific state models.

---

# 17. State Change Notifications

## 17.1 Purpose

Applications and framework services may subscribe to state changes.

## 17.2 Notification Data

A state-change notification should include:

- State identifier.
- Scope.
- Scope owner identifier.
- Revision.
- Change category.
- Correlation metadata.
- Optional current value.
- Timestamp.

## 17.3 Example

```json
{
  "event": "state.changed",
  "data": {
    "key": "application.workspace.active",
    "scope": "process",
    "revision": 7,
    "value": "workspace-002"
  }
}
```

The complete CLI event envelope is defined by the CLI protocol.

This example represents the application event payload.

## 17.4 Notification Ordering

For a single state key and store owner, successful committed mutations should produce notifications in revision order.

Global ordering across unrelated state keys is not guaranteed.

## 17.5 Subscription API

Conceptual interface:

```python
unsubscribe = state.subscribe(
    "application.workspace.active",
    on_workspace_changed,
)
```

## 17.6 Subscription Ownership

Every subscription must have a defined owner.

Possible owners:

- Application.
- Session.
- Request.
- Job.
- Component.

## 17.7 Subscription Cleanup

Subscriptions must be released when their owner terminates.

## 17.8 Slow Subscribers

The event subsystem must provide bounded buffering or controlled delivery policies.

Slow subscribers must not indefinitely block critical state mutations.

## 17.9 Delivery Guarantee

The initial state notification mechanism provides best-effort delivery.

Durable replay is not guaranteed unless explicitly supported by a persistent event mechanism.

## 17.10 Sensitive State

Sensitive state values must not automatically be published through Electron-facing events.

Only explicitly exposed state definitions may be forwarded.

---

# 18. Electron State Synchronization

## 18.1 Separation of Responsibilities

Electron owns presentation state.

Python owns authoritative backend state where required.

## 18.2 Synchronization Model

```text
Electron Renderer
       │
       │ Application Action
       ▼
AdharaSutra CLI
       │
       ▼
Application Use Case
       │
       ▼
State Manager
       │
       ▼
State Mutation
       │
       ▼
State Change Event
       │
       ▼
Electron Bridge
       │
       ▼
Authorized Renderer
```

## 18.3 Initial State

A renderer may need a current state snapshot when it starts or reloads.

The application should expose approved state-query actions or a controlled state snapshot facility.

## 18.4 Subscription Race

A renderer must not assume that fetching a state snapshot followed by subscribing to events is automatically race-free.

The design must define a synchronization approach.

**Proposed approach:**

1. Establish the subscription or event cursor.
2. Obtain a state snapshot with a revision.
3. Apply later events in revision order.
4. Detect gaps and refresh when necessary.

The exact mechanism depends on event subscription and replay capabilities.

## 18.5 Renderer Reload

A renderer reload must not automatically destroy process-scoped Python state.

Renderer-specific subscriptions must be cleaned up.

## 18.6 Multiple Windows

State exposed to multiple renderer windows must follow the application's access policy.

Application-private or window-specific state must not leak to unauthorized windows.

## 18.7 Lost Events

When event loss is detected or suspected, the renderer should query the authoritative Python state again.

## 18.8 UI Optimistic Updates

Electron may use optimistic UI updates.

However, Python remains authoritative for backend business state.

Rejected mutations must be reconciled.

---

# 19. Persistent State Restoration

## 19.1 Restoration Lifecycle

```text
Application Startup
        │
        ▼
Load Configuration
        │
        ▼
Initialize Persistence Adapter
        │
        ▼
Validate Stored State Schema
        │
        ▼
Migrate Compatible State
        │
        ▼
Restore Required Values
        │
        ▼
Initialize Dependent Services
        │
        ▼
Application READY
```

The exact ordering depends on declared service dependencies.

## 19.2 Restoration Policies

State definitions may specify:

- Required restoration.
- Optional restoration.
- Initialize default when missing.
- Reject incompatible stored values.
- Apply supported migration.

## 19.3 Restoration Failure

If required persistent state cannot be restored, the application must not silently report full readiness.

Optional state may be reset according to an explicitly configured policy.

## 19.4 Schema Versioning

Persistent state formats must be versioned when changes can affect restoration compatibility.

## 19.5 Migration Ownership

The application owns business-specific state migration logic.

The framework owns the storage and migration execution infrastructure.

## 19.6 Backup

State migrations that may affect important persistent data should support an appropriate backup and recovery procedure.

---

# 20. State Lifecycle and Cleanup

## 20.1 Lifecycle Events

State may be created or removed during:

- Application startup.
- Session creation.
- Request start.
- Job submission.
- Job completion.
- Session closure.
- Application shutdown.

## 20.2 Cleanup Responsibilities

The owner of a state scope determines when cleanup is required.

## 20.3 Expiration

State definitions may support expiration policies.

Possible expiration mechanisms:

- Explicit deletion.
- Owner termination.
- Time-to-live.
- Retention limits.
- Application-defined cleanup.

## 20.4 Persistent State Expiration

Persistent state expiration must not be confused with automatic deletion of domain records.

Business data retention policies remain application-owned.

## 20.5 Shutdown

Shutdown shall release volatile state and close persistence adapters.

Persistent state must not be deleted merely because the runtime stops.

## 20.6 Partial Failure

If initialization fails, state created during startup must be cleaned up where appropriate.

---

# 21. State Error Architecture

## 21.1 Proposed Error Categories

```text
STATE_NOT_REGISTERED
STATE_INVALID_SCOPE
STATE_VALIDATION_FAILED
STATE_ACCESS_DENIED
STATE_VERSION_CONFLICT
STATE_NOT_FOUND
STATE_STORE_UNAVAILABLE
STATE_PERSISTENCE_FAILED
STATE_RESTORATION_FAILED
STATE_TRANSACTION_FAILED
STATE_SCOPE_CLOSED
```

The final error identifiers must be reconciled with the framework-wide error catalog.

## 21.2 Error Information

State errors should provide:

- Stable error code.
- Safe message.
- State identifier where appropriate.
- Scope.
- Correlation metadata.
- Conflict revision where safe.
- Internal diagnostic cause.

## 21.3 Sensitive Values

Errors must not expose sensitive state values by default.

## 21.4 Persistence Failures

Persistence errors must distinguish definite failure from uncertain outcome where applicable.

## 21.5 Conflict Handling

Version conflicts should be explicit.

The framework must not silently overwrite newer state during compare-and-set operations.

---

# 22. State Performance and Resource Management

## 22.1 Performance Goals

Volatile state operations should be lightweight.

The framework must avoid unnecessary serialization or persistence for ordinary in-memory reads.

## 22.2 Memory Limits

Large state values may create memory pressure.

The framework should support:

- Value-size policies.
- Retention limits.
- Controlled caches.
- Explicit cleanup.

## 22.3 Large Artifacts

Large binary data must not be stored directly in general-purpose state by default.

Store managed artifact references instead.

## 22.4 Notification Performance

Notifications should avoid blocking critical state operations on slow subscribers.

## 22.5 Persistence Performance

Persistent state writes may be slower than volatile writes.

The framework must not imply equal performance characteristics.

## 22.6 Write Coalescing

Some application preferences may permit debounced or batched persistence.

Such behavior must be explicitly configured because it changes durability guarantees.

## 22.7 Benchmarking

Benchmarks should measure:

- Volatile reads.
- Volatile writes.
- Compare-and-set.
- Concurrent updates.
- State subscriptions.
- Persistent writes.
- Restoration.
- Cleanup.

Final thresholds will be derived from the non-functional requirements and representative workloads.

---

# 23. Security and Access Control

## 23.1 State Ownership Enforcement

Only authorized application or framework components may mutate protected state.

## 23.2 Framework State Protection

Framework lifecycle and job state must not be freely writable by arbitrary application actions.

## 23.3 Renderer Exposure

State must be explicitly approved for Electron-facing access.

## 23.4 Sensitive State

The state engine should support marking values as sensitive.

Sensitive values must not be automatically included in:

- Logs.
- Diagnostics.
- Events.
- Architecture reports.
- Error responses.

## 23.5 Storage Security

Persistent storage must follow application directory and filesystem permission policies.

## 23.6 State Isolation

Application, session, request, and job identifiers must be validated before resolving state access.

## 23.7 Untrusted Input

State mutations originating from Electron must pass action-level authorization and application business validation.

---

# 24. State Testing Strategy

## 24.1 Unit Tests

Verify:

- Registration.
- State definitions.
- Scope validation.
- Default initialization.
- Reads and writes.
- Deletion.
- Versioning.
- Compare-and-set.
- Access restrictions.

## 24.2 Concurrency Tests

Verify:

- Concurrent reads.
- Concurrent writes.
- Lost-update prevention.
- Version conflicts.
- Lock behavior.
- Independent state scopes.

## 24.3 Persistence Tests

Verify:

- Save and load.
- Durable commit.
- Delete.
- Restart restoration.
- Schema compatibility.
- Migration failures.
- Storage unavailability.
- Transaction rollback.

## 24.4 Subscription Tests

Verify:

- Notification publication.
- Ordering.
- Subscription filtering.
- Unsubscription.
- Owner cleanup.
- Slow subscribers.
- Sensitive-value filtering.

## 24.5 Lifecycle Tests

Verify:

- Application startup.
- Request completion.
- Session closure.
- Job termination.
- Application shutdown.
- Partial initialization failure.

## 24.6 Electron Integration Tests

Verify:

- State snapshots.
- Events.
- Renderer reload.
- Multiple windows.
- Missed-event recovery.
- Authorization.
- Stale revision handling.

## 24.7 Failure Injection

Simulate:

- Process crash.
- Storage corruption.
- Concurrent conflicts.
- Invalid state schema.
- Interrupted persistence writes.
- Slow event subscribers.
- Persistence adapter failure.

---

# 25. Architecture Verification Rules

The architecture verifier should enforce relevant state conventions.

| Rule ID | Rule |
|---|---|
| SM-VER-001 | Managed state definitions declare a valid scope |
| SM-VER-002 | State identifiers follow namespace rules |
| SM-VER-003 | Framework-owned state cannot be registered as application-owned |
| SM-VER-004 | Domain modules do not depend on concrete state store implementations |
| SM-VER-005 | Persistent state declares a storage adapter |
| SM-VER-006 | State subsystem does not directly depend on SQLite implementation |
| SM-VER-007 | State mutation uses approved interfaces where required |
| SM-VER-008 | Session state has defined cleanup ownership |
| SM-VER-009 | Job state ownership is declared |
| SM-VER-010 | Sensitive state is not exposed through unrestricted event mappings |
| SM-VER-011 | Persistent state schemas have applicable compatibility metadata |
| SM-VER-012 | State configuration satisfies registered schemas |
| SM-VER-013 | State-dependent services have valid initialization dependencies |
| SM-VER-014 | State persistence failures have appropriate tests |
| SM-VER-015 | Unmanaged mutable global state patterns are reported where detectable |
| SM-VER-016 | State architecture exceptions are documented |

Static analysis cannot fully prove concurrency correctness, event delivery, or cleanup behavior.

Those require executable tests.

---

# 26. Existing Application State Migration

## 26.1 Purpose

Existing applications may store state through:

- Module globals.
- Singleton objects.
- Custom dictionaries.
- Electron-side caches.
- SQLite tables.
- JSON files.
- Custom state managers.

AdharaSutra must support incremental migration.

## 26.2 Discovery

The migration engine should identify:

- State definitions.
- State mutations.
- State readers.
- State lifetime assumptions.
- Persistence mechanisms.
- Concurrency behavior.
- Electron synchronization.
- Cleanup behavior.

## 26.3 Migration Steps

```text
Existing State Implementation
          │
          ▼
Discover State Ownership
          │
          ▼
Classify State Scope
          │
          ▼
Record Existing Behavior
          │
          ▼
Define AdharaSutra State Schema
          │
          ▼
Introduce Compatibility Adapter
          │
          ▼
Migrate State Access
          │
          ▼
Verify Behavior and Persistence
          │
          ▼
Remove Obsolete Infrastructure
```

## 26.4 Migration Safety

Migration must preserve:

- Business state semantics.
- Stored data.
- Valid state transitions.
- Required persistence behavior.
- Relevant event notifications.
- Existing application compatibility.

## 26.5 Data Migration

Persistent state schema changes must have an explicit migration and recovery strategy.

## 26.6 Temporary Compatibility

Legacy state managers may be wrapped during incremental migration.

The framework must identify transitional architecture exceptions.

## 26.7 Migration Verification

Architecture compliance alone is insufficient.

Relevant behavioral and persistence regression tests must pass.

---

# 27. Representative Application Scenarios

## Scenario SM-S01 — Request Isolation

**Given** two concurrent application requests,

**When** each updates request-scoped state,

**Then** each request shall observe its own state without unintended interference.

## Scenario SM-S02 — Session Termination

**Given** an active persistent CLI session,

**When** the session closes,

**Then** session-scoped state shall be invalidated.

**And** process-scoped state shall remain available if the Python runtime continues.

## Scenario SM-S03 — Process Restart

**Given** process-scoped state exists,

**When** the Python process terminates and restarts,

**Then** the framework shall not assume the previous in-memory state remains available.

## Scenario SM-S04 — Persistent Preferences

**Given** application preferences are configured as persistent,

**When** the application commits new preferences and restarts,

**Then** the committed values shall be restored through the configured persistence adapter.

## Scenario SM-S05 — Concurrent Mutation

**Given** two requests read the same state revision,

**When** both attempt conditional updates,

**Then** only updates satisfying the required revision condition shall succeed.

**And** conflicting updates shall receive an explicit conflict outcome.

## Scenario SM-S06 — State Subscription

**Given** a subscriber observes a state key,

**When** a successful state mutation occurs,

**Then** the subscriber shall receive the applicable state-change notification according to the delivery policy.

## Scenario SM-S07 — Renderer Reload

**Given** Electron reloads a renderer while Python remains active,

**When** the new renderer initializes,

**Then** it shall be able to obtain an authoritative state snapshot.

**And** it shall not assume old renderer subscriptions remain valid.

## Scenario SM-S08 — Job Metadata

**Given** a job is running,

**When** its progress changes,

**Then** the job subsystem shall update the relevant state.

**And** publish progress through the supported event mechanism.

## Scenario SM-S09 — Storage Failure

**Given** a persistent-state adapter becomes unavailable,

**When** a required durable update is attempted,

**Then** the framework shall report a persistence failure.

**And** it shall not report a successful durable commit unless the configured guarantee has been satisfied.

## Scenario SM-S10 — Sensitive State

**Given** a state definition is marked sensitive,

**When** state events or diagnostics are generated,

**Then** the sensitive value shall not be exposed to unauthorized consumers.

## Scenario SM-S11 — One-Shot Application

**Given** a one-shot CLI application,

**When** the process executes and exits,

**Then** request- and process-scoped state shall not be assumed available to a later invocation.

## Scenario SM-S12 — State Migration

**Given** an existing application uses a custom state manager,

**When** the application adopts AdharaSutra state facilities,

**Then** its required state behavior shall remain verifiable.

**And** its persistence behavior shall remain compatible with the approved migration plan.

---

# 28. State Architecture Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| SM-D01 | State ownership | Explicit scope and owner |
| SM-D02 | State categories | Framework and application |
| SM-D03 | State scopes | Request, session, process, job, persistent |
| SM-D04 | Volatile storage | In-memory store |
| SM-D05 | Persistent storage | Port-based adapters |
| SM-D06 | Default persistent adapter | SQLite when enabled |
| SM-D07 | State updates | Validated controlled mutations |
| SM-D08 | Concurrency | Atomic operations and version checks |
| SM-D09 | Multi-key transactions | Backend-specific capability |
| SM-D10 | State notifications | Framework event integration |
| SM-D11 | Notification durability | Best-effort initially |
| SM-D12 | Electron synchronization | Snapshot plus revision-aware events |
| SM-D13 | State schema | Typed and validated |
| SM-D14 | State restoration | Explicit policies |
| SM-D15 | Large data | Artifact references rather than state blobs |
| SM-D16 | Sensitive state | Explicit access and exposure controls |
| SM-D17 | Domain persistence | Separate from generic state |
| SM-D18 | State module dependency | No direct SQLite implementation dependency |
| SM-D19 | State lifecycle | Owner-based cleanup |
| SM-D20 | Existing migration | Incremental with compatibility adapters |

All decisions remain proposed until reviewed and validated.

---

# 29. Outstanding Questions

## SM-OQ-001 — Default State API

Should the public interface use string keys, typed descriptors, or both?

**Recommendation:** Prefer typed state descriptors while permitting controlled string-key access at integration boundaries.

## SM-OQ-002 — State Schema Technology

Should state schemas use dataclasses, Pydantic, JSON Schema, or a combination?

**Recommendation:** Define a lightweight validation interface and avoid binding domain models to one framework-specific implementation.

## SM-OQ-003 — Synchronous and Asynchronous Access

Should volatile state use synchronous APIs while persistence uses asynchronous APIs?

**Recommendation:** Separate capabilities clearly rather than forcing every in-memory operation to incur asynchronous overhead.

## SM-OQ-004 — State Transaction Model

Should the framework support atomic updates across multiple keys?

**Recommendation:** Support single-key atomic operations initially and add multi-key transactions where a backend provides reliable guarantees.

## SM-OQ-005 — State Event Replay

Should state notifications support historical replay?

**Recommendation:** Defer durable replay. Provide authoritative snapshot retrieval and revision-based reconciliation.

## SM-OQ-006 — State Persistence Defaults

Should application preferences be persisted automatically?

**Recommendation:** No. Persistence must be explicitly declared by the application.

## SM-OQ-007 — State Sharing Across Processes

Should independent Python runtimes share persistent state through SQLite?

**Recommendation:** Support explicitly configured shared persistence but not implicit shared in-memory state.

## SM-OQ-008 — State Retention

Should terminal job state and abandoned session metadata have default expiration policies?

**Recommendation:** Define bounded defaults with application-specific overrides.

## SM-OQ-009 — Sensitive State Storage

Should the state subsystem provide encryption at rest?

**Recommendation:** Evaluate as an optional capability after establishing the threat model and credential storage requirements.

## SM-OQ-010 — Domain Events Versus State Events

Should domain events pass through the same event infrastructure?

**Recommendation:** Allow common event transport while keeping domain event semantics application-owned.

## SM-OQ-011 — State Synchronization Guarantees

Should the framework provide a dedicated subscribe-and-snapshot operation to avoid synchronization gaps?

**Recommendation:** Consider an atomic registration-and-snapshot API or equivalent revision-aware mechanism before finalizing Electron synchronization.

## SM-OQ-012 — Persistence Schema Migration

Should persistent-state schema migrations share infrastructure with application database migrations?

**Recommendation:** Reuse generic migration facilities while keeping state schema ownership distinct from domain schema ownership.

---

# 30. Functional Requirement Traceability

| Requirement group | State architecture responsibility |
|---|---|
| FR-STATE | State scopes, registry, stores, subscriptions |
| FR-RUN | State initialization and lifecycle |
| FR-JOB | Job-scoped state |
| FR-ELC | Electron state events and snapshots |
| FR-DB | Persistent state storage |
| FR-CFG | State configuration |
| FR-DI | State dependency composition |
| FR-ERR | State error classification |
| FR-LOG | State diagnostics |
| FR-SEC | State authorization and redaction |
| FR-TEST | State testing |
| FR-ARCH | State architecture verification |
| FR-MIG | Existing state migration |

---

# 31. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-PERF | Lightweight volatile operations |
| NFR-RES | Scoped ownership and bounded retention |
| NFR-REL | Validated mutations and explicit errors |
| NFR-AVAIL | Persistent restoration and recovery |
| NFR-SCALE | Concurrency control |
| NFR-SEC | Access restrictions and sensitive-state handling |
| NFR-MAINT | Separation of state mechanisms and business rules |
| NFR-EXT | Replaceable persistence adapters |
| NFR-TEST | Mockable stores and fault-injection tests |
| NFR-COMP | Versioned persistent schemas |
| NFR-ARCH | Enforceable state ownership rules |
| NFR-MIG | Incremental migration |
| NFR-OBS | Revision and correlation metadata |

---

# 32. State Management Acceptance Criteria

The architecture may be approved when:

- [ ] Framework and application state ownership are distinguished.
- [ ] Request, session, process, job, and persistent scopes are defined.
- [ ] State registration and schema validation are defined.
- [ ] State lifetime and cleanup rules are explicit.
- [ ] State APIs support controlled mutation.
- [ ] Missing, null, and invalid values are distinguishable.
- [ ] Concurrent mutation semantics are defined.
- [ ] Compare-and-set or equivalent conflict handling is specified.
- [ ] Multi-key transaction limitations are documented.
- [ ] Persistent storage uses an abstraction independent of SQLite.
- [ ] Durable-write acknowledgment semantics are defined.
- [ ] Restoration policies are defined.
- [ ] Schema evolution and migration responsibilities are clear.
- [ ] Subscription ownership and cleanup are defined.
- [ ] Event ordering and delivery limitations are documented.
- [ ] Sensitive state is protected from unauthorized exposure.
- [ ] Electron state synchronization has a gap-recovery strategy.
- [ ] Renderer reload and multiple-window behavior are addressed.
- [ ] One-shot and persistent CLI behavior are consistent with state lifetimes.
- [ ] Job metadata persistence is not confused with durable execution.
- [ ] Testing and architecture verification requirements are defined.
- [ ] Existing application migration is feasible.
- [ ] Major open decisions are approved or explicitly deferred.

---

# 33. Final Architecture Summary

AdharaSutra provides scoped state-management infrastructure for Python applications.

The framework manages:

- State definitions.
- State registration.
- State stores.
- Access and mutation.
- Scope ownership.
- Concurrency.
- State revisions.
- Change notifications.
- Optional persistence.
- Restoration.
- Lifecycle cleanup.
- Technical errors.

Consuming applications own:

- Business state models.
- Domain invariants.
- Business state transitions.
- Application-specific persistence semantics.
- Business data retention.
- State exposure policies.

State is divided into request, session, process, job, and persistent scopes.

Volatile state belongs to its execution owner and does not survive that owner's termination.

Persistent state requires an explicitly configured storage adapter.

SQLite is a proposed local persistence option, but it must not become mandatory for applications using only volatile state.

State-change events can be exposed through AdharaSutra's event infrastructure without coupling the state engine directly to Electron.

The architecture must support safe concurrent operations, accurate lifecycle semantics, controlled restoration, and incremental adoption by existing applications.

The central guarantee is:

**Every state value has a defined owner, scope, lifetime, and consistency policy.**

---

# 34. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending state-management architecture review

**Next Document:** `docs/design/job-management.md`

The next document should define job execution, scheduling, worker ownership, concurrency, progress reporting, cancellation, timeouts, durable job metadata, recovery, result handling, and process lifecycle integration.

---

**AdharaSutra — Build once. Standardize everywhere.**
