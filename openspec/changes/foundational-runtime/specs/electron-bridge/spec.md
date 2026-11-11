## ADDED Requirements

### Requirement: Process communication boundary

Electron SHALL communicate with the Python application through the versioned CLI
protocol, with backend process ownership in the main process. (FR-ELC-001, FR-ELC-002, NFR-SEC-007)

#### Scenario: Backend does not become ready

- **WHEN** the managed backend fails during startup or protocol negotiation
- **THEN** the bridge reports startup failure and does not dispatch ordinary application requests to it

### Requirement: Report lost backend communication

The bridge SHALL detect and report unexpected process termination or communication
failure. (FR-ELC-007)

#### Scenario: Python exits during a request

- **WHEN** the backend exits unexpectedly while a request is pending
- **THEN** the bridge reports the communication failure rather than representing the request as successful
