# AdharaSutra — CLI Communication Protocol

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/cli-protocol.md`  
**Document Version:** 0.1.0  
**Protocol Version:** 1.0 — Proposed  
**Status:** Draft — Architecture Planning  
**Classification:** Communication Protocol Design  
**Transport:** Standard Input / Standard Output  
**Serialization:** UTF-8 JSON / NDJSON  
**Primary Consumers:** Electron Bridge, Python Applications, CLI Automation

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`

---

# 1. Purpose

This document defines the standardized communication protocol between AdharaSutra applications and their external callers.

The primary communication boundary is between an Electron application and an AdharaSutra-powered Python runtime.

The protocol shall provide a consistent method for:

1. Executing application actions.
2. Submitting structured requests.
3. Receiving structured responses.
4. Reporting execution progress.
5. Managing long-running jobs.
6. Handling cancellation.
7. Reporting errors.
8. Managing persistent CLI sessions.
9. Detecting process and communication failures.
10. Validating protocol compatibility.
11. Supporting concurrent requests.
12. Enabling application-independent Electron integration.

The protocol must remain independent of application-specific business logic and the technologies used to execute that logic.

## 1.1 Central Principle

> Electron communicates with AdharaSutra through one stable CLI protocol. AdharaSutra is responsible for routing requests to applications and returning standardized responses, regardless of the external infrastructure involved.

For example:

```text
Electron
    │
    ▼
Unified CLI Protocol
    │
    ▼
AdharaSutra Runtime
    │
    ▼
Application Action
    │
    ├── HTTP → ComfyUI
    ├── HTTP → LM Studio
    ├── CLI  → audio.cpp
    ├── SQLite
    └── Local Python
```

Electron must not require different communication protocols for different connectors.

---

# 2. Protocol Scope

## 2.1 In Scope

The CLI protocol defines:

- Communication channels.
- Message framing.
- Message categories.
- JSON envelope structures.
- Protocol versioning.
- Request and response correlation.
- Action dispatch conventions.
- Input and output validation.
- Event delivery.
- Job notifications.
- Cancellation requests.
- Session initialization.
- Connection lifecycle.
- Timeout signaling.
- Error representation.
- Process exit semantics.
- Compatibility rules.
- Security boundaries.

## 2.2 Out of Scope

The protocol does not define:

- Application business rules.
- Domain-specific action names.
- Application-specific payload semantics.
- HTTP API endpoints.
- External CLI argument structures.
- Database schemas.
- AI model execution behavior.
- Image-generation workflows.
- Audio-processing algorithms.
- Electron UI components.

These belong to consuming applications or their external integration adapters.

---

# 3. Protocol Design Principles

## CP-001 — Transport Independence

The Electron-facing protocol shall remain unchanged regardless of the backend connector used by an application action.

## CP-002 — Structured Communication

Machine-readable communication shall use validated JSON messages.

## CP-003 — Stable Envelopes

The framework shall define common message envelopes shared across applications.

## CP-004 — Application Extensibility

Applications shall register their own actions and payload schemas without modifying the protocol runtime.

## CP-005 — Explicit Correlation

Responses and request-scoped events shall identify their originating request.

## CP-006 — Explicit Completion

The protocol must distinguish request completion from background job completion.

## CP-007 — Accurate Cancellation

Cancellation shall be represented as an asynchronous operation with an explicit outcome.

A cancellation request being accepted must not be mistaken for completed cancellation.

## CP-008 — Predictable Failure Handling

Transport, protocol, application, and connector failures must be distinguishable.

## CP-009 — Versioned Compatibility

Incompatible protocol versions must be rejected explicitly.

## CP-010 — No Business Logic

The protocol shall not contain service-specific or application-specific execution logic.

## CP-011 — Separation of Protocol and Diagnostics

Normal diagnostic logs must not corrupt structured protocol output.

## CP-012 — Bounded Resource Usage

Message sizes, queues, and concurrency must be configurable and bounded.

---

# 4. Communication Architecture

## 4.1 Process Communication

AdharaSutra uses operating-system process communication.

```text
┌─────────────────────────────────────────┐
│               Electron                  │
│                                         │
│ Renderer                                │
│    │                                    │
│    ▼                                    │
│ Preload API                             │
│    │                                    │
│    ▼                                    │
│ Main Process                            │
│    │                                    │
│    ▼                                    │
│ AdharaSutra Electron Bridge             │
└───────────────────┬─────────────────────┘
                    │
             Child Process
                    │
          ┌─────────┼─────────┐
          │         │         │
        stdin     stdout    stderr
          │         │         │
          ▼         ▲         ▲
┌─────────────────────────────────────────┐
│           Python Runtime                │
│                                         │
│ CLI Transport                           │
│      │                                  │
│      ▼                                  │
│ Protocol Engine                         │
│      │                                  │
│      ▼                                  │
│ Action Router                           │
│      │                                  │
│      ▼                                  │
│ Application Handler                     │
│      │                                  │
│      ▼                                  │
│ Result / Events / Errors                │
└─────────────────────────────────────────┘
```

## 4.2 Communication Channels

| Channel | Direction | Purpose |
|---|---|---|
| stdin | Electron → Python | Requests and control messages |
| stdout | Python → Electron | Structured responses and events |
| stderr | Python → Electron | Diagnostic logs |
| Process exit | Python → Electron | Process termination status |

## 4.3 Channel Rules

### stdin

- Accepts protocol messages in supported execution modes.
- Uses UTF-8 encoding.
- Must not be interpreted as arbitrary shell commands.
- Must enforce message-size limits.

### stdout

- Contains only valid protocol messages when the structured protocol is active.
- Must not contain ordinary logging.
- Must support multiple messages in persistent mode.
- Must preserve each message's framing.

### stderr

- Contains diagnostics and logging.
- Is not used for authoritative application results.
- Must support appropriate sensitive-data redaction.

### Process exit

- Indicates process termination.
- Does not replace structured application-level result reporting.
- An unexpected exit may invalidate active requests.

---

# 5. Serialization and Message Framing

## 5.1 Encoding

Protocol messages shall use UTF-8.

JSON encoding shall follow standard JSON syntax.

## 5.2 NDJSON Framing

The protocol shall use newline-delimited JSON for structured communication.

Each message occupies one logical line.

Example:

```jsonl
{"kind":"event","protocol_version":"1.0","event":"job.started","data":{"job_id":"job-123"}}
{"kind":"event","protocol_version":"1.0","event":"job.progress","data":{"job_id":"job-123","percent":40}}
{"kind":"event","protocol_version":"1.0","event":"job.completed","data":{"job_id":"job-123"}}
```

The receiver must buffer partial reads until a complete framed message is available.

A single operating-system stream read must not be assumed to contain exactly one message.

Multiple messages may arrive in one read.

## 5.3 Message Boundaries

A newline terminates a message.

Newline characters inside JSON string values must be escaped according to JSON rules.

The sender must not use pretty-printed multiline JSON on the protocol stream.

## 5.4 Maximum Message Size

**Proposed default:**

- Maximum protocol message size: 1 MiB.
- Configurable lower limits.
- Higher limits only through explicit configuration and validation.

Large data should be transferred using managed artifact references rather than embedding large binary payloads.

## 5.5 Oversized Messages

The receiver shall:

1. Detect that the configured limit has been exceeded.
2. Stop unbounded buffering.
3. Reject the message or terminate the affected session according to the transport policy.
4. Emit a structured error where it remains safe and possible.
5. Avoid executing the invalid request.

## 5.6 Output Flushing

Persistent communication must flush critical responses and progress events promptly.

Buffering must not indefinitely delay completed responses.

---

# 6. Protocol Message Model

## 6.1 Message Categories

The proposed protocol defines four principal message categories.

| Kind | Purpose |
|---|---|
| `request` | Invoke an application or framework action |
| `response` | Report the result of a request |
| `event` | Report an occurrence or progress update |
| `control` | Protocol-level session control |

Every message contains a `kind` field.

This is an intentional refinement of the earlier conceptual request and response examples. The final protocol includes a discriminator to make parsing and validation more reliable.

## 6.2 Common Envelope Fields

All protocol messages shall contain:

| Field | Type | Required |
|---|---|---|
| `kind` | string | Yes |
| `protocol_version` | string | Yes |

Other fields depend on the message category.

## 6.3 Protocol Version

Initial proposed protocol version:

`1.0`

The runtime must validate the protocol version before interpreting message-specific fields.

---

# 7. Request Message

## 7.1 Purpose

A request invokes a registered application or framework action.

## 7.2 Request Schema

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "req-001",
  "action": "voice.generate",
  "payload": {
    "text": "Hello",
    "voice_id": "voice-1"
  }
}
```

## 7.3 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `kind` | string | Yes | Must be `request` |
| `protocol_version` | string | Yes | Protocol version |
| `request_id` | string | Yes | Request correlation identifier |
| `action` | string | Yes | Registered action |
| `payload` | object | Yes | Application-defined request data |

## 7.4 Request Identifier

The request identifier must be unique among active requests within a session.

The framework must detect duplicate active identifiers.

The Electron bridge should generate sufficiently unique identifiers.

Identifiers must not be treated as authentication credentials.

## 7.5 Action Identifier

Action identifiers use a namespaced convention.

Examples:

```text
voice.generate
voice.list
audio.separate
model.status
image.generate
project.save
project.load
```

Application action names are defined by the consuming application.

Reserved framework namespaces must not be available for unrestricted application registration.

### Proposed reserved namespaces

```text
system.*
protocol.*
```

These namespaces are intended for framework-defined operations.

## 7.6 Payload

The payload contains application-defined data.

The framework validates:

1. Envelope structure.
2. Action existence.
3. Registered payload schema.
4. Configured size and security restrictions.

Business validation remains the application's responsibility.

## 7.7 Unknown Actions

Unknown action identifiers shall produce an `ACTION_NOT_FOUND` response.

The action handler must not execute.

---

# 8. Response Message

## 8.1 Purpose

A response communicates the outcome of a request.

Every valid accepted request must produce exactly one terminal response, provided the communication session remains functional.

## 8.2 Successful Response

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-001",
  "success": true,
  "data": {
    "output_path": "audio/generated.wav"
  },
  "error": null
}
```

## 8.3 Failed Response

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-001",
  "success": false,
  "data": null,
  "error": {
    "code": "CONNECTOR_UNAVAILABLE",
    "message": "The required external service is unavailable",
    "retryable": true
  }
}
```

## 8.4 Response Fields

| Field | Type | Required |
|---|---|---|
| `kind` | string | Yes |
| `protocol_version` | string | Yes |
| `request_id` | string | Yes |
| `success` | boolean | Yes |
| `data` | JSON value or null | Yes |
| `error` | error object or null | Yes |

## 8.5 Response Invariants

If `success` is `true`:

- `error` must be `null`.
- `data` may contain a result or be `null`.

If `success` is `false`:

- `error` must contain a valid error object.
- `data` must be `null`.

## 8.6 Request Completion

A response completes the corresponding request.

However, a request may start a managed background job.

In that case, the successful response may indicate that a job was accepted.

This must not be confused with successful completion of the job itself.

---

# 9. Background Job Acceptance

## 9.1 Accepted Job Response

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-002",
  "success": true,
  "data": {
    "job_id": "job-123",
    "status": "accepted"
  },
  "error": null
}
```

This means the framework accepted the job for execution under a defined execution owner.

It does not mean that the job finished successfully.

## 9.2 Job Status

Supported public job statuses should include:

- `pending`
- `running`
- `completed`
- `failed`
- `cancelled`
- `interrupted`

`accepted` is an acknowledgment status for job submission rather than a required internal lifecycle state.

The detailed job state machine will be finalized in the job-management design.

## 9.3 Execution Ownership

A job must have an identifiable owner.

Possible owners include:

- Current persistent Python runtime.
- Managed external process.
- Persistent worker.

A job must not be represented as durably executing after its owner exits unless execution has actually been transferred to a supported persistent worker.

---

# 10. Event Message

## 10.1 Purpose

Events report progress, lifecycle transitions, and other occurrences.

Unlike responses, events do not necessarily terminate a request.

## 10.2 Event Schema

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "request_id": "req-002",
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": 65,
    "stage": "generating"
  }
}
```

## 10.3 Event Fields

| Field | Type | Required |
|---|---|---|
| `kind` | string | Yes |
| `protocol_version` | string | Yes |
| `event` | string | Yes |
| `data` | JSON value | Yes |
| `request_id` | string | Conditional |

`request_id` is required for events directly associated with an active request.

For independently running jobs, `job_id` provides durable job correlation.

A job event may contain the originating request ID when available, but consumers must not assume the originating request is still active.

## 10.4 Standard Events

### Runtime Events

```text
application.ready
application.stopping
application.failed
```

### Job Events

```text
job.started
job.progress
job.completed
job.failed
job.cancelled
job.interrupted
```

### Connector Events

```text
connector.ready
connector.degraded
connector.unavailable
```

### Application Events

Applications may define namespaced events.

Examples:

```text
voice.preview_ready
image.artifact_created
project.saved
```

## 10.5 Event Contract

The framework owns:

- Event framing.
- Serialization.
- Dispatch.
- Correlation.
- Buffer management.
- Subscription lifecycle.
- Delivery to the Electron bridge.

The application owns the meaning of application-specific events.

---

# 11. Progress Reporting

## 11.1 Progress Event

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": 50,
    "stage": "processing",
    "message": "Processing audio segments"
  }
}
```

## 11.2 Progress Representation

The framework should support:

- Percentage progress where meaningful.
- Named stages.
- Human-readable status messages.
- Completed and total units.
- Optional additional progress metadata.

## 11.3 Unknown Progress

Some external tools cannot report a reliable percentage.

The framework must support indeterminate progress.

Example:

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": null,
    "stage": "processing",
    "message": "External process is running"
  }
}
```

## 11.4 Progress Accuracy

The framework must not invent percentage completion when the underlying operation does not provide sufficient information.

Progress mapping is the responsibility of application logic or its integration adapter.

---

# 12. Cancellation Protocol

## 12.1 Principle

Cancellation is a request to terminate or cooperatively stop an operation.

It is not an immediate guarantee of termination.

## 12.2 Cancellation Request

The proposed initial protocol represents cancellation as a reserved framework action.

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "req-cancel-001",
  "action": "system.cancel",
  "payload": {
    "target_type": "job",
    "target_id": "job-123"
  }
}
```

## 12.3 Cancellation Targets

Supported target types may include:

- `request`
- `job`

The implementation must define how cancellation is routed to the target's execution owner.

## 12.4 Cancellation Acknowledgment

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-cancel-001",
  "success": true,
  "data": {
    "target_id": "job-123",
    "status": "cancellation_requested"
  },
  "error": null
}
```

This only acknowledges that cancellation was requested.

## 12.5 Cancellation Completion

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "event": "job.cancelled",
  "data": {
    "job_id": "job-123",
    "status": "cancelled"
  }
}
```

## 12.6 Cancellation Failure

If cancellation is unsupported, impossible, or unsuccessful, the framework must report the actual outcome.

Possible errors:

```text
CANCELLATION_UNSUPPORTED
CANCELLATION_TARGET_NOT_FOUND
CANCELLATION_FAILED
```

## 12.7 External Process Cancellation

The process connector is responsible for implementing supported termination behavior.

The application-specific adapter is responsible for providing any cooperative cancellation logic required by the external tool.

## 12.8 Cancellation Race Conditions

The protocol must handle cases where:

- The job completes before cancellation is received.
- Cancellation is requested twice.
- The target does not exist.
- The target already failed.
- The Python process terminates during cancellation.
- The external tool ignores cancellation.

Cancellation must never overwrite an already confirmed terminal job result without an explicit state-machine rule.

---

# 13. Persistent CLI Session Protocol

## 13.1 Purpose

Persistent sessions enable repeated communication between Electron and one long-lived Python runtime.

## 13.2 Session Startup

Proposed sequence:

```text
Electron Main
      │
      ▼
Start Python Process
      │
      ▼
Python Initializes AdharaSutra
      │
      ▼
CLI Transport Ready
      │
      ▼
Electron Sends Handshake
      │
      ▼
Protocol Compatibility Check
      │
      ▼
Handshake Response
      │
      ▼
Session READY
      │
      ▼
Normal Request Processing
```

## 13.3 Handshake Request

The proposed handshake uses a reserved framework action.

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "handshake-001",
  "action": "system.hello",
  "payload": {
    "client": "electron",
    "client_version": "1.0.0",
    "supported_protocol_versions": [
      "1.0"
    ]
  }
}
```

## 13.4 Handshake Response

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "handshake-001",
  "success": true,
  "data": {
    "application": "vani",
    "application_version": "1.0.0",
    "framework_version": "0.1.0",
    "selected_protocol_version": "1.0",
    "session_id": "session-001",
    "capabilities": [
      "requests",
      "events",
      "cancellation",
      "jobs"
    ]
  },
  "error": null
}
```

## 13.5 Session Readiness

A persistent session is ready only after successful handshake and required runtime initialization.

Normal application actions must not execute before required session initialization completes.

## 13.6 Handshake Failure

Unsupported protocol combinations must produce a structured compatibility error where possible.

The session must not continue in an incompatible state.

## 13.7 Session Identity

The runtime may assign a session identifier.

Session identifiers identify communication sessions, not authenticated users.

## 13.8 Session Termination

The session ends when:

- The Python process exits.
- The transport closes.
- The bridge initiates a supported shutdown.
- A fatal protocol error terminates communication.
- A fatal runtime failure occurs.

Session-scoped resources must be cleaned up appropriately.

---

# 14. One-Shot CLI Protocol

## 14.1 Purpose

One-shot execution supports independent commands, scripts, automation, and simple operations.

## 14.2 Execution Model

```text
Caller
   │
   ▼
Launch Application CLI
   │
   ▼
Submit One Request
   │
   ▼
Initialize Required Runtime
   │
   ▼
Execute Registered Action
   │
   ▼
Return Response
   │
   ▼
Shutdown Runtime
   │
   ▼
Process Exit
```

## 14.3 Standardized Input

The canonical machine-readable one-shot mode should accept one request envelope via stdin.

Example:

```bash
python -m my_application --protocol oneshot
```

The caller writes one request to stdin.

The runtime returns one terminal response, optionally preceded by progress events.

The exact executable flags remain subject to the CLI implementation design.

## 14.4 Human-Friendly CLI

Applications may also expose ordinary command-line syntax.

Example:

```bash
vani voice generate --text "Hello"
```

Human-friendly commands must ultimately invoke registered application actions through the framework.

They must not implement separate business execution paths.

## 14.5 One-Shot Completion

The process must not exit before the required request has reached its terminal outcome.

A one-shot operation that submits durable background work may return an accepted job only when a separate supported execution owner actually exists.

Otherwise, the operation must complete within the process or fail explicitly.

## 14.6 One-Shot Compatibility

The one-shot protocol uses the same logical request, response, event, and error schemas as persistent mode.

A separate persistent-session handshake is not required for one-shot execution; the runtime validates the request's protocol version directly.

---

# 15. Request Concurrency

## 15.1 Persistent Runtime Concurrency

Persistent CLI mode may support multiple active requests.

Example:

```text
Request A ───────────────► Response A
Request B ─────► Response B
Request C ──────────► Response C
```

Responses may complete in a different order from request arrival.

## 15.2 Correlation Requirement

Every response must identify its originating request.

The bridge must not rely on arrival order to match responses with requests.

## 15.3 Request Isolation

Request-scoped state must be isolated.

One action must not unintentionally modify another action's execution context.

## 15.4 Concurrency Limits

The runtime must support configurable limits on active requests.

When capacity is exhausted, it may queue or reject requests according to documented policy.

## 15.5 Handler Concurrency

Application handlers must declare or document relevant execution constraints.

The framework should not automatically assume every handler is safe for concurrent execution.

## 15.6 Blocking Operations

Blocking work must not indefinitely block the protocol input/output processing loop.

The runtime should use appropriate asynchronous execution or managed worker facilities.

The detailed execution strategy is deferred to the runtime and job-management designs.

---

# 16. Message Ordering and Delivery Guarantees

## 16.1 Transport Ordering

Messages written sequentially to the same stdout stream preserve their byte order.

However, concurrent operations may produce interleaved logical events.

## 16.2 Response Ordering

Responses are not required to appear in request arrival order.

Correlation identifiers are authoritative.

## 16.3 Request Terminal Response

For each accepted request, the runtime must attempt to emit exactly one terminal response.

If the process or transport fails, delivery may be impossible.

## 16.4 Event Ordering

The runtime must define per-job event ordering.

A terminal job event must not be followed by new progress events for the same job execution.

## 16.5 Delivery Guarantees

The initial protocol provides best-effort event delivery over a live process stream.

It does not guarantee durable event replay following process termination.

Persistent event history requires an explicitly configured storage and replay mechanism.

## 16.6 Exactly-Once Execution

The protocol does not guarantee exactly-once business execution.

A caller may lose a response after an action has already executed.

Applications requiring safe retries must implement appropriate idempotency semantics.

A future protocol extension may introduce optional idempotency keys.

---

# 17. Timeout Handling

## 17.1 Timeout Categories

The framework distinguishes:

- Process startup timeout.
- Handshake timeout.
- Request execution timeout.
- Connector timeout.
- External process timeout.
- Job deadline.
- Graceful shutdown timeout.

## 17.2 Timeout Ownership

Different components own different timeouts.

| Timeout | Primary owner |
|---|---|
| Python process startup | Electron bridge |
| Handshake | Electron bridge and CLI runtime |
| Request deadline | Runtime execution |
| HTTP request | HTTP connector |
| External executable | Process connector |
| Job execution | Job manager |
| Shutdown | Lifecycle manager |

## 17.3 Timeout Semantics

A caller-side timeout does not necessarily mean the underlying operation stopped.

The framework must distinguish:

- Caller stopped waiting.
- Cancellation was requested.
- Execution actually terminated.
- Execution outcome remains unknown.

## 17.4 Timeout Errors

Example:

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-010",
  "success": false,
  "data": null,
  "error": {
    "code": "EXECUTION_TIMEOUT",
    "message": "The operation exceeded its execution deadline",
    "retryable": null
  }
}
```

`retryable: null` means retry safety is unknown.

The framework must not automatically mark all timeouts as retryable.

---

# 18. Error Protocol

## 18.1 Standard Error Object

```json
{
  "code": "CONNECTOR_UNAVAILABLE",
  "message": "External dependency is unavailable",
  "retryable": true,
  "details": {
    "connector": "comfyui"
  }
}
```

## 18.2 Error Fields

| Field | Type | Required |
|---|---|---|
| `code` | string | Yes |
| `message` | string | Yes |
| `retryable` | boolean or null | Yes |
| `details` | object | No |

## 18.3 Error Categories

### Protocol

```text
PROTOCOL_INVALID_MESSAGE
PROTOCOL_UNSUPPORTED_VERSION
PROTOCOL_MESSAGE_TOO_LARGE
PROTOCOL_INVALID_STATE
```

### Action Routing

```text
ACTION_NOT_FOUND
ACTION_ALREADY_REGISTERED
ACTION_VALIDATION_FAILED
ACTION_NOT_ALLOWED
```

### Runtime

```text
RUNTIME_NOT_READY
RUNTIME_INITIALIZATION_FAILED
RUNTIME_SHUTTING_DOWN
RUNTIME_EXECUTION_FAILED
```

### Connectors

```text
CONNECTOR_NOT_FOUND
CONNECTOR_UNAVAILABLE
CONNECTOR_TIMEOUT
CONNECTOR_EXECUTION_FAILED
```

### Jobs

```text
JOB_NOT_FOUND
JOB_FAILED
JOB_INTERRUPTED
JOB_CONFLICT
```

### Cancellation

```text
CANCELLATION_UNSUPPORTED
CANCELLATION_TARGET_NOT_FOUND
CANCELLATION_FAILED
```

### Persistence

```text
PERSISTENCE_UNAVAILABLE
PERSISTENCE_TRANSACTION_FAILED
PERSISTENCE_CONFLICT
```

## 18.4 Business Errors

Applications may define additional namespaced error codes.

For example:

```text
VOICE_INVALID_PROFILE
IMAGE_WORKFLOW_INVALID
PROJECT_ALREADY_EXISTS
```

Application-specific errors must still use the standard error envelope.

## 18.5 Error Security

Error messages returned to Electron must not include:

- Sensitive credentials.
- Raw authentication tokens.
- Unnecessary environment variables.
- Internal stack traces by default.
- Private application data unrelated to the failure.

Detailed diagnostics belong in controlled logs.

---

# 19. Process Exit Codes

## 19.1 Purpose

Process exit codes communicate process-level outcomes to calling tools.

They do not replace structured protocol responses.

## 19.2 Proposed Exit-Code Categories

| Code | Meaning |
|---|---|
| `0` | Normal process completion |
| `2` | Invalid invocation or input |
| `3` | Configuration or initialization failure |
| `4` | Action execution failure |
| `5` | Timeout |
| `6` | Cancellation |
| `7` | Required dependency unavailable |
| `8` | Protocol failure |
| `10` | Internal runtime failure |

These values are proposed and require approval.

## 19.3 Persistent Mode

In persistent mode, individual action failures must not automatically cause a nonzero process exit.

The process may continue serving other requests.

The final process exit status represents the overall runtime termination outcome, not the result of the last action executed.

## 19.4 Unexpected Exit

If Python terminates before delivering a response, the Electron bridge must report a transport-level failure to the caller.

The bridge must not fabricate a successful application response.

---

# 20. Large Input and Output Handling

## 20.1 Large Payload Principle

The protocol should not carry large binary artifacts directly.

Examples include:

- Audio files.
- Generated images.
- Video files.
- Model files.
- Large workflow datasets.

## 20.2 Artifact References

Large outputs may be represented using a managed artifact descriptor.

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-020",
  "success": true,
  "data": {
    "artifact": {
      "artifact_id": "artifact-001",
      "type": "file",
      "path": "outputs/generated.wav",
      "media_type": "audio/wav"
    }
  },
  "error": null
}
```

## 20.3 Artifact Access

Artifact references must follow filesystem access controls.

The framework must define:

- Allowed storage roots.
- Path resolution.
- Artifact ownership.
- File lifetime.
- Cleanup.
- Access validation.

## 20.4 Large Inputs

Large application inputs should be submitted through managed files or another explicitly supported mechanism.

Long command-line arguments should not be the default transfer mechanism.

## 20.5 Binary Streaming

Binary streaming over the JSON protocol is not required for the initial version.

If needed later, it should use a separately versioned transport extension.

---

# 21. Health and Readiness

## 21.1 Framework Health Action

The protocol should reserve a framework action for runtime status.

Proposed action:

```text
system.health
```

## 21.2 Example

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "health-001",
  "action": "system.health",
  "payload": {}
}
```

Response:

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "health-001",
  "success": true,
  "data": {
    "application": "vani",
    "status": "ready",
    "connectors": {
      "audiocpp": "ready",
      "sqlite": "ready"
    }
  },
  "error": null
}
```

## 21.3 Health Versus Readiness

Health indicates whether the runtime is operating.

Readiness indicates whether it can accept relevant requests.

An application may be healthy while an optional external dependency is unavailable.

## 21.4 Connector Health

The framework must not assume every connector supports an equivalent health check.

Connector health information may be incomplete or unavailable.

---

# 22. Protocol Versioning and Compatibility

## 22.1 Independent Protocol Version

The protocol version is independent of:

- AdharaSutra Python package version.
- Electron bridge package version.
- Consuming application version.
- External integration version.

## 22.2 Proposed Version Format

`MAJOR.MINOR`

Example:

```text
1.0
1.1
2.0
```

## 22.3 Compatibility Rules

### Major Version

May introduce incompatible message structures or semantics.

### Minor Version

May introduce backward-compatible optional fields, events, or capabilities.

A minor-version feature must not be assumed supported until compatibility is established.

## 22.4 Compatibility Negotiation

Persistent sessions must negotiate a supported protocol version before application actions execute.

One-shot requests must validate their protocol version before dispatch.

## 22.5 Unknown Fields

The protocol must define handling for optional and unknown fields.

**Proposed rule:**

- Unknown optional fields may be ignored when explicitly permitted by the schema.
- Missing required fields are rejected.
- Unknown message kinds are rejected.
- Unknown required capabilities are rejected.

## 22.6 Deprecation

Deprecated message fields and capabilities must have documented compatibility and removal policies.

---

# 23. Reserved Framework Actions

The following reserved actions are proposed.

| Action | Purpose |
|---|---|
| `system.hello` | Session handshake |
| `system.health` | Runtime health |
| `system.version` | Version information |
| `system.capabilities` | Capability discovery |
| `system.cancel` | Cancellation |
| `system.shutdown` | Controlled shutdown |

Applications must not override these reserved actions.

Exact naming and supported execution modes will be finalized with the action-registry design.

## 23.1 Framework Action Authorization

Reserved actions must obey the same validation and authorization boundaries as ordinary application actions.

For example, `system.shutdown` must not be exposed to arbitrary untrusted callers without appropriate controls.

---

# 24. Security Architecture

## 24.1 Trust Boundary

The standard protocol operates between a local Electron main process and a Python child process.

It does not require a network listener.

However, local process communication must not be assumed secure against a compromised Electron renderer or malicious application code.

## 24.2 Action Allowlisting

Only registered and permitted actions may execute.

Unknown identifiers must never be interpreted as executable commands.

## 24.3 Process Execution Security

The Python framework must validate application-controlled external process execution according to connector policy.

Renderer-provided strings must not directly become arbitrary executable paths or shell commands.

## 24.4 Payload Validation

Protocol envelopes and registered action payloads must be validated before execution.

## 24.5 Resource Limits

The protocol must enforce or support:

- Maximum message sizes.
- Request concurrency limits.
- Bounded queues.
- Execution timeouts.
- Cancellation.
- Controlled artifact access.

## 24.6 Logging Security

Sensitive payload values must not be logged indiscriminately.

## 24.7 Session Isolation

Session identifiers are correlation aids, not authentication tokens.

Separate application instances must not accidentally share request state.

---

# 25. Electron Bridge Responsibilities

The Electron bridge is the primary protocol client.

## 25.1 Responsibilities

- Start the Python executable.
- Manage its lifecycle.
- Negotiate protocol version.
- Submit requests.
- Generate request identifiers.
- Parse responses.
- Correlate responses.
- Subscribe to events.
- Handle timeouts.
- Request cancellation.
- Handle disconnections.
- Report process failures.
- Coordinate shutdown.

## 25.2 Conceptual TypeScript API

```typescript
const result = await pythonBridge.execute(
  "voice.generate",
  {
    text: "Hello",
    voice_id: "voice-1"
  }
);
```

Progress subscription:

```typescript
const unsubscribe = pythonBridge.on(
  "job.progress",
  event => {
    console.log(event.data);
  }
);
```

Cancellation:

```typescript
await pythonBridge.cancelJob("job-123");
```

These APIs are illustrative.

The final TypeScript interface will be defined in `electron-integration.md`.

## 25.3 Bridge State

The bridge manages:

- Python process status.
- Session readiness.
- Pending requests.
- Request timeouts.
- Event subscriptions.
- Protocol compatibility.
- Shutdown state.

## 25.4 Bridge Failure Behavior

If the Python process exits unexpectedly:

1. Mark the runtime connection unavailable.
2. Reject pending requests with transport-level errors.
3. Clear invalid session resources.
4. Report the failure to Electron.
5. Follow configured restart policy.

Automatic restart must not automatically replay non-idempotent actions.

---

# 26. Representative End-to-End Protocol Scenarios

## Scenario CP-S01 — Successful Synchronous Action

```text
Electron                      Python
   │                            │
   │──── voice.list ───────────►│
   │                            │
   │                      Validate
   │                      Dispatch
   │                      Execute
   │                            │
   │◄── successful response ────│
   │                            │
```

**Expected outcome:** One correlated terminal response.

## Scenario CP-S02 — Long-Running Streaming Request

```text
Electron                      Python
   │                            │
   │──── audio.process ────────►│
   │                            │
   │◄── progress event ─────────│
   │◄── progress event ─────────│
   │◄── progress event ─────────│
   │                            │
   │◄── terminal response ──────│
   │                            │
```

**Expected outcome:** Events and final response use the same protocol.

## Scenario CP-S03 — Background Job Submission

```text
Electron                      Python
   │                            │
   │──── image.generate ───────►│
   │                            │
   │◄── accepted job-123 ───────│
   │                            │
   │◄── job.started ────────────│
   │◄── job.progress ───────────│
   │◄── job.completed ──────────│
   │                            │
```

The request completes when the job is accepted.

The job completes later under its execution owner.

## Scenario CP-S04 — Cancellation

```text
Electron                      Python
   │                            │
   │──── system.cancel ────────►│
   │                            │
   │◄── cancellation requested ─│
   │                            │
   │                      Stop Work
   │                            │
   │◄── job.cancelled ──────────│
   │                            │
```

The acknowledgment is not proof of termination.

## Scenario CP-S05 — External Dependency Failure

```text
Electron                      Python
   │                            │
   │──── voice.generate ───────►│
   │                            │
   │                      audio.cpp
   │                         fails
   │                            │
   │◄── structured error ───────│
   │                            │
```

The framework maps the failure into a standardized error envelope.

## Scenario CP-S06 — Protocol Version Mismatch

```text
Electron                      Python
   │                            │
   │──── system.hello ─────────►│
   │                            │
   │                      Incompatible
   │                            │
   │◄── protocol error ─────────│
   │                            │
   │        Session rejected    │
```

Normal actions must not execute after an incompatible handshake.

## Scenario CP-S07 — Unexpected Python Exit

```text
Electron                      Python
   │                            │
   │──── long action ──────────►│
   │                            │
   │                         Crash
   │                            X
   │
   │ Detect Process Exit
   │ Reject Pending Request
   │ Report Transport Failure
```

The bridge must not invent a successful application result.

## Scenario CP-S08 — Multiple Concurrent Requests

```text
Electron                      Python
   │                            │
   │──── Request A ────────────►│
   │──── Request B ────────────►│
   │──── Request C ────────────►│
   │                            │
   │◄── Response B ─────────────│
   │◄── Response C ─────────────│
   │◄── Response A ─────────────│
   │                            │
```

Correlation identifiers ensure correct matching.

---

# 27. Protocol Validation Rules

The following rules are proposed for deterministic validation.

| Rule ID | Description |
|---|---|
| PROTO-001 | Every message has a supported protocol version |
| PROTO-002 | Every message has a valid kind |
| PROTO-003 | Request messages contain required fields |
| PROTO-004 | Request identifiers follow the defined format |
| PROTO-005 | Active request identifiers are unique |
| PROTO-006 | Actions are registered and allowed |
| PROTO-007 | Payloads satisfy registered schemas |
| PROTO-008 | Responses follow success/error invariants |
| PROTO-009 | Correlated responses identify originating requests |
| PROTO-010 | Protocol stdout contains valid framed messages |
| PROTO-011 | Message-size limits are enforced |
| PROTO-012 | Persistent sessions complete required handshake |
| PROTO-013 | Events follow registered event schemas |
| PROTO-014 | Terminal job events obey lifecycle rules |
| PROTO-015 | Cancellation follows target-state rules |
| PROTO-016 | Incompatible protocol versions are rejected |
| PROTO-017 | Diagnostic logging does not corrupt stdout |
| PROTO-018 | Unexpected process exits invalidate pending requests |
| PROTO-019 | Request completion is distinguished from job completion |
| PROTO-020 | Protocol behavior is consistent across external connector types |

These rules require a combination of schema validation, static analysis, and executable contract tests.

---

# 28. Protocol Testing Strategy

## 28.1 Schema Tests

Verify:

- Valid request envelopes.
- Invalid request envelopes.
- Valid response envelopes.
- Error invariants.
- Event schemas.
- Version validation.

## 28.2 Framing Tests

Verify:

- Partial messages.
- Multiple messages in one read.
- Invalid UTF-8.
- Malformed JSON.
- Oversized messages.
- Escaped newline characters.
- Stream closure.

## 28.3 Correlation Tests

Verify:

- Concurrent requests.
- Out-of-order responses.
- Duplicate request identifiers.
- Unknown response identifiers.
- Request timeout.

## 28.4 Cancellation Tests

Verify:

- Cancellation accepted.
- Cancellation unsupported.
- Already completed job.
- Missing target.
- External process termination.
- Cancellation during process failure.

## 28.5 Lifecycle Tests

Verify:

- Handshake success.
- Handshake failure.
- Runtime startup.
- Runtime shutdown.
- Broken pipes.
- Unexpected Python termination.
- Electron bridge cleanup.

## 28.6 Compatibility Tests

Verify supported Python-runtime and Electron-bridge protocol combinations.

## 28.7 Connector Independence Tests

The same protocol contract tests should be run against representative actions backed by:

- Local Python code.
- HTTP connector.
- External CLI connector.
- SQLite connector.

The Electron protocol must not depend on the connector type.

---

# 29. Performance and Resource Requirements

The CLI protocol shall follow the approved non-functional requirements.

Proposed targets include:

| Metric | Proposed target |
|---|---|
| Warm dispatch p95 | ≤ 20 ms |
| Warm dispatch p99 | ≤ 50 ms |
| Progress delivery p95 | ≤ 50 ms |
| 16 KB serialization p95 | ≤ 10 ms |
| Maximum default message size | 1 MiB |
| Queue sizes | Configurable and bounded |
| Persistent session throughput | Benchmark-defined target |

These are provisional design targets.

Measurements must exclude external business execution when evaluating protocol overhead.

---

# 30. Protocol Architecture Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| CP-D01 | Primary transport | stdin/stdout |
| CP-D02 | Serialization | UTF-8 JSON |
| CP-D03 | Persistent framing | NDJSON |
| CP-D04 | Message identification | `kind` discriminator |
| CP-D05 | Request correlation | `request_id` |
| CP-D06 | Job correlation | `job_id` |
| CP-D07 | Session initialization | `system.hello` |
| CP-D08 | Error format | Structured error object |
| CP-D09 | Cancellation | Reserved `system.cancel` action |
| CP-D10 | Execution modes | One-shot and persistent |
| CP-D11 | Default Electron mode | Persistent CLI |
| CP-D12 | Background job completion | Separate lifecycle events |
| CP-D13 | Large artifacts | Managed file references |
| CP-D14 | Protocol compatibility | Version negotiation |
| CP-D15 | Logging separation | stderr diagnostics |
| CP-D16 | Concurrent requests | Supported with correlation |
| CP-D17 | Event durability | Best-effort initial protocol |
| CP-D18 | Exact-once execution | Not guaranteed |
| CP-D19 | Replay protection | Application idempotency policies |
| CP-D20 | Protocol schema storage | Versioned machine-readable contracts |

These decisions remain proposed until the architecture is reviewed.

---

# 31. Outstanding Questions

The following questions require final resolution.

## CP-OQ-001 — Startup Readiness

Should Python proactively emit an application-ready event before handshake, or should readiness be established entirely by the handshake response?

**Current recommendation:** Use the successful handshake as the authoritative session readiness signal.

## CP-OQ-002 — Request Deadlines

Should each request support an optional execution deadline in its envelope?

**Current recommendation:** Support a future optional deadline field; define timeout ownership carefully before approval.

## CP-OQ-003 — Event Sequence Numbers

Should job events include sequence numbers?

**Current recommendation:** Consider sequence numbers for detecting gaps and duplicate processing, particularly if durable jobs are introduced.

## CP-OQ-004 — Request Idempotency

Should the protocol support an optional idempotency key?

**Current recommendation:** Add this only when application storage and retry semantics are clearly defined.

## CP-OQ-005 — Capability Discovery

Should capability discovery include registered action schemas?

**Current recommendation:** Support action discovery through a framework-defined diagnostic operation.

## CP-OQ-006 — Persistent Session Restart

Should the Electron bridge automatically restart a failed Python runtime?

**Current recommendation:** Make restart policy configurable and prohibit automatic replay of non-idempotent operations.

## CP-OQ-007 — Message Size

Is 1 MiB an appropriate default maximum message size?

**Current recommendation:** Validate against representative applications and favor artifact references for large data.

## CP-OQ-008 — Protocol Schema Distribution

How should TypeScript and Python share authoritative schema definitions?

**Current recommendation:** Maintain versioned JSON Schema files and generate or validate language-specific types from them.

## CP-OQ-009 — Human-Friendly CLI Compatibility

How should legacy commands map to the unified structured protocol during migration?

**Current recommendation:** Use compatibility adapters that route legacy invocations into the same registered action handlers.

## CP-OQ-010 — Durable Event Delivery

Should durable job events support historical replay?

**Current recommendation:** Defer to the job-management architecture and avoid making event persistence mandatory for the initial protocol.

---

# 32. Functional Requirement Traceability

| Requirement group | Protocol responsibility |
|---|---|
| FR-CLI | Routing, validation, execution, serialization |
| FR-ELC | Electron communication |
| FR-RUN | Runtime lifecycle integration |
| FR-JOB | Job identifiers and lifecycle notifications |
| FR-STATE | State-related event publication |
| FR-ERR | Error envelopes |
| FR-LOG | Diagnostic separation |
| FR-SEC | Protocol validation and action restrictions |
| FR-TEST | Contract tests |
| FR-PKG | Protocol compatibility in packaged applications |
| FR-REP | Protocol versioned reporting where applicable |

---

# 33. Non-Functional Requirement Traceability

| Requirement group | Protocol mechanism |
|---|---|
| NFR-PERF | Efficient framing, dispatch, serialization |
| NFR-RES | Bounded messages and queues |
| NFR-REL | Explicit errors, correlation, terminal semantics |
| NFR-AVAIL | Session readiness and failure handling |
| NFR-SCALE | Concurrent request handling |
| NFR-SEC | Input validation and action allowlisting |
| NFR-PORT | Cross-platform process communication |
| NFR-TEST | Executable protocol contract tests |
| NFR-COMP | Version negotiation and compatibility |
| NFR-OBS | Correlation and diagnostic separation |

---

# 34. Protocol Acceptance Criteria

The CLI protocol design may be approved when:

- [ ] A canonical message envelope is defined.
- [ ] Request and response schemas are unambiguous.
- [ ] Event schemas and correlation rules are defined.
- [ ] Persistent framing is specified.
- [ ] One-shot execution semantics are specified.
- [ ] Request and job completion are distinguished.
- [ ] Session handshake and compatibility are defined.
- [ ] Concurrent request behavior is defined.
- [ ] Cancellation semantics are accurate.
- [ ] Timeout ownership is defined.
- [ ] Error categories are consistent.
- [ ] Process exit behavior is specified.
- [ ] Unexpected process failures are handled.
- [ ] Large artifact handling is defined.
- [ ] Protocol security boundaries are documented.
- [ ] Resource limits and backpressure are addressed.
- [ ] Version compatibility rules are defined.
- [ ] Electron bridge responsibilities are clear.
- [ ] Machine-readable contract generation is feasible.
- [ ] Representative HTTP, external CLI, and SQLite scenarios use the same protocol.
- [ ] Contract test coverage is defined.
- [ ] Important unresolved decisions are closed or explicitly deferred.

---

# 35. Final Protocol Summary

AdharaSutra establishes a single versioned CLI communication protocol for Python applications and Electron frontends.

The protocol uses structured JSON messages over operating-system process streams.

It supports:

- One-shot execution.
- Persistent CLI sessions.
- Application action routing.
- Typed request and response envelopes.
- Request correlation.
- Event streaming.
- Background jobs.
- Progress reporting.
- Cancellation.
- Structured errors.
- Runtime diagnostics.
- Protocol compatibility.
- Process lifecycle management.

The protocol is independent of external dependencies.

Applications may execute operations through HTTP, WebSocket, external CLI executables, SQLite, or local Python code without requiring Electron to change its communication mechanism.

AdharaSutra owns the transport, validation, routing, correlation, serialization, and protocol lifecycle.

Consuming applications own their business actions and domain-specific payloads.

The central protocol guarantee is:

**One Electron communication contract. Many independent application capabilities.**

---

# 36. Document Status

**Status:** Draft — Architecture Planning  
**Document Version:** 0.1.0  
**Proposed Protocol Version:** 1.0  
**Approval:** Pending detailed protocol review

**Next Document:** `docs/design/electron-integration.md`

The next design document will define how the Electron bridge implements this protocol, including Python process discovery, startup, readiness, request handling, IPC security, subscriptions, cancellation, crash recovery, shutdown, and production packaging.

---

**AdharaSutra — Build once. Standardize everywhere.**
