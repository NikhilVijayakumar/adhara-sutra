---
type: Concept
title: CLI protocol
description: Proposed communication model between callers and the Python runtime.
status: draft
tags: [cli, protocol, electron]
---

# Communication boundary

Electron and other callers communicate with the Python runtime over process
streams. Application actions remain independent of the caller and of whether
their work uses HTTP, a subprocess, SQLite, or another connector. The proposed
transport uses UTF-8 JSON messages framed as NDJSON: one JSON object per line,
with stdin for requests, stdout for protocol messages, and stderr for diagnostics.
Readers must handle partial reads and multiple messages in one read.

# Proposed message model

Each message has `kind` and `protocol_version`. Proposed kinds are `request`,
`response`, `event`, and `control`. A request carries `request_id`, `action`,
and an object payload. Its ID is unique among active requests in a session.
Reserved framework namespaces are proposed as `system.*` and `protocol.*`.

A response carries the matching request ID, `success`, `data`, and `error`.
On success, `error` is null; on failure, `data` is null and `error` is a
structured object containing a code, message and retryability, with optional
details. Sensitive values and internal stack traces are not exposed by default.
An accepted request should receive one terminal response while the session is
functional. A response accepting a background job is an acknowledgement, not
evidence that the job completed; execution must have an identifiable owner.

# Sessions and compatibility

One-shot and persistent execution share action semantics. The proposed persistent
session negotiates a compatible protocol version before actions run; one-shot
requests validate the version before dispatch. Protocol versions are independent
of framework and Electron package versions. Major versions can break compatibility;
minor versions may add backward-compatible capabilities, which must not be assumed
available without establishing support.

The draft proposes a 1 MiB message limit, configurable lower limits, and managed
artifact references for large data. Oversized input must not cause unbounded
buffering or execution. This size is a proposed value, not an approved threshold.

# Open questions

- Whether readiness is announced separately or established by handshake.
- Request deadlines, event sequence numbers and optional idempotency keys.
- Discovery of action schemas and distribution of shared Python/TypeScript schemas.
- Restart policy, replay safety and durable event delivery.
- The default message-size limit and legacy command compatibility.

See [CLI requirements](../../docs/requirements/functional-cli-framework-requirements.md),
[Electron requirements](../../docs/requirements/functional-electron-communication-requirements.md),
and the [draft OpenSpec change](../../openspec/changes/foundational-runtime/proposal.md).
