# Preserve sequential controls and compatible cooperative jobs

Status: proposed. Date: 2026-11-13. Decision ID: ADR-001.

## Context

The runtime dispatches persistent requests sequentially and runs background jobs
on the same event loop. Sync callable jobs are accepted today; HTTP is synchronous.
The product needs responsive desktop controls without an unproven concurrency
rewrite. Immediate sync-job rejection would break the public callable contract.

## Decision

Retain sequential short controls and recommend background jobs for long work.
Preserve sync job registration with a warning describing inline execution limits;
do not set an unsupported removal date. Add managed async HTTP for that workflow.
Business actions own submission; the framework adds get/status beside cancel.
Caller timeout means outcome unknown and never implies automatic replay.

## Alternatives

- Concurrent request dispatch: requires reentrancy and shared-state decisions not
  justified by the first integration yet.
- Automatically thread all handlers: violates thread ownership assumptions for
  SQLite, context state, and protocol writers; threads cannot be force-cancelled.
- Reject sync jobs now: conflicts with the currently documented callable API.

## Consequences

Async bodies still must yield; the framework cannot prove they do. CPU-heavy Python
execution needs a later executor or external process. Applications must reconcile
lost submission acknowledgments. General execution/retry/durability is not promised.

## References

[Review A03/A05/A06/A15](../../docs/architecture-review-2026-11-13.md),
[OpenSpec target](../../openspec/changes/architecture-integrity-review/design.md),
[existing decisions](../../docs/decisions.md).
