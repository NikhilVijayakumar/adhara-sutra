# Review and implementation evidence

## Review baseline

Source: c320dcf. The report/plan, knowledge annotations, proposed ADRs, and this
OpenSpec change are documentation work. No runtime correction has been implemented.

Source inspection covered all architecture subsystems listed in the review's scope
matrix. Small probes used temporary local fixtures and did not edit runtime source.

Observed outputs from the independent review:

```text
generated_cli_documented_loader: ImportError attempted relative import with no known parent package
new_seventh_violation_acknowledged: True evidence_count: 5
non_git_changed_source_matches: True
verification_status: pass source_revision: None
missing_revision_completion: True
non_json_job_result_state: succeeded result_type: object
```

Earlier focused probes in this same session confirmed missing configured store,
failed admission, empty-session detachment, and cleanup skipping. Their source
paths were re-examined in the independent review; they are retained findings, not
the scope boundary. The report distinguishes probe evidence from static reasoning.

## Documentation validation

Validation performed against the documentation-only working tree on 2026-11-13:

- `.\.venv\Scripts\python.exe -m unittest tests.test_documentation tests.test_docs`:
  10 tests passed, no failures or skips.
- `git diff --check`: passed; Git emitted only local CRLF conversion notices.
- Inline local validator: all 25 changed Markdown files had resolvable local
  links and no trailing whitespace. All 16 proposed requirements have scenarios;
  all 22 scenarios have WHEN/THEN clauses; cited requirement IDs exist.
- Task cross-check: 17 findings, 19 unique task IDs matched between handoff and
  OpenSpec. Only T00 is checked; the 18 runtime/governance/workflow/closeout tasks
  remain open. No implementation acceptance result was substituted by a probe.
- `openspec validate architecture-integrity-review --strict`: could not run;
  PowerShell reported that openspec was not recognized. It was also not found in
  the inspected user npm/venv locations. Local checks do not replace official CLI
  validation. Run that command in an environment with the CLI installed before
  treating the proposal as officially validated or archiving it.

T00 evidence: current runtime/protocol/job/scaffold source was compared with the
new current-behavior map and proposed ADRs. Knowledge concepts, existing decision
summary, requirement caveat, and foundational-runtime proposal/design are linked
without promoting proposed fixes to implemented. Documentation acceptance passed.
All changes are uncommitted at this point; source implementation remains c320dcf.

## Task evidence format

### T01 — explicit job-store validation

Working tree based on c320dcf with prior review and T10 changes uncommitted.
`application.py` now rejects unresolved/empty named stores, invalid store objects,
and recovery without a store with `INVALID_JOB_STORE`. Startup cleanup remains
active. Three new tests failed before the fix; after adding the named-empty case,
`.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence` passed eight
tests with no skips. Existing SQLite recovery and default no-store tests passed.
The runtime-ownership OpenSpec requirement describes the implemented behavior.

### T10 — complete baseline evidence

Working tree based on c320dcf with the review documents and T10 changes uncommitted.
Updated verification/discovery evidence retention, occurrence-count matching,
baseline regression tests, and the architecture rule reference. The two initial
regression tests failed before the fix as expected. After adding layer and line
movement coverage, `.\.venv\Scripts\python.exe -m unittest tests.test_baseline
tests.test_verification` passed 18 tests with no skips. `git diff --check` passed
before the final documentation/test additions. The architecture-integrity spec
already describes this behavior; the remaining tasks have not been implemented.

For each completed T-ID append: source revision/dirty state, files changed, exact
commands, pass/failure/skip counts, unresolved limitations, and directly updated
spec/knowledge sections. Then check only the corresponding task in tasks.md.
Do not copy the review probe outcomes as evidence that the fix passed.

### T11 ? captured input and evaluator identities

Working tree based on c320dcf, dirty with earlier uncommitted review and task changes.
Updated `discovery.py`, `verification.py`, `migration.py`, `report.py`,
`tests/test_incremental_analysis.py`, `tests/test_migration_tracking.py`, and the
architecture-integrity specification. Inspection hashes a sorted manifest of captured
source/configuration bytes; verification and plans carry profile and analyzer identities.
Custom rules and analyzers require supplied stable identities for completion eligibility.
`.\.venv\Scripts\python.exe -m unittest tests.test_reports tests.test_migration_tracking tests.test_incremental_analysis`
passed 17 tests with no skips. `.\.venv\Scripts\python.exe -m unittest
tests.test_baseline tests.test_verification` passed 18 tests with no skips. An earlier
extra invocation included nonexistent `tests.test_discovery` and failed to import that
module; the other 18 tests passed. Strict comparison of saved plans and evidence is
still T12; this task only blocks incomplete identities, and the checklist remains open
for that gate. The captured input set is not a filesystem transaction.

### T12 ? saved-plan checks and completion gates

Working tree based on c320dcf, dirty with previous uncommitted work. Updated
`migration.py`, `cli.py`, `report.py`, `tests/test_migration_tracking.py`,
`docs/migration.md`, and architecture-integrity completion scenarios. Saved-plan
identity is compared with current captured inputs; completion requires matching
identities, mandatory passes and explicit required test results. Test evidence is
a caller assertion. `.\.venv\Scripts\python.exe -m unittest
tests.test_migration_tracking tests.test_reports tests.test_exit_codes` passed 25
tests with no skips. `.\.venv\Scripts\python.exe -m unittest
tests.test_incremental_analysis tests.test_baseline tests.test_verification` passed
21 tests with no skips. `git diff --check` passed, with existing line-ending
warnings. The first focused run had one failure and one error in pre-existing test
expectations, updated for mandatory checks and strict status validation. The dirty
Git test holds revision and dirty metadata constant using a mock; the saved-plan
CLI test uses a non-Git directory.

### T02 ? rejected job admission rollback

Working tree based on c320dcf, dirty with prior uncommitted work. Updated
`jobs.py`, `tests/test_job_persistence.py`, `README.md`, and the runtime-ownership
specification. Context creation and initial save occur before local publication;
task-creation failure closes the coroutine and attempts a terminal failure save.
If that second save fails, recovery marks the durable queued record interrupted.
`.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence` passed 12
tests without skips. The required combined command `.\.venv\Scripts\python.exe
-m unittest tests.test_job_persistence tests.test_lifecycle` ran 20 tests with one
error: the previously documented `test_shutdown_cancels_jobs_and_terminates_subprocesses`
timed out waiting for the external process; the other 19 passed. This unrelated
known lifecycle failure remains open and is not claimed fixed by T02.

### T07 ? cleanup after failed job shutdown

Working tree based on c320dcf with prior uncommitted changes. Updated
`application.py`, `jobs.py`, `tests/test_lifecycle.py`, `README.md`, and the
runtime-ownership specification. Shutdown closes admission before its first await,
reserves half the cooperative budget for cleanup, preserves individual or grouped
errors, and propagates external cancellation after attempting cleanup. The five
new acceptance tests, three existing lifecycle cases, and the 12 persistence tests
passed (20 total). The required `.\.venv\Scripts\python.exe -m unittest
tests.test_lifecycle` ran 13 tests: 12 passed and the previously documented real
subprocess termination test timed out while awaiting its process (one error).
That platform-specific failure remains open and is not claimed fixed. Cooperative
budgets cannot bound synchronous blocking or cancellation-resistant coroutines.

### T04 ? shared session mapping identity

Working tree based on c320dcf with earlier uncommitted changes. Updated
`application.py`, `tests/test_protocol.py`, `README.md`, and the runtime-ownership
specification. Dispatch normalizes omitted state once and gives the same mapping to
the action and its job facade. The regression test checks identity and updates for
empty and populated mappings, an isolated session, and fresh omitted scopes, using
job completion rather than timing. `.\.venv\Scripts\python.exe -m unittest
tests.test_protocol` passed 11 tests without skips. Expected logs from existing
error-classification tests were printed.

### T17 ? terminal job outcomes

Working tree based on c320dcf with prior uncommitted changes. Updated `jobs.py`,
`tests/test_job_persistence.py`, `docs/protocol-reference.md`, and runtime-ownership
scenarios. A single terminalization path validates results, attempts terminal save
before signaling, and exposes local persistence diagnostics. Running-save failures
prevent handler execution; queued cancellation and completion signal once.
`.\.venv\Scripts\python.exe -m unittest tests.test_job_persistence tests.test_protocol`
passed 28 tests without skips. The required combined persistence/lifecycle run
(before the last additional queued-cancellation regression test) ran 29 tests:
28 passed and the known real subprocess termination test timed out. Its platform
failure remains open and is not claimed fixed. The first focused run also exposed a
test fixture name collision; unique fixture names corrected it.

### T03 ? cooperative job execution

Working tree based on c320dcf with previous uncommitted changes. Updated
`application.py`, `tests/test_lifecycle.py`, `README.md`, `docs/connectors.md`,
and the runtime-ownership specification. Synchronous registration warns while
remaining callable, including functions returning awaitables; async handlers do
not warn. Event-coordinated coverage checks health and cancellation while an async
job waits. The focused new cases plus protocol suite passed 13 tests without skips.
The required `.\.venv\Scripts\python.exe -m unittest tests.test_lifecycle
tests.test_protocol` ran 26 tests: 25 passed and the previously documented real
subprocess termination test timed out. Its platform-specific failure remains open.

### T05 ? read-only job-status action and bridge helper

Working tree based on c320dcf with previous uncommitted changes. Updated
`application.py`, `bridge/index.js`, `bridge/index.d.ts`, `tests/test_protocol.py`,
`bridge/test/fixture_app.py`, `bridge/test/bridge.test.js`, protocol and bridge
references, and the runtime-ownership spec. The action preserves the 1.0 envelope,
returns null for unknown IDs, and requires readiness and a nonempty string ID.
Python tests cover invalid, unknown, active, completed, and cancelled jobs; the
Node fixture submits app-owned work and polls its final status. `.\.venv\Scripts\python.exe
-m unittest tests.test_protocol` passed 13 tests; `node --test bridge/test/bridge.test.js`
passed two tests. No skips. Existing expected error-classification logs appeared.

### T06 ? bridge timeout outcome

Working tree based on c320dcf with earlier uncommitted work. Updated
`bridge/index.js`, `bridge/test/fixture_app.py`, `bridge/test/bridge.test.js`,
`bridge/README.md`, and the runtime-ownership specification. Timeout details retain
request identity and state unknown outcome and no cancellation request. The real
bridge test observes entry, lets the request time out, releases the fixture, checks
the correlated late response is reported as uncorrelated, and sends a later request.
Temporary fixture files are removed in finally. `node --test bridge/test/bridge.test.js`
passed three tests without skips. No cancellation or retry is implied by timeout.

### T13 ? generated package startup

Working tree based on c320dcf with prior uncommitted work. Updated
`scaffolding.py`, `cli.py`, `tests/test_scaffolding.py`,
`tests/test_developer_commands.py`, and the integration-bootstrap specification.
Generated READMEs install first and describe package module targets; standalone
relative-import failures provide remediation and retain their original cause.
Subprocess tests exercise both generated module commands, both profiles, and
with/without SQLite via configured source paths, without installing dependencies.
`.\.venv\Scripts\python.exe -m unittest tests.test_scaffolding
tests.test_developer_commands` passed eight tests without skips. The first run
failed three cases because the intended loader edit was not applied; the edit
was corrected and the command rerun successfully.

### T14 ? shared profile selection

Working tree based on c320dcf with earlier uncommitted changes. Added `profiles.py`
and updated `scaffolding.py`, `discovery.py`, `verification.py`, `migration.py`,
`cli.py`, `report.py`, `tests/test_scaffolding.py`, `tests/test_verification.py`,
`tests/test_baseline.py`, `docs/migration.md`, and architecture-integrity scenarios.
Generated metadata selects minimal/cli version 1 with the package name; verification
and migration share selection and explicit overrides. Profile configuration is
resolved from the same captured bytes used in the source fingerprint. Required
paths, metadata, versions, and custom configuration are validated.
`.\.venv\Scripts\python.exe -m unittest tests.test_scaffolding tests.test_verification
tests.test_migration_tracking` passed 27 tests. The expanded suite adding reports,
baseline, developer commands, and documentation passed 49 tests without skips. The
first expanded run found an older baseline fixture without the now-required `src`
directory; the fixture was updated and the expanded suite rerun successfully.

### T15 ? bounded static claims and coverage

Working tree based on c320dcf with previous uncommitted changes. Updated
`discovery.py`, `verification.py`, `migration.py`, `report.py`, `scaffolding.py`,
`tests/test_verification.py`, `tests/test_reports.py`, `docs/architecture-rules.md`,
`docs/migration.md`, and architecture-integrity scenarios. Framework recognition
now requires supported direct bindings; unresolved dynamic/rebound bindings do not
prove adoption. Generated starters use directly recognizable action and runtime
bindings. Verification and migration reports expose coverage and bounded syntax
claims; analyzer identity was bumped from static-1 to static-2.
`.\.venv\Scripts\python.exe -m unittest tests.test_verification tests.test_reports`
passed 18 tests without skips. The expanded suite adding scaffolding, incremental
analysis, migration tracking, baselines, and documentation passed 57 tests without
skips. Static analysis remains heuristic and does not prove whole-program behavior.

### T09 - partial documentation closeout

Working tree based on c320dcf, with prior work uncommitted and no task commits.
Reconciled `docs/decisions.md`, `docs/protocol-reference.md`, `docs/packaging.md`,
`docs/requirements/status.md`, `bridge/README.md`, the architecture, protocol and
job knowledge concepts, historical foundational-runtime design/tasks and its
state-and-jobs, CLI and Electron specs. Current sequential requests, job ownership,
status/cancel, event ordering, timeout outcome, profile/identity evidence and
persistence limits are distinguished from proposals. No numbered ADR was accepted.
No first integration has been identified: HTTP T16 and Electron T18 remain
conditional; optional T08 remains deferred. The proposal stays open.

`.\.venv\Scripts\python.exe -m unittest tests.test_documentation tests.test_docs`
passed 10 tests without skips. `node --test bridge/test/bridge.test.js` passed
three tests without skips. Final `.\.venv\Scripts\python.exe -m unittest discover
-s tests` ran 193 tests: 181 passed, 11 skipped, and one error. The error was the
previously documented `test_shutdown_cancels_jobs_and_terminates_subprocesses`,
which timed out while waiting for the subprocess; this is unresolved, not a pass.
`git diff --check` passed with existing line-ending warnings. Broad release,
security, reliability and maintainability qualification remains deferred.

### Closure and Windows subprocess fix

The prior Windows subprocess shutdown error was traced to `taskkill` returning a
nonzero exit status while `_kill_sync` treated that status as success. Updated
`external.py` so synchronous and asynchronous termination fall back to killing
the directly owned process when `taskkill` fails or cannot start. This fallback
does not establish termination of descendant processes. Added focused Windows
regression coverage and documented that limit in `docs/connectors.md`.

`.\.venv\Scripts\python.exe -m unittest tests.test_lifecycle` passed 16 tests,
including the formerly failing real subprocess case. Final
`.\.venv\Scripts\python.exe -m unittest discover -s tests` passed 194 tests
with 11 skipped, and `node --test bridge/test/bridge.test.js` passed three tests.
After adding extra fallback assertions, the lifecycle and documentation suites
passed 26 tests. Local links in both change directories resolved; `git diff --check`
passed with a line-ending warning. No commit was created.

At the user's request this integrity scope is closed by explicitly transferring
unimplemented T16, T18, and T08, along with their requirements, to the separate
[integration workflows follow-up](../integration-workflows-followup/tasks.md).
They remain unchecked. Official OpenSpec validation and archival have not been
performed: `openspec` is not installed or on PATH in this environment. The
completed source remains in place pending that validation; no approved baseline
or accepted ADR is implied.
