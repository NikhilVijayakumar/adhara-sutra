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
