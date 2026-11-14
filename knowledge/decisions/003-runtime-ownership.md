# Preserve explicit ownership through admission and shutdown failure

Status: proposed. Date: 2026-11-13. Decision ID: ADR-003.

## Context

The framework owns resource lifetimes and job execution. A configured store can
silently resolve to none, rejected admission can retain a record without a task,
and job shutdown failure can skip service cleanup. Those paths undermine ownership
even before production reliability qualification.

## Decision

Reject invalid requested persistence. Give admission rollback semantics for local
records/tasks, with conservative durable recovery when saves cannot be reversed.
Validate terminal DTOs and expose local persistence failure separately from actual
execution outcome. Preserve session mapping identity. Close admission on shutdown
and reserve at least half the existing cooperative overall budget for service cleanup.
Electron main owns locating its first backend command before spawning Python.

## Alternatives

- Silently disable persistence: violates explicit configuration intent.
- Treat any local return as durable success: hides serialization/save failure.
- Skip resources after a job error: discards lifecycle ownership.
- Double shutdown_timeout for a second phase: changes existing caller expectations.
- Locate the first Python only through Python: circular desktop bootstrap.

## Consequences

Failing configuration becomes visible sooner. Asyncio cannot enforce a hard
deadline on blocking or cancellation-resistant code. Resource cleanup can race
misbehaving jobs after their cooperative budget; this is a degraded failure path,
not proof that the work stopped. A crash can still lose unsaved terminal outcomes.
Independent platform/process-tree testing remains integration-dependent.

## References

[Review](../../docs/architecture-review-2026-11-13.md),
[OpenSpec ownership requirements](../../openspec/changes/architecture-integrity-review/specs/runtime-ownership/spec.md),
[bootstrap requirements](../../openspec/changes/architecture-integrity-review/specs/integration-bootstrap/spec.md).
