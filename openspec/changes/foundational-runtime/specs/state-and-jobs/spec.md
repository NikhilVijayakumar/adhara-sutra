## ADDED Requirements

### Requirement: Application-defined state

The framework SHALL provide state facilities while applications define their own
state schemas and values. It SHALL distinguish request, session, process and
persistent state. (FR-STATE-001, FR-STATE-002, FR-STATE-005)

#### Scenario: Request scope ends

- **WHEN** a request ends
- **THEN** its request-scoped state follows the documented cleanup policy

### Requirement: Job execution ownership

Every managed job SHALL have an identifiable execution record and an execution
owner. Persisted metadata SHALL NOT imply that execution continues after the
owner exits unless a persistent execution mechanism exists. (FR-JOB-002, FR-JOB-009, FR-JOB-010)

#### Scenario: Job owner exits unexpectedly

- **WHEN** the process owning an active job exits without transferring execution to a persistent worker
- **THEN** the framework does not report the job as still executing solely because metadata exists

### Requirement: Job progress and cancellation

Jobs SHALL support structured progress, configured timeouts and cancellation
when the underlying operation supports it. (FR-JOB-004, FR-JOB-005, FR-JOB-006)

#### Scenario: Unsupported cancellation

- **WHEN** cancellation is requested for an operation that cannot be cancelled
- **THEN** the outcome reports that cancellation is unsupported rather than claiming that the operation stopped
