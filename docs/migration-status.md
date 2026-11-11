# Documentation migration status

The original brainstorming corpus under `docs/raw/` has been migrated into the
target structure and removed. Requirements live in `docs/requirements/`,
behavioral draft specifications in OpenSpec, and durable design context
(`knowledge/`, OKF). Git history preserves the original documents.

| Original source | Requirements | Knowledge concept |
| --- | --- | --- |
| functional-requirements.md | All FR-* topic files plus [scenarios and acceptance gates](requirements/functional-scenarios-and-acceptance-gates.md) | — |
| non-functional-requirements.md | All NFR-* topic files plus [validation and quality gates](requirements/non-functional-validation-and-quality-gates.md) | — |
| vision-and-scope.md | — | [Product and scope](../knowledge/product.md) |
| system/application/module-architecture.md | — | [Architecture and boundaries](../knowledge/architecture.md) |
| cli-protocol.md | FR-CLI, FR-ELC | [CLI protocol](../knowledge/concepts/cli-protocol.md) |
| electron-integration.md | FR-ELC | [Electron integration](../knowledge/concepts/electron-integration.md) |
| connector-framework.md | FR-CON and connector topic files | [Connector framework](../knowledge/concepts/connectors.md) |
| configuration-and-lifecycle.md | FR-CFG, FR-RUN, FR-DI | [Configuration and lifecycle](../knowledge/concepts/configuration-and-lifecycle.md) |
| state-management.md | FR-STATE, FR-DB | [State and jobs](../knowledge/concepts/state-and-jobs.md) |
| job-and-process-management.md | FR-JOB | [Job and process management](../knowledge/concepts/job-and-process-management.md) |
| error-handling-and-observability.md | FR-ERR, FR-LOG | [Error handling and observability](../knowledge/concepts/error-handling-and-observability.md) |
| security-and-reliability.md | FR-SEC, NFR-SEC, NFR-REL | [Security and reliability](../knowledge/concepts/security-and-reliability.md) |
| architecture-discovery.md | FR-DISC | [Architecture discovery](../knowledge/concepts/architecture-discovery.md) |
| architecture-verification.md | FR-ARCH, NFR-ARCH | [Architecture verification](../knowledge/concepts/architecture-verification.md) |
| migration-framework.md | FR-MIG, NFR-MIG | [Migration framework](../knowledge/concepts/migration-framework.md) |
| project-scaffolding.md | FR-SCAF | [Project scaffolding](../knowledge/concepts/project-scaffolding.md) |
| testing-strategy.md | FR-TEST, NFR-TEST | [Testing strategy](../knowledge/concepts/testing-strategy.md) |
| packaging-and-distribution.md | FR-PKG, NFR-OPS, NFR-PORT | [Packaging and distribution](../knowledge/concepts/packaging-and-distribution.md) |

Migration distilled the durable substance of each source: requirement
statements, design principles, proposed contracts and state machines,
alternatives considered, and open questions (kept with their original IDs).
Scenario walkthroughs and diagrams were summarized rather than copied
wholesale; their conclusions live in the concept files, requirements, and
OpenSpec scenarios.

Remaining work is review, not migration: reconcile contradictions between the
former sources, resolve the recorded open questions, and decide the traced
requirements before approving any specification. Do not treat an illustrative
example as an approved API or a proposed target as measured performance.
