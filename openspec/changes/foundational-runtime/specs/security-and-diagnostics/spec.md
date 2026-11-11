## ADDED Requirements

### Requirement: Protect sensitive diagnostics

The framework SHALL protect sensitive values in logs, errors and diagnostics.
(FR-SEC-004, NFR-SEC-005, NFR-SEC-011)

#### Scenario: A request fails with credentials in its context

- **WHEN** the failure is reported through diagnostics
- **THEN** credentials are not exposed in the diagnostic output

### Requirement: Restrict Electron IPC

Electron integration SHALL expose controlled operations through the preload
boundary. (FR-SEC-007, NFR-SEC-007, NFR-SEC-008)

#### Scenario: Renderer requests an unexposed operation

- **WHEN** renderer code requests an operation outside the exposed interface
- **THEN** it cannot invoke that operation through the bridge

### Requirement: Standard error model

Framework and application errors SHALL be classified into a standard error
model and serialized through the protocol error envelope. (FR-ERR-001, FR-ERR-002, FR-ERR-004)

#### Scenario: Application handler raises a domain error

- **WHEN** an application handler raises an error during a request
- **THEN** the failure reaches the caller as a structured protocol error with a stable category and no internal traceback by default

### Requirement: Structured diagnostics with correlation

Logging SHALL be structured, correlated across requests and jobs, and kept
separate from protocol output. (FR-LOG-002, FR-LOG-003, FR-LOG-004)

#### Scenario: Concurrent requests log diagnostics

- **WHEN** two requests are processed concurrently and one logs a diagnostic
- **THEN** each log line identifies the request it belongs to and protocol messages on stdout remain unpolluted
