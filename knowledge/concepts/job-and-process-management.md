---
type: Concept
title: Job and process management
description: Durable knowledge on jobs, processes, executors, lifecycle, cancellation and recovery.
status: draft
tags: [jobs, processes, execution, lifecycle]
---

# Jobs versus processes

Current/proposed boundary (2026-11-13): the implemented manager uses queued,
running, succeeded, failed, cancelled, and interrupted states. Persistence is
metadata-only and does not replay jobs. The extended definition/executor/policy
model below is draft context, not the implemented API. `system.jobs.get`, cancellation,
terminal persistence diagnostics, and the reserved cleanup budget are implemented;
async HTTP remains conditional work in the [architecture integrity change](../../openspec/changes/architecture-integrity-review/proposal.md).
Results are JSON-validated and waiters are released after the terminal save attempt.
A failed terminal save leaves the local outcome visible but may leave an older durable
snapshot; recovery never replays it. See [ADR-001](../decisions/001-cooperative-execution.md) and
[ADR-003](../decisions/003-runtime-ownership.md); both remain proposed.

A job is a managed unit of work with a lifecycle, cancellation policy and result; a process is an operating-system execution resource. A job may run without a subprocess, a subprocess may exist without a job record, and one job may run several processes sequentially. The proposed rule: every running operation has a defined execution owner and every managed subprocess a lifecycle owner — job records do not imply running, persisted metadata does not imply survival, cancellation acknowledgments do not prove termination, and process exits do not prove business success.

# Framework-owned infrastructure

AdharaSutra owns the execution infrastructure; applications define the work. The Job Manager owns registration, admission, scheduling, lifecycle state, progress, cancellation coordination, results, recovery and metadata; the Process Connector owns executable resolution, spawning, arguments, streams, exit monitoring, timeout, termination and process-tree cleanup; application adapters own tool-specific arguments, output interpretation, domain progress mapping and result validation. The Job Manager must not reimplement subprocess handling, and application domains must not manage subprocess lifecycles directly.

# Job definitions, identifiers and submission

A job definition declares a namespaced type identifier (`audio.generate`), input and result schemas, execution strategy, concurrency, timeout, cancellation, persistence, recovery and retention policies; applications own type names and business meaning. Every execution receives a unique `job_id` — not an authorization token — with attempt identity and executor owner tracked separately. Submission validates definition and input, checks admission, queues or starts work and returns an acknowledgment; an accepted ID is returned only once the job is registered with its intended execution owner. Admission may reject on invalid input, missing dependencies, unavailable executors, concurrency or queue limits, shutdown or unsupported policy. Queues are bounded with explicit overflow; submissions are distinct executions, exactly-once business execution is not guaranteed, and deduplication requires explicit idempotency policy.

# Job lifecycle

The implemented public states are `queued`, `running`, `succeeded`, `failed`, `cancelled` and `interrupted` (stopped or ownership lost without confirmed success); the following ideas about additional internal states and attempt policies remain proposed. Invalid transitions should be rejected: completed jobs cannot rerun without a new attempt, failed jobs cannot be marked completed without verified execution, and cancelled attempts must not publish progress. Retries create explicitly tracked new attempts rather than rewriting terminal history.

# Execution strategies and ownership

- Async task — nonblocking I/O; owned by the active Python runtime; does not survive runtime termination; blocking code stays off the event loop.
- Managed thread — blocking Python functions; cooperative cancellation only, since threads cannot be safely force-terminated; bounded pools and weaker isolation than a process.
- Managed external process — external CLI tools via the Process Connector; not durable by default.
- Durable worker — deferred extension for independently owned recoverable work (claiming, heartbeats, safe retry); not advertised until a tested durable owner exists.

# Progress and events

The following lifecycle-event and attempt metadata are proposals, not currently emitted framework events. Progress may carry job and attempt IDs, stage, percentage or unit counts, message, timestamp and metadata; unknown completion is reported as indeterminate, and progress must not be emitted after an attempt's confirmed terminal event. Lifecycle events (`job.started`, `job.progress`, `job.completed`, `job.failed`, `job.cancelled`, `job.interrupted`) flow through the framework event subsystem, never by handlers writing JSON to protocol stdout; clients recover from best-effort delivery via implemented `system.jobs.get`; listing and authorization are application-owned.

# Cancellation and timeouts

Cancellation coordinates caller, Job Manager, executor, underlying task or process, and optional external service; acknowledgment means the request was accepted, while `cancelled` requires executor-confirmed termination. Processes get graceful termination with configurable escalation; remote services need service-specific adapters, since cancelling a local HTTP request does not cancel remote work. Cancellation races must not overwrite confirmed terminal outcomes. Timeouts (queue wait, execution, executor startup, process, cancellation grace, shutdown) each have a defined owner; job deadlines propagate downstream, and timeouts never automatically retry non-idempotent work.

# Process termination and orphan recovery

A process record tracks identity, owner, exit status and termination reason; the OS PID alone is not durable identity since PIDs are reused. Processes must not detach implicitly when their parent request completes. Streams are drained, decoded explicitly and captured within bounds — never forwarded to protocol stdout, since subprocess output is untrusted; shell execution is disabled by default and renderer-supplied executable paths are not blindly trusted. After a crash, recovery distinguishes recorded from actual status: reassociate a confirmed live worker, retry when explicitly safe, or mark interrupted when the outcome is unknown; orphan reclamation requires ownership evidence, not PID matching. Proposed policies: `none`, `mark_interrupted`, `retry_if_safe`, `manual`, `resume`; interrupted coroutines cannot resume without a checkpointing contract.

# Concurrency and resource limits

The proposed scheduler is in-process with bounded queues and configurable concurrency — FIFO baseline with optional priority and per-job-type limits, starvation avoidance and backpressure: exhausted capacity queues within limits or rejects explicitly, never accepting unlimited jobs into an unbounded memory queue. Limits apply at application-wide, per-type and per-resource-class scopes; resource classifications (CPU, I/O, memory, external-process, GPU) drive admission without promising OS-level isolation. Cleanup runs on completion, failure, cancellation, timeout, shutdown or invalid owner; business and cleanup outcomes may differ.

# Alternatives considered

Explicitly out of scope initially: distributed queues or scheduling, Kubernetes or cloud orchestration, GPU allocation, distributed consensus, exactly-once execution, durable workers for every application, automatic recovery of arbitrary interrupted Python functions, direct Electron management of Python worker subprocesses, and a general-purpose workflow orchestration platform. Existing applications adopt incrementally, moving subprocess calls to the Process Connector before removing duplicated infrastructure.

# Open questions

- JPM-OQ-001 — Whether applications register jobs via decorators, typed descriptors, or both.
- JPM-OQ-002 — Whether the initial release needs a dedicated worker-process executor for CPU-heavy pure-Python tasks.
- JPM-OQ-003 — Whether priority scheduling belongs in the initial implementation or FIFO with per-type limits suffices.
- JPM-OQ-004 — Whether the Job Manager should support dependency graphs and chained jobs.
- JPM-OQ-005 — Whether retry policies belong to the Job Manager or application handlers.
- JPM-OQ-006 — Whether full job inputs belong in SQLite or only recoverable metadata and references.
- JPM-OQ-007 — What retention policy applies to completed job history.
- JPM-OQ-008 — What graceful and forced termination periods to use, pending cross-platform testing.
- JPM-OQ-009 — Whether the framework should attempt to reattach to external processes after a crash.
- JPM-OQ-010 — Whether durable workers are a separate Python executable or service.
- JPM-OQ-011 — `system.jobs.get` is implemented; listing remains application-owned. See the [protocol reference](../../docs/protocol-reference.md).
- JPM-OQ-012 — Whether job events carry monotonically increasing per-job sequence numbers.
- JPM-OQ-013 — Whether the framework automatically removes artifacts when job metadata expires.
- JPM-OQ-014 — Whether jobs can declare GPU resource requirements.
- JPM-OQ-015 — Whether AdharaSutra provides universal cancellation for external HTTP-based services.

See [job requirements](../../docs/requirements/functional-job-management-requirements.md),
[state requirements](../../docs/requirements/functional-state-management-requirements.md),
and the [state and jobs concept](state-and-jobs.md).
