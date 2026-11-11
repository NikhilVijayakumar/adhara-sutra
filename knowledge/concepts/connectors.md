---
type: Concept
title: Connector framework
description: Integration boundaries and resource ownership for external systems.
status: draft
tags: [connectors, architecture]
---

Connectors are the proposed shared infrastructure for HTTP, WebSocket, external CLI, SQLite and filesystem access.
AdharaSutra standardizes how external dependencies are reached; applications define what they are used for — endpoint
mapping, argument semantics, domain SQL, retry safety. Changing external transport must not change the
Electron-facing CLI contract. HTTP, external CLI, SQLite and filesystem are P0; WebSocket and custom connectors are
P1. Capabilities are declared explicitly; no universal `execute()` is imposed.

# Shared connector contract

An application-scoped registry validates identifiers and configuration, resolves dependencies, rejects duplicates
(explicit override is test-only) and resolves lookups by stable identifier; a missing connector is a documented
framework error, and applications never share connector instances or configuration. Lifecycle runs REGISTERED →
INITIALIZING → READY → DEGRADED or FAILED → CLOSING → CLOSED; initialization is distinct from acquiring external
resources — an HTTP client may be READY while ComfyUI is offline. Eager, lazy or conditional initialization is
declared; startup follows dependency order, shutdown the reverse. A required startup failure blocks readiness and
triggers structured cleanup; optional failures may continue degraded; every connector and resource has one
lifecycle owner.

Configuration is validated before initialization; credentials arrive only through protected facilities, never
committed config. Health checking is optional — absence does not imply unhealthy — and readiness is reported
separately from remote dependency health (healthy, degraded, unavailable, unknown, not checked). Infrastructure
exceptions map to stable technical categories (CONNECTOR_NOT_FOUND, CONNECTOR_TIMEOUT, CONNECTOR_CANCELLED, and
peers; names proposed) carrying safe message, correlation ID and retryability; adapters may re-map them into
domain errors inside the standard error envelope. Unused connectors never load their optional dependencies.

# Connector-specific contracts

- HTTP (HTTPX proposed): pooled reusable clients with base URL, authentication, streaming bodies and timeouts; transport errors stay distinct from non-success statuses; adapters interpret endpoint responses.
- External CLI: argument sequences with shell execution disabled by default; streamed, drained stdout/stderr; raw exit status; timeout, cancellation and process-tree cleanup with platform-specific termination isolated.
- SQLite: no unsafe cross-thread connection sharing; explicit commit, rollback and nesting transaction semantics; configurable busy timeout and optional WAL; backups via a consistent SQLite mechanism, never raw copies.
- WebSocket: connector owns transport, applications interpret messages; bounded buffering for backpressure; reconnection never replays messages or actions without explicit policy; session scope declared explicitly.
- Filesystem: path validation against configured access boundaries (traversal, symbolic links, resolved targets, race-aware where security-sensitive); explicit temporary-resource ownership; streamed large files; artifact descriptors
  grant the Electron renderer no unrestricted filesystem capability.

# Timeouts, retries and cancellation

Timeouts sit at distinct layers — Electron bridge, framework action deadline, connector timeouts, SQLite busy
timeout, job deadline — and propagate downward; a connector timeout must not silently exceed the remaining
operation deadline, and a timeout never proves the external operation had no effect. The framework never
automatically retries potentially non-idempotent operations (HTTP POSTs, file-modifying CLI commands, database
writes) without an explicitly declared safe policy. Cancellation is capability-specific — HTTP cancels the local
request, WebSocket stops receiving, CLI terminates the process, SQLite interrupts or rolls back — and local
cancellation does not cancel an already-accepted remote operation; remote cancellation is the adapter's
responsibility.

# Testing, custom connectors and migration

Connector dependencies must be replaceable with fakes or mocks; adapters test against doubles (controlled
executables rather than audio.cpp), live services separate and optional. Applications and optional packages may
register custom connectors, following the same ownership conventions; use cases depend on application-defined
ports, not registry lookups. Service-specific adapters are application-owned or optional plugins, never a
competing framework runtime; existing applications migrate incrementally behind temporary compatibility wrappers.

# Failure handling and security

One optional connector failing must not impair unrelated healthy connectors; resource exhaustion is reported,
with bounded queues and independent per-connector concurrency limits. Connectors default to conservative
security, timeout, retry and resource settings; secrets, tokens and sensitive request data never surface in
frontend-facing errors or logs, and configuration must not contain embedded secrets.

# Alternatives considered

- Capability-oriented connectors over a universal `execute()` API — SQLite is not forced into an HTTP-like interface.
- Explicit, safety-aware retry and replay-free reconnection over automatic retries; on-demand health over periodic defaults.
- No distributed atomic transactions across SQLite, files and HTTP — applications coordinate compensating operations instead.
- Generic core with separately distributed adapters; ordinary subprocess execution before persistent interactive sessions.
- Incremental migration with temporary compatibility wrappers over immediate replacement.

# Open questions

- CF-OQ-001 — Typed connector descriptors, declarative configuration, or both? (Recommended: typed registration with configuration-file integration.)
- CF-OQ-002 — Should all connectors default to lazy initialization? (Recommended: lazy for optional connectors, eager for required.)
- CF-OQ-003 — SQLite synchronous, asynchronous through an adapter, or both? (Recommended: decide from representative workloads; never fake nonblocking.)
- CF-OQ-004 — Should common HTTP requests retry automatically? (Recommended: conservative defaults; explicit eligibility for side-effecting retries.)
- CF-OQ-005 — Should health checks run periodically by default? (Recommended: on-demand first, optional scheduled later.)
- CF-OQ-006 — Persistent interactive subprocesses in the initial release? (Recommended: no — ordinary subprocess execution first.)
- CF-OQ-007 — Filesystem as a connector or a separate framework service? (Recommended: infrastructure capability; revisit connector-lifecycle value.)
- CF-OQ-008 — Service-specific integrations in the framework or separate? (Recommended: generic core; distribute adapters when reuse justifies.)
- CF-OQ-009 — Live connector reconfiguration? (Recommended: defer until lifecycle and concurrency semantics are validated.)
- CF-OQ-010 — Artifacts inside filesystem services or a dedicated module? (Recommended: lightweight first; split out if complexity grows.)
- CF-OQ-011 — A higher-level unit-of-work above the SQLite connector? (Recommended: evaluate repository needs; no premature ORM-like abstraction.)
- CF-OQ-012 — Cross-connector transactions over SQLite, files and HTTP? (Recommended: no distributed atomicity; compensating operations instead.)

See [connector framework requirements](../../docs/requirements/functional-connector-framework-requirements.md), [HTTP](../../docs/requirements/functional-http-connector-requirements.md),
[external CLI](../../docs/requirements/functional-external-cli-connector-requirements.md), [WebSocket](../../docs/requirements/functional-websocket-connector-requirements.md),
[filesystem](../../docs/requirements/functional-filesystem-requirements.md), and [SQLite](../../docs/requirements/functional-sqlite-and-persistence-requirements.md) requirements.
