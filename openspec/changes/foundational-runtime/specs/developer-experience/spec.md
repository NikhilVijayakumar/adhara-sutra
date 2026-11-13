## ADDED Requirements

### Requirement: Working examples

The framework SHALL ship representative, runnable examples of common integration
patterns and SHALL exercise them in its own test suite. (FR-DEV-003)

#### Scenario: Running the basic application example

- **WHEN** the shipped basic application is started through the test client and `greeting.create` is called
- **THEN** it answers with the documented greeting for the supplied or default name

#### Scenario: Running the repository example

- **WHEN** the shipped repository example adds items and lists them
- **THEN** the items are stored and returned through the managed SQLite connector

### Requirement: Agent-friendly structured reports

Implementation, verification, and migration reports SHALL expose stable,
versioned, machine-readable context for coding agents: rule identifiers,
evidence locations, remediation, and migration tasks with verification and
rollback guidance; implementation and migration reports SHALL also identify the
inspected source. (FR-DEV-005)

#### Scenario: An agent reads a verification report

- **WHEN** a verification report is produced
- **THEN** every check carries its stable rule identifier, status, evidence, and remediation, and the report carries a schema version

#### Scenario: An agent reads a migration report

- **WHEN** a migration report is produced
- **THEN** each task carries an identifier, phase, status, verification, and rollback guidance, and recorded statuses appear in the summary

#### Scenario: Reports remain machine-readable

- **WHEN** a report is rendered as JSON
- **THEN** it parses back to the same structured report without loss
