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
