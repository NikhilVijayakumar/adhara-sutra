# Architecture rule reference

Baselines match every discovered violation occurrence, including repeated
snippets in one file. Line movement alone does not invalidate an exception;
a new occurrence requires a separate entry. Older baselines with fewer entries
may therefore stop acknowledging a check until reviewed again.

`adhara verify` evaluates the rules below against an inspected project. Every
rule has a stable identifier that does not change across compatible catalog
versions, a severity, and a documented purpose. Each check reports `pass`,
`fail`, `needs_review`, or `not_checked`, with source evidence where available
and a remediation where one exists.

A pass describes recognized syntax, not whole-program correctness or blanket
protocol coverage. Framework recognition supports direct imported `Application`
(and aliases), stable module-level application assignments, and their direct
`run`/`serve` calls. Dynamic factories, decorator owners, rebinding, reflection,
and interprocedural data flow can remain unresolved. Job and state checks do not
prove all work or state is managed. Reports list evaluated IDs, not-checked IDs,
and mandatory-unresolved IDs; aggregate pass can coexist with unchecked rules.

This table is kept in step with `RULE_CATALOG` in
[`verification.py`](../src/nikhi/adhara_sutra/verification.py); the test suite
fails when a rule is added, removed, or changed without updating it.

| Identifier | Rule | Severity | Purpose |
| --- | --- | --- | --- |
| `ARCH-STRUCT-001` | Required project files | error | The project contains the files required by the architecture profile. |
| `ARCH-STRUCT-002` | Required project directories | error | The project contains the directories required by the architecture profile. |
| `ARCH-STRUCT-003` | Python modules | error | The project contains at least one analyzable Python module. |
| `ARCH-STRUCT-004` | Parseable sources | error | Every Python module can be parsed, so the analysis is complete. |
| `ARCH-DEP-001` | Forbidden dependencies | error | The project does not import dependencies forbidden by the architecture profile. |
| `ARCH-LAYER-001` | Module-layer boundaries | error | Imports respect the module-layer boundaries configured by the architecture profile. |
| `ARCH-FW-001` | Framework application | error | The project creates an Application with the framework. |
| `ARCH-FW-002` | Registered actions | warning | The application registers at least one action. |
| `ARCH-ENTRY-001` | Runtime entry point | error | The application has an entry point that starts the framework runtime. |
| `ARCH-PROTO-001` | CLI protocol integrity | warning | Recognizes selected direct standard stream access syntax. |
| `ARCH-CONN-001` | Managed HTTP connector | warning | HTTP access goes through the managed connector instead of a direct client. |
| `ARCH-CONN-002` | Managed external CLI connector | warning | External programs run through the managed connector instead of subprocess. |
| `ARCH-CONN-003` | Managed SQLite connector | warning | Database access goes through the managed connector instead of sqlite3 directly. |
| `ARCH-STATE-001` | Scoped application state | warning | Recognizes selected context state access syntax. |
| `ARCH-JOB-001` | Managed job execution | warning | Recognizes job decorator or context.jobs access syntax. |
| `ARCH-JOB-002` | Managed background work | warning | Recognizes selected unmanaged task and thread creation syntax. |

## Custom profiles and rules

A profile is configuration, not code: `ArchitectureProfile` declares required
files and directories, forbidden imports, and layer boundaries, and `verify`
evaluates it without changing the verifier. Applications can also add their own
rules. `Rule` supplies the stable identifier, title, and severity, `check_for`
builds the result, and `verify(..., rules=...)` appends it to the catalog checks:

```python
from nikhi.adhara_sutra import Rule, check_for, verify
from nikhi.adhara_sutra.verification import FAIL, PASS

readme = Rule("APP-DOC-001", "Project README", "warning", "The project documents itself.")

def evaluate(project, profile):
    if "README.md" in project.files:
        return check_for(readme, PASS, detail="README.md is present")
    return check_for(readme, FAIL, detail="README.md is missing", remediation="Add README.md")

result = verify(project, rules=[(readme, evaluate)])
```

Custom checks appear alongside catalog checks in verification reports and use
the same statuses, evidence, and remediation fields.

## Custom migration analyzers

`analyze_migration(..., analyzers=...)` accepts callables that receive the
inspected project and verification result and return `MigrationFinding` objects.
Their findings become plan and report findings, and receive the same verifiable
task treatment as built-in findings, so a project-specific layout or CLI library
can be covered without changing the migration core.

## Related documentation

- [Architecture governance specification](../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md)
- [Architecture verification requirements](requirements/functional-architecture-verification-requirements.md)
- [Framework README](../README.md)
