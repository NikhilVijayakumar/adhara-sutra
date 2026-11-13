## ADDED Requirements

### Requirement: Consistent developer commands

The framework SHALL provide a consistent noninteractive developer CLI for
creating, running, inspecting, verifying, migrating, diagnosing, reporting, and
version reporting. (FR-DEV-001)

#### Scenario: Discovering the commands

- **WHEN** the developer runs the command with no subcommand
- **THEN** it lists the supported operations

#### Scenario: An invalid target

- **WHEN** a command is given a missing or non-directory target
- **THEN** it reports the problem and exits with the invalid-invocation status

#### Scenario: Emitting a report

- **WHEN** the report-producing commands run with `--json` or `--output FILE`
- **THEN** the report can be consumed by tooling or written to a file

### Requirement: Documentation entry points

The README SHALL link developers to the relevant framework documentation:
requirements, the architecture rule reference, the connector reference, the
protocol reference, OpenSpec changes, and the knowledge index, with resolvable
internal links. (FR-DEV-004)

#### Scenario: Locating capability documentation

- **WHEN** a developer opens the README
- **THEN** it links to the requirements, architecture rules, connector reference, protocol reference, OpenSpec changes, and knowledge index, and those targets exist

### Requirement: Connector reference

Every public connector category SHALL have documented configuration, lifecycle,
and error behavior. (FR-DOC-004)

#### Scenario: Reading connector documentation

- **WHEN** a developer consults the connector reference
- **THEN** it documents configuration, lifecycle, and error behavior for each public connector category (HTTP, external CLI, SQLite, filesystem and artifacts, and persistent state)

### Requirement: Traceable rules and protocol contracts

Important architecture rules and public protocol contracts SHALL be traceable to
documentation and verification evidence. (NFR-DOC-003)

#### Scenario: Tracing a rule or protocol contract

- **WHEN** a developer follows the architecture rule or protocol reference
- **THEN** it leads to the governing specification or requirements and to verification evidence (the rule catalogue tests or protocol behavior)

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
rollback guidance. Reports that analyze a project SHALL identify the inspected
source and its revision where supported, so stale analysis can be detected.
(FR-DEV-005, NFR-DOC-004, NFR-DOC-005, NFR-DOC-006)

#### Scenario: An agent reads a verification report

- **WHEN** a verification report is produced
- **THEN** every check carries its stable rule identifier, status, evidence, and remediation, and the report carries a schema version

#### Scenario: An agent reads a migration report

- **WHEN** a migration report is produced
- **THEN** each task carries an identifier, phase, status, verification, and rollback guidance, and recorded statuses appear in the summary

#### Scenario: A report identifies its source

- **WHEN** an implementation, verification, or migration report is produced for a project
- **THEN** it carries a schema version and identifies the analyzed source, including its revision and dirty state when supported

#### Scenario: Reports remain machine-readable

- **WHEN** a report is rendered as JSON
- **THEN** it parses back to the same structured report without loss
