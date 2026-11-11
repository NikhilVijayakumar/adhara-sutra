## ADDED Requirements

### Requirement: Connector registration and lifecycle

The framework SHALL register and resolve connectors by stable identifier, validate
their configuration and dependencies, and provide lifecycle conventions. (FR-CON-001 through FR-CON-003)

#### Scenario: Duplicate connector identifier

- **WHEN** a connector is registered with an identifier already in use
- **THEN** the framework detects and reports the duplicate registration

### Requirement: Connector substitution

The framework SHALL support custom connectors and test doubles without changes to
core framework source. (FR-CON-007, FR-CON-008)

#### Scenario: Test with a connector double

- **WHEN** an application registers a compatible test double for a connector
- **THEN** the application can exercise its integration without the live external service

### Requirement: Safe process invocation

The external CLI connector SHALL use structured argument arrays, support timeout
and cancellation policies, and manage child process cleanup. (FR-EXT-003, FR-EXT-006, FR-EXT-007)

#### Scenario: Arguments contain shell metacharacters

- **WHEN** an application supplies an argument containing shell metacharacters
- **THEN** ordinary execution passes it as an argument without requiring shell interpretation
