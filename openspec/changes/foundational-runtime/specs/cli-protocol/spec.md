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
action semantics. (FR-RUN-006, FR-CLI-005, FR-CLI-006, FR-CLI-010)

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

#### Scenario: Background job emits after submission

- **WHEN** a submitted job emits progress after its submission action has returned
- **THEN** the event carries its `job_id` and need not precede the submission response

#### Scenario: Caller asks for help

- **WHEN** a caller sends `system.help`
- **THEN** the response lists the registered actions with their descriptions and schema hooks
- **AND** an unknown action reports the available action names

#### Scenario: Requests arrive on standard input

- **WHEN** requests are provided as newline-delimited JSON on stdin
- **THEN** they are validated and dispatched without command-line arguments

#### Scenario: Malformed event

- **WHEN** a handler emits an event with an invalid name or non-serializable data
- **THEN** the event is not written
- **AND** the request fails with a structured error

### Requirement: Standard process exit codes

The CLI SHALL exit with consistent, documented codes that distinguish success,
invalid invocation, initialization or configuration failure, action failure,
timeouts, cancellation, dependency failure, protocol failure, and internal
failure. Persistent sessions SHALL keep a zero exit status when individual
actions fail. (FR-CLI-007, FR-RUN-006)

#### Scenario: A one-shot action succeeds

- **WHEN** a one-shot request produces a successful response
- **THEN** the process exits `0`

#### Scenario: A one-shot action times out

- **WHEN** a one-shot action fails because a connector operation timed out
- **THEN** the response reports the timeout error and the process exits `5`

#### Scenario: A persistent session action fails

- **WHEN** an action fails during a persistent session and the process later ends cleanly
- **THEN** the failure is reported in its response and the process exits `0`

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

The runtime SHALL validate the request's `protocol_version` against
`SUPPORTED_PROTOCOL_VERSIONS` before dispatching an action, and `system.hello`
SHALL advertise `PROTOCOL_VERSION` and every supported version. Persistent
sessions SHALL establish a compatible version before application actions
execute. (FR-ELC-001, FR-ELC-003, NFR-COMP-002)

#### Scenario: Unsupported version

- **WHEN** a request uses an unsupported protocol version
- **THEN** it is rejected and its action handler is not executed
