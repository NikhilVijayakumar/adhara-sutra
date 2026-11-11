# AdharaSutra — Job and Process Management Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/job-and-process-management.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Detailed Runtime Infrastructure Architecture  
**Architecture Style:** Explicit Execution Ownership, Managed Jobs, Capability-Based Executors  
**Primary Language:** Python 3.12+

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`
- `docs/design/electron-integration.md`
- `docs/design/connector-framework.md`
- `docs/design/state-management.md`

---

# 1. Purpose

This document defines the architecture for managing long-running application work and operating-system processes within AdharaSutra.

The framework shall provide reusable facilities for:

1. Defining and registering jobs.
2. Submitting and scheduling execution.
3. Tracking execution lifecycle.
4. Selecting execution strategies.
5. Managing concurrency and resource limits.
6. Executing asynchronous and synchronous workloads.
7. Executing external CLI programs.
8. Reporting progress.
9. Handling cancellation.
10. Enforcing execution deadlines.
11. Managing job results and artifacts.
12. Persisting job metadata where configured.
13. Recovering from interrupted execution.
14. Managing subprocess lifecycle.
15. Coordinating application shutdown.
16. Publishing events to Electron.
17. Supporting architecture verification.
18. Migrating existing job and process implementations.

The design must remain independent of application-specific processing algorithms.

## 1.1 Central Principle

**Every running operation must have a defined execution owner, and every managed subprocess must have a defined lifecycle owner.**

A job record does not imply that a job is running.

A persisted job record does not imply that execution survives process termination.

A cancellation acknowledgment does not prove that execution has stopped.

A process exit does not necessarily prove that an external operation completed successfully.

## 1.2 Distinguishing Jobs from Processes

A **job** represents a managed unit of work with a lifecycle, status, cancellation policy, and result.

A **process** represents an operating-system execution resource.

A job may execute without creating a subprocess.

A subprocess may be created for a short application operation without requiring a persistent job record.

One job may execute one or more processes sequentially.

The framework must not treat these concepts as interchangeable.

---

# 2. Scope

## 2.1 In Scope

- Job definitions and registration.
- Job scheduling and admission control.
- Execution strategies.
- Async task execution.
- Blocking workload execution.
- External process management.
- Execution identifiers and ownership.
- Job lifecycle and transition validation.
- Process lifecycle tracking.
- Progress reporting.
- Cancellation coordination.
- Timeout and deadline enforcement.
- Concurrency limits.
- Job result handling.
- Artifact ownership.
- Job metadata persistence.
- Recovery policies.
- Runtime shutdown integration.
- Electron event integration.
- Diagnostics and observability.
- Testing.
- Architecture verification.
- Incremental migration.

## 2.2 Out of Scope

The initial architecture does not require:

- A distributed job queue.
- A cloud task orchestration service.
- Kubernetes job management.
- Distributed scheduling.
- GPU resource allocation.
- Automatic workload migration between computers.
- Distributed consensus.
- Exactly-once business execution.
- Durable workers for every application.
- Automatic recovery of arbitrary interrupted Python functions.
- Direct Electron management of Python worker subprocesses.
- Reimplementation of external tools such as audio.cpp.
- A general-purpose workflow orchestration platform.

These may be considered as future extensions when justified by application requirements.

---

# 3. Architectural Principles

## JPM-001 — Framework-Owned Execution Infrastructure

AdharaSutra shall own common job and process management infrastructure.

Applications shall define the work to be performed.

## JPM-002 — Explicit Execution Ownership

Every active job shall have an identifiable executor or worker responsible for its execution.

## JPM-003 — Explicit Process Ownership

Every framework-managed subprocess shall have an owner and documented termination policy.

## JPM-004 — Execution Strategy Independence

The public job lifecycle shall not depend on whether the work executes asynchronously, in a thread, or in a managed subprocess.

Execution guarantees may differ by strategy and must be reported accurately.

## JPM-005 — Accurate Lifecycle Reporting

Job status shall represent confirmed lifecycle transitions.

The framework must distinguish accepted, running, completed, failed, cancelled, and interrupted execution.

## JPM-006 — Cancellation Is Cooperative or Enforced

Cancellation shall follow the capabilities of the executor and underlying workload.

Cancellation requests shall not be reported as successful termination until termination is confirmed.

## JPM-007 — No Implicit Durability

In-process jobs shall not be represented as continuing after their runtime terminates.

## JPM-008 — Explicit Recovery

Recovery behavior shall be declared for jobs that retain metadata across application restarts.

## JPM-009 — Controlled Concurrency

The framework shall enforce applicable limits before starting work.

## JPM-010 — Bounded Resource Usage

Execution queues, processes, streams, and retained results shall have defined resource limits.

## JPM-011 — Application Business Independence

The framework shall not implement application-specific workflow semantics, domain retries, or processing algorithms.

## JPM-012 — Unified Event Reporting

Job progress and lifecycle transitions shall use AdharaSutra's event infrastructure and CLI protocol.

## JPM-013 — Process Connector Reuse

All framework-managed external executable operations shall use the common process execution infrastructure.

The Job Manager must not independently reimplement subprocess creation or termination.

## JPM-014 — Testability

Jobs and processes shall be testable through controlled executors, clocks, fixtures, and failure injection.

## JPM-015 — Incremental Adoption

Existing applications shall be able to adopt AdharaSutra job and process facilities without unnecessary rewrites of working business logic.

---

# 4. High-Level Architecture

## 4.1 Component Diagram

```text
┌─────────────────────────────────────────────────────┐
│                    ELECTRON                         │
│                                                     │
│ Renderer → Preload → Main → AdharaSutra Bridge       │
└────────────────────────┬────────────────────────────┘
                         │
                         │ CLI Protocol
                         ▼
┌─────────────────────────────────────────────────────┐
│                 ADHARASUTRA RUNTIME                 │
│                                                     │
│  CLI Action Router                                  │
│         │                                           │
│         ▼                                           │
│  Application Action / Use Case                      │
│         │                                           │
│         ▼                                           │
│  ┌───────────────────────────────────────────────┐  │
│  │                JOB MANAGER                    │  │
│  │                                               │  │
│  │ Registry | Scheduler | State Machine          │  │
│  │ Admission | Progress | Cancellation           │  │
│  │ Results  | Recovery  | Ownership              │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                           │
│                         ▼                           │
│  ┌───────────────────────────────────────────────┐  │
│  │              EXECUTOR INTERFACES              │  │
│  │                                               │  │
│  │ Async | Thread | Managed Process | Worker     │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                           │
│          ┌──────────────┼──────────────┐            │
│          ▼              ▼              ▼            │
│      Async Task      Thread       Process Runner    │
│                                        │            │
│                                        ▼            │
│                               OS Process Manager    │
│                                                     │
│  Supporting Services:                               │
│  State | Events | Configuration | Logging           │
│  Persistence Ports | Artifact Facilities            │
└────────────────────────┬────────────────────────────┘
                         │
                ┌────────┼────────┐
                ▼        ▼        ▼
           Python     audio.cpp   Other
           Services   Executable  Processes
```

## 4.2 Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Application action | Accept application operation and return execution acknowledgment or result |
| Application use case | Define business workflow |
| Job Manager | Own managed job lifecycle and scheduling |
| Executor | Run a unit of work using a supported execution strategy |
| Process Manager | Own subprocess creation, monitoring, and termination |
| State subsystem | Store scoped job metadata |
| Persistence adapter | Store durable metadata when configured |
| Event subsystem | Publish execution lifecycle and progress |
| CLI protocol | Deliver structured messages to clients |
| Electron bridge | Submit work and observe job status |

## 4.3 Execution Boundary

The framework must distinguish three levels of execution:

1. **Request execution:** An action executes within an active CLI request.
2. **Managed job execution:** Work continues under the Job Manager after a submission request has completed.
3. **Durable worker execution:** Work continues under an independently managed execution owner that can survive or be restarted independently of the CLI session.

These models shall not be conflated.

---

# 5. Proposed Module Structure

```text
src/adharasutra/
│
├── jobs/
│   ├── __init__.py
│   ├── contracts.py
│   ├── definitions.py
│   ├── registry.py
│   ├── manager.py
│   ├── scheduler.py
│   ├── admission.py
│   ├── lifecycle.py
│   ├── context.py
│   ├── progress.py
│   ├── cancellation.py
│   ├── deadlines.py
│   ├── results.py
│   ├── errors.py
│   │
│   ├── executors/
│   │   ├── contracts.py
│   │   ├── async_executor.py
│   │   ├── thread_executor.py
│   │   └── process_executor.py
│   │
│   ├── persistence/
│   │   ├── ports.py
│   │   ├── records.py
│   │   └── recovery.py
│   │
│   └── policies/
│       ├── concurrency.py
│       ├── retention.py
│       └── shutdown.py
│
├── connectors/
│   └── process/
│       ├── contracts.py
│       ├── runner.py
│       ├── executable.py
│       ├── arguments.py
│       ├── environment.py
│       ├── streams.py
│       ├── termination.py
│       └── platform/
│           ├── windows.py
│           ├── linux.py
│           └── macos.py
│
└── events/
    └── ...
```

The file structure is provisional.

The important boundaries are:

- Job orchestration remains in `jobs`.
- Generic subprocess infrastructure remains in `connectors.process`.
- State and persistence remain separate from execution.
- Electron communication remains outside both modules.
- Application business handlers remain in consuming applications.

---

# 6. Job Definition Architecture

## 6.1 Job Definition

A job definition describes a type of work an application can execute.

Its metadata should include:

- Job type identifier.
- Description.
- Input schema.
- Result schema.
- Execution strategy.
- Required capabilities.
- Concurrency policy.
- Timeout policy.
- Cancellation capability.
- Persistence policy.
- Recovery policy.
- Retention policy.
- Optional resource classification.

## 6.2 Job Identifiers

Every job execution receives a unique `job_id`.

The identifier must distinguish execution instances even when they use the same job definition.

A job identifier is not an authorization token.

## 6.3 Job Type Identifier

Job types should use namespaced identifiers.

Examples:

```text
audio.generate
audio.separate
image.generate
model.infer
project.export
document.process
```

The application owns job type names and meaning.

## 6.4 Registration

Conceptual registration:

```python
app.register_job(
    name="audio.generate",
    handler=GenerateAudioJob,
    executor="async",
)
```

This is illustrative, not an approved public API.

## 6.5 Validation

The Job Registry shall validate:

- Job identifier format.
- Duplicate definitions.
- Supported execution strategy.
- Required dependencies.
- Configuration validity.
- Persistence compatibility.
- Cancellation capability.
- Recovery policy compatibility.

## 6.6 Business Ownership

The framework shall not determine the business meaning of:

- Audio generation.
- Image generation.
- Model inference.
- Project export.
- Other application-specific jobs.

Those remain application-defined operations.

---

# 7. Job Submission Architecture

## 7.1 Submission Process

```text
Application Action
        │
        ▼
Validate Job Definition
        │
        ▼
Validate Job Input
        │
        ▼
Check Admission Policy
        │
        ▼
Allocate Job Identifier
        │
        ▼
Create Job Metadata
        │
        ▼
Queue or Start Execution
        │
        ▼
Return Job Acknowledgment
```

## 7.2 Job Submission Semantics

The system must distinguish:

- Rejected submission.
- Accepted but pending.
- Accepted and running.
- Failed before acceptance.

The framework must not return an accepted job identifier if the job was not successfully registered with its intended execution owner.

## 7.3 Admission Control

Job submission may be rejected because of:

- Invalid input.
- Missing dependencies.
- Executor unavailable.
- Concurrency limits.
- Queue capacity.
- Insufficient configured resources.
- Runtime shutdown.
- Unsupported execution policy.

## 7.4 Queue Capacity

The Job Manager shall support bounded pending-job capacity.

Queue overflow behavior must be explicit.

## 7.5 Duplicate Submission

Each submission normally creates a distinct execution.

The framework does not guarantee exactly-once business execution.

Applications requiring duplicate prevention must use an explicitly supported idempotency or deduplication policy.

---

# 8. Job Lifecycle

## 8.1 Proposed State Machine

```text
                 ┌───────────┐
                 │  CREATED  │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │  PENDING  │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │  RUNNING  │
                 └─────┬─────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     COMPLETED       FAILED      CANCELLED
```

An interruption may occur when the execution owner disappears or becomes unable to confirm the result.

The internal state machine may additionally contain:

- Cancellation requested.
- Starting.
- Recovering.

These states are not necessarily all exposed through the public protocol.

## 8.2 Public Job States

| State | Meaning |
|---|---|
| `pending` | Accepted and awaiting execution |
| `running` | Execution owner confirms work is running |
| `completed` | Successful completion confirmed |
| `failed` | Execution failure confirmed |
| `cancelled` | Cancellation completed |
| `interrupted` | Execution stopped or ownership was lost without confirmed success |

## 8.3 Terminal States

For an execution attempt, terminal outcomes include:

- Completed.
- Failed.
- Cancelled.
- Interrupted.

Retries or recovery must create an explicitly tracked new attempt rather than silently rewriting a prior terminal attempt's history.

## 8.4 State Transition Validation

Invalid lifecycle transitions shall be rejected.

Examples:

- A completed job cannot become running again without a new execution attempt.
- A failed job cannot be marked completed without verified subsequent execution.
- A cancelled job cannot continue publishing progress for the cancelled attempt.
- An interrupted job cannot be represented as successfully completed without appropriate evidence.

## 8.5 Job Attempt Identity

A job may have multiple execution attempts.

The framework should distinguish:

- Stable job identifier.
- Execution attempt identifier.
- Executor owner identifier.
- Attempt status.
- Attempt timestamps.

This is essential for recovery and retries.

---

# 9. Execution Strategies

## 9.1 Purpose

Execution strategies define how registered work is performed.

The framework should support different strategies through a common execution contract.

## 9.2 Execution Strategy Matrix

| Strategy | Best suited for | Survives runtime termination |
|---|---|---|
| Async task | Nonblocking I/O and async workflows | No |
| Managed thread | Blocking Python functions | No |
| Managed external process | External CLI tools | Not by default |
| Durable worker | Recoverable independently owned workloads | Only with explicit implementation |

## 9.3 Executor Contract

Conceptual interface:

```python
from typing import Protocol


class JobExecutor(Protocol):
    async def execute(
        self,
        job,
        context,
    ):
        ...

    async def request_cancel(
        self,
        execution_id: str,
    ):
        ...
```

The final interface must also define execution ownership, status observation, result handling, and termination guarantees.

## 9.4 Executor Selection

Executor selection should be based on:

- Workload characteristics.
- Required isolation.
- Blocking behavior.
- Cancellation capability.
- Resource requirements.
- Reliability requirements.

The framework must not assume that every Python function is safe to run directly inside the async event loop.

---

# 10. Asynchronous Job Execution

## 10.1 Purpose

The async executor handles cooperative asynchronous workloads.

Examples:

- HTTP requests.
- WebSocket processing.
- Async orchestration.
- Nonblocking filesystem or connector operations.

## 10.2 Execution Ownership

The active Python runtime owns the asynchronous task.

## 10.3 Cancellation

The executor may request cooperative cancellation.

The application handler and underlying dependencies must cooperate for timely termination.

## 10.4 Blocking Restrictions

CPU-heavy or blocking synchronous functions must not execute directly on the protocol event loop.

## 10.5 Failure Isolation

Expected exceptions in a job must be captured and classified.

A failed job should not automatically terminate unrelated requests or the entire Python runtime.

## 10.6 Shutdown

Active asynchronous jobs follow the configured shutdown policy.

---

# 11. Thread-Based Job Execution

## 11.1 Purpose

Thread execution supports synchronous Python operations that should not block the main async event loop.

## 11.2 Appropriate Workloads

Examples include:

- Blocking library calls.
- Some filesystem operations.
- Synchronous integrations.
- Blocking utilities that release the GIL or primarily wait on I/O.

## 11.3 CPU-Bound Limitations

Python threads do not universally provide parallel CPU execution for pure-Python CPU-heavy workloads.

The architecture shall not promise thread-based CPU parallelism without considering interpreter behavior and the chosen workload.

## 11.4 Cancellation Limitation

The framework cannot generally forcefully terminate an arbitrary running Python thread safely.

Cancellation may be cooperative.

If a thread cannot be stopped, the framework must report the actual execution state rather than falsely claiming termination.

## 11.5 Executor Capacity

Thread pools must have configurable capacity.

Unbounded thread creation is prohibited.

## 11.6 Isolation

A thread does not provide the isolation guarantees of a separate operating-system process.

Workloads requiring stronger failure isolation may require a worker-process strategy.

---

# 12. External Process Execution

## 12.1 Purpose

The external process executor integrates the Job Manager with the framework's generic process connector.

It is particularly important for audio.cpp-style workloads.

## 12.2 Responsibility Boundary

**Job Manager owns:**

- Job identity.
- Scheduling.
- Job state.
- Progress.
- Cancellation coordination.
- Result metadata.
- Recovery policy.

**Process Connector owns:**

- Executable resolution.
- Process creation.
- Arguments.
- Environment.
- stdin/stdout/stderr.
- Process status.
- Timeout mechanisms.
- Termination.
- Process cleanup.

**Application adapter owns:**

- Executable-specific arguments.
- Output interpretation.
- Tool-specific progress mapping.
- Application-specific errors.
- Domain result processing.

## 12.3 Execution Flow

```text
Application Audio Job
        │
        ▼
Job Manager
        │
        ▼
External Process Executor
        │
        ▼
Process Connector
        │
        ▼
Operating System
        │
        ▼
audio.cpp Executable
        │
        ├── stdout
        ├── stderr
        ├── Exit Status
        └── Output Artifacts
                │
                ▼
        Application Adapter
                │
                ▼
         Job Result / Error
```

## 12.4 No Duplicate Process Engine

The Job Manager shall not implement its own separate subprocess launcher.

All managed external process execution must use the established framework process facilities.

---

# 13. Process Manager Architecture

## 13.1 Purpose

The Process Manager manages operating-system subprocess resources.

## 13.2 Responsibilities

- Executable discovery.
- Execution configuration.
- Process spawning.
- Process identity.
- stdout/stderr capture.
- stdin communication.
- Exit monitoring.
- Timeout enforcement.
- Termination.
- Process-tree cleanup.
- Ownership tracking.
- Diagnostics.

## 13.3 Process Identifier

A process record should identify:

- Managed execution ID.
- Operating-system PID where available.
- Executable identity.
- Owning request or job.
- Start timestamp.
- Exit timestamp.
- Exit status.
- Termination reason.

The OS PID alone is not sufficient as a durable process identity because PIDs may be reused.

## 13.4 Process Ownership

Possible owners:

- One-shot action.
- Persistent runtime service.
- Managed job.
- Explicitly configured external worker.

A process must not be implicitly detached simply because its parent request has completed.

## 13.5 Process Registration

A managed process should be registered with its owner before being treated as fully active.

Creation failure must not leave a falsely running record.

---

# 14. Process Lifecycle

## 14.1 Proposed States

```text
REGISTERED
     │
     ▼
STARTING
     │
     ▼
RUNNING
     │
     ├────────► EXITED
     │
     ├────────► TERMINATING
     │                 │
     │                 ▼
     │               EXITED
     │
     └────────► FAILED
```

A process exit may be successful or unsuccessful.

The process status must not be confused with its job's business result.

## 14.2 Exit Handling

The process connector must capture:

- Exit code when available.
- Termination signal where supported.
- Timeout outcome.
- Termination request status.
- Relevant output.
- Failure metadata.

## 14.3 Exit-Code Interpretation

The process connector reports technical exit information.

Application adapters interpret executable-specific exit codes.

For example, an external tool may return zero while producing an invalid output file.

The application adapter must validate required business outputs.

## 14.4 Unexpected Termination

Unexpected process exit should produce a classified execution failure unless application-specific semantics establish a different valid outcome.

## 14.5 Exit Cleanup

Exited processes must be reaped or otherwise finalized according to the platform's process-management semantics.

---

# 15. Process Execution Contract

## 15.1 Proposed Process Specification

A process execution specification should support:

- Executable path or registered executable identity.
- Arguments.
- Working directory.
- Environment.
- stdin policy.
- stdout policy.
- stderr policy.
- Timeout.
- Cancellation policy.
- Output limits.
- Process-tree ownership policy.
- Optional resource limits.

## 15.2 Conceptual Interface

```python
result = await process_runner.run(
    executable="audio-cli",
    args=[
        "--input", input_path,
        "--output", output_path,
    ],
    timeout_seconds=600,
)
```

This is illustrative pseudocode, not a finalized framework method or verified audio.cpp command.

## 15.3 Shell Execution

Shell execution shall be disabled by default.

Ordinary executable invocation shall use structured argument arrays.

## 15.4 Environment Policy

The framework should support controlled environment construction.

Applications must not log sensitive environment values indiscriminately.

## 15.5 Working Directory

Working directories must be validated against configured application permissions and deployment constraints.

## 15.6 Executable Discovery

Executable resolution must support:

- Explicit paths.
- Approved application tool directories.
- Packaged executable manifests.
- Controlled system lookup.

Renderer-provided executable paths must not be blindly trusted.

---

# 16. Process Output and Streaming

## 16.1 stdout and stderr

External subprocess stdout and stderr are distinct from AdharaSutra's own CLI protocol output.

The process connector captures subprocess output internally.

It must not forward arbitrary subprocess text directly to the Python runtime's protocol stdout.

## 16.2 Stream Architecture

```text
External Executable
      │
      ├── stdout ──► Process Stream Reader
      │
      └── stderr ──► Process Stream Reader
                             │
                             ▼
                      Output Adapter
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
          Progress Parser            Diagnostics
                │
                ▼
          Job Progress
                │
                ▼
          Framework Event
```

## 16.3 Deadlock Prevention

Both stdout and stderr must be drained appropriately to avoid blocking a subprocess when an operating-system pipe buffer fills.

## 16.4 Partial Output

The stream reader must handle output arriving in arbitrary byte chunks.

It must not assume one read equals one complete log line.

## 16.5 Character Encoding

Text decoding policy must be explicit.

Binary outputs should be handled separately from textual log streams.

## 16.6 Output Limits

Captured process output must have bounded memory usage.

Options may include:

- Ring buffers.
- Size-limited capture.
- Streaming to files.
- Incremental parsing.

## 16.7 Sensitive Output

Diagnostic retention and forwarding must support redaction and access restrictions.

---

# 17. Progress Reporting

## 17.1 Purpose

Jobs shall support meaningful progress reporting.

## 17.2 Progress Model

A progress update may contain:

- Job identifier.
- Attempt identifier.
- Stage.
- Percentage, if known.
- Completed units.
- Total units.
- Human-readable message.
- Timestamp.
- Optional application metadata.

## 17.3 Percentage Semantics

Percentage progress must be based on meaningful underlying measurements.

When completion percentage cannot be determined, the framework shall represent progress as indeterminate.

## 17.4 Progress Example

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": 45,
    "stage": "audio-generation",
    "message": "Generating audio segments"
  }
}
```

## 17.5 Application Progress Mapping

An application adapter may transform raw external progress into domain-specific progress.

For example:

```text
audio.cpp Output
       │
       ▼
Audio Adapter Parser
       │
       ▼
Structured Progress
       │
       ▼
Job Manager
       │
       ▼
AdharaSutra Event
       │
       ▼
Electron
```

## 17.6 Event Frequency

The framework should support throttling or coalescing repetitive progress events.

## 17.7 Terminal Event Ordering

For one execution attempt, progress events must not be emitted after its confirmed terminal event.

## 17.8 Progress Persistence

Persisting every progress update is not required.

The framework may retain the latest progress snapshot and selected milestones according to job policy.

---

# 18. Job Status Queries

## 18.1 Purpose

Clients must be able to retrieve authoritative job status.

This is important when:

- Electron renderer reloads.
- Event subscriptions begin late.
- Progress events are missed.
- A job outlives its submission request.
- A process reconnects.
- Recovery is attempted.

## 18.2 Proposed Framework Actions

```text
system.jobs.get
system.jobs.list
```

These are proposed additions to the reserved action catalog in `cli-protocol.md`.

## 18.3 Status Response

Conceptual example:

```json
{
  "job_id": "job-123",
  "job_type": "audio.generate",
  "status": "running",
  "attempt": 1,
  "progress": {
    "percent": 45,
    "stage": "generating"
  },
  "execution_owner": {
    "type": "runtime",
    "status": "active"
  }
}
```

## 18.4 Query Authorization

Job status must not be exposed indiscriminately.

The runtime shall apply the relevant application and session access policies.

## 18.5 Status Freshness

Responses should distinguish cached metadata from actively confirmed execution status when that distinction matters.

---

# 19. Cancellation Architecture

## 19.1 Cancellation Model

Cancellation is a coordinated operation involving:

1. Caller.
2. Job Manager.
3. Executor.
4. Underlying task or process.
5. Optional external service.

## 19.2 Cancellation Sequence

```text
Electron
    │
    ▼
system.cancel
    │
    ▼
Job Manager
    │
    ▼
Record Cancellation Request
    │
    ▼
Executor Cancellation
    │
    ├── Async Task Cancellation
    ├── Cooperative Thread Cancellation
    ├── Process Termination
    └── Remote Service Cancellation
    │
    ▼
Confirm Actual Outcome
    │
    ▼
Update Job Status
    │
    ▼
Publish Terminal Event
```

## 19.3 Cancellation Acknowledgment

A successful cancellation-request response indicates only that the request was accepted for processing.

## 19.4 Confirmed Cancellation

The job enters `cancelled` only when the executor has confirmed the applicable cancellation condition.

## 19.5 Cancellation Failure

Possible outcomes:

- Cancellation unsupported.
- Job already completed.
- Job already failed.
- Target not found.
- Cancellation failed.
- Cancellation still pending.
- Execution outcome unknown.

## 19.6 Async Cancellation

Async tasks should use cooperative cancellation.

## 19.7 Thread Cancellation

Threads require cooperative cancellation unless the application can safely isolate execution elsewhere.

## 19.8 Process Cancellation

The process manager attempts graceful termination followed by configurable escalation.

## 19.9 Remote Service Cancellation

Cancelling a local HTTP request does not necessarily cancel remote work.

Service-specific adapters must implement supported remote cancellation operations.

## 19.10 Cancellation Races

The framework must define behavior when:

- A job completes during cancellation.
- Cancellation is submitted multiple times.
- The owner process exits during cancellation.
- A remote service accepts cancellation but completion remains uncertain.
- A terminal result arrives after cancellation was requested.

Confirmed terminal results must not be overwritten incorrectly.

---

# 20. Timeout and Deadline Management

## 20.1 Timeout Categories

The framework shall distinguish:

- Job queue-wait timeout.
- Job execution timeout.
- Executor startup timeout.
- External process timeout.
- Connector operation timeout.
- Cancellation grace period.
- Shutdown deadline.

## 20.2 Timeout Ownership

| Timeout | Owner |
|---|---|
| CLI request | CLI runtime / Electron bridge |
| Queue wait | Job Manager |
| Job deadline | Job Manager |
| Process execution | Process Connector |
| HTTP operation | HTTP Connector |
| Worker readiness | Executor |
| Shutdown | Application lifecycle |

## 20.3 Deadline Propagation

Where supported, a job execution deadline should constrain downstream operations.

The effective timeout should not exceed the remaining job execution time without an explicitly documented exception.

## 20.4 Timeout Outcome

A timeout may result in:

- Confirmed cancellation.
- Confirmed failure.
- Continuing execution.
- Unknown external outcome.

The framework must report the actual condition.

## 20.5 Retry After Timeout

Timeouts shall not automatically trigger retries of potentially non-idempotent operations.

---

# 21. Scheduling and Concurrency

## 21.1 Scheduler Responsibilities

The scheduler controls:

- Job admission.
- Pending queues.
- Execution ordering.
- Executor selection.
- Concurrency.
- Resource limits.
- Start eligibility.

## 21.2 Initial Scheduling Strategy

The proposed initial scheduler is an in-process scheduler with bounded queues and configurable concurrency.

A distributed scheduling service is not required.

## 21.3 Scheduling Policies

Possible policies:

- FIFO.
- Priority-aware scheduling.
- Per-job-type limits.
- Per-resource-class limits.

**Initial recommendation:** FIFO as the baseline, with controlled extensions for job-type limits and priority.

## 21.4 Concurrency Limits

Limits should be configurable at multiple scopes.

Examples:

```text
Application-wide active jobs
        │
        ├── Audio jobs
        ├── Image jobs
        ├── External process jobs
        └── Other jobs
```

## 21.5 Resource Classification

Applications may classify jobs according to resources such as:

- CPU-bound.
- I/O-bound.
- Memory-intensive.
- External-process.
- GPU-intensive.

The framework initially uses classifications for admission and concurrency policy rather than promising actual operating-system-level resource isolation.

## 21.6 Queue Fairness

Scheduling should avoid indefinite starvation under supported priority policies.

## 21.7 Admission Failure

If execution capacity is exhausted, the framework must either queue the job within capacity limits or reject it with an explicit outcome.

## 21.8 Backpressure

The Job Manager must not accept unlimited jobs into an unbounded memory queue.

---

# 22. Resource Management

## 22.1 Resource Ownership

Every job may own:

- Execution context.
- Cancellation token.
- Connector references.
- Temporary files.
- External processes.
- Intermediate artifacts.
- Event subscriptions.
- Result metadata.

## 22.2 Cleanup

The framework shall clean up resources when:

- Jobs complete.
- Jobs fail.
- Jobs are cancelled.
- Execution times out.
- A runtime shuts down.
- An owner becomes invalid.

## 22.3 Cleanup Ordering

Cleanup must respect resource dependencies.

A connector should not be closed while a job legitimately using it is still active unless shutdown policy requires termination.

## 22.4 Cleanup Failure

A job's business outcome and cleanup outcome may differ.

For example, processing may complete successfully while deletion of temporary files fails.

The framework should preserve the business result while recording a cleanup warning or failure according to policy.

## 22.5 Temporary Artifacts

Temporary artifacts must have explicit retention and cleanup ownership.

## 22.6 Resource Leaks

Runtime diagnostics should expose relevant indicators of leaked processes, jobs, handles, and subscriptions.

---

# 23. Job Result Architecture

## 23.1 Result Categories

A job may produce:

- Structured JSON-compatible data.
- Managed file artifacts.
- Domain-defined result references.
- No result.
- Structured failure information.

## 23.2 Result Ownership

The application owns result meaning.

The framework owns generic result storage and retrieval mechanisms where enabled.

## 23.3 Large Artifacts

Large binary outputs must not be embedded directly into the normal CLI protocol by default.

The framework should use managed artifact references.

## 23.4 Result Retention

Result retention must be configurable.

Potential policies:

- Until request completion.
- Until job cleanup.
- Fixed retention period.
- Persistent until application deletion.

## 23.5 Result Consistency

A job must not be marked completed before required output validation and result finalization succeed.

## 23.6 Partial Results

Applications may expose partial outputs where supported.

Partial outputs must be identified as incomplete and must not be confused with the final successful result.

---

# 24. Job Metadata Persistence

## 24.1 Purpose

Optional persistence allows job information to survive application restart.

## 24.2 Persistable Metadata

Potential fields:

- Job ID.
- Job type.
- Input reference.
- Current status.
- Attempt records.
- Execution owner.
- Progress snapshot.
- Result reference.
- Error category.
- Submission timestamp.
- Start timestamp.
- Completion timestamp.
- Recovery policy.

## 24.3 Persistence Abstraction

The Job Manager shall use a persistence port.

It must not depend directly on SQLite implementation details.

## 24.4 SQLite Adapter

SQLite is a proposed local persistence option.

The adapter must use AdharaSutra's SQLite connector infrastructure.

## 24.5 Metadata Versus Execution

Persisting metadata does not keep the job running.

The actual execution owner must be independently verified.

## 24.6 Persisted Inputs

Recovery-capable jobs must retain sufficient validated input information or references to reconstruct an execution attempt.

Sensitive inputs require appropriate protection.

## 24.7 Transaction Integrity

State transitions and persisted metadata must follow documented transaction and recovery semantics.

## 24.8 Atomicity Limitations

The framework must not promise an atomic transaction spanning:

- Job metadata.
- External CLI execution.
- Remote HTTP actions.
- Filesystem writes.

Applications may require idempotency or compensating recovery steps.

---

# 25. Crash Recovery Architecture

## 25.1 Recovery Principle

After a runtime crash, the framework must distinguish recorded job status from actual execution status.

## 25.2 Recovery Sequence

```text
Python Runtime Starts
        │
        ▼
Initialize Job Metadata Store
        │
        ▼
Load Nonterminal Job Records
        │
        ▼
Inspect Previous Ownership
        │
        ▼
Determine Recovery Eligibility
        │
        ├── Confirmed Live Worker
        │          │
        │          ▼
        │      Reassociate
        │
        ├── Safe Retry Allowed
        │          │
        │          ▼
        │      New Attempt
        │
        └── Outcome Unknown
                   │
                   ▼
             Mark Interrupted
                   │
                   ▼
             Publish Status
```

## 25.3 Recovery Policies

Proposed policies:

| Policy | Behavior |
|---|---|
| `none` | No automatic recovery |
| `mark_interrupted` | Record interruption |
| `retry_if_safe` | Retry only with approved idempotency guarantees |
| `manual` | Require explicit user/application action |
| `resume` | Resume only through an executor supporting verifiable continuation |

## 25.4 Orphaned Processes

If an external process remains alive after its owner disappears, recovery must not assume that matching an old PID is sufficient to reclaim it.

Process identity and ownership must be verified using platform-appropriate evidence.

## 25.5 Unknown Results

A process may finish work after the Python parent crashes.

The restarted runtime may be unable to determine whether output is complete.

The framework must retain an unknown or interrupted outcome until valid evidence establishes completion.

## 25.6 Retry Safety

Automatic retry must account for side effects and duplicate outputs.

## 25.7 Recovery Limitations

Arbitrary Python coroutine execution cannot be resumed at the exact interrupted instruction after process termination.

Resumption requires a specific checkpointing or recoverable-work contract.

---

# 26. Durable Worker Architecture

## 26.1 Purpose

Durable workers are a future-compatible extension for workloads requiring execution continuity independent of the Electron-controlled Python session.

## 26.2 Durable Execution Requirements

A genuine durable worker design requires:

- Independent worker lifecycle.
- Persistent job metadata.
- Persistent input references.
- Job claiming or leasing.
- Ownership validation.
- Heartbeats or equivalent liveness evidence.
- Restart or recovery policy.
- Safe retry semantics.
- Output recovery.
- Reconnection support.

## 26.3 Initial Scope

The first framework implementation should not require a separate durable worker service.

It should establish executor contracts compatible with later durable execution.

## 26.4 Correctness Principle

The framework shall not advertise durable job execution until an actual durable execution owner and tested recovery mechanism exist.

---

# 27. Application Shutdown Integration

## 27.1 Shutdown Responsibilities

The AdharaSutra lifecycle manager coordinates shutdown.

The Job Manager controls job shutdown behavior.

The Process Connector handles subprocess termination.

## 27.2 Shutdown Sequence

```text
Application Shutdown
        │
        ▼
Stop New Job Admission
        │
        ▼
Apply Job Shutdown Policy
        │
        ├── Finish
        ├── Cancel
        ├── Interrupt
        └── Transfer (if supported)
        │
        ▼
Wait Within Deadline
        │
        ▼
Escalate Where Permitted
        │
        ▼
Finalize Job Metadata
        │
        ▼
Release Process Resources
        │
        ▼
Close Connector Dependencies
        │
        ▼
Runtime Stops
```

## 27.3 Shutdown Policies

Potential policies:

- Wait for active jobs.
- Request cancellation.
- Cancel and enforce deadline.
- Mark remaining work interrupted.
- Transfer to an independently managed worker where supported.

## 27.4 Non-Cooperative Workloads

A non-cooperative workload may not stop immediately.

The framework must report that behavior accurately and apply only safe supported escalation methods.

## 27.5 Electron Shutdown

Electron main coordinates Python runtime shutdown through the shared bridge.

The Electron renderer does not directly terminate managed subprocesses.

---

# 28. Cross-Platform Process Management

## 28.1 Windows

The process implementation must account for:

- Windows executable resolution.
- Argument quoting.
- Process handles.
- Process groups.
- Graceful termination limitations.
- Forced termination.
- Child-process cleanup.
- Job Objects where appropriate.

## 28.2 Linux

The process implementation must account for:

- POSIX process groups and sessions.
- Signals.
- Process reaping.
- Permission boundaries.
- Descendant termination.
- Child-process cleanup.

## 28.3 macOS

The process implementation must account for:

- POSIX process behavior.
- Application bundle restrictions.
- Executable permissions.
- Process groups and signals.
- Packaged runtime paths.

## 28.4 Cross-Platform Contract

The framework shall expose consistent high-level execution outcomes.

It must not falsely claim that all platforms implement identical graceful termination semantics.

## 28.5 Testing

Process lifecycle and termination tests must execute on each supported platform before that platform is declared fully supported.

---

# 29. Security Architecture

## 29.1 Executable Allowlisting

Applications should register approved external executables.

Untrusted renderer input must not become an unrestricted executable path.

## 29.2 Argument Safety

The framework shall use structured argument sequences.

Shell invocation shall be disabled by default.

## 29.3 Environment Safety

Sensitive environment variables shall not be exposed in routine logs.

## 29.4 Working Directory Restrictions

Process execution must respect configured filesystem access boundaries.

## 29.5 Resource Exhaustion Protection

The framework shall enforce configurable queue, process, and concurrency limits.

## 29.6 Job Authorization

Clients must not be able to inspect, cancel, or retrieve unrelated jobs without authorization.

## 29.7 Result Exposure

Artifact references must follow approved access policies.

## 29.8 Sensitive Job Metadata

Persistent job metadata must not indiscriminately store credentials, secrets, or sensitive request bodies.

## 29.9 Process Output

Subprocess output is untrusted data.

It must not be treated as executable instructions by the framework.

---

# 30. Error Architecture

## 30.1 Job Errors

Proposed error identifiers:

```text
JOB_NOT_FOUND
JOB_ALREADY_TERMINAL
JOB_ADMISSION_REJECTED
JOB_QUEUE_FULL
JOB_EXECUTOR_UNAVAILABLE
JOB_EXECUTION_FAILED
JOB_EXECUTION_TIMEOUT
JOB_CANCEL_UNSUPPORTED
JOB_CANCEL_FAILED
JOB_INTERRUPTED
JOB_RESULT_UNAVAILABLE
JOB_RECOVERY_FAILED
```

## 30.2 Process Errors

Proposed error identifiers:

```text
PROCESS_EXECUTABLE_NOT_FOUND
PROCESS_EXECUTABLE_NOT_ALLOWED
PROCESS_START_FAILED
PROCESS_EXECUTION_FAILED
PROCESS_TIMEOUT
PROCESS_TERMINATION_FAILED
PROCESS_OUTPUT_LIMIT_EXCEEDED
PROCESS_PERMISSION_DENIED
PROCESS_EXIT_STATUS_UNKNOWN
```

These must be reconciled with the shared connector and CLI error catalogs.

## 30.3 Error Mapping

```text
Operating-System Error
        │
        ▼
Process Connector Error
        │
        ▼
Executor Failure
        │
        ▼
Job Manager Classification
        │
        ▼
Framework CLI Error / Job Event
        │
        ▼
Electron Bridge
```

## 30.4 Error Metadata

Errors should preserve:

- Stable error code.
- Job ID.
- Attempt ID.
- Process execution ID where applicable.
- Failure stage.
- Retry eligibility when known.
- Safe human-readable explanation.
- Internal diagnostic evidence.

---

# 31. Observability and Diagnostics

## 31.1 Diagnostic Requirements

The framework should record:

- Job registration.
- Job acceptance.
- Scheduling.
- Execution start.
- Progress.
- Cancellation.
- Completion.
- Failure.
- Interruption.
- Retry attempts.
- Recovery decisions.
- Process start and exit.
- Cleanup failures.

## 31.2 Correlation

The framework must support correlation between:

```text
Electron Request ID
        │
        ▼
Application Action
        │
        ▼
Job ID
        │
        ▼
Execution Attempt ID
        │
        ▼
Process Execution ID
        │
        ▼
External Tool / Service
```

## 31.3 Diagnostics

Diagnostics should expose:

- Active jobs.
- Pending jobs.
- Executor availability.
- Queue utilization.
- Managed process count.
- Interrupted jobs.
- Recent failures.

## 31.4 Logging Security

Diagnostics must not expose sensitive payloads or credentials by default.

## 31.5 Optional Metrics

Optional metrics may include:

- Queue wait duration.
- Execution duration.
- Cancellation latency.
- Failure rate.
- Retry count.
- Process startup duration.
- Resource utilization.

---

# 32. Integration with State Management

## 32.1 State Ownership

The Job Manager owns job lifecycle state.

The state subsystem provides storage and observation mechanisms.

## 32.2 State Scope

Active job execution may use job-scoped volatile state.

Persistent job metadata uses an explicitly configured persistence adapter.

## 32.3 Domain State

Application business state is separate from job lifecycle state.

For example:

- `job.status = completed` is framework execution metadata.
- `audio_asset.status = approved` is application business state.

The framework must not confuse these responsibilities.

## 32.4 State Revision

Job state updates should support revision or attempt identification to prevent stale updates from overwriting newer terminal states.

## 32.5 Notification Ownership

Job lifecycle events are published through the framework event subsystem.

They are not emitted by directly writing arbitrary JSON to stdout from application handlers.

---

# 33. Integration with the CLI Protocol

## 33.1 Job Submission

Application actions may submit work and return an accepted job descriptor.

## 33.2 Job Lifecycle Events

The protocol shall support:

```text
job.started
job.progress
job.completed
job.failed
job.cancelled
job.interrupted
```

## 33.3 Job Status Query

Proposed reserved actions:

```text
system.jobs.get
system.jobs.list
```

## 33.4 Cancellation

The protocol uses:

```text
system.cancel
```

## 33.5 Request Versus Job Completion

A job-submission request may complete before the job.

The original request's response must not be treated as the job's terminal outcome.

## 33.6 Event Delivery

The initial protocol supports best-effort event delivery.

Clients must use status queries to recover from missed events.

## 33.7 Compatibility

New job event fields and actions must follow the protocol's versioning policy.

---

# 34. Integration with Electron

## 34.1 Electron Responsibilities

Electron may:

- Submit a job.
- Display progress.
- Query job status.
- Request cancellation.
- Retrieve approved results.
- Reconnect after renderer reload.

Electron does not directly own Python job execution.

## 34.2 Renderer Reload

Reloading a renderer must not automatically cancel jobs owned by the active Python runtime.

## 34.3 Python Runtime Crash

When Python crashes, in-process jobs lose their execution owner.

The bridge must not report those jobs as still running solely because their metadata exists.

## 34.4 Multiple Windows

Multiple windows may observe the same job when application authorization permits.

Subscription ownership must remain per renderer.

## 34.5 UI Progress

The renderer should present actual progress supplied by the framework.

Indeterminate progress must be displayed as such.

---

# 35. Testing Strategy

## 35.1 Unit Tests

Verify:

- Job definitions.
- Registration.
- Submission.
- State transitions.
- Executor selection.
- Queue admission.
- Result handling.
- Cancellation state.
- Timeout calculations.

## 35.2 Scheduler Tests

Verify:

- FIFO ordering.
- Concurrency limits.
- Queue capacity.
- Priority handling where enabled.
- Starvation prevention.
- Shutdown admission rejection.

## 35.3 Async Executor Tests

Verify:

- Successful execution.
- Exceptions.
- Cooperative cancellation.
- Nonblocking behavior.
- Runtime shutdown.

## 35.4 Thread Executor Tests

Verify:

- Blocking work execution.
- Pool limits.
- Cooperative cancellation.
- Non-terminable work reporting.
- Resource cleanup.

## 35.5 Process Executor Tests

Use controlled executable fixtures to verify:

- Executable discovery.
- Process startup.
- stdout/stderr streaming.
- Exit codes.
- Timeouts.
- Cancellation.
- Forced termination.
- Descendant cleanup.
- Process failure.

## 35.6 Persistence Tests

Verify:

- Job record creation.
- State transitions.
- Attempt history.
- Restart restoration.
- Corrupted metadata.
- Recovery policy.
- Unknown outcomes.

## 35.7 Integration Tests

Verify:

- CLI job submission.
- Progress events.
- Job status queries.
- Cancellation requests.
- Electron subscriptions.
- Renderer reload.
- Python crash handling.

## 35.8 Failure Injection

Simulate:

- Executor crash.
- External process crash.
- Runtime termination.
- Queue overflow.
- Persistence failure.
- Cancellation timeout.
- Cleanup failure.
- Missing output artifact.
- Duplicate submissions.

## 35.9 Platform Tests

Validate process termination and cleanup on Windows, Linux, and macOS.

---

# 36. Architecture Verification Rules

The following rules are proposed for deterministic architecture verification.

| Rule ID | Rule |
|---|---|
| JPM-VER-001 | Managed jobs use the framework Job Manager |
| JPM-VER-002 | Job definitions have valid identifiers |
| JPM-VER-003 | Active jobs have execution owners |
| JPM-VER-004 | Job state transitions follow approved lifecycle rules |
| JPM-VER-005 | External process jobs use framework process facilities |
| JPM-VER-006 | Application domains do not directly manage subprocess lifecycles |
| JPM-VER-007 | Process execution configuration follows safety policy |
| JPM-VER-008 | Job queues have bounded capacity |
| JPM-VER-009 | Job concurrency limits are configured where required |
| JPM-VER-010 | Durable-job claims require supported execution ownership |
| JPM-VER-011 | Persistent job metadata uses approved storage facilities |
| JPM-VER-012 | Cancellation paths follow documented executor capabilities |
| JPM-VER-013 | Process output is not written directly to protocol stdout |
| JPM-VER-014 | Job lifecycle events use framework event facilities |
| JPM-VER-015 | Recovery policy is declared for persisted nonterminal jobs |
| JPM-VER-016 | Job results and artifact references follow access policy |
| JPM-VER-017 | Required process cleanup mechanisms are present |
| JPM-VER-018 | Job and process dependencies follow module boundaries |
| JPM-VER-019 | Runtime does not import development-only tooling |
| JPM-VER-020 | Job architecture exceptions are documented |

Some rules require executable tests or review.

Static inspection cannot prove that a subprocess always terminates or that cancellation is always successful.

---

# 37. Existing Application Migration

## 37.1 Migration Goal

Existing applications may use:

- Direct `subprocess` calls.
- Custom thread pools.
- Custom async task registries.
- Custom job state dictionaries.
- Custom progress callbacks.
- SQLite job tables.
- Electron-specific process management.
- Unmanaged background tasks.

AdharaSutra shall support their incremental adoption.

## 37.2 Migration Pipeline

```text
Existing Application
        │
        ▼
Discover Current Execution Model
        │
        ▼
Identify Jobs and Processes
        │
        ▼
Determine Execution Ownership
        │
        ▼
Record Existing Behavior
        │
        ▼
Define AdharaSutra Job Contracts
        │
        ▼
Introduce Framework Executors
        │
        ▼
Migrate Process Execution
        │
        ▼
Migrate Progress and Cancellation
        │
        ▼
Verify Behavioral Compatibility
        │
        ▼
Remove Legacy Execution Infrastructure
```

## 37.3 Migration Safety

Migration must preserve:

- Job input semantics.
- Business execution order.
- Required output artifacts.
- Error behavior relied upon by callers.
- Cancellation behavior.
- Persistence requirements.
- Existing user-visible progress where feasible.

## 37.4 Compatibility Adapters

Existing job handlers may be wrapped temporarily.

Existing subprocess operations may adopt the Process Connector before the entire job orchestration layer is migrated.

## 37.5 Verification

Completion requires architecture checks and representative behavioral regression tests.

---

# 38. Representative End-to-End Scenarios

## JPM-S01 — Asynchronous HTTP Job

**Given** an application submits an async job using an HTTP-based service,

**When** the scheduler starts the job,

**Then** the async executor shall invoke the application handler.

**And** the framework shall track its lifecycle and report its actual outcome.

## JPM-S02 — External CLI Audio Job

**Given** an application submits an audio-processing job,

**When** the external process executor launches the configured executable,

**Then** the Process Connector shall manage execution and output streams.

**And** the application adapter shall interpret the output.

**And** the Job Manager shall publish the resulting lifecycle events.

## JPM-S03 — Concurrent Jobs

**Given** multiple jobs are submitted,

**When** the concurrency limit is reached,

**Then** additional eligible jobs shall remain pending within queue capacity.

**And** no unbounded number of processes shall be created.

## JPM-S04 — Job Cancellation

**Given** a running job,

**When** cancellation is requested,

**Then** the framework shall acknowledge the request separately from confirmed cancellation.

**And** report the actual terminal outcome.

## JPM-S05 — Non-Cooperative Thread

**Given** a blocking thread cannot stop cooperatively,

**When** cancellation is requested,

**Then** the framework shall not falsely report that the thread has terminated.

## JPM-S06 — External Process Crash

**Given** an external executable crashes,

**When** the Process Connector detects its exit,

**Then** the associated job shall receive a classified failure unless the application establishes a valid alternate outcome.

## JPM-S07 — Python Runtime Crash

**Given** an in-process job is running,

**When** the owning Python runtime terminates,

**Then** a later runtime shall not assume the job is still executing.

**And** persisted metadata shall be reconciled according to recovery policy.

## JPM-S08 — Job Result Recovery

**Given** a job produced an artifact before an unexpected runtime interruption,

**When** recovery occurs,

**Then** the application shall validate whether the artifact represents a complete result before marking the job successful.

## JPM-S09 — Renderer Reload

**Given** a Python-owned job remains active,

**When** the Electron renderer reloads,

**Then** the new renderer shall be able to query job status through the framework.

## JPM-S10 — Queue Overflow

**Given** a job queue is at capacity,

**When** additional jobs are submitted,

**Then** the Job Manager shall enforce the configured admission policy.

**And** avoid unbounded resource growth.

## JPM-S11 — Graceful Shutdown

**Given** active jobs and external processes exist,

**When** shutdown begins,

**Then** the lifecycle manager shall apply the configured job shutdown policy.

**And** the Process Connector shall manage required termination and cleanup.

## JPM-S12 — Retry Safety

**Given** a job performs a non-idempotent operation,

**When** execution fails with an uncertain outcome,

**Then** the framework shall not automatically retry without an approved safety policy.

## JPM-S13 — Multiple Processes in One Job

**Given** an application workflow executes multiple external commands,

**When** one command fails,

**Then** the application determines whether the workflow can continue or requires compensating actions.

**And** the framework tracks the managed processes and resulting job outcome.

## JPM-S14 — Optional Persistence

**Given** an application does not require persistent job history,

**When** the Job Manager initializes,

**Then** it shall operate without initializing SQLite.

## JPM-S15 — Migration from Custom Process Runner

**Given** an existing application executes external tools through custom subprocess code,

**When** it adopts AdharaSutra's Process Connector,

**Then** its existing tool-specific behavior shall remain testable.

**And** duplicated execution infrastructure may be removed after verification.

---

# 39. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| JPM-D01 | Job and process ownership | Separate responsibilities |
| JPM-D02 | Job execution model | Executor abstractions |
| JPM-D03 | Initial executors | Async, thread, external process |
| JPM-D04 | Scheduler | Bounded in-process scheduler |
| JPM-D05 | Default scheduling | FIFO |
| JPM-D06 | Concurrency | Configurable limits |
| JPM-D07 | Job lifecycle | Explicit state machine |
| JPM-D08 | Execution attempts | Separately tracked |
| JPM-D09 | Process execution | Shared Process Connector |
| JPM-D10 | Process security | Structured arguments, no shell by default |
| JPM-D11 | Process output | Buffered/streamed with limits |
| JPM-D12 | Progress | Structured events |
| JPM-D13 | Cancellation | Capability-specific, outcome-aware |
| JPM-D14 | Timeouts | Explicit owner and propagation |
| JPM-D15 | Results | Structured data and artifact references |
| JPM-D16 | Job metadata | Optional persistence |
| JPM-D17 | Default persistent storage | SQLite adapter when enabled |
| JPM-D18 | Recovery | Explicit policies |
| JPM-D19 | Durable workers | Deferred extension |
| JPM-D20 | Electron job API | Standard CLI actions and events |
| JPM-D21 | Shutdown | Lifecycle-coordinated |
| JPM-D22 | Process termination | Platform-specific adapters |
| JPM-D23 | Testing | Controlled fixtures and failure injection |
| JPM-D24 | Architecture enforcement | Deterministic-first |

All decisions remain proposed until reviewed and validated.

---

# 40. Outstanding Questions

## JPM-OQ-001 — Public Job API

Should applications register jobs through decorators, typed descriptors, or both?

**Recommendation:** Support explicit registration with optional decorator convenience.

## JPM-OQ-002 — CPU-Bound Python Execution

Should the initial release include a dedicated Python worker-process executor for CPU-heavy pure-Python tasks?

**Recommendation:** Validate real workloads first. If required, define a separate isolated process executor rather than assuming ordinary threads deliver suitable parallelism.

## JPM-OQ-003 — Job Priority

Should priority scheduling be part of the initial implementation?

**Recommendation:** Start with FIFO and per-job-type concurrency limits. Add priorities when justified.

## JPM-OQ-004 — Job Dependencies

Should the Job Manager support dependency graphs and chained jobs?

**Recommendation:** Keep the initial engine focused on individual managed jobs. Applications may orchestrate sequential operations through use cases.

## JPM-OQ-005 — Retry Ownership

Should retry policies belong to the Job Manager or application handlers?

**Recommendation:** The framework implements retry mechanics while applications define retry eligibility and business safety.

## JPM-OQ-006 — Persistent Job Inputs

Should full job inputs be stored in SQLite?

**Recommendation:** Store only necessary recoverable metadata and references. Avoid persisting sensitive or large payloads indiscriminately.

## JPM-OQ-007 — Job History Retention

What retention policy should apply to completed jobs?

**Recommendation:** Define configurable limits and a small bounded default for volatile job history.

## JPM-OQ-008 — Process Termination Escalation

What graceful and forced termination periods should be used?

**Recommendation:** Define executor-specific defaults after cross-platform testing.

## JPM-OQ-009 — Orphan Process Recovery

Should the framework attempt to reattach to an external process after a crash?

**Recommendation:** Do not promise automatic reattachment initially. Require strong process identity and ownership evidence before supporting it.

## JPM-OQ-010 — Durable Worker Packaging

Should durable workers be implemented as a separate Python executable or service?

**Recommendation:** Defer until a consuming application requires independent execution continuity.

## JPM-OQ-011 — Job Status Actions

Should the standard reserved protocol include `system.jobs.get` and `system.jobs.list`?

**Recommendation:** Yes, with authorization, filtering, and bounded response sizes.

## JPM-OQ-012 — Job Event Sequence Numbers

Should job events carry monotonically increasing per-job sequence numbers?

**Recommendation:** Include an attempt-aware revision or sequence mechanism to assist reconciliation and gap detection.

## JPM-OQ-013 — Artifact Cleanup

Should the framework automatically remove artifacts when job metadata expires?

**Recommendation:** Only when artifact ownership and retention policy explicitly authorize deletion.

## JPM-OQ-014 — GPU Workload Limits

Should jobs be able to declare GPU resource requirements?

**Recommendation:** Support resource classification and user-configured concurrency limits initially, without claiming GPU resource reservation.

## JPM-OQ-015 — Remote Cancellation

Should AdharaSutra provide universal cancellation for external HTTP-based services?

**Recommendation:** No. Generic connector cancellation and service-specific remote cancellation must remain distinct.

---

# 41. Functional Requirement Traceability

| Requirement group | Job/process responsibility |
|---|---|
| FR-JOB | Job lifecycle, scheduling, cancellation, recovery |
| FR-EXT | External process execution |
| FR-RUN | Runtime integration |
| FR-CLI | Job actions and responses |
| FR-ELC | Electron job interaction |
| FR-STATE | Job state storage |
| FR-CON | Connector integration |
| FR-FS | Artifact and temporary file management |
| FR-CFG | Execution policies |
| FR-ERR | Job and process failures |
| FR-LOG | Execution diagnostics |
| FR-DI | Executor composition |
| FR-SEC | Process and job security |
| FR-TEST | Execution contract tests |
| FR-ARCH | Job/process architecture verification |
| FR-MIG | Existing execution infrastructure migration |

---

# 42. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-PERF | Managed scheduling and execution |
| NFR-RES | Bounded queues and resource ownership |
| NFR-REL | Explicit lifecycle and failure classification |
| NFR-AVAIL | Recovery policies |
| NFR-SCALE | Concurrency limits and backpressure |
| NFR-SEC | Safe subprocess execution |
| NFR-PORT | Platform-aware process management |
| NFR-MAINT | Separate orchestration and execution modules |
| NFR-EXT | Pluggable executors |
| NFR-TEST | Controlled executors and fault injection |
| NFR-COMP | Versioned job contracts and events |
| NFR-ARCH | Deterministic dependency and policy checks |
| NFR-MIG | Incremental process/job migration |
| NFR-OBS | Correlation and execution diagnostics |

---

# 43. Architecture Acceptance Criteria

The Job and Process Management architecture may be approved when:

- [ ] Job and process responsibilities are distinct.
- [ ] Job registration and submission contracts are defined.
- [ ] Job identifiers and execution attempts are distinguishable.
- [ ] Job lifecycle transitions are explicit.
- [ ] Execution owners are identifiable.
- [ ] Async execution is supported conceptually.
- [ ] Blocking thread execution limitations are documented.
- [ ] External process execution reuses the framework Process Connector.
- [ ] Executable discovery and argument safety are defined.
- [ ] stdout/stderr streaming and buffering are defined.
- [ ] Process lifecycle and termination semantics are documented.
- [ ] Cross-platform process behavior is accounted for.
- [ ] Scheduling and concurrency limits are defined.
- [ ] Queue admission and overload behavior are defined.
- [ ] Progress reporting is structured and accurate.
- [ ] Job status retrieval is defined.
- [ ] Cancellation acknowledgment and termination are separate.
- [ ] Timeout ownership is defined.
- [ ] Result and artifact ownership are explicit.
- [ ] Persistence remains optional.
- [ ] Persisted metadata is not confused with durable execution.
- [ ] Recovery and retry policies are defined.
- [ ] Shutdown coordinates jobs and processes.
- [ ] Electron integration uses the standard CLI protocol.
- [ ] Security boundaries prevent arbitrary process execution.
- [ ] Testing and failure-injection strategies are defined.
- [ ] Architecture verification rules are identifiable.
- [ ] Existing application migration is feasible.
- [ ] Critical unresolved decisions are approved or explicitly deferred.

---

# 44. Final Architecture Summary

AdharaSutra provides a unified infrastructure for managing long-running application work and the operating-system processes used to execute that work.

The Job Manager owns:

- Job registration.
- Submission.
- Admission.
- Scheduling.
- Execution lifecycle.
- Progress.
- Cancellation coordination.
- Timeouts.
- Job results.
- Recovery policy.
- Job metadata.

The Process Connector owns:

- Executable discovery.
- Process creation.
- Argument handling.
- stdin/stdout/stderr.
- Exit monitoring.
- Process termination.
- Process-tree cleanup.
- Platform-specific behavior.

Applications own:

- Job business logic.
- Workflow semantics.
- Domain progress stages.
- External tool-specific arguments and output interpretation.
- Retry safety decisions.
- Business result validation.

The initial architecture uses bounded in-process scheduling with async, thread, and managed external-process execution strategies.

Persistent metadata is optional.

Durable execution requires a separate, explicitly managed execution owner and is not implied by the presence of SQLite records.

Jobs communicate with Electron through the standardized AdharaSutra CLI protocol.

The framework must provide truthful execution status, safe resource ownership, bounded concurrency, accurate cancellation outcomes, and controlled recovery.

**The central guarantee is: Every job has an execution owner. Every process has a lifecycle owner. Every outcome is reported according to verified execution evidence.**

---

# 45. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architecture review

**Next Document:** `docs/design/configuration-and-lifecycle.md`

The next document should define centralized configuration, configuration sources and precedence, validation, environment isolation, service composition, application initialization, dependency-aware startup, readiness, graceful shutdown, and lifecycle failure handling.

---

**AdharaSutra — Build once. Standardize everywhere.**
