---
type: Concept
title: CLI protocol
description: Proposed communication model between callers and the Python runtime.
status: draft
tags: [cli, protocol, electron]
---

# Communication boundary

Callers and the Python runtime communicate over process streams: stdin carries requests and control
messages, stdout carries framed protocol messages, and stderr carries diagnostics, never
authoritative results. Framing is NDJSON, one UTF-8 JSON object per line, so readers must buffer
partial reads and expect several messages per read. A 1 MiB message limit is proposed; oversized
messages are rejected without unbounded buffering. Large artifacts travel as managed descriptors.

# Proposed message model

Every message carries `kind` and `protocol_version` (draft `1.0`). Proposed kinds:

- `request` — invoke a registered application or framework action
- `response` — report the outcome of a request
- `event` — report progress or occurrences without terminating a request
- `control` — protocol-level session control

# Request lifecycle and correlation

A request carries `request_id`, `action` and an application-defined `payload`; IDs are unique among
active requests, and actions are namespaced with `system.*` and `protocol.*` reserved to the
framework. Each accepted request should produce one terminal response — on success `error` is
null; on failure `data` is null and `error` is structured. A background-job response only
acknowledges the job: it needs an identifiable owner and must not appear durably executing after
that owner exits. Concurrent requests may complete in any order, so correlation, not arrival order,
is authoritative; request state is isolated, concurrency is bounded by configurable limits, and
handlers must declare concurrency constraints. Event delivery is best-effort; exactly-once
execution is not guaranteed — retries need application idempotency.

# Events and control semantics

Events carry `event`, `data`, and `request_id` when tied to an active request; for independent jobs
`job_id` is the durable correlation. Standard events cover application and job lifecycle, connector
readiness and namespaced application events; progress may be indeterminate (`percent: null`), and
a terminal event is never followed by new progress. Cancellation is the reserved `system.cancel`
action: its response only acknowledges the request — the outcome arrives later as `job.cancelled`
or a cancellation error, never overwriting a confirmed terminal result. Shutdown is the reserved
`system.shutdown` action under ordinary authorization boundaries.

# Sessions and versioning

One-shot and persistent modes share the same schemas: one-shot accepts a single stdin request and
returns one terminal response, validating its version at dispatch; persistent sessions — the
proposed Electron default — begin with a `system.hello` handshake exchanging supported versions, a
`session_id` and capabilities, and are ready only after the handshake and initialization succeed;
incompatible versions are rejected outright. Versions use `MAJOR.MINOR`, independent of package
versions: majors may break compatibility, minors add backward-compatible capabilities that must
not be assumed until established. Unknown optional fields may be ignored where the schema permits;
missing required fields, unknown kinds and capabilities are rejected.

# Errors and exit codes

The error object carries `code`, `message`, `retryable` (boolean or null, null meaning unknown)
and optional `details`. Proposed categories: protocol, action routing, runtime, connector, job,
cancellation and persistence codes, plus namespaced application codes. Proposed exit codes: 0
normal, 2 invalid invocation, 3 initialization failure, 4 action failure, 5 timeout, 6
cancellation, 7 dependency unavailable, 8 protocol failure, 10 internal failure. In persistent
mode an action failure must not force a nonzero exit, and after an unexpected Python exit the
bridge must report a transport failure, never fabricated success.

# Security constraints

The protocol runs between a local Electron main process and a Python child, with no network
listener, yet a compromised renderer or malicious application code must not be trusted. Only
registered, permitted actions may execute; unknown identifiers never become commands, and renderer
strings must not become executable paths or shell commands. Payloads are validated before
execution; errors and logs must not leak credentials, tokens or stack traces.

# Alternatives considered

Proposed directions: stdin/stdout NDJSON transport, a `kind` discriminator, `request_id`/`job_id`
correlation, reserved framework actions for handshake, cancellation and shutdown, one-shot and
persistent modes, separate job-completion events and managed artifact references. Deferred: durable
event replay, exactly-once guarantees, binary streaming and shared Python/TypeScript schemas.

# Open questions

- CP-OQ-001 — Should readiness be signaled before the handshake, or only by it?
- CP-OQ-002 — Should requests carry an optional execution deadline in the envelope?
- CP-OQ-003 — Should job events carry sequence numbers for gap and duplicate detection?
- CP-OQ-004 — Should the protocol support an optional idempotency key?
- CP-OQ-005 — Should capability discovery include registered action schemas?
- CP-OQ-006 — Should the Electron bridge restart a failed Python runtime automatically?
- CP-OQ-007 — Is 1 MiB the appropriate default maximum message size?
- CP-OQ-008 — How should TypeScript and Python share authoritative schema definitions?
- CP-OQ-009 — How should legacy commands map to the unified protocol during migration?
- CP-OQ-010 — Should durable job events support historical replay?

See [CLI requirements](../../docs/requirements/functional-cli-framework-requirements.md),
[Electron requirements](../../docs/requirements/functional-electron-communication-requirements.md),
and the [draft OpenSpec change](../../openspec/changes/foundational-runtime/proposal.md).
