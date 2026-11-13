# Migration Guide

How AdharaSutra analyzes and reviews an existing Python application, and how a
consuming application carries out the migration.

## Scope

This library **evaluates and reviews** a migration. It inspects sources, verifies
the target architecture, and produces a deterministic plan with evidence,
verification steps, rollback guidance, and the behavioral regression tests that
must keep passing.

It does **not** transform, rewrite, or apply changes to application sources or
data. Applying the plan is the consuming team's responsibility, performed with
its own review and version control. No LLM review is performed here either; any
advisory review belongs to the consuming application.

## Workflow

1. Inspect and verify the current project:

   ```console
   adhara inspect .
   adhara verify . --strict
   adhara verify . --write-baseline baseline.json   # record reviewed exceptions
   ```

2. Produce a migration plan (Markdown by default, `--json` for machines):

   ```console
   adhara migrate . --strategy incremental
   adhara migrate . --strategy adapter-first --json --output plan.json
   ```

   Strategies: `incremental` (default), `adapter-first`, `rebuild`. Each plan
   lists findings, tasks with verification and rollback, preservation
   constraints, completion criteria, and required behavioral regression tests.

3. Record progress in a status file:

   ```json
   {"tasks": {"MIG-001": "done"}, "findings": {"MIG-ARCH-STRUCT-001": "deferred"}}
   ```

   ```console
   adhara migrate . --status migration-status.json
   ```

   Valid statuses: `pending`, `in_progress`, `done`, `deferred`, `blocked`.

4. Supply behavioral test evidence and evaluate completion:

   ```json
   {"tests": {"status": "passed", "command": "python -m unittest", "revision": "<git revision>"}}
   ```

   ```console
   adhara migrate . --status migration-status.json --evidence evidence.json
   adhara migrate . --check-source        # detect a stale plan after source changes
   ```

Completion is evidence-based, never declarative. A plan is `complete` only when
`adhara verify` passes, no tasks or findings remain pending/in progress/blocked,
and the supplied test evidence passed for the analyzed source revision.
Otherwise the evaluation is `incomplete` or `not_evidenced`, with reasons.

## Compatibility requirements

- Python 3.12 or newer.
- CLI protocol versions are declared by the runtime; the Electron bridge must
  match a supported protocol version.
- Reports carry `schema_version`; consumers should accept additive fields and
  check the version before relying on structure.
- `adhara migrate --check-source` compares the plan's recorded `root`,
  `revision`, and `dirty` state with the current source and flags stale plans.

## Limitations

- Analysis is static and heuristic; findings are marked `observed` or `inferred`
  and unresolved facts are reported as uncertain, not assumed.
- Analysis is non-destructive: it changes no source files and no data.
- Automated source transformation and migration apply are out of scope.
- Advisory LLM/agent review is out of scope; deterministic results stand alone.

## Recovery procedures

- Because analysis changes nothing, discard a stale plan and rerun `adhara migrate`
  after source changes.
- Revert applied migration edits with version control; keep the existing
  application entry point runnable until the migrated runtime is verified.
- Before any persistence or schema change, back up the database and exercise a
  restore. Irreversible tasks in a plan require a reviewed backup and recovery
  procedure.
- If verification fails after a change, restore the previous revision, rerun
  `adhara verify`, and regenerate the plan.
