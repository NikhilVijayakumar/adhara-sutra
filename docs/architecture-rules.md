# Architecture rule reference

`adhara verify` evaluates the rules below against an inspected project. Every
rule has a stable identifier that does not change across compatible catalog
versions, a severity, and a documented purpose. Each check reports `pass`,
`fail`, `needs_review`, or `not_checked`, with source evidence where available
and a remediation where one exists.

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
| `ARCH-PROTO-001` | CLI protocol integrity | warning | The application does not bypass the CLI protocol with direct standard stream access. |
| `ARCH-CONN-001` | Managed HTTP connector | warning | HTTP access goes through the managed connector instead of a direct client. |
| `ARCH-CONN-002` | Managed external CLI connector | warning | External programs run through the managed connector instead of subprocess. |
| `ARCH-CONN-003` | Managed SQLite connector | warning | Database access goes through the managed connector instead of sqlite3 directly. |
| `ARCH-STATE-001` | Scoped application state | warning | Application state is accessed through the request-scoped context. |
| `ARCH-JOB-001` | Managed job execution | warning | Long-running work uses the managed job manager. |
| `ARCH-JOB-002` | Managed background work | warning | Background work uses the managed job manager instead of unmanaged tasks or threads. |

## Related documentation

- [Architecture governance specification](../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md)
- [Architecture verification requirements](requirements/functional-architecture-verification-requirements.md)
- [Framework README](../README.md)
