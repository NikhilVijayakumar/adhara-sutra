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
