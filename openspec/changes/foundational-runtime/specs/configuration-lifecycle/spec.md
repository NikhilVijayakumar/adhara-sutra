## ADDED Requirements

### Requirement: Validate configuration before dependent startup

The runtime SHALL validate configuration before starting dependent components.
(FR-RUN-002, FR-CFG-003, FR-CFG-004, FR-CFG-008)

#### Scenario: Higher-priority configuration is invalid

- **WHEN** an override contains an invalid value
- **THEN** startup reports validation failure instead of silently falling back to a lower-priority value
- **AND** dependent components do not start

### Requirement: Deterministic configuration sources

The runtime SHALL merge documented configuration sources in a deterministic
precedence before validation. (FR-CFG-002, FR-CFG-004, FR-CFG-006, FR-CFG-007)

#### Scenario: Sources overlap

- **WHEN** defaults, a config file, environment values, and runtime overrides all define a key
- **THEN** the highest-priority source wins, in the order overrides, environment, file, defaults

#### Scenario: A higher-priority source is invalid

- **WHEN** the config file is missing, unreadable, or not a JSON object
- **THEN** startup fails with an actionable error naming the file and no service starts

### Requirement: Clean up failed initialization

The runtime SHALL clean up successfully initialized resources after a later
required initialization fails. (FR-RUN-002, NFR-REL-003)

#### Scenario: Cleanup also fails

- **WHEN** initialization fails and cleanup of an initialized resource also fails
- **THEN** diagnostics retain the original initialization failure and report the cleanup failure

### Requirement: Coordinate shutdown

The runtime SHALL stop admitting ordinary new work during shutdown and release
managed resources according to documented policies. (FR-RUN-003, FR-RUN-007, NFR-REL-007)

#### Scenario: Shutdown is requested again

- **WHEN** shutdown is requested while shutdown is already in progress
- **THEN** the runtime does not perform unsafe duplicate cleanup
- **AND** repeating shutdown after it completes leaves managed resources in their released state

#### Scenario: Shutdown races active work

- **WHEN** shutdown starts while background jobs and managed subprocesses are running
- **THEN** the jobs are cancelled and reported as cancelled
- **AND** the subprocesses are terminated and their release runs once

#### Scenario: Shutdown fails

- **WHEN** releasing a managed resource raises during shutdown
- **THEN** the failure is raised to the caller and the runtime is marked failed
- **AND** a later shutdown request does not retry unsafe cleanup

#### Scenario: The process is interrupted

- **WHEN** the process is interrupted while serving
- **THEN** managed resources are released and the process exits with the cancellation status
