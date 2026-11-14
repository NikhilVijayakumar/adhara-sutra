# Design: foundational runtime

## Context

This remains a draft specification, but substantial runtime, connector, bridge,
and governance code exists at c320dcf. Proposed status is not the same as absent
implementation. The [current behavior map](../../../knowledge/architecture.md)
and [recorded decisions](../../../docs/decisions.md) identify implemented choices.
The [architecture integrity review](../architecture-integrity-review/proposal.md)
tracks corrections and must be reconciled before this draft is accepted/archived.

## Boundaries

Applications register business handlers through framework extension points;
the framework must not import application-specific business logic. Runtime
initialization validates configuration before starting dependent resources and
cleans up resources if initialization fails. CLI transport validates requests
before dispatch and separates protocol output from diagnostics.

## Earlier decision checklist and current disposition

- Lifecycle transitions exist in Application; T07 closes admission and attempts cleanup after job shutdown failure within a cooperative budget.
- The protocol reference documents status/cancel actions, detached job event ordering, and bridge timeout outcomes.
- Requests are sequential, jobs are concurrent/cooperative, and synchronous job registration warns while preserving compatibility.
- One Python distribution and a separate Node package are recorded choices; import-boundary and Node-bootstrap gaps are tracked as A08/A17.

Do not infer current APIs from illustrative concepts. Proposed numbered ADRs in
knowledge/decisions record rationale for the corrections; they remain proposed.
This annotation does not mark the historical review/implementation tasks complete.
