## ADDED Requirements

### Requirement: Project generation

The framework SHALL provide a developer command that generates a new
application project. (FR-SCAF-001)

#### Scenario: A project is generated

- **WHEN** `adhara new <path>` runs in an empty or missing directory
- **THEN** it writes packaging, application, entry-point, test, and documentation files and reports the created paths

### Requirement: Architecture profiles

Generation SHALL support predefined architecture profiles that determine the
generated structure. (FR-SCAF-002, FR-SCAF-003)

#### Scenario: A minimal project is generated

- **WHEN** the `minimal` profile is selected
- **THEN** the application registers one action inline and needs no console-script package split

#### Scenario: A CLI project is generated

- **WHEN** the `cli` profile is selected
- **THEN** the application separates actions into a package and registers a console-script entry point

### Requirement: Bootstrap, connectors, tests, and documentation

Generated applications SHALL include a working framework bootstrap, the selected
connectors, example tests, and initial documentation. (FR-SCAF-004, FR-SCAF-005,
FR-SCAF-006, FR-SCAF-007, FR-DOC-002)

#### Scenario: Connectors are selected

- **WHEN** `--connectors http,sqlite,external` is passed
- **THEN** the generated bootstrap registers the managed connector services and the packaging includes the required extras

#### Scenario: A generated project is tested

- **WHEN** the generated example test runs
- **THEN** it starts the application and exercises the example action

### Requirement: Verification readiness

A generated application SHALL pass the applicable architecture checks without
structural corrections. (FR-SCAF-008)

#### Scenario: A generated project is verified

- **WHEN** `adhara verify <path>` runs against a generated project
- **THEN** the project reports no failures or review findings

### Requirement: Safe generation

Generation SHALL NOT overwrite existing user files without explicit
authorization. (FR-SCAF-009)

#### Scenario: A target file exists

- **WHEN** generation would overwrite an existing file and `--force` is not set
- **THEN** the command writes nothing, reports the conflicts, and exits with the invalid-invocation status

#### Scenario: Overwrite is authorized

- **WHEN** `--force` is set
- **THEN** the conflicting files are regenerated
