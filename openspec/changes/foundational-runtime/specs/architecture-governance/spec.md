## ADDED Requirements

### Requirement: Evidence-backed architecture verification

The verifier SHALL report findings with traceable evidence and distinguish
unsupported or incomplete checks from successful checks. (FR-ARCH-001, NFR-ARCH-001)

#### Scenario: Required evidence is unavailable

- **WHEN** a rule cannot be evaluated because its required evidence is unavailable
- **THEN** the verifier reports the check as unresolved rather than passing it

### Requirement: Reviewable migration

Migration planning SHALL produce reviewable changes and SHALL verify affected
behavior when migration changes are applied. (FR-MIG-012, FR-MIG-013)

#### Scenario: Proposed migration change

- **WHEN** a migration plan proposes a source change
- **THEN** the change is reviewable and is not represented as verified before its required checks succeed

### Requirement: Source-backed discovery

Architecture discovery SHALL record source-backed facts with uncertainty kept
visible. (FR-DISC-001, FR-DISC-009, FR-DISC-010)

#### Scenario: Discovery cannot determine a fact

- **WHEN** discovery cannot establish a fact from available source evidence
- **THEN** it reports the fact as unknown or uncertain rather than inferring a favorable conclusion

### Requirement: Current implementation report

The framework SHALL inspect an existing Python project and report its current
implementation: entry points, registered actions, jobs, services, integrations,
dependencies, state and job access, and Electron boundaries. (FR-DISC-001..008)

#### Scenario: Inspecting a project

- **WHEN** a developer runs `adhara inspect` on a project directory
- **THEN** the report lists discovered implementation facts with source evidence

#### Scenario: An unreadable module

- **WHEN** a Python module cannot be parsed
- **THEN** the report records a parse error with its location instead of omitting the module silently

### Requirement: Report formats and versioning

Reports SHALL be available as machine-readable JSON and human-readable
Markdown, SHALL identify their schema version, and SHALL record the source
revision when available. (FR-REP-001, FR-REP-004, FR-REP-005, FR-REP-006, FR-REP-007)

#### Scenario: Consuming a report

- **WHEN** a report is generated for tooling
- **THEN** it is valid JSON carrying a schema version and source revision, and the Markdown form carries the same findings

### Requirement: Traceable findings

Each reported finding SHALL carry source evidence where available and SHALL
distinguish observed facts from inferences. (FR-DISC-009, FR-DISC-010, FR-REP-008)

#### Scenario: A finding has no direct evidence

- **WHEN** a fact is inferred from an import or usage pattern rather than a direct declaration
- **THEN** the finding is marked as inferred and still cites the source location

### Requirement: Safe project generation

Scaffolding SHALL NOT silently overwrite application-owned files.
(FR-SCAF-001, FR-SCAF-009)

#### Scenario: Regenerating an existing project

- **WHEN** a scaffold command runs in a project that already contains application-owned files
- **THEN** the generator requires explicit confirmation before replacing any such file

### Requirement: Migration status tracking

Migration SHALL track task and application-level status without presenting a
partially migrated application as conforming. (FR-MIG-009, FR-MIG-010)

#### Scenario: Partially migrated application is verified

- **WHEN** verification runs on an application with unfinished migration tasks
- **THEN** the result reflects remaining gaps rather than reporting full conformance
