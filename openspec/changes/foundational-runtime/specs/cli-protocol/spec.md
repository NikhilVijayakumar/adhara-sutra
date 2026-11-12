## ADDED Requirements

### Requirement: Action routing and validation

The CLI SHALL route registered actions by identifier and validate request envelopes
and action payloads before executing handlers. (FR-CLI-001, FR-CLI-002, FR-CLI-003, FR-SEC-001, NFR-SEC-003)

#### Scenario: Unknown action

- **WHEN** a request names an unregistered action
- **THEN** the CLI returns a standardized error without executing a handler

#### Scenario: Invalid envelope

- **WHEN** a request is not an object or its `kind`, `protocol_version`, `request_id`, `action`, or `payload` is missing or malformed
- **THEN** it is rejected with a structured protocol error and no handler runs

#### Scenario: Invalid payload

- **WHEN** a payload fails validation
- **THEN** the CLI returns a structured validation error identifying affected fields without exposing sensitive values
- **AND** the handler is not executed

### Requirement: Structured communication

The CLI SHALL use versioned request and response envelopes, with structured errors,
and keep diagnostics separate from protocol output. (FR-CLI-004, FR-ELC-001 through FR-ELC-004)

#### Scenario: Failed action

- **WHEN** an action fails and communication remains possible
- **THEN** the CLI returns a structured error response associated with the request
- **AND** diagnostic logs do not corrupt protocol output

### Requirement: Execution modes

The framework SHALL support one-shot and persistent CLI execution with consistent
action semantics. (FR-RUN-006, FR-CLI-005, FR-CLI-006)

#### Scenario: Persistent process handles multiple requests

- **WHEN** multiple requests are sent during one process lifetime
- **THEN** the process can handle them and correlate each response with its request

### Requirement: Events during request execution

The runtime SHALL let handlers emit structured events correlated with the active
request, distinguishable from terminal responses. (FR-CLI-006, FR-ELC-005)

#### Scenario: Handler reports progress

- **WHEN** a handler emits events while processing a request
- **THEN** each event carries the request's `request_id` and a `kind` of `event`
- **AND** the terminal response is still returned with a `kind` of `response`

#### Scenario: Malformed event

- **WHEN** a handler emits an event with an invalid name or non-serializable data
- **THEN** the event is not written
- **AND** the request fails with a structured error

### Requirement: Version information

The runtime SHALL expose application, framework, and supported protocol
versions. (FR-CLI-009)

#### Scenario: Version discovery

- **WHEN** a caller sends `system.hello`
- **THEN** the response reports the application name and version, the framework version, and the supported protocol versions

### Requirement: Framed protocol messages

The protocol SHALL use UTF-8 newline-delimited JSON and SHALL handle partial
stream reads and multiple messages in a read. (FR-ELC-002, FR-CLI-004)

#### Scenario: Request arrives in fragments

- **WHEN** a request is received across multiple stream reads
- **THEN** the receiver buffers it until a complete newline-terminated message is available before processing it

### Requirement: Version validation

The runtime SHALL validate the protocol version before dispatching an action.
Persistent sessions SHALL establish a compatible version before application
actions execute. (FR-ELC-001, FR-ELC-003)

#### Scenario: Unsupported version

- **WHEN** a request uses an unsupported protocol version
- **THEN** it is rejected and its action handler is not executed
