## ADDED Requirements

### Requirement: Application-defined state

The framework SHALL provide state facilities while applications define their own
state schemas and values. It SHALL distinguish request, session, process and
persistent state. (FR-STATE-001, FR-STATE-002, FR-STATE-003, FR-STATE-005)

#### Scenario: Request scope ends

- **WHEN** a request ends
- **THEN** its request-scoped state follows the documented cleanup policy

#### Scenario: Process and session state

- **WHEN** a handler stores a value in process or session state
- **THEN** process state is shared by every request in the process and session state only by requests in the same session

### Requirement: State change notifications

Applications SHALL be able to subscribe to top-level process-state changes for
one key or all keys and unsubscribe when no longer interested. (FR-STATE-004)

#### Scenario: A subscribed value changes

- **WHEN** a watched process-state key is set or deleted
- **THEN** synchronous listeners receive the operation, key, and value, and deletion includes the removed value

#### Scenario: A listener fails

- **WHEN** a listener raises an exception
- **THEN** the failure is logged and the state change still applies

#### Scenario: A nested value is edited in place

- **WHEN** a nested value is mutated without assigning its key again
- **THEN** no notification is emitted because only top-level mutations are observed

### Requirement: Persistent state scope

Applications SHALL be able to configure persistent state storage, and that state
SHALL be recoverable after restart subject to the selected persistence policy.
(FR-STATE-006, FR-STATE-008)

#### Scenario: Persistent state is restored

- **WHEN** an application configures a persistent state adapter and restarts
- **THEN** previously stored values are available and remain separate from process state

### Requirement: Concurrent state access

The framework SHALL provide one shared lock per application for compound
process-state updates and SHALL document that plain state mappings are otherwise
unsynchronized. (FR-STATE-007)

#### Scenario: Concurrent jobs update process state

- **WHEN** concurrent jobs read and write process state within `context.state_lock`
- **THEN** updates are serialized and no update is lost

#### Scenario: State is accessed without the lock

- **WHEN** an application performs compound updates without the lock while work runs concurrently
- **THEN** the application is responsible for its own synchronization

### Requirement: Concurrency safety and application isolation

Framework-managed metadata SHALL follow documented concurrency rules, and
independent applications SHALL NOT share state, configuration, jobs, or services.
(NFR-SCALE-002, NFR-SCALE-006)

#### Scenario: Independent applications run together

- **WHEN** two applications with their own state, configuration, and jobs are started in one process
- **THEN** each request observes only its own application's facilities and stopping one does not affect the other

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

### Requirement: Job lifecycle and bounded concurrency

Managed jobs SHALL follow the documented lifecycle states and bounded
concurrency rules. (FR-JOB-001, FR-JOB-003, FR-JOB-007, FR-JOB-008)

#### Scenario: Job completes with a result

- **WHEN** a registered job completes successfully
- **THEN** its execution record reports the succeeded state and the returned result

#### Scenario: Admission limit reached

- **WHEN** a job submission arrives while the configured concurrency or queue limit is reached
- **THEN** the framework rejects or queues the submission explicitly rather than accepting unbounded work

### Requirement: Interruption recovery

After an owning process exits unexpectedly, recovery SHALL distinguish
interruption from confirmed terminal outcomes before reporting job status.
(FR-JOB-011)

#### Scenario: Owner process crashes mid-execution

- **WHEN** the process owning a running job exits unexpectedly
- **THEN** the recovered job is marked interrupted rather than completed or failed without evidence

### Requirement: Bounded queues and backpressure

Job submission SHALL enforce configurable concurrency and queue limits, and
SHALL reject work beyond the queue with a structured retryable error instead of
unbounded growth. (NFR-RES-002, NFR-RES-005, NFR-SCALE-003, NFR-SCALE-004)

#### Scenario: The queue is full

- **WHEN** the configured queue capacity is reached
- **THEN** another submission fails with `JOB_QUEUE_FULL` in the lifecycle category and `retryable: true`

#### Scenario: Concurrency is limited

- **WHEN** more jobs are submitted than the configured concurrent limit
- **THEN** at most that many jobs run at once and the rest wait in the bounded queue

#### Scenario: Event output exceeds the consumer

- **WHEN** a handler emits events faster than the caller reads them
- **THEN** the synchronous stdout write provides backpressure instead of buffering without bound

### Requirement: Cancellation phases

Cancellation SHALL distinguish requested, completed, unsupported, and failed
outcomes and SHALL NOT report completion before the job is terminal.
(NFR-REL-006)

#### Scenario: Cancellation is requested

- **WHEN** `system.cancel` targets an active job
- **THEN** the response reports `cancellation: "requested"` or `"completed"` with the current job status

#### Scenario: Cancellation is unsupported

- **WHEN** `system.cancel` targets a terminal or unknown job
- **THEN** the response reports `cancelled: false` and `cancellation: "unsupported"`
