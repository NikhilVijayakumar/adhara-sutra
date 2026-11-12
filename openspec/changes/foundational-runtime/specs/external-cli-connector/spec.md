## ADDED Requirements

### Requirement: Safe external invocation

The framework SHALL execute external CLI programs without a shell, pass
structured argument arrays, and locate executables through the process `PATH` or
a configured search path. (FR-EXT-001, FR-EXT-002, FR-EXT-003)

#### Scenario: Arguments containing spaces

- **WHEN** a handler passes an argument that contains spaces
- **THEN** the child receives it as one argument and no shell interprets it

#### Scenario: A missing executable

- **WHEN** the configured executable cannot be found at startup
- **THEN** startup fails with a non-retryable connector error

### Requirement: Output capture and streaming

The connector SHALL capture stdout, stderr, and the exit status, and SHALL deliver
output incrementally while the process runs. (FR-EXT-004, FR-EXT-005)

#### Scenario: Streaming progress

- **WHEN** a long-running command writes lines
- **THEN** an output callback receives each line before the process exits, and the final result still contains the complete output

### Requirement: Timeouts and cancellation

The connector SHALL support timeouts and cooperative cancellation of a running
command. (FR-EXT-006)

#### Scenario: A command exceeds its timeout

- **WHEN** a command runs longer than its timeout
- **THEN** the connector stops it and reports a retryable connector error with the timeout

#### Scenario: The owning request is cancelled

- **WHEN** the run is cancelled
- **THEN** the connector stops the process before the cancellation completes

### Requirement: Child-process cleanup

The connector SHALL define and apply a platform-specific cleanup policy for
running processes on timeout, cancellation, and application shutdown. (FR-EXT-007)

#### Scenario: Application shutdown

- **WHEN** the application stops while a command is still running
- **THEN** the connector terminates the command's process tree

### Requirement: Process limits and outcome uncertainty

External execution SHALL support an explicit concurrency limit and SHALL report
an unknown outcome when a terminated command may have produced side effects.
(NFR-RES-005, NFR-REL-010)

#### Scenario: Concurrency is limited

- **WHEN** an `ExternalCommand` is configured with `max_concurrent`
- **THEN** no more than that many runs execute at once on the instance

#### Scenario: A command is terminated after a timeout

- **WHEN** a command exceeds its timeout and is terminated
- **THEN** the connector error reports `details.outcome: "unknown"`
