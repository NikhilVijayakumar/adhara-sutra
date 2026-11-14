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

   Copy the identity values from the saved JSON plan into the test evidence,
   and record a passing result for every ID in its `required_test_ids` list:

   ```json
   {"tests": {"status": "passed", "source_fingerprint": "<fingerprint>",
     "analyzer_version": "<analyzer version>", "profile_digest": "<digest>",
     "results": {"actions": "passed", "cli": "passed"}}}
   ```

   Add the other IDs listed in the plan when those capabilities are present.
   Summary-only evidence from older versions must be replaced with these identities
   and individual results; Git revision alone does not establish input identity.

   ```console
   adhara migrate . --status migration-status.json --evidence evidence.json
   adhara migrate . --check-source --plan plan.json
   ```

Completion requires matching plan, verification and test identities, passes for
mandatory architecture rules, resolved task/finding statuses, and passed results
for every required test ID. Other unacknowledged failures and reviews also block
completion. Evidence is supplied by the caller; it is an assertion, not a
cryptographic attestation of test execution.

## Selecting an architecture profile

Generated projects record `profile`, `profile_version`, and `package` in
`[tool.adhara]` in `pyproject.toml`. Verification and migration both select that
profile, or `minimal` version `1` when metadata is absent. Use `--profile minimal`
or `--profile cli`, and optionally `--profile-version 1`, to override selection;
reports show the selection and its configuration digest. The CLI profile requires
its declared package's generated entry and action files. Unsupported profile names
or versions fail explicitly.

A project may add `.adhara-profile.json` with `required_files`,
`required_directories`, `forbidden_imports` (pairs of import and remediation), or
`layer_boundaries` (triples of source path, import prefix, and remediation). Paths
must be project-relative. These settings extend the selected profile and change its
configuration digest. For example:

```json
{"layer_boundaries": [["src/ui", "app.data", "Use the application service"]]}
```

## Compatibility requirements

- Python 3.12 or newer.
- CLI protocol versions are declared by the runtime; the Electron bridge must
  match a supported protocol version.
- Reports carry `schema_version`; consumers should accept additive fields and
  check the version before relying on structure.
- `adhara migrate --check-source --plan plan.json` compares the saved plan's source fingerprint, analyzer version, and profile digest with current analysis.

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
