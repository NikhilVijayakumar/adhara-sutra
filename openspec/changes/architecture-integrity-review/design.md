# Design: architecture integrity and ownership

Status: proposed. Source baseline: c320dcf. This document defines the recommended
target; the current behavior map is in knowledge/architecture.md. T16, T18 and T08 are transferred to [the follow-up](../integration-workflows-followup/tasks.md).

## Boundaries and decisions

Retain the modular monolith and a separate Node bridge. Business/domain code stays
in the consuming application. Applications submit jobs through business actions;
the framework supplies lifecycle/status/cancel, not domain authorization or generic
remote execution. Retain sequential request dispatch and bounded concurrent jobs.
Preserve sync callable compatibility with warnings; provide async I/O for long work.
Do not imply that async syntax enforces nonblocking behavior.

A future Node resolver is tracked in the follow-up. Currently the application supplies the fixed backend command; Python runtime discovery remains a Python-host helper. One process owns a job;
persisted metadata is not durable execution and recovery does not replay work.

## Contracts

- `system.jobs.get` takes `{job_id}` and returns `{job_id, status}`; unknown IDs
  return null status. Existing system.cancel remains. Listing/submission are app-owned.
- Bridge timeout keeps work outcome unknown and requests no cancellation. Never
  automatically replay side effects. Lost submission acknowledgments require an
  application operation identity before resubmission.
- Results must be JSON-compatible before success. Status exposes local persistence
  outcome separately; save failure cannot hang waiters or claim durable success.
- Configured stores must resolve; admission is rolled back before local acceptance
  if setup or initial save fails. No cross-SQLite/asyncio atomicity is claimed.
- Session mappings preserve object identity even when empty.
- Shutdown closes admission, gives jobs at most half the existing cooperative budget,
  and always attempts resources with the remaining overall budget. Cancellation-
  resistant or synchronous blocking code cannot be given a hard asyncio deadline.

## Governance and data flow

The inspector captures a deterministic manifest of analyzed source and relevant
configuration bytes. Source fingerprint, analyzer version, and normalized profile
digest travel through verification, reports, plans, and supplied test evidence.
Revision/root/dirty remain descriptive metadata. New custom evaluators must supply
stable identity to qualify for strict completion.

Compare saved plans against current captured inputs. Completion requires matching
nonempty identities, passing mandatory rules, resolved work statuses, and explicit
passing required-test IDs. This binds assertions to inputs but is not a signed
test attestation or an application execution sandbox.

Machine checks retain complete violation evidence and occurrence counts. Human
summaries may abbreviate. Baselines do not match unseen occurrences. Static
analysis supports documented syntax bindings and exposes unsupported/unchecked
coverage rather than claiming whole-program guarantees.

Creation, verification, and migration share only supported minimal/cli profile
definitions, versions, and selection precedence. Candidate profiles remain future
work. Profile/config/analyzer changes invalidate prior completion evidence.

## Compatibility and alternatives

Rejected: concurrent request rewrite without an integration requirement; automatic
threading of contexts/SQLite; immediate rejection of supported sync jobs; doubling
shutdown time; source identity based only on Git; baselines built from display
samples; package splitting; generic public job submission.

Public APIs are additive where possible. Existing reports remain readable, but
legacy evidence without exact identity is not sufficient for new strict completion.
The previously ineffective --check-source requires a saved --plan; document the
invocation change. Frozen commands and synchronous HTTP consumers remain supported.

## Knowledge and draft-spec reconciliation

T00 documents current facts and proposed ADRs. Each task updates its directly
affected reference/scenario. T09 reconciles the foundational-runtime drafts and
knowledge with implemented outcomes. No task or requirement is completed solely
because this proposal exists. Do not rewrite historical decisions as if they
already endorsed the new target.

## Verification and limitations

Use focused deterministic checks in the handoff. Record actual command results in
evidence.md and complete matching task checkboxes only after they pass. The Windows subprocess shutdown failure was fixed and rerun; see evidence.md.
No benchmarks, security audit, OS matrix, or first-project integration is claimed.
