# Independent architecture review before first integration

Reviewed revision: `c320dcf` on `develop`, 2026-11-13.
Revision 2: independently reassessed from product scope and requirements, then
checked against source and adversarial probes. Supersedes the earlier focused review.
Disposition: retain the modular-monolith architecture; resolve the integrity and
ownership gaps below before relying on the affected adoption workflows.
These are recommendations, not approved or implemented changes.

## Scope and evidence

The starting points were `knowledge/product.md`, the system boundaries, functional
requirements, and representative CLI/process, HTTP, Electron, and migration
workflows. Earlier findings were re-examined rather than treated as the scope.
The method was an adversarial self-review: challenge each architectural promise,
trace its ownership and failure path, consider alternatives, and recommend a choice.
No dedicated "grill me" skill was available or invoked. No user questions were
needed. This is a full architecture-scope review, not an exhaustive code/security
audit or empirical qualification of every supported platform.

| Area reviewed | Architectural challenge | Result |
| --- | --- | --- |
| Product boundary and package model | Is the framework replacing business logic or requiring distributed infrastructure? | Keep registration and one distribution; preserve domain independence. A08. |
| Runtime, services, configuration | Can requested capabilities silently disappear; who cleans up failure? | A01, A07. Explicit composition is sound; validation/cleanup are incomplete. |
| Actions, jobs, events, state | Can controls progress; who owns results and session scope? | A02–A06, A16. Preserve sequential controls, fix ownership contracts. |
| HTTP, WebSocket, process, SQLite, files/artifacts | Do specialized capabilities fit the execution model? | A03, A15. Keep specialized connectors; do not impose one universal execute API. SQLite stays on its owning thread; explicit artifact lifetime stays app-owned. |
| Electron and bootstrap | Can the owner locate/start Python without Python already running? | A06, A17. Main process remains owner; bootstrap guidance is incomplete. |
| Scaffolding and profiles | Do created projects run as documented and share verification targets? | A12, A13. |
| Discovery, verification, exceptions | Does evidence justify the claim; do exceptions admit new violations? | A10, A14. Mandatory checks need complete evidence and bounded claims. |
| Migration and reporting | Does completion refer to the exact source and tests actually checked? | A11. Source provenance is insufficient. |
| Knowledge, requirements, specs, decisions | Can two agents derive the same implemented contract? | A09. Separate current facts, recommendations, and future options. |
| Packaging, API compatibility, extension points | Does a proposed correction break a documented public API? | Revised A03 and A07 recommendations below; retain additive APIs and defer package splitting. |

## Priority and execution order

P0 means correct before trusting the affected architecture/adoption mechanism;
it does not assert a production incident. P1 means finish before using the affected
workflow in the first integration. P2 means useful follow-up that does not gate
that integration. Document priorities are independent of original requirement
priorities. No broad quality/security program is pulled forward.

| Priority | Findings | Recommended order and reason |
| --- | --- | --- |
| P0 | A09 | T00: publish the current/proposed distinction before another agent follows conflicting instructions. |
| P0 | A10, A11 | T10, T11, T12: prevent false exception/completion claims before using governance or migration. |
| P0 | A01, A02, A07 | T01, T02, T07: preserve explicit persistence, admission, and cleanup ownership before enabling jobs. |
| P1 | A04, A16, A03 | T04, T17, T03: preserve scope and valid results, then clarify cooperative execution without breaking sync registrations. |
| P1 | A05, A06 | T05, T06: give desktop callers a status contract and honest timeout outcomes. |
| P1 | A12, A13, A14 | T13, T14, T15: align generated projects, selected profiles, and evidence claims. |
| P1 when HTTP/Electron is selected | A15, A17 | T16, T18: provide a nonblocking HTTP path and bootstrap owned by the process that starts Python. |
| P2 | A08 | T08: isolate imports without requiring a physical module/package rewrite. |
| P0 closeout for implemented tasks | A09 | T09: synchronize knowledge, specs, task evidence, and remaining limits. |

Task IDs are stable links, not numeric execution order. The handoff specifies
dependencies and the OpenSpec task list is the source of completion tracking.

The user deferred broad release readiness, testing/reliability qualification,
maintainability assessment, and security assessment until a real project integrates
the framework. Keep those deferred. The narrow regression checks in the companion
plan validate the proposed corrections; they do not complete that deferred program.

## Recommended architecture and reasoning

1. Keep one persistent backend process per application and sequential request
   dispatch. Long operations use background jobs and return a job ID immediately.
   Existing jobs already provide bounded concurrency. Concurrent request dispatch
   would additionally require decisions about action reentrancy and shared state,
   with no demonstrated requirement from a consuming application yet.
2. Keep business submission actions in the application, for example
   `audio.transcribe`. That action validates business input and submits a registered
   job. Do not expose every registered handler through a generic submission action.
   The framework should add one standard read-only job-status action alongside its
   existing cancellation action. Applications retain ownership of job-list access
   and any application-specific authorization.
3. Recommend async handlers for long jobs and preserve existing synchronous job
   registrations with an explicit deprecation/limitation warning. The prior plan's
   immediate rejection would break the documented callable API; that recommendation
   is withdrawn. Async bodies must yield. Add an optional AsyncHttpClient for the
   HTTP workflow; use the existing async process connector for executables. Do not
   silently move contexts, SQLite, or event writers into threads. CPU-heavy Python
   execution and general executors remain integration-driven extensions.
4. A bridge timeout means the caller stopped waiting; it does not prove cancellation
   or failure. Keep that behavior and make the unknown outcome machine-readable.
   Never automatically retry submission or other side-effecting actions. Once a job
   ID is known, query status or request cancellation. If submission timed out before
   its ID arrived, reconciliation belongs to the application's operation identity;
   this review does not promise exactly-once submission.
5. Keep optional SQLite metadata persistence and mark crashed work interrupted.
   Do not add durable workers, implicit databases, automatic restart, or replay.
6. Keep one Python distribution and the separate Node bridge. Remove eager imports
   across the runtime/tooling boundary while preserving public import names.

Example flow: `audio.transcribe` validates input -> submits job -> returns
`{job_id}` -> desktop calls `system.jobs.get` and optionally `system.cancel`.
Jobs can emit progress after the submission response; job ID is their correlation
key. An action waiting for job completion would block the sequential request loop
and defeats this recommended desktop flow.

## Findings

### A01 — Configured persistence can silently disappear (high)

**Evidence:** `Application.start` in `src/nikhi/adhara_sutra/application.py` resolves
a string store name with `services.get`. `job_store="typo", recover_jobs=True`
starts successfully in state `ready`, with the manager's actual store equal to
`None`. This was reproduced during review.

**Consequence:** an application configured to recover jobs can run without
persistence and give no configuration failure. This violates explicit ownership
of a requested capability.

**Fix:** fail bootstrap for unresolved or invalid stores and for recovery without
a store. Keep the no-store/no-recovery default. See T01.

### A02 — Failed job admission leaves ownerless records (high)

**Evidence:** `JobManager.submit` in `jobs.py` inserts the record into `_jobs`
before saving it or creating its task. With a store whose `save` raises, submission
raises but leaves a `queued` record without a task. Shutdown leaves it queued.
Both outcomes were reproduced.

**Consequence:** rejected work consumes queue capacity and appears accepted in
status listings even though no execution owner exists.

**Fix:** give admission a rollback boundary; no task or local record survives a
failed admission. Distinguish storage failure from a handler failure. See T02.

### A03 — Sync job execution undermines the control path (high)

**Evidence:** `JobManager._run` calls `handler(payload, context)` directly before
checking whether the result is awaitable. `Application.job` accepts any callable;
its docstring says timeouts apply only to async handlers. `HttpClient.request` is
synchronous. These are source-confirmed properties, not a timing benchmark.

**Scenario:** a synchronous handler performs a slow HTTP request or CPU loop.
During that call the event loop cannot process health, job cancellation, or other
async jobs. Merely submitting it as a background job does not isolate it.

**Fix:** recommend async jobs and warn on sync job registration while preserving
existing behavior until a documented removal version. A warning is not proof of
nonblocking execution. Add a genuinely async HTTP path (A15). Do not silently move
all handlers to threads: shared context, event output, and SQLite have no universal
thread-safe contract. Repository job examples/tests currently use async handlers.
T03 supersedes the earlier breaking rejection proposal.

### A04 — Empty session state is detached from submitted jobs (medium)

**Evidence:** `Application.dispatch` gives the action the supplied session mapping,
but constructs its job facade with `session_state or {}`. An empty supplied mapping
is replaced. A job writing `session_state['job_value'] = 1` left the original session
equal to `{}` in the review probe.

**Consequence:** job/session behavior depends on whether the mapping already has
an unrelated key.

**Fix:** normalize the mapping once using an explicit `is None` check and share
the same object between action and job contexts. See T04.

### A05 — Job control is only partly standardized (medium)

**Evidence:** `Application.dispatch` exposes `system.cancel`, but not job status.
`JobService.status` and `.list` exist only on the Python side. The job concept
proposes reserved get/list actions, while the protocol reference defines neither.

**Consequence:** every desktop application must invent status routing and response
shapes even though the framework owns the job lifecycle.

**Fix:** add `system.jobs.get` and `bridge.jobStatus(jobId)`. Retain app-owned
submission/list actions and existing `system.cancel`. Use current state strings
`queued/running/succeeded/failed/cancelled/interrupted`; do not rename persisted
states to the older concept's `pending/completed`. See T05.

### A06 — Timeout behavior is correct but its outcome contract is incomplete (medium)

**Evidence:** `Bridge.#send` deletes the pending entry on timeout and rejects with
`BRIDGE_TIMEOUT`. It does not cancel Python work; this is already documented.
The later response is currently reported as an uncorrelated protocol error.

**Scenario:** an action commits a change after the bridge times out. A UI interprets
the rejection as an operation failure and resubmits it.

**Fix:** retain caller-only timeouts, add `details.outcome = "unknown"` and
`details.cancellation_requested = false`, retain request identity, and document
safe follow-up behavior. Late-response classification is optional follow-up;
do not introduce an unbounded timeout-ID registry. See T06.

### A07 — Job shutdown failure skips resource ownership cleanup (high)

**Evidence:** the cleanup coroutine inside `Application.stop` awaits job shutdown
before `_stack.aclose`, without a `finally` between them. A probe that injected a
job-shutdown exception confirmed that a registered resource's exit method was
never called. Services were nevertheless cleared and state became `failed`.

**Consequence:** the runtime discards its published references to services without
attempting their owned cleanup. A subsequent `stop` returns immediately in failed
state, so it does not finish that cleanup.

**Fix:** always attempt service cleanup after job shutdown failure or timeout and
preserve failure evidence. Keep the existing overall shutdown budget and reserve
part for resource cleanup. The previous proposal to double the effective budget
is withdrawn: it conflicts with callers' existing shutdown expectations. This is
an ownership correction, not proof of cross-platform termination.
See T07. The previously observed real subprocess shutdown test failure is separate
evidence requiring reproduction; this review does not claim the same root cause.

### A08 — Runtime imports pull in development tooling (medium)

**Evidence:** `__init__.py` eagerly imports discovery, migration, scaffolding-related
reporting, verification, documentation validation, and testing exports. `cli.py`
also imports tooling before choosing a command. A fresh runtime import confirmed
`nikhi.adhara_sutra.migration` was already in `sys.modules`.

**Consequence:** the stated runtime/tooling separation is not enforced at the import
boundary. Tooling import failures can prevent a packaged runtime from loading even
when the application only needs `Application`. No startup latency claim is made.

**Fix:** lazy-load non-core public exports, preserve names and `__all__`, and import
developer command dependencies inside the relevant branches. T08.

### A09 — Architecture records describe incompatible contracts (medium)

**Evidence:** `knowledge/architecture.md` proposes concurrent requests;
`docs/decisions.md` chooses sequential requests. The OpenSpec design lists lifecycle
and compatibility decisions as open despite concrete implementations and decision
records. The status introduction says connectors/migration/verification are absent.
The protocol/bridge references say events precede the request's terminal response,
without explaining detached job events after submission completes.

**Consequence:** a coding agent can faithfully follow one document and contradict
another. This is especially costly for a smaller model implementing changes.

**Fix:** reconcile the specific contracts after T01–T08, link authoritative sources,
and retain a distinction between recommended, implemented, and integration-proven.
Do not mass-approve requirements or check stale tasks without evidence. T09.

## Additional findings from the independent review

### A10 — Truncated evidence makes baselines admit new violations (P0)

**Evidence:** `_protocol`, `_layer_boundaries`, and other rules in `verification.py`
truncate the evidence stored in Check. `Baseline.acknowledges` compares only those
locations. A probe captured a baseline with six stdout-bypass files, added a
seventh, and still received `acknowledged=True` with five evidence entries.
FR-ARCH-013/014 and NFR-ARCH-003 require scoped exceptions and honest statuses.

**Consequence:** a CI exception silently expands beyond the reviewed violations.
**Recommendation:** retain the full machine evidence set for exception matching;
truncate display only. Match duplicate locations by occurrence count so two
identical snippets in one file cannot share one exception. Keep line-independent
matching for unrelated edits. T10 precedes migration and profile work.

### A11 — Migration provenance cannot establish the source being approved (P0)

**Evidence:** `MigrationPlan.source_matches` uses root/revision/dirty only. A non-Git
source change still matched in a probe. Two dirty worktrees at the same commit
also have indistinguishable identity. In `cli.py`, `--check-source` compares a plan
just generated from project with that same project, so it cannot detect stale plans.
With passing verification and completed task/finding statuses, test evidence with
only `{status: passed}` allowed completion when both revisions were absent; reproduced.
FR-MIG-013, FR-REP-007, NFR-MIG source-safety requirements are affected.

**Recommendation:** hash the exact analyzed file set/content and include profile
configuration plus analyzer identity. Compare a supplied saved plan to current
inputs; never a plan to its own input. Require matching nonempty source identity,
passed required test identifiers, and matching verification provenance for completion.
Revision remains useful metadata, not the sole identity. Reject legacy evidence as
not evidenced rather than guessing. T11 adds identity; T12 fixes the completion/CLI gate.

### A12 — Generated CLI bootstrap contradicts its own run instructions (P1)

**Evidence:** `_readme` emits `adhara run src/<package>/app.py`. CLI-profile app.py
uses `from .actions import register`; `_load` executes the path under a synthetic
top-level name. The generated command reproduced `ImportError: attempted relative
import with no known parent package`. FR-SCAF-004/007/008 are affected.

**Recommendation:** use installed package/module entry points for generated CLI
projects and document `adhara run <package>.app` after installation. Retain file
loading only for standalone files without package-relative imports; provide a clear
loader diagnostic. Do not grow an implicit import-system replacement. T13.

### A13 — Creation and governance have no shared selected-profile identity (P1)

**Evidence:** scaffolding.PROFILES is `minimal/cli`; ArchitectureProfile has only
a version/configuration and no name. `adhara verify`/`migrate` always use the default
profile; there is no shared profile selection. DDD/Electron/AI profiles in knowledge
are future candidates. FR-SCAF-002/008, FR-ARCH-001, FR-MIG-003 are affected.

**Recommendation:** a single versioned built-in profile registry initially contains
only minimal/cli; generated pyproject records the selected name/version. Verification
and migration resolve the same selection with explicit overrides. Custom Python
profiles remain supported and get deterministic configuration identity. Do not
invent empty DDD layers or mark future profiles available. T14.

### A14 — Discovery syntax heuristics are reported as semantic guarantees (P1)

**Evidence:** discovery recognizes any call spelled `Application(...)`, regardless
of its import binding; action/job decorators by attribute spelling; entry points
only for variables app/application with `.run`. An arbitrary user-defined
Application can satisfy framework detection, while a valid aliased import can be
missed. `_jobs` says long-running work uses the manager merely from one job access.
Aggregate verification can pass while relevant checks are not checked.
FR-DISC-010 and FR-ARCH-008/010 are affected.

**Recommendation:** track supported framework import aliases and simple bindings;
unsupported dynamic patterns remain needs-review/not-checked. State presence of
recognized syntax as the checked fact, not universal lifecycle or protocol behavior.
Publish evaluated/not-checked coverage; strict migration completion requires its
profile's mandatory rules to have evidence. No whole-program analyzer is proposed.
T15, with the completion prerequisite established in T12.

### A15 — The HTTP scenario lacks a nonblocking managed connector (P1 for HTTP)

**Evidence:** HttpClient uses httpx.Client and time.sleep; its streaming iterator
is synchronous. Jobs, WebSocket, and process streaming use asyncio. An async job
calling HttpClient directly still blocks the shared control loop. A03 alone does
not solve this architectural mismatch. FR-HTTP and the representative HTTP scenario
are affected.

**Recommendation:** add optional AsyncHttpClient with async lifecycle, request,
and context-managed byte streaming. Share DTOs/error semantics; retain HttpClient
for synchronous consumers. Initially no automatic retry in the async path, matching
the default policy. Cancelling local I/O does not cancel a remote inference job.
Do not present a thread-wrapped synchronous stream as equivalent. T16.

### A16 — A job can succeed with an unusable terminal result (P1)

**Evidence:** JobManager._run sets succeeded on any Python return value. A probe
returned object() and received state succeeded. Such a result cannot be serialized
for the protocol or SQLiteJobStore. Finalization signals its event before saving
the final snapshot; persistence failures can escape in callbacks or leave durable
and in-memory outcomes inconsistent. FR-JOB-008/009/011 are affected.

**Recommendation:** one terminalization path validates JSON data before success,
persists before signaling waiters when possible, and reports terminal persistence
failure explicitly without losing local completion or falsely claiming durability.
Use existing artifact references for large data. Define valid lifecycle/result DTOs
once and reuse them in status and persistence. T17.

### A17 — Desktop bootstrap instructions require Python before locating Python (P1 for Electron)

**Evidence:** docs/packaging.md tells packaged Electron apps to call Python's
locate_backend to obtain the command that starts Python. The Node bridge requires
command at construction and exports no locator. The Python helper is useful inside
Python, but cannot bootstrap a machine without an already located interpreter.
FR-PKG-004/005/006 and the Electron ownership boundary are affected.

**Recommendation:** add a Node-side resolver for explicit override/bundled paths,
owned by Electron main. Packaged mode fails if configured bundled candidates are
missing; development PATH fallback is explicit. Return a command path, use fixed
arguments, then let bridge.start perform compatibility/readiness checks. Keep the
Python helper for Python hosts. No release packaging matrix is implied. T18.

## Challenge outcomes

The review challenged these assumptions without requiring user decisions:

| Assumption | Verdict and reason |
| --- | --- |
| Concurrent requests are necessary for a responsive desktop | Not established. Async background jobs plus short control requests fit the existing decision. |
| A background job makes any Python function nonblocking | False; current sync calls execute on the same event loop. |
| A configured store will either work or reject startup | False; unresolved service names currently become no persistence. |
| A rejected submission creates no work record | False; failed storage can leave a queued record with no owner. |
| Cancellation and timeout both mean the operation stopped | False; timeout ends waiting, and cancellation acceptance is distinct from completion. |
| Standard jobs require exposing all jobs for generic submission | False; shared status/cancel can coexist with business-owned submission and list visibility. |
| A failed shutdown still attempts every cleanup phase | False in the current job-error path. |
| One distribution requires eager loading of all tooling | False; preserve packaging and public names with lazy imports. |
| A baseline covers only violations explicitly captured | False when evidence is truncated; retain full evidence and occurrence counts. |
| A Git revision plus dirty flag uniquely identifies analyzed content | False; fingerprint exact inputs, including profile/analyzer identity. |
| Passing test evidence without revision identifies a non-Git source | False; absent identities matching each other prove nothing. |
| Generated projects necessarily run using their documented command | False for the CLI profile's file-loader command. |
| Creation and verification already share named profiles | False; introduce one registry for the two actually supported profiles. |
| Finding one job proves all long-running work is managed | False; report only the recognized fact and expose unsupported checks. |
| Async job syntax makes the current HTTP connector nonblocking | False; provide an async connector for that workflow. |
| A successful Python return is necessarily a usable job result | False; validate protocol/persistence DTOs before success. |
| Electron can use Python code to discover its first interpreter | Circular bootstrap; resolve bundled paths in Node main. |
| The first correction plan was automatically compatible | False; immediate sync-job rejection and doubled shutdown budgets are withdrawn. |

## Delivery and deferred work

Use [the implementation handoff](architecture-fix-plan.md), one task per model
session. The authoritative checklist is the
[OpenSpec change](../openspec/changes/architecture-integrity-review/tasks.md).
Each task has bounded files, fixed behavior, and acceptance checks.
Do not ask a smaller model to "fix the architecture" in one pass.

After these tasks, integrate one real project to validate the architecture. Broad
benchmarks, coverage targets, soak tests, OS/Python/Electron matrices, production
packaging, dependency/security audits, and general maintainability work remain
deferred as requested. No NFR is completed merely because this review exists.
