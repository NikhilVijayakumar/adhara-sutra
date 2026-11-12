## ADDED Requirements

### Requirement: Connector registration and lifecycle

The framework SHALL register and resolve connectors by stable identifier, validate
their configuration and dependencies, and provide lifecycle conventions. (FR-CON-001 through FR-CON-003)

#### Scenario: Connector configuration and dependencies

- **WHEN** a connector declares dependencies and reads configuration
- **THEN** its dependencies start first and it receives the validated merged configuration

#### Scenario: Duplicate connector identifier

- **WHEN** a connector is registered with an identifier already in use
- **THEN** the framework detects and reports the duplicate registration

### Requirement: Connector substitution

The framework SHALL support custom connectors and test doubles without changes to
core framework source. (FR-CON-007, FR-CON-008)

#### Scenario: Test with a connector double

- **WHEN** an application registers a compatible test double for a connector
- **THEN** the application can exercise its integration without the live external service

### Requirement: Connector isolation

Applications SHALL be able to use one connector without installing unrelated
integration dependencies. (FR-CON-005)

#### Scenario: Only one connector is installed

- **WHEN** an application installs a single connector
- **THEN** the framework and the application remain usable without additional integration packages

### Requirement: Connector health and failure mapping

Connectors SHALL be able to expose health information and SHALL translate
failures into a consistent framework error category. (FR-CON-004, FR-CON-006, NFR-OBS-004)

#### Scenario: A connector is unavailable

- **WHEN** a handler raises a connector failure
- **THEN** the response reports the connector category and retryability, and one-shot execution exits with the dependency-unavailable status

#### Scenario: Health is requested

- **WHEN** a caller sends `system.health` after startup
- **THEN** each service with a health check reports its availability and the overall status reflects them

### Requirement: Safe process invocation

The external CLI connector SHALL use structured argument arrays, support timeout
and cancellation policies, and manage child process cleanup. (FR-EXT-003, FR-EXT-006, FR-EXT-007)

#### Scenario: Arguments contain shell metacharacters

- **WHEN** an application supplies an argument containing shell metacharacters
- **THEN** ordinary execution passes it as an argument without requiring shell interpretation
