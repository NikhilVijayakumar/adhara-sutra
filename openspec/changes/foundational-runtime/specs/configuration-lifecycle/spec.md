## ADDED Requirements

### Requirement: Validate configuration before dependent startup

The runtime SHALL validate configuration before starting dependent components.
(FR-RUN-002, FR-CFG-003, FR-CFG-004)

#### Scenario: Higher-priority configuration is invalid

- **WHEN** an override contains an invalid value
- **THEN** startup reports validation failure instead of silently falling back to a lower-priority value
- **AND** dependent components do not start

### Requirement: Clean up failed initialization

The runtime SHALL clean up successfully initialized resources after a later
required initialization fails. (FR-RUN-002, NFR-REL-003)

#### Scenario: Cleanup also fails

- **WHEN** initialization fails and cleanup of an initialized resource also fails
- **THEN** diagnostics retain the original initialization failure and report the cleanup failure

### Requirement: Coordinate shutdown

The runtime SHALL stop admitting ordinary new work during shutdown and release
managed resources according to documented policies. (FR-RUN-003, FR-RUN-007)

#### Scenario: Shutdown is requested again

- **WHEN** shutdown is requested while shutdown is already in progress
- **THEN** the runtime does not perform unsafe duplicate cleanup

#### Scenario: The process is interrupted

- **WHEN** the process is interrupted while serving
- **THEN** managed resources are released and the process exits with the cancellation status
