# Architecture integrity before first integration

## Why

An independent architecture review traced product promises through runtime,
connectors, Electron bootstrap, scaffolding, verification, migration, and durable
knowledge. It found ownership defects and governance paths that can overstate
what was verified. The code baseline is c320dcf; the review and implementation
handoff began as documentation changes; implemented outcomes and tests are recorded in [evidence.md](evidence.md). The completed scope is closed with T16, T18 and T08 explicitly transferred to [the follow-up](../integration-workflows-followup/proposal.md).

## What Changes

- P0: full evidence for scoped exceptions, exact analyzed-input identity, saved-plan
  comparison and source-bound completion evidence, explicit store validation,
  admission rollback, cleanup ownership, and honest current-contract documentation.
- P1: session/result ownership, compatible cooperative job guidance, job status,
  timeout outcomes, executable generated-project instructions, shared profile
  selection, and static-analysis coverage limits.
- Transferred follow-up: managed async HTTP, Node-owned backend resolution, and lazy development-tool imports; none is claimed implemented.
- Correct knowledge/specification contradictions and record proposed durable
  decisions with alternatives. Do not promote proposed features to implemented.

## Capabilities

### New Capabilities

- `architecture-integrity`: evidence scope, source identity, completion gates,
  selected-profile consistency, and bounded static claims.
- `runtime-ownership`: requested persistence, admission, session/result ownership,
  cooperative controls, cleanup, and nonblocking connector integration.
- `integration-bootstrap`: executable generated-project startup and backend
  discovery owned by the Electron main process.

### Modified Capabilities

None in the accepted baseline: `openspec/specs/` has no accepted capabilities yet.
The new requirements refine the draft foundational-runtime specifications. These
are ADDED requirements in this dependent proposal, not modifications of an
accepted spec. Reconcile overlapping draft text before either change is archived.

## Impact

Affected code: application/jobs, discovery/verification/migration/reporting,
scaffolding/developer CLI, optional HTTP, Node bridge, public export facade.
Affected docs: knowledge boundaries/concepts/ADRs, protocol/connectors/packaging,
requirement status caveats, and foundational-runtime draft specs.

Requirement trace: FR-RUN-002/003/007, FR-CFG-003, FR-CON-002, FR-STATE-003/005,
FR-JOB-001/002/003/005/006/008/009/010/011, FR-ELC-006/007/008, FR-HTTP-001/002/003/006/007,
FR-SCAF-002/004/007/008, FR-ARCH-001/008/010/013/014, FR-DISC-010,
FR-MIG-003/010/013, FR-REP-006/007, FR-PKG-004/005/006. Individual scenarios cite
their source groups; task-specific trace corrections must follow actual requirement
wording rather than invent new IDs. Existing requirement priorities are unchanged.

## Dependencies

Depends on the existing foundational-runtime draft and implementation. Its review
tasks remain open; this proposal does not archive or approve that change.
Task IDs and priorities are in [tasks.md](tasks.md), with implementation packets in
[the handoff](../../../docs/architecture-fix-plan.md) and evidence/rationale in
[the review](../../../docs/architecture-review-2026-11-13.md).

## Decisions and open questions

Recommended decisions are fixed in [design.md](design.md) and proposed ADRs linked
by [adr.md](adr.md). The first consuming integration and its workflows remain undecided. Integration evidence is still
needed for concurrency capacity, CPU executors, production packaging and platform
qualification. Those are deferred validation topics, not reasons to invent a new
architecture now. Broad release, reliability, maintainability, and security
qualification remains deferred by the user.
