# Architecture correction handoff

Baseline: `c320dcf`. Review: [findings and rationale](architecture-review-2026-11-13.md).
Revision 2: independent architecture review. Status: proposed tasks; no runtime
implementation has been performed by this review. The authoritative checklist is
[OpenSpec tasks](../openspec/changes/architecture-integrity-review/tasks.md).

Current disposition: the completed integrity scope was closed after the Windows
subprocess fix. Unimplemented T16, T18, and T08 were transferred to the
[integration workflows follow-up](../openspec/changes/integration-workflows-followup/tasks.md).
This document preserves the original handoff and detailed acceptance packets.

## Priorities, execution order, and tracking

P0 blocks trust in the affected adoption mechanism. P1 is needed before using its
workflow in integration. P2 can follow integration. Read the review for evidence.

| Order | Task | Priority | Dependency | Finding |
| --- | --- | --- | --- | --- |
| 1 | T00 current-contract knowledge/spec map | P0 | none | A09 |
| 2 | T10 complete baseline evidence | P0 | T00 | A10 |
| 3 | T11 source/profile fingerprints | P0 | T00 | A11 |
| 4 | T12 saved-source and completion gates | P0 | T10, T11 | A11 |
| 5 | T01 explicit job store | P0 | T00 | A01 |
| 6 | T02 admission rollback | P0 | T01 | A02 |
| 7 | T07 cleanup ownership | P0 | T02 | A07 |
| 8 | T04 session identity | P1 | T02 | A04 |
| 9 | T17 terminal results | P1 | T02, T07 | A16 |
| 10 | T03 cooperative execution contract | P1 | T00 | A03 |
| 11 | T05 job-status API | P1 | T04, T17 | A05 |
| 12 | T06 timeout outcome | P1 | T05 | A06 |
| 13 | T13 generated bootstrap | P1 | T00 | A12 |
| 14 | T14 shared profile registry | P1 | T11, T12, T13 | A13 |
| 15 | T15 supported analysis and coverage | P1 | T10, T12, T14 | A14 |
| 16 | T16 async HTTP connector | P1 for HTTP | T03 | A15 |
| 17 | T18 Node bootstrap resolver | P1 for Electron | T00 | A17 |
| 18 | T08 lazy tooling imports | P2 | T14 | A08 |
| 19 | T09 evidence/document closeout | P0 closeout | completed applicable tasks | A09 |

Every row has a matching T-ID in OpenSpec. Update only that task's
checkbox after acceptance checks pass; T00 is now checked because its documentation
map and proposed ADRs were verified during this review. Include actual results in its evidence
log. A skipped workflow task remains unchecked and explicitly deferred. Do not
close the whole change while deferred or failed tasks remain.

T00 and T09 include knowledge and specification fixes. Each implementation task
also updates its directly affected reference/spec scenario as part of that task;
do not postpone all contract documentation until the end.

## T00 — Establish one honest current-contract map

Priority P0. Finding A09. Files: `knowledge/architecture.md`,
`knowledge/decisions/index.md`, `docs/requirements/status.md`,
`openspec/changes/foundational-runtime/design.md` and `proposal.md`, and the new
OpenSpec change. Current/proposed annotations also link the CLI/job knowledge concepts
and the existing decision summary.

This review has added the current/proposed distinction and proposed ADR links.
Before implementation, verify these entries against source. Current facts are
sequential requests, callable jobs with cooperative limits, optional explicitly
configured persistence, fixed-command Node bridge, and minimal/cli scaffolding.
Planned changes remain marked proposed. Candidate DDD/Electron/AI profiles are
not implemented. Knowledge owns durable rationale; maintained references own
current wire/API shapes; OpenSpec owns proposed scenarios and completion tracking.
Do not rewrite old decision history or promote drafts to accepted.

Acceptance: all five facts are discoverable with no claim that the new APIs already
exist; proposed ADRs include alternatives and consequences. Run documentation checks.

## Instructions for the implementing model

Work on one task at a time, in order. Read the referenced finding and the files
listed for that task. Inspect current Git status before editing. Preserve existing
unrelated changes. Do not add dependencies, split packages, introduce concurrent
request dispatch, add generic executors, or implement durable workers.

Use `unittest`; pytest is absent from the current virtual environment. Windows
commands below run from the repository root. On another OS, use that environment's
Python executable with the same `-m unittest` arguments.

Each task must add the focused regression checks specified below, run its
targeted command, and report changed files and results. If unrelated checks fail,
record the actual output rather than expanding scope. Do not mark broad deferred
NFRs complete. Commit only when asked. The suggested commit titles identify task
boundaries; they are not an instruction to commit automatically.

The earlier full-suite run had 153 tests, 11 skips, and a timeout in
`test_shutdown_cancels_jobs_and_terminates_subprocesses`; the Node suite passed
both tests. This is baseline context, not a claim about the current environment.

## T01 — Validate explicit job-store configuration

Finding: A01. Dependencies: none.
Files: `src/nikhi/adhara_sutra/application.py`, `tests/test_job_persistence.py`.

Implementation:
1. Resolve a string `job_store` only after managed services have been entered.
2. If that name is missing, or the resolved object is `None`, raise
   `BootstrapError("INVALID_JOB_STORE", ...)` naming the configured service.
3. A directly supplied object must have callable `save` and `load_all` methods.
   Those are the operations JobManager actually needs; do not require inheritance
   from the Protocol or require an unused `update` method.
4. `recover_jobs=True` with no configured store raises the same code.
5. Keep `job_store=None, recover_jobs=False` working unchanged. Let real recovery
   read failures continue to produce `RECOVERY_FAILED` with the original cause.

Acceptance checks: missing name, named service returning `None`, malformed object,
and recovery-without-store each fail startup; initialized resources are closed;
normal no-store mode and the existing SQLite recovery cases still pass.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence`
Suggested title: `Reject invalid explicit job-store configuration`.

## T02 — Roll back rejected job admission

Finding: A02. Dependency: T01.
Files: `src/nikhi/adhara_sutra/jobs.py`, `tests/test_job_persistence.py`.

Implementation:
1. Construct the record and job context locally before publishing a local record.
2. Persist the initial queued snapshot before scheduling the handler.
3. Publish/register the task and record within one synchronous admission method,
   with rollback if context creation, initial persistence, or task creation raises.
   On initial save failure, leave no `_jobs` entry or task and propagate the cause.
4. If task creation fails after initial persistence, remove the local record and
   best-effort persist a terminal failed snapshot with `JOB_ADMISSION_FAILED`.
   A storage failure after that point may leave a durable queued snapshot; startup
   recovery must mark it interrupted. Document that limit rather than claiming a
   transaction spanning SQLite and asyncio. Close any unsubmitted coroutine.
5. Failed admission returns no job ID and consumes no local queue capacity. Avoid
   changing normal job execution or swallowing an admission exception.

Acceptance checks: a fail-once store rejects the first submission, leaves no local
record/task, never invokes its handler, and allows a second submission to succeed.
A context-factory failure leaves no local record. An injected task-creation failure
does not leak a coroutine and makes a terminal save attempt. Existing recovery
tests remain valid.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence tests.test_lifecycle`
Suggested title: `Roll back failed background job admission`.

## T03 — Document cooperative execution without breaking callable jobs

Finding: A03. Dependency: T00.
Files: `src/nikhi/adhara_sutra/application.py`, `tests/test_lifecycle.py`,
`README.md`, `docs/connectors.md`.

Implementation:
1. Preserve acceptance of synchronous handlers. At registration, emit a
   DeprecationWarning for handlers not recognized by inspect.iscoroutinefunction,
   with stacklevel=2 and a message explaining inline execution and that timeout
   does not bound the synchronous portion. Do not execute the handler to inspect it.
2. Retain short synchronous action handlers. Do not add automatic thread dispatch
   in `dispatch` or `JobManager`.
3. Document that async functions must not call blocking functions directly, that
   timeout/cancellation is cooperative, and that CPU-heavy work needs an external
   process or a later executor design.
4. Show an async job awaiting `ExternalCommand.run`. For synchronous HTTP usage,
   document explicit adapter offload of an isolated blocking call; do not suggest
   moving SQLite or the whole application context to a thread.
5. Recommend async adapters for long work. State that removal of sync registration
   needs a future declared incompatible version; this task sets no removal date.
   Changing `def` to `async def` alone does not make blocking bodies safe. Link T16
   for nonblocking HTTP, rather than claiming an async connector already exists.

Acceptance checks: async registration works without a warning; sync registration
warns and still executes; sync functions returning awaitables retain behavior and
warn without being invoked during registration. During an async job held
on an `asyncio.Event`, a health request succeeds and cancellation can complete.
Coordinate with events; do not use timing benchmarks as pass/fail criteria.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_lifecycle tests.test_protocol`
Suggested title: `Clarify cooperative job execution and warn on inline sync handlers`.

## T04 — Preserve the session mapping's identity

Finding: A04. Dependency: T02.
Files: `src/nikhi/adhara_sutra/application.py`, `tests/test_protocol.py`.

Implementation: normalize `session_state` once in dispatch using
`session_state if session_state is not None else {}`. Pass that identical object
to the request context and its `JobService`. Do not use truthiness for mappings
whose identity represents scope. Keep a fresh mapping for each omitted scope.

Acceptance checks: jobs submitted from actions see and update the same empty or
populated mapping supplied to dispatch. A separate session sees none of those
updates. Use job completion events/wait to coordinate the checks.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_protocol`
Suggested title: `Preserve session state identity for submitted jobs`.

## T05 — Add a shared read-only job-status contract

Finding: A05. Dependencies: T04, T17.
Files: `application.py` in the runtime package, `bridge/index.js`,
`bridge/index.d.ts`, `tests/test_protocol.py`, `bridge/test/fixture_app.py`,
`bridge/test/bridge.test.js`, `docs/protocol-reference.md`, `bridge/README.md`.

Fixed interface:

```text
action: system.jobs.get
payload: {"job_id": "non-empty string"}
success data: {"job_id": "the requested ID", "status": <existing snapshot or null>}
bridge helper: jobStatus(jobId) -> Promise of that data object
```

Implementation:
1. Require ready/running state as `system.cancel` does. Malformed `job_id` returns
   `ACTION_VALIDATION_FAILED` with details `job_id`. Unknown IDs are successful
   reads with `status: null`. Use the existing snapshot method and state names.
2. Keep business submission actions, listing visibility, and authorization in the
   consuming app. Do not add `system.jobs.submit` or `system.jobs.list` in this task.
3. Add `jobStatus` helper and matching type declarations. Preserve `cancel` and
   protocol `1.0`; this is an additive reserved action, not an envelope change.
4. Extend the fixture with an app-owned submit action and an async job. Query its
   final state through the real bridge, using bounded polling and a clear timeout.

Acceptance checks: invalid, unknown, active, completed, and cancelled job queries
match the exact response shape. Node helper rejects invalid IDs locally, and the
real bridge fixture returns a submitted job's final snapshot.

Run Python: `.\.venv\Scripts\python.exe -m unittest tests.test_protocol`
Run Node: `node --test bridge/test/bridge.test.js`
Suggested title: `Expose a consistent job status action and bridge helper`.

## T06 — Mark bridge timeout outcomes as unknown

Finding: A06. Dependency: T05.
Files: `bridge/index.js`, `bridge/test/bridge.test.js`, `bridge/test/fixture_app.py`,
`bridge/README.md` (and `index.d.ts` only if details already have a structured type).

Implementation: retain `BRIDGE_TIMEOUT`, request ID, action, and existing pending
cleanup. Add `outcome: "unknown"` and `cancellation_requested: false` to its details.
Do not send cancellation, kill the backend, resubmit work, or add retries.
Document that a known job ID allows status lookup; a lost submission response
needs application-specific reconciliation before resubmission. Keep the existing
late-response `protocolError` behavior explicit for now.

Acceptance check: a deterministic fixture emits an event confirming it entered
a waiting action. Let that request time out, then release its wait through a
fixture-controlled signal/file and observe that it finishes. Assert the timeout
details and that a later ordinary request still works. Remove fixture resources
in a finally block. Do not call this timeout proof of backend cancellation.

Run: `node --test bridge/test/bridge.test.js`
Suggested title: `Expose unknown operation outcomes on bridge timeout`.

## T07 — Attempt service cleanup after failed job shutdown

Finding: A07. Dependency: T02; execute here to keep the sequence simple.
Files: `src/nikhi/adhara_sutra/application.py`, `src/nikhi/adhara_sutra/jobs.py`, `tests/test_lifecycle.py`,
`docs/protocol-reference.md` or the maintained lifecycle section of `README.md`.

Fixed policy for this proposal: keep `shutdown_timeout` as the overall cooperative
budget. Set a monotonic deadline at entry. Cap the job phase at half the configured
budget, reserving at least half for resources; unused job time is available for
resource cleanup. This reservation prioritizes releasing owned processes/services
over indefinitely waiting on jobs. Do not double the caller's budget. Synchronous blocking
cleanup and cancellation-resistant coroutines cannot be given a hard wall-clock
guarantee by asyncio; do not claim otherwise or introduce force-kill logic here.

Implementation:
1. Run job shutdown with the capped budget, capture ordinary failure/timeout, and
   attempt `_stack.aclose()` with the remaining budget regardless of that outcome.
2. Add a manager admission flag initialized true and set false at the start of
   `JobManager.shutdown`, before its first await. `submit` checks it before saving
   or scheduling and raises `RuntimeError("Job manager is shutting down")` when
   false. This covers existing Python job facades as well as protocol callers,
   which already encounter the application's state check. Ensure startup/shutdown
   ownership remains on the same event loop; do not move exit methods to threads.
3. If either phase fails, enter failed state and surface the failure; if both fail,
   use `ExceptionGroup` to retain both errors (Python >=3.12 is already required).
   A single failure keeps its existing exception type. Preserve cancellation as
   cancellation; never convert an external `CancelledError` to success. Attempt
   resource cleanup in the cancellation path with remaining budget and re-raise
   cancellation. Do not catch BaseException broadly and relabel it an ordinary error.
4. Clear published services only after the cleanup attempt, including failure paths.
   Successful shutdown still enters stopped; repeated stop remains harmless.

Acceptance checks: injected job-shutdown failure still closes a resource; job
timeout still attempts resource cleanup; dual ordinary errors remain inspectable;
successful shutdown and existing idempotency expectations remain valid. A captured
Python job facade rejects submission after shutdown begins, without creating work.
Keep the real subprocess test and report its result independently; do not disable it or
claim this task resolves its platform-specific cause.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_lifecycle`
Suggested title: `Preserve resource cleanup after job shutdown failure`.

## T08 — Enforce the runtime/tooling import boundary

Finding: A08. Dependency: T14. Priority P2; may follow first integration.
Files: `src/nikhi/adhara_sutra/__init__.py`, `src/nikhi/adhara_sutra/cli.py`,
`tests/test_packaging.py`, `tests/test_developer_commands.py`.

Implementation:
1. Keep runtime exports eager where needed, but move discovery, migration,
   verification, report, docs validation, and testing exports behind a fixed
   name-to-module mapping resolved by module-level `__getattr__` using importlib.
2. Preserve every existing public name and `__all__`. Cache resolved attributes
   in module globals. Unknown attributes raise `AttributeError`. Do not use
   filesystem scanning or string eval. A star import may load all exports.
3. Move developer-tool imports in `cli.py` into the subcommands needing them.
   Keep parser choices available through small static CLI constants if necessary;
   verify those values against the existing authoritative constants in a test.
4. Keep the installed command and package/module paths unchanged.

Acceptance checks: in separate fresh Python processes, importing Application and
loading/executing `adhara run` do not import discovery/migration/verification/
scaffolding/testing modules; explicit imports of their public names still work.
Existing public API and developer-command tests pass. Inspect sys.modules in fresh
processes; an already-imported test runner is not a valid isolation check.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_packaging tests.test_developer_commands`
Suggested title: `Load development tooling only when requested`.

## T09 — Reconcile architecture records with the completed changes

Finding: A09. Dependencies: all implemented applicable tasks, with actual results.
Files: `docs/decisions.md`, `knowledge/architecture.md`,
`knowledge/concepts/job-and-process-management.md`, `docs/protocol-reference.md`,
`bridge/README.md`, `docs/requirements/status.md`,
`openspec/changes/foundational-runtime/design.md`,
`openspec/changes/foundational-runtime/tasks.md`, and only the directly affected
OpenSpec capability specs (`state-and-jobs`, `cli-protocol`, `electron-bridge`).

Implementation:
1. Record sequential short actions plus async background jobs as the current
   baseline. Explain why concurrent request dispatch stays deferred.
2. Record app-owned business submission/listing, implemented get/cancel behavior,
   timeout unknown outcomes, store validation, and the reserved total shutdown budget.
3. Distinguish action events before their response from detached job events after
   submission returns. Clients correlate job progress with job ID, not a promise
   that it precedes the submission response.
4. Use actual persisted job states everywhere. Preserve the no-durable-execution
   and no-automatic-replay limits. Correct the stale tracker introduction.
5. Replace obsolete open-decision statements with links to the actual decisions;
   keep unresolved integration questions explicit. Do not globally change draft
   to approved or mark all architecture tasks complete.
6. Update OpenSpec task checkboxes/evidence with commit references if available and
   actual outcomes. Preserve review/plan links. Mark superseded recommendations as
   superseded; preserve proposed status until an actual decision is accepted.
7. Reconcile profile configuration, fingerprint/evidence schema, baseline matching,
   supported static patterns, async HTTP, and Node bootstrap only for completed
   tasks; explicitly retain deferred items. Never claim deferred APIs are shipped.

Acceptance: a reader can determine the current request model, job execution model,
status/cancel API, persistence failure policy, event ordering, and timeout meaning
without encountering contrary current guidance. No broad deferred NFR is marked
complete as a side effect. Existing documentation checks pass or their failures
are recorded with the exact unresolved link/section.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_documentation tests.test_docs`
Suggested title: `Align architecture records with runtime ownership contracts`.

## T10 — Keep complete evidence for scoped baselines

P0; A10; dependency T00. Files: `verification.py`, `tests/test_baseline.py`,
`tests/test_verification.py`, `docs/architecture-rules.md` (runtime package paths
are under `src/nikhi/adhara_sutra/`). Spec: architecture-integrity / exception scope.

Remove rule-evidence slicing from machine Check objects. Text summaries may remain
short, but exception matching must use every discovered location. Use a multiset
of `(rule, path, snippet)` keys: an acknowledged count must cover the current count.
Baseline.capture must preserve repeated occurrences rather than deduplicating them.
Keep line numbers out of matching so unrelated edits do not invalidate exceptions.
Existing v1 baseline files remain readable; old undercounted files conservatively
stop acknowledging additional occurrences. Do not widen an exception automatically.

Acceptance: baseline six bypass files, add a seventh beyond the old first-five
window, and assert the check is unacknowledged. Repeat for a layer rule. Two equal
snippets in the same file require two captured occurrences. Moving an unchanged
occurrence by adding blank lines preserves its acknowledgement. Inspect JSON to
confirm it contains all locations, not merely the displayed first few.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_baseline tests.test_verification`

## T11 — Add reproducible input and verification identities

P0; A11; dependency T00. Files: `discovery.py`, `verification.py`, `migration.py`,
`report.py`, `tests/test_reports.py`, `tests/test_migration_tracking.py`,
`tests/test_incremental_analysis.py`. Spec: architecture-integrity / input identity.

Fixed design:
1. Add an optional `source_fingerprint` field at the end of ProjectProfile, default
   None for existing Python constructors. Inspector always populates a SHA-256 hex
   string from a sorted manifest of relative POSIX paths and SHA-256 byte digests.
2. Manifest input includes analyzed Python/JS/TS files, root pyproject.toml,
   setup.cfg, package.json, and `.adhara-profile.json` when present. Use existing
   exclusions. Exclude report outputs, timestamps, absolute root, and Git metadata.
   Additions/deletions/renames count; root relocation alone does not. Define the
   supported JS/TS suffixes once and reuse them.
3. Hash bytes actually parsed. Refactor inspection to pass the read byte content
   into parsing/cache logic; do not hash once and independently reread different
   bytes. A single inspection is a captured input set, not a filesystem transaction.
4. Add an analyzer version constant (`static-1`) and a normalized profile digest
   (SHA-256 of sorted-key JSON of the complete profile configuration). Changing
   analyzer semantics requires bumping this identifier.
5. VerificationResult carries source_fingerprint, analyzer_version, and
   profile_digest as additive fields with legacy defaults. Reports and migration
   plans copy the actual identities. Existing schema major remains 1; legacy
   documents can be read but do not qualify for strict completion.
6. Custom rule/analyzer sets need explicit stable IDs/versions in the supplied
   identity. If they are omitted, allow exploratory analysis but make its identity
   incomplete and completion ineligible. Never hash repr(callable) or its address.

Acceptance: clean/non-Git/dirty inputs all receive identities; edit/add/delete or
change profile config changes identity; generated report output or root relocation
does not. Cache reuse preserves identical results. Legacy constructors still work.
Custom evaluators without declared identity cannot claim completion eligibility.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_reports tests.test_migration_tracking tests.test_incremental_analysis`

## T12 — Compare saved plans and require matching completion evidence

P0; A11; dependencies T10/T11. Files: `migration.py`, `cli.py`, `report.py`,
`tests/test_migration_tracking.py`, `tests/test_reports.py`, `docs/migration.md`.
Spec: architecture-integrity / migration completion.

Fixed interface: keep `--check-source` but require `--plan <saved-migration.json>`
with it. A missing --plan is invalid invocation (exit 2). A mismatching fingerprint,
analyzer version, or profile digest returns exit 1. Matching returns normal analysis
output; never compare a newly constructed plan with its own ProjectProfile. Read
saved reports with load_report and validate kind and required identity fields.

Completion policy:
1. Require matching nonempty identities on plan, verification, and test evidence.
   Revision is optional metadata and None==None is never source evidence.
2. Add `required_test_ids` to MigrationPlan. Initially derive fixed identifiers:
   `actions` and `cli` for every framework migration; add `electron`, `http`,
   `external`, `sqlite`, `state`, `jobs` only when those capabilities are discovered.
   Existing prose regression_tests remains guidance, not a test identifier.
3. Evidence shape is `{tests: {status: "passed", source_fingerprint: "...",
   analyzer_version: "static-1", profile_digest: "...", results:
   {actions: "passed", cli: "passed", ...}}}`. Missing IDs, skipped/failed required
   tests, absent identity, or old summary-only evidence means not evidenced.
4. Default mandatory architecture IDs are STRUCT-001/003/004, FW-001/002, ENTRY-001
   with the existing `ARCH-` prefix. Each must have an evaluated pass; exceptions
   do not turn a mandatory not-checked prerequisite into a pass. Other unacknowledged
   failures/needs-review still block strict completion. T14 will let profiles declare
   this list; T15 exposes coverage to readers.
5. Status files continue to track work; marking tasks done is not test evidence.
   Validate IDs/status values even through the direct Python API. Evidence is a
   caller-supplied assertion, not a cryptographic attestation; document that limit.

Acceptance: a changed dirty source/non-Git source fails a saved-plan check; identity
missing on legacy plans is not evidenced; source/profile/analyzer mismatch blocks;
missing required test, skipped result, or mandatory not-checked rule blocks completion.
A fully matching explicit fixture completes. No execution of inspected application
code is introduced. Document migration from old evidence files.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_migration_tracking tests.test_reports tests.test_exit_codes`

## T13 — Repair the generated package bootstrap contract

P1; A12; dependency T00. Files: `scaffolding.py`, `cli.py`,
`tests/test_scaffolding.py`, `tests/test_developer_commands.py`.
Spec: integration-bootstrap / generated projects.

Generated README must install the project first, then use `python -m <package>`
or `adhara run <package>.app`. CLI-profile package modules must never be advertised
as standalone script paths. Keep `_load` file behavior for actual standalone apps.
On an attempted relative import from a supplied file path, produce an actionable
message to install/use the dotted module target; preserve the exception cause.
Do not manipulate __package__ or emulate package installation implicitly.

Acceptance: generated minimal and CLI projects, both without and with SQLite
selection, load by documented module command and execute greeting through the
protocol. Use a subprocess with its generated src path configured for tests;
the published README still says to install. The CLI app.py file attempt fails with
the remediation message. No dependency installation is necessary for these checks.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_scaffolding tests.test_developer_commands`

## T14 — Select one profile consistently for create, verify, and migrate

P1; A13; dependencies T11/T12/T13. Files: new `profiles.py`, `scaffolding.py`,
`verification.py`, `migration.py`, `cli.py`, `tests/test_scaffolding.py`,
`tests/test_verification.py`, `tests/test_migration_tracking.py`.
Spec: architecture-integrity / selected profiles.

Fixed design: a lightweight profiles module defines only minimal/cli, version 1.
Record selection in generated pyproject `[tool.adhara]` as `profile = "cli"` and
`profile_version = "1"`. Each definition declares required files/directories and
mandatory rule IDs; minimal requires pyproject and source, CLI additionally its
package actions and entry structure. Profile requirements are expressed relative
to the declared generated package, not hardcoded to a project name.

verify/migrate CLI accept `--profile` and `--profile-version`. Explicit flags win,
then project metadata, then minimal/1. Unknown names/versions fail with exit 2.
If `.adhara-profile.json` supplies custom required files/dirs/imports/layers, load
it as explicit configuration and include it in the profile digest. Validate all
paths are project-relative. Preserve custom Python ArchitectureProfile calls;
add optional name/mandatory-rule fields at the end with compatible defaults.
Scaffolding consumes the same named registry. No DDD/Electron/AI templates are
added. Resolve the selected profile once and pass it through verification/migration.

Acceptance: both generated profiles pass their applicable mandatory rules; deleting
a CLI-required file fails CLI verification but cannot be concealed by migration
using a different default; explicit override is visible in reports and changes the
digest; malformed metadata/unknown versions fail predictably. Custom config layer
violations fail without application execution. Preserve existing custom Python tests.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_scaffolding tests.test_verification tests.test_migration_tracking`

## T15 — Bound static claims and expose evaluated coverage

P1; A14; dependencies T10/T12/T14. Files: `discovery.py`, `verification.py`,
`report.py`, `tests/test_verification.py`, `tests/test_reports.py`,
`docs/architecture-rules.md`. Spec: architecture-integrity / evidence limits.

Support direct `from nikhi.adhara_sutra import Application [as Alias]` and
`import nikhi.adhara_sutra as alias` bindings, plus a simple assigned application
variable and its .run/.serve calls. Exclude locally defined unrelated Application
classes from a positive framework claim; do not execute imports. Treat dynamic
factory/decorator/alias rebinding outside the supported subset as unresolved.
Do not promise interprocedural data-flow or reflection support.

Change job/state/protocol rule details to say what syntax was recognized. One
context.jobs use cannot prove all long work is managed. Add report coverage:
evaluated rule IDs, not_checked IDs, and mandatory-unresolved IDs. Keep existing
status names and aggregate status behavior for exploratory verification; explicit
completion gates in T12 use mandatory prerequisites. Documentation must explain
that aggregate pass is not whole-program correctness or blanket protocol coverage.

Acceptance: valid aliases are found; an unrelated user Application is not a proven
framework app; direct .serve is recognized; unsupported dynamic bindings stay
unresolved; a single jobs use does not generate a universal safety statement.
Coverage lists include every rule exactly once with honest mandatory unresolved IDs.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_verification tests.test_reports`

## T16 — Add a managed async HTTP path for the HTTP workflow

P1 if HTTP is selected; A15; dependency T03. Files: `http.py`, `__init__.py`,
new `tests/test_http_async.py`, `docs/connectors.md`.
Spec: runtime-ownership / nonblocking connectors.

Add AsyncHttpClient with the same base_url/auth/header/TLS/timeout constructor
semantics as HttpClient, async __aenter__/__aexit__, async request/get/post methods,
and async-context-managed stream(method,url,...). Use httpx.AsyncClient from the
existing optional http extra; no new dependency. Ordinary responses use HttpResponse.
Async stream response provides `aiter_bytes` and reuses status/error/JSON outcome
semantics where applicable. Its lifetime cannot outlive the context manager.
Do not share a sync stream iterator or insert time.sleep. No retry loop initially.
Health reports local client initialization; it does not claim remote readiness.
Local cancellation propagates after local cleanup and does not promise remote cancel.
Close each response/client exactly once, including early exit and cancellation.

Split execution into two small model sessions if needed: request/lifecycle, then
streaming/cancellation; mark T16 complete only after both acceptance sets pass.
Acceptance: MockTransport or a guarded local fixture verifies request/error mapping,
incremental streaming and early close. While a stream waits on an asyncio.Event,
a health request still proceeds. Cancellation closes the local stream. Existing
sync HttpClient tests pass unchanged. Skip with an explicit optional-dependency
reason if httpx is absent; a skip is not completion evidence.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_http_async tests.test_http_retry tests.test_http_stream`

## T17 — Finalize a valid, inspectable job outcome exactly once

P1; A16; dependencies T02/T07. Files: `jobs.py`, `tests/test_job_persistence.py`,
`tests/test_lifecycle.py`, protocol/job reference sections.
Spec: runtime-ownership / terminal results.

Use one terminalization helper for _run and pre-start cancellation callbacks.
Validate a result with json.dumps(allow_nan=False) before setting succeeded.
Unsupported values produce state failed, result null, and error code
JOB_OUTPUT_INVALID with a fixed safe message. Reject bytes/object/NaN; applications
use ArtifactStore references for binary/large data.

Persist the terminal snapshot before waking waiters when saving succeeds. On
terminal-save failure, retain the actual local execution outcome but add
`persistence: {status: "failed", error_code: "JOB_PERSISTENCE_FAILED"}` to the public
snapshot, log the cause, and still release waiters exactly once. Never recursively
retry persistence in a done callback. With no store, use status `disabled`; with
successful terminal persistence, `saved`. The additive persistence field is local
diagnostic metadata, not a new SQL column; recovered old records report `saved`
after successful read. Do not claim the field itself is durably stored if save failed.

If the initial running-state save fails, fail the job before calling its handler;
use JOB_PERSISTENCE_FAILED and do not create side effects knowingly without the
configured state record. Shutdown remains possible after storage failures.

Acceptance: invalid result produces failed on both no-store and SQLite paths;
save failures before execution do not invoke the handler; failure on terminal save
never hangs wait, emits no unhandled callback exception, preserves local outcome
with failed persistence metadata, and does not claim recovery can read that outcome.
Queued cancellation and normal completion each signal once. Existing state names
and old SQLite rows remain usable.

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence tests.test_lifecycle`

## T18 — Resolve bundled backends in the Node process that owns startup

P1 if Electron is selected; A17; dependency T00. Files: new `bridge/runtime.js`,
`bridge/index.js`, `bridge/index.d.ts`, `bridge/package.json`,
new `bridge/test/runtime.test.js`, `docs/packaging.md`, `bridge/README.md`.
Spec: integration-bootstrap / backend resolution.

Export async `locateBackend({appRoot, bundled = [], env = process.env,
allowSystemPython = false}) -> Promise<string>`. Resolution: ADHARA_PYTHON explicit
file override, then configured bundled paths relative to appRoot. A missing explicit
override is an error, not permission to select an unrelated interpreter. If no
candidate exists and allowSystemPython is false, reject with
BRIDGE_BACKEND_NOT_FOUND and actionable details. Development fallback searches
platform interpreter names using the supplied PATH/PATHEXT only when explicitly
enabled. Never invoke a shell. No Python code may be required to locate the command.

Export through the current package entry and types; include runtime.js in published
files. Document Electron main calling the resolver before constructing Bridge.
Keep frozen executables usable as explicit commands. Resolution proves candidate
existence, not compatibility: bridge.start owns handshake/readiness verification.
Keep the Python helper for Python hosts; remove the circular desktop instruction.

Acceptance: temp files/dirs verify override precedence, missing override, bundled
relative paths, no implicit system fallback in packaged mode, explicit development
fallback with a controlled PATH, and a command containing spaces returned as one
path. No requirement to install Electron or produce release artifacts.

Run: `node --test bridge/test/bridge.test.js bridge/test/runtime.test.js`

## Completion check and copyable task prompt

After the last task, run once:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
node --test bridge/test/bridge.test.js
git diff --check
```

Report failures and skips honestly. Optional-dependency/platform skips remain gaps
in evidence. A successful correction suite is not release or integration approval.

Paste this prompt into Terra or another coding agent, replacing `T10` with the next
task ID in the priority/dependency order above:

> Read docs/architecture-fix-plan.md and implement T10 only. Read the linked
> architecture finding for rationale. Inspect Git status and applicable repository
> instructions first. Follow the task's fixed interfaces and acceptance checks.
> Preserve unrelated work and public behavior outside this task. Add the specified
> focused checks, run the targeted command, and report files changed plus actual
> results. Update only this task's OpenSpec checkbox after its acceptance checks
> pass, and record the command/outcome under evidence.md in that change. Keep the
> directly affected spec/reference honest about implemented versus proposed behavior.
> Do not implement later tasks, install dependencies, commit, or mark broad
> deferred requirements complete. If the current source differs materially from
> the described baseline, report the exact difference before inventing a redesign.
