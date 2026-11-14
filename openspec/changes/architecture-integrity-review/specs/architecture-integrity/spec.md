## ADDED Requirements

### Requirement: Complete evidence for scoped exceptions

The verifier SHALL retain every discovered violation occurrence for baseline
matching and SHALL NOT use truncated display samples as the exception scope.
Matching SHALL preserve occurrence counts while ignoring unrelated line movement.
(FR-ARCH-012, FR-ARCH-013, FR-ARCH-014)

#### Scenario: New violation occurs after the display window

- **WHEN** a captured baseline covers six violations and a seventh is added
- **THEN** the new occurrence remains unacknowledged even if the display abbreviates the list

#### Scenario: Equal snippets appear twice

- **WHEN** two violations share a rule, path, and snippet but only one was captured
- **THEN** one captured occurrence does not acknowledge both

### Requirement: Identity of captured governance inputs

Inspection SHALL identify captured analyzed source/configuration content with a
deterministic fingerprint. Verification, reports, plans, and completion evidence
SHALL carry source fingerprint, analyzer version, and normalized profile identity.
Missing identities SHALL NOT be treated as matching evidence. (FR-DISC-009,
FR-ARCH-009, FR-REP-007, FR-MIG-013)

#### Scenario: Dirty source changes without a new commit

- **WHEN** analyzed bytes change while Git revision and dirty status remain the same
- **THEN** the source fingerprint changes

#### Scenario: Saved plan is checked

- **WHEN** migration is invoked with --check-source and a saved --plan
- **THEN** its recorded identities are compared with current captured inputs
- **AND** a mismatch fails the source check rather than comparing a new plan to itself

#### Scenario: Captured analysis inputs retain identities
- **WHEN** inspection reads supported source files and root configuration
- **THEN** its fingerprint hashes the captured bytes and relative paths, and verification and migration reports carry the resulting identity

#### Scenario: Undeclared custom evaluator identity
- **WHEN** custom rules or migration analyzers omit a stable identity
- **THEN** analysis remains available but completion is not evidenced

### Requirement: Evidenced migration completion

Completion SHALL require matching nonempty input identities, evaluated passes for
mandatory profile rules, resolved task/finding statuses, and explicit passing
results for required behavioral test IDs. Legacy summary-only evidence SHALL be
reported as not evidenced. (FR-MIG-010, FR-MIG-013, FR-MIG-015, FR-ARCH-010)

#### Scenario: Source and test revisions are both absent

- **WHEN** a non-Git plan and a passed-test summary contain no exact input identities
- **THEN** migration completion is not evidenced

#### Scenario: Required test is skipped

- **WHEN** matching input identities exist but a required test result is skipped or missing
- **THEN** migration is not reported complete

#### Scenario: Mandatory prerequisite is not checked

- **WHEN** a mandatory rule is not checked, even if acknowledged
- **THEN** migration completion is blocked

#### Scenario: Recorded work has invalid status identifiers

- **WHEN** a caller supplies an unknown task or finding ID or an invalid status
- **THEN** migration evaluation rejects the status data

### Requirement: Consistent selected architecture profile

Creation, verification, and migration SHALL use a common supported profile registry
and SHALL report the selected profile name, version, and configuration digest.
Selection precedence SHALL be explicit override, project metadata, then minimal/1.
Unsupported names/versions SHALL fail explicitly. (FR-SCAF-002, FR-SCAF-008,
FR-ARCH-001, FR-MIG-003)

#### Scenario: CLI project loses a required generated file

- **WHEN** a CLI-profile project is verified and migrated without an override
- **THEN** both operations use its recorded CLI requirements and report the missing file

#### Scenario: Explicit profile override

- **WHEN** verification or migration supplies a supported explicit profile override
- **THEN** the selected profile and its configuration digest appear in the report

#### Scenario: Custom layer configuration

- **WHEN** project configuration declares a project-relative layer boundary
- **THEN** verification evaluates it without executing application code
- **AND** malformed or escaping paths are rejected

### Requirement: Bounded static-analysis claims

The inspector SHALL distinguish supported framework bindings from unrelated symbols.
Reports SHALL expose evaluated, not-checked, and mandatory-unresolved rule coverage.
Recognizing one state/job usage SHALL NOT claim universal behavioral conformance.
(FR-DISC-010, FR-ARCH-008, FR-ARCH-010)

#### Scenario: Unrelated Application class

- **WHEN** source constructs a locally defined class named Application
- **THEN** that spelling alone does not prove framework adoption

#### Scenario: Unsupported dynamic binding

- **WHEN** framework behavior depends on an unsupported dynamic binding
- **THEN** the relevant unproven prerequisite remains unresolved rather than receiving a semantic pass

#### Scenario: Framework bindings use supported aliases

- **WHEN** a directly imported Application alias is assigned to a stable module-level name
- **THEN** that binding and its direct run or serve calls can be reported as recognized syntax

#### Scenario: Coverage has unresolved prerequisites

- **WHEN** a mandatory rule is missing, not checked, or does not pass
- **THEN** verification and migration reports list it as mandatory unresolved
- **AND** evaluated and not-checked rule identifiers are reported separately
