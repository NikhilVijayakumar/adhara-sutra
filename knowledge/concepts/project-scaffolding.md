---
type: Concept
title: Project scaffolding
description: Proposed profile-driven generation of conforming AdharaSutra applications with validated, non-destructive output.
status: draft
tags: [scaffolding, generation, profiles]
---

# Generation boundary

The proposed `adhara new` CLI command creates new applications that already conform to the architecture AdharaSutra
expects of them, generating structure, bootstrap, configuration, selected registrations, tests and documentation while
never reimplementing framework-owned infrastructure or inventing business entities. Generated applications use the
framework runtime and supported interfaces; business logic remains application-owned. Scaffolding is proposed to work
deterministically without an LLM or cloud services across Windows/Linux/macOS; existing-project transformation belongs
to the Migration subsystem.

# Proposed profiles

Application structure is determined by a selected architecture profile plus explicitly enabled capabilities.
Proposed initial profiles:

- `minimal` — small utilities; no DDD layers
- `cli` — standard multi-action CLI with actions, services, composition and configuration packages
- `ddd` — domain/application/infrastructure/interfaces/composition layer boundaries
- `electron-cli` — Electron desktop app over the Python runtime via the shared bridge package (not a copied
  transport): main owns bridge and Python lifecycle, context isolation, restricted preload, Node integration disabled
- `ai-worker` — processing-intensive applications with jobs, adapters and composition

Profiles compose rather than multiply templates: a developer may pick structure `ddd`, interface `electron-cli`, and
capabilities `jobs`, `process`, `sqlite`. A profile is a versioned definition (identifier, schema version, required
directories, modules, configuration and tests, applicable rules, optional capabilities, prohibited combinations,
default files) shared by the scaffolder and the architecture verifier. Inheritance is explicit and acyclic and never
silently overrides mandatory rules; generated projects record the profile version used at creation.

# Generated project contents

Each generation is proposed to produce:

- folder structure per profile (minimal stays flat; ddd adds the five layer packages)
- a valid framework bootstrap registering actions through framework registration — no import-time side effects,
  unnecessary connector initialization, or custom stdin/protocol parsing; one-shot or persistent entry-point modes
- configuration from approved schemas: metadata, runtime mode, logging, selected connectors, optional environment
  files, secret references only — never real credentials
- `pyproject.toml` with only required dependencies; unused connector dependencies are excluded
- testing foundations: unit tests, CLI action/protocol contract tests, controlled integration fixtures per selected
  connector, architecture checks, Electron bridge/IPC tests — examples must assert real outcomes, not pass trivially
- minimal documentation: README, purpose, installation, startup, profile, configuration, tests, dev commands — linking
  framework docs rather than duplicating them, reflecting actually-selected capabilities

# Capability and connector selection

Proposed selectable capabilities: `http`, `websocket`, `process`, `sqlite`, `filesystem`, `state`, `jobs`, `events`,
`electron`. Only declared capabilities are configured — unused ones never enter dependency declarations or startup
registration. Capability relationships drive selection: `electron` requires the CLI protocol and bridge; `jobs`
requires execution and state contracts; persistent state requires a persistence adapter; auto-selected transitive
capabilities must appear explicitly in the generation plan. The resolver rejects unsupported capabilities, missing
dependencies, invalid combinations, cycles and unsupported profile/capability mixes before any file is written.
Connector scaffolding supplies registration and adapter placeholders — SQLite yields a repository structure and
migration directory, not invented domain schemas; process disables shell execution by default.

# Generation pipeline and safety

Proposed pipeline: validate inputs → resolve profile → resolve capabilities → validate compatibility → select
templates → construct generation plan → detect destination conflicts → render to staging → validate rendered files →
apply → run applicable verification → report. Dry-run mode displays profile, capabilities, planned files,
dependencies, conflicts and planned verification without writing. Inputs are normalized per naming context (display,
distribution, import package, CLI command, application identifier), checked against keywords, reserved namespaces and
existing files, and treated as data — never executable template code — with paths kept inside the approved
destination and checked for traversal and symbolic links. Default policy rejects generation into a nonempty
destination where conflicts are possible; existing unrelated files are never silently overwritten; partial-write
failures clean up only files created by the current operation. Identical inputs and template versions produce
equivalent output, excluding explicitly variable metadata.

# Ownership and template evolution

Every generated file carries a declared ownership category: application-owned (developer freely modifies — services,
models, adapters, actions, configuration, README, tests), generated contract (regenerable from an authoritative
schema, e.g. TypeScript action types), framework-managed metadata, or temporary. The framework must never treat
application files as replaceable templates or assume they remain identical to their source. Templates declare
identifier, version, compatible profile versions, required capabilities, variables, outputs, ownership policy and
validation requirements in declarative manifests; two templates must never silently write different content to the
same destination. Existing projects are never automatically regenerated when templates change — upgrades go through
explicit, reviewable migrations, with regenerable contracts following different rules when the authoritative source
is available and the output unedited. Compatibility spans framework public API, profile, CLI protocol, bridge and
configuration schema versions.

# Verification and reporting

Scaffolding and verification share the same versioned profile definitions. Post-generation checks cover valid Python
syntax, required files, package metadata, bootstrap, dependency direction, required configuration, selected
capabilities, CLI contracts, Electron structure and applicable profile rules (proposed PS-VER-001..020), reported
PASS, FAIL, NEEDS_REVIEW or NOT_CHECKED — unavailable tooling yields NOT_CHECKED, never PASS. A machine-readable JSON
report records plan, result, validation and provenance; completed file generation and a fully verified application
are distinct outcomes that must not be conflated.

# Alternatives considered

Proposed decisions: profile-based selection with capability composition; declarative versioned template manifests;
plan → stage → validate → apply → verify with non-destructive defaults and dry run; `pyproject.toml` packaging;
profile-specific test fixtures; Markdown and JSON reports; no AI dependency; migration tooling — not the scaffolder —
for existing projects; template upgrades only as explicit reviewable migrations.

# Open questions

- PS-OQ-001 — Should `adhara new` default to `minimal` or `cli` (recommended: `minimal`)?
- PS-OQ-002 — Is `electron-cli` a standalone profile or a composable interface capability with a preset?
- PS-OQ-003 — Should templates use Jinja2 or a smaller custom restricted renderer?
- PS-OQ-004 — Should the initial developer CLI include an interactive wizard?
- PS-OQ-005 — Should profiles be owned by the scaffolder or the verifier (recommended: shared contract)?
- PS-OQ-006 — Should organizations or applications supply custom templates?
- PS-OQ-007 — Should the scaffolder automatically run pip or an Electron package manager?
- PS-OQ-008 — How much documentation should minimal applications receive?
- PS-OQ-009 — Should every project receive a sample `application.ping` action?
- PS-OQ-010 — Should Electron action types be generated from registered Python action schemas?
- PS-OQ-011 — Should per-file hashes be recorded in generation metadata?
- PS-OQ-012 — Should the developer CLI provide an `adhara scaffold upgrade` command?
- PS-OQ-013 — Should the scaffolder guarantee all-or-nothing generation rollback?
- PS-OQ-014 — Should profiles include desktop-specific packaging settings?
- PS-OQ-015 — Which capability combinations should be tested (compatibility matrix)?

See [project scaffolding requirements](../../docs/requirements/functional-project-scaffolding-requirements.md).
