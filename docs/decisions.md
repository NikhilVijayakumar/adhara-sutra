# Architecture Decisions

Resolutions for the open questions in the requirements drafts. Each decision is
implemented by the referenced specification and code; a resolved question is a
decision, not an implementation task.

The independent [architecture review](architecture-review-2026-11-13.md) proposes
refinements tracked in [OpenSpec](../openspec/changes/architecture-integrity-review/tasks.md).
Numbered [proposed ADRs](../knowledge/decisions/index.md) describe the rationale
for those corrections and remain proposed. The [task evidence](../openspec/changes/architecture-integrity-review/evidence.md)
records implemented changes and remaining failures; neither historical decisions
nor proposed ADRs alone establish full release qualification.

## NFR-OQ-001 — Python Runtime Packaging

**Decision:** support both a bundled Python interpreter and a frozen backend.
The Python helper `nikhi.adhara_sutra.runtime.locate_backend` can locate bundled
interpreters once Python is already running; a frozen executable can be supplied
as the bridge command directly. Node-owned pre-start discovery is not implemented
and is tracked as T18. Discovery and layouts are documented in [packaging.md](packaging.md).

## NFR-OQ-002 — Persistent Process Model

**Decision:** one persistent Python process per application is the default
Electron integration. The bridge spawns one backend, negotiates `system.hello`
once, and serves requests sequentially over the persistent CLI protocol.
One-shot execution remains available for scripts and CI through `adhara run`.
Sequential processing keeps action reentrancy and shared-state coordination out
of the transport contract; concurrent request dispatch remains deferred. Short
actions may submit managed async background jobs and return an application-owned ID.

## NFR-OQ-003 — Job Execution Isolation

**Decision:** jobs execute in the runtime process, owned by `JobManager`, with
bounded concurrency and queueing. Durable execution is never claimed: an
optional persistent store keeps job metadata, and recovery marks non-terminal
jobs `interrupted` instead of re-running them. An invalid explicitly configured
store fails startup. Shutdown closes admission and reserves at least half its
cooperative budget for service cleanup. Terminal save failures leave the local
outcome inspectable with failed persistence metadata, but do not guarantee recovery
of that outcome. Executing jobs under a separate durable worker is out of scope.

## NFR-OQ-004 — State Persistence

**Decision:** SQLite remains an explicitly configured optional facility. The
framework creates no implicit global state database; applications choose and
register the persistent store they need. Scoped in-memory state is the default.

## NFR-OQ-005 — Connector Reliability

**Decision:** no automatic retries by default. Connectors report
`retryable` in structured errors and honor explicit timeouts; a caller that
needs retry or backoff implements it with full knowledge of the operation's
side effects. Connectors may expose a health check, and `system.health`
aggregates availability without mutating dependencies.

## NFR-OQ-006 — Architecture Verification Scope

**Decision:** profile version 1 enforces structural, dependency, layer,
framework, and entry-point checks as errors; integration, state, and job
adoption checks are warnings. `adhara verify` reports both; `--strict` makes a
`needs_review` status fail regardless of severity, rather than failing every warning. Profiles are versioned and replaceable,
so an application can tighten or relax the catalog deliberately.

## NFR-OQ-009 — Release Compatibility

**Decision:** releases follow Semantic Versioning. The CLI protocol carries a
version independent of the application version, and the bridge rejects peers
that do not advertise a supported protocol version. Public API and protocol
versions remain supported for the current major release; deprecations are
announced one minor release before removal, with upgrade guidance in the
release notes and [packaging.md](packaging.md). Report schema versions are
independent and accept additive fields.

## NFR-OQ-010 — Framework Packaging

**Decision:** AdharaSutra ships as one Python distribution
(`nikhi-adhara-sutra`) with optional extras (`http`, `websocket`). Connectors
that require third-party packages stay optional and are not imported at
startup unless configured. Splitting into independently versioned packages is
deferred until an independent release cadence is actually needed.
