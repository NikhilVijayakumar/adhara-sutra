## ADDED Requirements

### Requirement: Action allowlisting

The router SHALL execute only actions registered with the application and SHALL
report unknown actions without invoking a handler. (FR-SEC-002, NFR-SEC-002)

#### Scenario: An unregistered action is requested

- **WHEN** a request names an action that was not registered
- **THEN** the response is an `ACTION_NOT_FOUND` error listing the available actions and no handler runs

### Requirement: Safe process execution

External command execution SHALL keep the executable and its arguments separate,
SHALL NOT invoke a shell, and SHALL reject a command string or non-string
arguments. (FR-SEC-003, NFR-SEC-001)

#### Scenario: An argument contains shell syntax

- **WHEN** an argument contains shell metacharacters
- **THEN** it is passed to the program verbatim and no shell interprets it

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

#### Scenario: Shutdown fails while another error is propagating

- **WHEN** a request fails and resource cleanup also fails
- **THEN** the original failure propagates and the cleanup failure is reported in diagnostics

#### Scenario: Errors are classified by kind

- **WHEN** an error is returned for a protocol, validation, action, lifecycle, or internal failure
- **THEN** its `category` identifies the failure kind and stays stable for that error code across requests

### Requirement: Structured diagnostics with correlation

Logging SHALL be structured, correlated across requests and jobs, and kept
separate from protocol output. (FR-LOG-001, FR-LOG-002, FR-LOG-003, FR-LOG-004, FR-LOG-005)

#### Scenario: Concurrent requests log diagnostics

- **WHEN** two requests are processed concurrently and one logs a diagnostic
- **THEN** each log line identifies the request it belongs to and protocol messages on stdout remain unpolluted

#### Scenario: A handler logs during a request

- **WHEN** an application handler writes a diagnostic through standard logging
- **THEN** the record identifies the request's `request_id` and `action`, and stdout carries only protocol messages

#### Scenario: A diagnostic is logged outside a request

- **WHEN** the runtime logs while no request is active
- **THEN** the record's request correlation fields are empty

#### Scenario: Log verbosity is configured

- **WHEN** the environment sets `ADHARA_LOG_LEVEL` or the application configures a level
- **THEN** records below that level are suppressed and protocol output is unchanged
