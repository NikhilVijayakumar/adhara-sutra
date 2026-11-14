# Architecture integrity implementation tracking

Status: completed for the rescoped integrity work; follow-up tasks are transferred below.
The source remains here pending official OpenSpec validation and archival. Execute according to the priorities and dependencies
below, observing dependencies in [the implementation packets](../../../docs/architecture-fix-plan.md).
That document specifies files, fixed interfaces, acceptance checks, and commands.
This checklist is the authoritative completion tracker; record command results and
commit references, if available, in [evidence.md](evidence.md).

## P0 — current contract and trustworthy governance

- [x] T00 Verify the current-contract map, proposed ADRs, and current/proposed separation; run documentation checks. Evidence: documentation validation recorded in evidence.md; no runtime fix claimed.
- [x] T10 Preserve complete machine evidence and occurrence-scoped baseline matching; run baseline/verification checks. See evidence.md.
- [x] T11 Carry deterministic source, analyzer, and profile identities across inspection, verification, reports, and plans; run provenance checks.
- [x] T12 Compare supplied saved plans and require matching identities, mandatory-rule passes, and required-test results for completion; run CLI/completion checks.

## P0 — runtime ownership

- [x] T01 Reject unresolved/invalid explicit job stores and recovery without a store; run persistence/startup cleanup checks. See evidence.md.
- [x] T02 Roll back rejected admission without ownerless local records, tasks, or coroutine leaks; run admission/recovery checks.
- [x] T07 Close admission and attempt resource cleanup after job shutdown failure/cancellation within the existing cooperative total budget; run lifecycle checks.

## P1 — scope, results, execution, and desktop control

- [x] T04 Preserve the exact supplied session mapping for actions and jobs, including empty mappings; run isolation checks.
- [x] T17 Validate terminal results, expose persistence outcomes, and release waiters exactly once under failures; run job finalization checks.
- [x] T03 Preserve callable compatibility, warn on synchronous inline job execution, and document cooperative cancellation; run registration/control checks.
- [x] T05 Add the shared job-status action and Node helper without generic submission/listing; run Python and real bridge checks.
- [x] T06 Report bridge timeout outcome as unknown without cancellation/replay; run timeout/late-response checks.

## P1 — creation and evidence-backed adoption

- [x] T13 Repair generated package startup instructions and standalone-loader diagnostics; run both generated profile checks.
- [x] T14 Share versioned minimal/cli profile selection across creation, verification, and migration; run registry/override/configuration checks.
- [x] T15 Recognize supported bindings and publish bounded claims plus evaluated/not-checked/mandatory-unresolved coverage; run analysis/report checks.

## Transferred follow-up work

T16 (async HTTP), T18 (Node backend discovery), and T08 (lazy tooling imports)
are unimplemented and explicitly transferred to the [integration workflows follow-up](../integration-workflows-followup/tasks.md).
They remain unchecked there and are not waived or claimed complete.

## Closeout — documentation and evidence for completed work

- [x] T09 Reconcile knowledge, references, requirement caveats, and overlapping foundational-runtime draft scenarios with actual outcomes; run documentation checks and final regression checks once.

The remaining conditional and optional work is tracked in the separate follow-up.
Official archival remains pending the OpenSpec CLI validation described in evidence.md.
