## ADDED Requirements

### Requirement: Process communication boundary

Electron SHALL communicate with the Python application through the versioned CLI
protocol, with backend process ownership in the main process. (FR-ELC-001, FR-ELC-002, NFR-SEC-007)

#### Scenario: Backend does not become ready

- **WHEN** the managed backend fails during startup or protocol negotiation
- **THEN** the bridge reports startup failure and does not dispatch ordinary application requests to it

### Requirement: Report lost backend communication

The bridge SHALL detect and report unexpected process termination or communication
failure, and pending requests SHALL receive explicit failure outcomes.
(FR-ELC-007, NFR-REL-005)

#### Scenario: Python exits during a request

- **WHEN** the backend exits unexpectedly while a request is pending
- **THEN** the bridge reports the communication failure rather than representing the request as successful

### Requirement: Events, correlation, and ordering

The bridge SHALL deliver structured events and correlate messages with requests
and jobs. (FR-ELC-005, FR-ELC-008)

#### Scenario: Distinguishing events from results

- **WHEN** a request emits events before returning
- **THEN** the bridge delivers the events in order before the terminal response, and both carry the message `kind`

#### Scenario: Correlating job events

- **WHEN** a job emits progress
- **THEN** the event carries the job identifier so the frontend can associate it with the submission
- **AND** it may arrive after the submission response

### Requirement: Cancellation

The bridge SHALL request cancellation of supported operations and report an
explicit outcome. (FR-ELC-006)

#### Scenario: Cancelling a job

- **WHEN** the frontend requests cancellation of a managed job
- **THEN** the bridge reports whether cancellation was accepted and the job's current status
- **AND** an accepted cancellation does not by itself claim that an external dependency stopped

#### Scenario: Cancellation is unsupported

- **WHEN** cancellation is requested for an operation that cannot be interrupted
- **THEN** the bridge reports that it was not accepted rather than claiming the operation stopped

### Requirement: Protocol compatibility

The bridge SHALL negotiate the protocol version during startup and refuse
incompatible backends. (FR-ELC-009)

#### Scenario: Unsupported protocol

- **WHEN** the backend does not advertise the bridge's protocol version
- **THEN** startup fails and no application requests are dispatched

### Requirement: Reusable bridge package

The framework SHALL provide a reusable Electron main-process bridge that manages
the backend process, requests, responses, events, cancellation, timeouts, and
error propagation. (FR-ELC-010, FR-PKG-004)

#### Scenario: Installing the bridge

- **WHEN** an Electron application installs the bridge package
- **THEN** it can start the backend, send requests, receive events, cancel jobs, and close the backend without writing protocol code

#### Scenario: Testing the bridge against a Python fixture

- **WHEN** the shared bridge integration tests run
- **THEN** they drive a representative Python runtime fixture through start, request, help, error propagation, and close (FR-TEST-009)

### Requirement: Electron security boundary

The bridge SHALL prevent renderer-provided input from selecting the executable,
arguments, or shell command. (FR-ELC-011)

#### Scenario: Renderer input

- **WHEN** a renderer supplies a request
- **THEN** the input can only become an action name and payload for the fixed backend command
