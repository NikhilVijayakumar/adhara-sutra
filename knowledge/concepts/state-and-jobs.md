---
type: Concept
title: State, jobs and execution ownership
description: Scope, persistence, job lifecycle, and recovery boundaries.
status: draft
tags: [state, jobs, lifecycle]
---

# State model and ownership

The framework owns state infrastructure — registry, stores, access controls, concurrency, notifications, optional persistence, restoration and cleanup — while applications own business state models, domain invariants, transition policies and retention rules. Every state value has a defined owner, scope, lifetime and consistency policy; nothing is durable unless stored through an explicitly configured persistent mechanism. Framework, application, derived (calculated, not independently persisted) and UI-only (kept in Electron, never synchronized) state are classified, and mutable module-level globals are discouraged for business data.

# State scopes and lifetimes

Scopes describe ownership and lifetime, not interchangeable storage backends:

- Request: owned by the request execution context; created at request start, released at terminal state. Volatile and isolated between concurrent requests; surviving values move explicitly to a longer-lived scope.
- Session: owned by the persistent CLI session; invalidated on close, process termination, communication failure or explicit shutdown. New sessions inherit no volatile state; a renderer reload is not necessarily the session's end.
- Process: owned by the application runtime; initialized at startup, released at shutdown, shared by concurrent requests and jobs. Survives session closure but not process termination; reconstruction is not guaranteed unless designed, and processes must not accidentally share it.
- Job: framework job metadata is owned by the job manager, business data and transitions by the application; may be retained after completion per policy.
- Persistent: survives process restarts through a configured durable storage adapter; durable only when committed.

# Definitions, registry and access

Each managed state definition declares its key, owner, scope, value schema, initializer, mutability, persistence, notification, concurrency, retention and access policy, under namespaced identifiers (`application.*`, `framework.*`) with framework namespaces protected from application mutation; registration happens at composition. Access uses documented interfaces — conceptually `context.state` get/set/delete/compare-and-set — distinguishing an unregistered key, a key without a current value, a stored null and a failed read. The state manager enforces declared ownership with classified errors; validation at registration, initialization, mutation and restoration checks structure in the framework and domain invariants in the application — invalid state is never silently accepted.

# Change notifications and subscriptions

State changes may publish structured notifications through the framework event subsystem — key, scope, revision, change category, optional value — in revision order per key and store owner, with no global ordering across unrelated keys. Subscriptions have an owner (application, session, request, job or component) released at owner termination; bounded buffering keeps slow subscribers from blocking mutations. Delivery is best-effort initially; sensitive values reach Electron only through explicitly exposed definitions. Electron owns presentation state while Python stays authoritative; proposed synchronization is a snapshot plus revision-aware events — subscribe, snapshot with a revision, apply later events in order, detect gaps and refresh — because snapshot-then-subscribe is not race-free. Renderer reload must not destroy process state; lost events trigger re-querying Python; optimistic UI updates must reconcile rejections.

# Concurrency and transactions

A single update appears atomic within its scope; compare-and-set succeeds only when the expected revision matches, and version conflicts are explicit — the framework never silently overwrites newer state. Mutable state carries monotonically increasing revisions within its ownership scope for conflict detection, subscriptions and diagnostics. Reads return immutable or copied values; locks are never held across long-running business operations, and lock ordering avoids deadlocks. In-memory controls do not coordinate separate processes — cross-process guarantees come from persistent adapters. Multi-key transactions are backend-specific within one compatible store; atomicity is never promised across independent stores, HTTP services, external CLI tools or the filesystem.

# Persistence and the SQLite question

Persistence is explicit: applications can use volatile state without installing or initializing SQLite. Persistent state depends on a storage port — conceptually load, save and delete plus scope identity, revisions, serialization and transaction semantics — never a direct engine-to-SQLite coupling. SQLite is the proposed default local adapter when persistence is enabled, built on AdharaSutra's SQLite connector facilities; a durable write is acknowledged only after the adapter's documented commit succeeds, and persistence failures are classified, distinguishing definite failure from uncertain outcome. Generic state must not replace domain repositories — a selected voice-profile identifier may be persistent state while complete entities belong in a domain repository. Large binaries are stored as artifact references; debounced or batched writes must be explicitly configured because they change durability guarantees.

# Restoration and cleanup

Restoration initializes the persistence adapter, validates stored schemas, migrates compatible state and restores required values before dependent services start; policies choose required, optional, default-when-missing, reject-incompatible or migrate, and failed restoration of required state must not silently report full readiness. Cleanup follows the scope owner across startup, session and request boundaries, job completion and shutdown; expiration uses explicit deletion, owner termination, time-to-live or retention limits — never implying deletion of domain records. Shutdown releases volatile state and closes adapters without deleting persistent state.

# Alternatives considered

- Automatic persistence of all application variables — rejected; persistence is explicitly declared per definition.
- Mandatory SQLite — rejected; persistence is optional behind a storage port, with SQLite only the proposed default.
- A universal database abstraction replacing domain entities and repositories — rejected.
- Event sourcing and durable replay by default — rejected; best-effort notifications plus revision-based reconciliation.
- Synchronizing every Electron UI variable with Python — rejected; UI-only state stays in Electron.

# Jobs

Applications define job behavior. The framework provides identifiable job
records, execution, progress, results, supported cancellation, and timeouts.
The current states are queued, running, succeeded, failed, cancelled and
interrupted. An accepted job is not a completed job. Each active execution has
an owner: persisted metadata alone does not mean a job survives its owning
process. Recovery must distinguish interruption from actual durable execution.

# Open questions

- SM-OQ-001 — String keys, typed descriptors, or both in the public state API? (Recommended: typed descriptors, controlled string keys at integration boundaries.)
- SM-OQ-002 — Dataclasses, Pydantic, JSON Schema, or a combination for state schemas? (Recommended: lightweight validation interface, no binding to one framework.)
- SM-OQ-003 — Synchronous volatile access alongside asynchronous persistence? (Recommended: separate capabilities, not async overhead everywhere.)
- SM-OQ-004 — Atomic updates across multiple keys? (Recommended: single-key atomic operations first; multi-key only with reliable backend guarantees.)
- SM-OQ-005 — Historical replay of state notifications? (Recommended: defer durable replay; authoritative snapshots plus revision-based reconciliation.)
- SM-OQ-006 — Persist application preferences automatically? (Recommended: no — persistence must be explicitly declared.)
- SM-OQ-007 — Independent Python runtimes sharing persistent state through SQLite? (Recommended: explicitly configured shared persistence only, never implicit in-memory sharing.)
- SM-OQ-008 — Default expiration for terminal job state and abandoned session metadata? (Recommended: bounded defaults with application overrides.)
- SM-OQ-009 — Encryption at rest for sensitive state? (Recommended: evaluate after the threat model and credential storage requirements.)
- SM-OQ-010 — Domain events through the same event infrastructure? (Recommended: common transport, application-owned semantics.)
- SM-OQ-011 — A dedicated subscribe-and-snapshot operation to avoid synchronization gaps? (Recommended: consider an atomic registration-and-snapshot or revision-aware mechanism.)
- SM-OQ-012 — Shared migration infrastructure for persistent-state and application database schemas? (Recommended: reuse facilities, keep schema ownership distinct.)

See [state requirements](../../docs/requirements/functional-state-management-requirements.md), [job requirements](../../docs/requirements/functional-job-management-requirements.md), and [SQLite requirements](../../docs/requirements/functional-sqlite-and-persistence-requirements.md).
