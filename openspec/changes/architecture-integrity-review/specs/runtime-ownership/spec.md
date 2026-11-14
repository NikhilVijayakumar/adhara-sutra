## ADDED Requirements

### Requirement: Explicit persistence configuration

Bootstrap SHALL reject unresolved or malformed explicitly configured job stores
and recovery without a store, while preserving the no-store/no-recovery default.
Initialized resources SHALL receive cleanup attempts on bootstrap failure.
(FR-CFG-003, FR-RUN-002, FR-JOB-009, FR-JOB-011)

#### Scenario: Named store service is missing

- **WHEN** job_store names an unregistered service
- **THEN** startup fails with INVALID_JOB_STORE rather than silently disabling persistence

### Requirement: Admission has an execution owner

Rejected job admission SHALL return no accepted ID and leave no local queued
record/task. Failure after an initial durable save SHALL be reported conservatively;
no cross-store-and-event-loop atomicity is promised. (FR-JOB-002, FR-JOB-003, FR-JOB-009, FR-JOB-010)

#### Scenario: Initial store write fails

- **WHEN** saving the queued snapshot fails during submission
- **THEN** no local record consumes queue capacity and no handler is scheduled

#### Scenario: Scheduling fails after the queued snapshot is saved

- **WHEN** task creation fails after the initial durable write
- **THEN** the unscheduled coroutine is closed and a failed admission snapshot is attempted
- **AND** if that save also fails, recovery marks any remaining queued snapshot interrupted

### Requirement: Shared session scope

An action and jobs submitted through its context SHALL receive the identical
session mapping, including when it is empty. Separate sessions SHALL not share
that scope implicitly. (FR-STATE-003, FR-STATE-005)

#### Scenario: Job updates an initially empty session

- **WHEN** a submitted job writes a session value
- **THEN** later actions in that session observe it

#### Scenario: Omitted session scope

- **WHEN** independent dispatch calls omit session state and submit jobs
- **THEN** each action and its job share a fresh mapping isolated from the other call

### Requirement: Inspectable terminal job outcome

Jobs SHALL validate JSON-compatible results before success, finalize once, and
release waiters despite terminal persistence failure. Status SHALL distinguish
execution outcome from local persistence diagnostic status. (FR-JOB-008, FR-JOB-009,
FR-JOB-011)

#### Scenario: Result cannot be serialized

- **WHEN** a job returns a non-JSON object or non-finite number
- **THEN** its state is failed with JOB_OUTPUT_INVALID instead of succeeded

#### Scenario: Terminal snapshot cannot be saved

- **WHEN** execution succeeds but its terminal save fails
- **THEN** local status preserves the execution outcome and exposes persistence failure
- **AND** waiters finish without a claim that recovery can read the unsaved result

#### Scenario: Running-state snapshot cannot be saved

- **WHEN** saving the running state fails
- **THEN** the handler is not invoked and the job reports JOB_PERSISTENCE_FAILED

#### Scenario: Queued job is cancelled before its task starts

- **WHEN** cancellation is requested before execution begins
- **THEN** the job is finalized once and its waiters are released even if persistence fails

### Requirement: Cooperative execution and control

Persistent requests SHALL remain sequential; long work SHOULD return a background
job identifier promptly. Existing synchronous job handlers SHALL retain callable
compatibility with a registration warning explaining inline execution limits.
Timeout/cancellation guarantees SHALL be described as cooperative. (FR-CLI-006,
FR-JOB-001, FR-JOB-005, FR-JOB-006, FR-ELC-006)

#### Scenario: Async job waits for external I/O

- **WHEN** a managed async job yields while waiting
- **THEN** short health/status/cancel requests can be processed

#### Scenario: Synchronous handler is registered

- **WHEN** a synchronous callable is registered as a job handler
- **THEN** registration warns about inline execution and its timeout limitation while preserving callable behavior

### Requirement: Standard job status and honest caller timeout

system.jobs.get SHALL accept a nonempty job_id and return {job_id, status}, with
null status for unknown jobs. Business submission/listing SHALL remain app-owned.
Bridge timeout SHALL report unknown outcome and no cancellation request; it SHALL
NOT replay side effects automatically. (FR-JOB-008, FR-ELC-006, FR-ELC-007, FR-ELC-008)

#### Scenario: Caller times out while backend work continues

- **WHEN** a bridge request exceeds the caller's wait timeout
- **THEN** BRIDGE_TIMEOUT details identify an unknown outcome and cancellation_requested false
- **AND** no backend cancellation or automatic retry is implied

#### Scenario: Timed-out request finishes later

- **WHEN** a bridge request times out and the backend later completes it
- **THEN** timeout details report an unknown outcome and no cancellation request
- **AND** the late response is reported as an uncorrelated protocol error

#### Scenario: Read a managed job through the bridge

- **WHEN** the Node helper requests an existing job ID
- **THEN** it returns the same status snapshot as system.jobs.get
- **AND** an unknown ID returns a null status without exposing generic submission or listing

### Requirement: Cleanup ownership survives job shutdown failure

Shutdown SHALL close job admission and attempt service cleanup after job shutdown
failure, timeout, or cancellation using the remaining cooperative total budget.
Both ordinary phase failures SHALL remain inspectable. (FR-RUN-003, FR-RUN-007,
FR-CON-002)

#### Scenario: Job shutdown raises

- **WHEN** job shutdown fails
- **THEN** registered service cleanup is still attempted before published services are discarded

#### Scenario: Job shutdown and service cleanup both fail

- **WHEN** job shutdown and service cleanup both raise ordinary errors
- **THEN** both errors are retained and the application enters failed state

#### Scenario: Shutdown begins with a retained job facade

- **WHEN** an existing job facade submits work after shutdown begins
- **THEN** admission fails without saving or scheduling the job
