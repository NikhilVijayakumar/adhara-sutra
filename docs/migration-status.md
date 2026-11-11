# Documentation migration status

The target is requirements in `docs/requirements/`, behavioral specifications
in OpenSpec, and durable context in `knowledge/`. `docs/raw/` is temporary input,
not a long-term authority. A source can be removed only after its substantive
content and open questions have been reviewed, placed in the target structure,
and checked for traceability and unresolved contradictions.

| Source area | Status | Remaining work |
| --- | --- | --- |
| Functional and non-functional requirements | Requirement sections split by topic; context remains | Migrate cross-cutting acceptance gates, scenarios, measurement rules, and open questions; reconcile duplicates and status. |
| Vision and scope | Product summary drafted | Migrate remaining scope, goals, non-goals, and open decisions. |
| System, module, and application architecture | Boundary summary drafted | Migrate component responsibilities, dependency rules, diagrams, alternatives, and open decisions. |
| CLI protocol | Concept and initial scenarios drafted | Migrate detailed event, control, session, cancellation, concurrency, ordering, errors, security, testing, and compatibility contracts; reconcile alternatives. |
| Electron integration | Not migrated | Extract bridge and process boundaries, security, lifecycle, scenarios, and open decisions. |
| Connector framework | Not migrated | Extract shared and connector-specific contracts, lifecycle, failures, security, and scenarios. |
| State management | Not migrated | Extract state ownership, persistence, consistency, recovery, and open decisions. |
| Jobs and process management | Not migrated | Extract state machines, ownership, cancellation, recovery, and process semantics. |
| Configuration and lifecycle | Partly covered by initial runtime change | Extract configuration, bootstrap, lifecycle, cleanup, and error contracts. |
| Error handling and observability | Not migrated | Extract error taxonomy, logging, redaction, diagnostics, and correlation. |
| Project scaffolding | Not migrated | Extract profiles, generated artifacts, validation, and compatibility. |
| Architecture discovery and verification | Boundary summary drafted | Extract evidence, rules, coverage, reporting, and deterministic verification contracts. |
| Migration framework | Product summary drafted | Extract planning, baselines, safety, review, rollback, and verification. |
| Testing strategy | Not migrated | Extract test layers, fixtures, acceptance gates, and evidence requirements. |
| Security and reliability | Not migrated | Extract trust boundaries, controls, failure and recovery scenarios. |
| Packaging and distribution | Not migrated | Extract Python, npm, desktop packaging, compatibility, and release contracts. |

For each area, trace specifications to requirement IDs and use draft status until
decisions are reviewed. Do not treat an illustrative example as an approved API
or a target as measured performance. The source corpus includes repeated and
potentially conflicting proposals; migration needs semantic review, not just file
relocation or mechanical conversion.
