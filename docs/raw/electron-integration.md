# AdharaSutra — Electron Integration Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/electron-integration.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Platform Integration Design  
**Python Framework:** AdharaSutra  
**Electron Integration:** Shared TypeScript Bridge  
**Communication:** CLI over stdin/stdout/stderr  
**Protocol:** AdharaSutra CLI Protocol 1.0 — Proposed

**Related Documents:**
- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`

---

# 1. Purpose

This document defines how Electron applications integrate with AdharaSutra-powered Python applications.

The integration architecture must provide a reusable, standardized, secure, and reliable communication mechanism that can be shared across multiple independent Electron applications.

AdharaSutra shall provide a common TypeScript bridge that manages communication with the Python application runtime.

The bridge must eliminate the need for consuming applications to independently implement:

- Python process discovery.
- Python process startup.
- Process lifecycle management.
- CLI request serialization.
- CLI response parsing.
- Request correlation.
- Progress-event subscriptions.
- Cancellation messaging.
- Timeout management.
- Protocol compatibility negotiation.
- Python process crash detection.
- Controlled shutdown.
- Common transport error handling.

Consuming applications remain responsible for their UI, application-specific actions, and business workflows.

## 1.1 Architectural Goal

A consuming Electron application should be able to invoke its Python business capabilities through a common API, regardless of the external systems used by those capabilities.

For example:

```typescript
const result = await bridge.execute(
  "voice.generate",
  {
    text: "Hello",
    voice_id: "voice-1"
  }
);
```

The Electron bridge should not need to know whether the Python implementation uses audio.cpp, ComfyUI, LM Studio, SQLite, or another dependency.

## 1.2 Scope

This document covers:

1. Electron integration boundaries.
2. Shared TypeScript bridge responsibilities.
3. Renderer, preload, and main-process architecture.
4. Python runtime discovery.
5. Python process startup and readiness.
6. Persistent and one-shot execution modes.
7. CLI transport management.
8. Request/response correlation.
9. Streaming events and progress.
10. Cancellation.
11. Job tracking.
12. Timeouts and failure handling.
13. Process crash recovery.
14. Graceful shutdown.
15. Security.
16. Application configuration.
17. Development and production packaging.
18. Platform compatibility.
19. Testing and verification.
20. Migration from existing Electron integrations.

---

# 2. Fundamental Architectural Principles

## EI-001 — Unified Communication

All Electron-to-Python application communication shall use the versioned AdharaSutra CLI protocol.

## EI-002 — Shared Bridge

Electron applications shall use the shared AdharaSutra Electron bridge rather than independently implementing Python process communication.

## EI-003 — Main-Process Ownership

The Electron main process shall own the Python runtime process.

## EI-004 — Restricted Renderer Access

The renderer shall access Python capabilities only through explicitly exposed preload APIs.

## EI-005 — Framework-Owned Transport

The bridge shall own request serialization, response parsing, framing, correlation, and transport lifecycle.

## EI-006 — Application Business Independence

The bridge shall not implement consuming application business logic.

## EI-007 — Connector Independence

The bridge shall not depend on the external connector used by a Python action.

## EI-008 — Explicit Process Ownership

Every Python process started through the bridge shall have a defined owner and cleanup policy.

## EI-009 — Accurate Execution Outcomes

The bridge shall distinguish request completion, job acceptance, job completion, timeout, cancellation, and unknown outcomes.

## EI-010 — Versioned Compatibility

The bridge and Python runtime shall negotiate or validate compatible CLI protocol versions.

## EI-011 — Secure Defaults

The bridge shall not expose unrestricted executable invocation to renderer code.

## EI-012 — Cross-Platform Support

Process management and executable discovery shall account for differences between Windows, Linux, and macOS.

---

# 3. High-Level Architecture

## 3.1 Component Diagram

```text
┌─────────────────────────────────────────────────────┐
│                  ELECTRON APPLICATION               │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │                 RENDERER                      │  │
│  │                                               │  │
│  │  React / Vue / HTML                           │  │
│  │  UI Components                                │  │
│  │  Application Screens                          │  │
│  │  UI State                                     │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                           │
│                         ▼                           │
│  ┌───────────────────────────────────────────────┐  │
│  │                 PRELOAD                       │  │
│  │                                               │  │
│  │  Restricted Public API                        │  │
│  │  Request Validation                           │  │
│  │  Subscription Management                      │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                           │
│                         ▼                           │
│  ┌───────────────────────────────────────────────┐  │
│  │               MAIN PROCESS                    │  │
│  │                                               │  │
│  │  IPC Handlers                                 │  │
│  │  Runtime Ownership                            │  │
│  │  Application Lifecycle                        │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │       ADHARASUTRA ELECTRON BRIDGE      │  │  │
│  │  │                                         │  │  │
│  │  │  Process Manager                        │  │  │
│  │  │  Protocol Client                        │  │  │
│  │  │  Request Manager                        │  │  │
│  │  │  Event Dispatcher                       │  │  │
│  │  │  Cancellation Manager                   │  │  │
│  │  │  Compatibility Manager                  │  │  │
│  │  └──────────────────────┬──────────────────┘  │  │
│  └─────────────────────────┼─────────────────────┘  │
└────────────────────────────┼────────────────────────┘
                             │
                stdin / stdout / stderr
                             │
                             ▼
┌─────────────────────────────────────────────────────┐
│              PYTHON APPLICATION RUNTIME             │
│                                                     │
│  AdharaSutra CLI Transport                          │
│         │                                           │
│         ▼                                           │
│  Protocol Validation                                │
│         │                                           │
│         ▼                                           │
│  Action Router                                      │
│         │                                           │
│         ▼                                           │
│  Application Actions                                │
│         │                                           │
│         ▼                                           │
│  Application Use Cases                              │
│         │                                           │
│         ▼                                           │
│  Framework-Managed Connectors                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 3.2 Communication Boundary

The communication sequence shall be:

1. Renderer invokes an approved preload API.
2. Preload forwards the request through Electron IPC.
3. Main process validates the caller and requested operation.
4. Main process invokes the shared bridge.
5. Bridge serializes the request using the CLI protocol.
6. Python runtime validates and dispatches the request.
7. Application business logic executes.
8. Python returns structured responses or events.
9. Bridge parses and correlates messages.
10. Main process forwards approved results to the relevant renderer.

The renderer does not directly access Python stdin, stdout, or stderr.

---

# 4. Electron Layer Responsibilities

## 4.1 Renderer Layer

The renderer owns:

- User-interface components.
- Screen navigation.
- Form interactions.
- Presentation state.
- User-facing progress visualization.
- Application-specific UI workflows.

The renderer shall not own:

- Python executable discovery.
- Child-process creation.
- CLI message framing.
- Python runtime lifecycle.
- Direct operating-system command execution.
- Framework transport error normalization.

## 4.2 Preload Layer

The preload layer exposes a controlled API to the renderer.

Responsibilities:

- Expose approved operations.
- Validate basic argument structure.
- Forward requests through IPC.
- Manage event-subscription cleanup.
- Prevent access to unrestricted Node.js or Electron internals.

Conceptual API:

```typescript
interface ApplicationBackend {
  execute(
    action: string,
    payload: unknown
  ): Promise<unknown>;

  cancelJob(
    jobId: string
  ): Promise<unknown>;

  onEvent(
    eventName: string,
    listener: (data: unknown) => void
  ): () => void;
}
```

This is an illustrative interface.

The final preload API may use generated, application-specific action typings.

## 4.3 Main Process

The Electron main process owns:

- Python backend lifecycle.
- IPC registration.
- Renderer authorization.
- Bridge initialization.
- Application shutdown coordination.
- Backend readiness.
- Runtime error presentation.

## 4.4 Shared Bridge

The bridge provides reusable Python runtime communication.

Its responsibilities are technical and application-independent.

It shall not contain application-specific action handlers.

---

# 5. Shared Electron Bridge Package

## 5.1 Proposed Package Identity

**Package:** `@adharasutra/electron-bridge`  
**Language:** TypeScript  
**Runtime:** Electron main process / Node.js  
**Status:** Proposed

The actual package name is subject to package availability and release planning.

## 5.2 Bridge Architecture

```text
electron-bridge/
├── src/
│   ├── index.ts
│   ├── bridge.ts
│   │
│   ├── process/
│   │   ├── process-manager.ts
│   │   ├── executable-resolver.ts
│   │   ├── startup.ts
│   │   └── shutdown.ts
│   │
│   ├── protocol/
│   │   ├── types.ts
│   │   ├── serializer.ts
│   │   ├── parser.ts
│   │   ├── compatibility.ts
│   │   └── framing.ts
│   │
│   ├── requests/
│   │   ├── request-manager.ts
│   │   ├── correlation.ts
│   │   └── timeouts.ts
│   │
│   ├── events/
│   │   ├── event-dispatcher.ts
│   │   └── subscriptions.ts
│   │
│   ├── jobs/
│   │   ├── job-client.ts
│   │   └── cancellation.ts
│   │
│   ├── errors/
│   │   ├── bridge-error.ts
│   │   └── error-mapping.ts
│   │
│   └── platform/
│       ├── windows.ts
│       ├── linux.ts
│       └── macos.ts
│
├── tests/
├── package.json
└── tsconfig.json
```

This structure describes logical responsibilities.

It may be simplified during implementation as long as the boundaries remain explicit.

---

# 6. Python Runtime Discovery

## 6.1 Purpose

Electron must locate the Python application runtime before launching it.

The bridge must support development and production deployment arrangements.

## 6.2 Supported Runtime Forms

The architecture shall accommodate:

1. Python module execution through an installed interpreter.
2. An application-specific Python virtual environment.
3. A bundled Python interpreter and application package.
4. A frozen or otherwise packaged Python executable.

Not every application must support every form.

## 6.3 Runtime Resolution Policy

Runtime discovery shall follow an explicit ordered configuration.

A proposed order is:

1. Application-provided executable configuration.
2. Packaged application runtime manifest.
3. Approved development runtime configuration.
4. Explicitly enabled system-runtime discovery.

System `PATH` discovery should not be assumed in production.

## 6.4 Executable Validation

Before launching the backend, the bridge shall validate:

- Executable existence.
- File type and basic accessibility.
- Platform compatibility where determinable.
- Required arguments.
- Allowed launch configuration.
- Required working directory.

Production applications should use known executable locations rather than arbitrary renderer-provided paths.

## 6.5 Runtime Manifest

Packaged applications should include a runtime manifest.

Conceptual example:

```json
{
  "runtime": {
    "type": "bundled-python",
    "platform": "win32",
    "executable": "python/python.exe",
    "module": "my_application",
    "protocol": "1.0"
  }
}
```

The exact manifest schema will be defined in the packaging design.

Manifest paths must be resolved relative to approved package resource roots, not untrusted working directories.

---

# 7. Python Process Lifecycle

## 7.1 Process State Model

The Electron bridge shall manage an explicit process state machine.

```text
STOPPED
   │
   ▼
STARTING
   │
   ▼
INITIALIZING
   │
   ▼
HANDSHAKING
   │
   ▼
READY
   │
   ▼
RUNNING
   │
   ├────────► FAILED
   │
   ▼
STOPPING
   │
   ▼
STOPPED
```

`READY` indicates successful runtime initialization and protocol handshake.

`RUNNING` indicates the runtime is accepting or executing operations.

These states should not imply exclusive execution.

## 7.2 Startup Sequence

```text
Electron Main
     │
     ▼
Resolve Runtime
     │
     ▼
Validate Launch Configuration
     │
     ▼
Spawn Python Process
     │
     ▼
Attach stdout/stderr Handlers
     │
     ▼
Initialize Protocol Parser
     │
     ▼
Wait for Transport Availability
     │
     ▼
Send system.hello
     │
     ▼
Validate Handshake Response
     │
     ▼
Mark Bridge READY
     │
     ▼
Allow Application Requests
```

## 7.3 Startup Failure

The bridge must detect:

- Executable not found.
- Permission denied.
- Invalid working directory.
- Process exits during initialization.
- Handshake timeout.
- Unsupported protocol version.
- Invalid handshake response.
- Required backend initialization failure.

The bridge must report a structured startup error.

## 7.4 Startup Timeout

A configurable startup timeout shall be supported.

The timeout must cover process startup and required handshake completion according to documented policy.

If startup fails, the bridge shall terminate or clean up the process it owns.

## 7.5 Readiness

The successful protocol handshake is the authoritative readiness signal for the initial design.

Ordinary application requests shall not be sent before the bridge reaches the ready state.

---

# 8. Persistent CLI Integration

## 8.1 Default Electron Mode

Persistent CLI communication is the recommended default for interactive Electron applications.

This allows one Python runtime to retain initialized services and connectors across requests.

## 8.2 Process Model

```text
Electron Main
      │
      ▼
One Managed Python Runtime
      │
      ├── Request A
      ├── Request B
      ├── Request C
      │
      ├── Job Events
      └── State Events
```

The standard bridge shall not spawn a new Python process for each request in persistent mode.

## 8.3 Request Multiplexing

Multiple requests may be active concurrently.

The bridge must correlate responses using request identifiers.

Responses may arrive in a different order from requests.

## 8.4 Session Ownership

The bridge owns the client-side session state.

The Python runtime owns the server-side session state.

Session identifiers are correlation metadata, not authentication credentials.

## 8.5 Persistent Resource Behavior

Python-managed resources may remain initialized while the persistent runtime is active.

Examples include:

- HTTP client connection pools.
- SQLite connections.
- External service adapters.
- Application state.
- Job managers.

Each resource must follow its declared lifecycle.

---

# 9. One-Shot CLI Integration

## 9.1 Purpose

One-shot execution is supported for:

- Independent operations.
- Diagnostics.
- Automation.
- Short-lived commands.
- Applications without persistent state requirements.

## 9.2 Process Model

```text
Electron / CLI Caller
       │
       ▼
Start Python Process
       │
       ▼
Send One Request
       │
       ▼
Receive Result
       │
       ▼
Process Exits
```

## 9.3 Bridge Requirements

The bridge may expose a one-shot execution helper.

It must:

- Launch the configured executable.
- Submit one structured request.
- Read protocol messages.
- Detect terminal response.
- Observe process exit.
- Enforce timeouts.
- Clean up resources.

## 9.4 One-Shot Limitations

One-shot mode must not assume:

- In-memory state survives between invocations.
- Connections remain initialized.
- Jobs continue after the process exits.
- Events can be replayed after termination.

---

# 10. Protocol Communication

## 10.1 Protocol Ownership

The Python runtime and TypeScript bridge shall implement the same versioned protocol contract.

The protocol definition is owned by AdharaSutra, not by individual applications.

## 10.2 Standard Request

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "req-001",
  "action": "voice.generate",
  "payload": {
    "text": "Hello"
  }
}
```

## 10.3 Standard Response

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

## 10.4 Transport Framing

The bridge shall implement UTF-8 newline-delimited JSON framing.

It must correctly handle:

- Partial stream reads.
- Multiple messages per read.
- Escaped newlines.
- Malformed JSON.
- Oversized messages.
- Stream termination.
- Buffer limits.

## 10.5 stdout and stderr

The bridge shall treat stdout as the structured protocol stream.

stderr shall be captured separately for diagnostics.

Ordinary stderr output must not be interpreted as successful application results.

## 10.6 Protocol Schema Validation

Incoming messages shall be validated against the supported protocol schema.

Unexpected message kinds and invalid required fields shall be rejected or treated as protocol faults according to the documented error policy.

---

# 11. Request Management

## 11.1 Request Registry

The bridge shall maintain a registry of active requests.

Conceptual structure:

```typescript
interface PendingRequest {
  requestId: string;
  action: string;
  createdAt: number;
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
}
```

Actual implementation must also manage timeout and cancellation resources safely.

## 11.2 Request Lifecycle

```text
CREATED
   │
   ▼
QUEUED
   │
   ▼
SENT
   │
   ▼
AWAITING_RESPONSE
   │
   ├────────► COMPLETED
   │
   ├────────► FAILED
   │
   ├────────► TIMED_OUT
   │
   └────────► DISCONNECTED
```

Cancellation may be requested while a request is active.

A caller-side cancellation does not automatically guarantee remote execution termination.

## 11.3 Request Identifiers

The bridge shall generate request identifiers that are unique among active requests in the current session.

## 11.4 Response Correlation

Each incoming response shall be matched to a pending request using `request_id`.

Unrecognized or duplicate terminal responses shall be handled as protocol anomalies.

## 11.5 Out-of-Order Responses

The bridge shall support out-of-order completion of concurrently active requests.

## 11.6 Request Cleanup

When a request reaches a terminal client-side state, the bridge shall release:

- Pending request registrations.
- Timeout resources.
- Cancellation listeners.
- Request-specific subscriptions.

The bridge must retain sufficient bounded diagnostic information to recognize late responses.

---

# 12. Event and Progress Management

## 12.1 Event Dispatcher

The bridge shall maintain an event dispatcher for structured Python events.

## 12.2 Event Subscription

Electron consumers shall be able to subscribe to approved event categories.

Conceptual example:

```typescript
const unsubscribe = bridge.on(
  "job.progress",
  event => {
    console.log(event.data);
  }
);
```

## 12.3 Event Filtering

Subscriptions should support filtering by relevant correlation identifiers.

Examples:

- Request ID.
- Job ID.
- Event name.

This prevents unrelated progress events from being mixed into the wrong UI operation.

## 12.4 Subscription Cleanup

Subscriptions must be removed when:

- The subscriber unsubscribes.
- The associated renderer is destroyed.
- The bridge shuts down.
- The session becomes invalid.

## 12.5 Event Ordering

The bridge shall preserve the order in which complete messages are received from stdout.

It must not assume different jobs emit events in a globally meaningful sequence.

## 12.6 Progress Accuracy

The bridge shall display or forward progress supplied by Python.

It shall not invent percentage completion.

## 12.7 Event Backpressure

The bridge shall support bounded event buffering and an explicit overload policy.

Low-value repetitive progress notifications may be coalesced where allowed.

Terminal job events must not be silently discarded.

---

# 13. Job Management Integration

## 13.1 Separation of Responsibilities

The Python job manager owns actual job execution and lifecycle.

The Electron bridge acts as a client for job operations.

## 13.2 Job Submission

An application action may return:

```json
{
  "job_id": "job-123",
  "status": "accepted"
}
```

This means a job was accepted by an execution owner.

It does not indicate completion.

## 13.3 Job Tracking

The bridge should support:

- Job identifiers.
- Job status queries.
- Progress subscriptions.
- Terminal job events.
- Cancellation requests.

## 13.4 Job Completion

A job may complete after the original request's terminal response.

The bridge must not keep the original request pending solely because an accepted job remains active.

## 13.5 Missed Events

The initial protocol does not guarantee event replay.

If a renderer subscribes after a job starts, the UI should retrieve current status through a supported job query rather than assuming all historical events will arrive.

The corresponding reserved job-status action must be defined in the CLI protocol design before implementation.

## 13.6 Renderer Independence

Closing a renderer window must not automatically cancel every Python job unless the application explicitly defines that ownership behavior.

Job lifecycle ownership belongs to the Python runtime.

---

# 14. Cancellation Architecture

## 14.1 Cancellation Request

The bridge shall use the standard framework cancellation action.

Example:

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

## 14.2 Cancellation Acknowledgment

The response may indicate:

- Cancellation requested.
- Target not found.
- Cancellation unsupported.
- Target already completed.
- Cancellation failed.

## 14.3 Cancellation Completion

The bridge shall distinguish cancellation acknowledgment from confirmed termination.

Confirmed cancellation is determined by the job or request's actual terminal state.

## 14.4 Cancellation Races

The bridge must handle:

- Completion before cancellation.
- Repeated cancellation.
- Cancellation after failure.
- Python process exit during cancellation.
- Timeout while waiting for cancellation.
- External process ignoring cancellation.

## 14.5 Cancellation API

Conceptual interface:

```typescript
await bridge.cancelJob("job-123");
```

The API must document whether it waits for acknowledgment or actual terminal cancellation.

A separate status or completion promise may be required.

---

# 15. Timeout Architecture

## 15.1 Timeout Categories

The Electron bridge shall manage:

- Process startup timeout.
- Handshake timeout.
- Request response timeout.
- Cancellation acknowledgment timeout.
- Graceful shutdown timeout.

Python manages its own execution, connector, process, and job timeouts.

## 15.2 Timeout Ownership

The bridge shall not assume that a local request timeout terminates remote Python work.

## 15.3 Timeout Result

When the bridge stops waiting for a response, it shall report a client-side timeout.

If remote execution status is unknown, that uncertainty must be preserved.

## 15.4 Timeout Defaults

Timeout defaults should depend on operation category.

Long-running job submission should generally have a shorter acknowledgment timeout than the overall job execution deadline.

Exact values will be validated during implementation design and benchmarking.

## 15.5 Automatic Retry

The bridge shall not automatically retry non-idempotent actions following a timeout or disconnection.

Retry eligibility must be explicit.

---

# 16. Python Process Crash Detection

## 16.1 Failure Conditions

The bridge shall detect:

- Python process exits unexpectedly.
- Python process terminates without returning a terminal response.
- stdout closes unexpectedly.
- stdin becomes unavailable.
- Protocol parsing becomes unrecoverably invalid.
- Required handshake fails.

## 16.2 Pending Requests

When the Python process terminates unexpectedly:

1. Mark the session unavailable.
2. Reject unresolved pending requests with transport-level errors.
3. Preserve the fact that remote business outcomes may be unknown.
4. Release request-specific resources.
5. Emit a runtime failure notification.
6. Follow the configured restart policy.

## 16.3 Diagnostic Capture

The bridge should retain bounded, sanitized diagnostic information from recent stderr output.

This may be used to explain startup or runtime failures.

## 16.4 Crash Recovery

The bridge may support restarting the Python process.

Restart must create a new protocol session.

Previously active in-memory request state cannot be assumed to survive.

## 16.5 Retry Safety

Automatic process restart must not automatically replay application actions.

An action may have completed before the process or communication channel failed.

The bridge must not risk repeating a side-effecting operation without an explicit idempotency contract.

---

# 17. Restart and Recovery Policy

## 17.1 Restart Modes

Proposed restart policies:

| Policy | Behavior |
|---|---|
| Disabled | Do not restart automatically |
| Manual | Restart only when explicitly requested |
| On crash | Restart after unexpected termination |
| Limited retry | Restart up to a configured limit |

## 17.2 Recommended Default

For interactive desktop applications:

- Permit configurable restart on crash.
- Limit repeated restart attempts.
- Apply a delay or backoff between attempts.
- Do not replay pending actions automatically.
- Report recovery attempts to the application.

## 17.3 Persistent State

Python process restart may restore application state only through explicitly configured persistent storage.

## 17.4 Job Recovery

Job recovery is controlled by Python's job subsystem.

The Electron bridge must not infer that jobs resumed merely because the Python process restarted.

---

# 18. Graceful Shutdown

## 18.1 Shutdown Sequence

```text
Electron Shutdown Requested
          │
          ▼
Stop Accepting New UI Requests
          │
          ▼
Notify Python Runtime
          │
          ▼
Python Begins Graceful Shutdown
          │
          ▼
Complete / Cancel / Transfer Jobs
          │
          ▼
Close Connectors and State Stores
          │
          ▼
Python Process Exits
          │
          ▼
Bridge Cleans Up Resources
          │
          ▼
Electron Terminates
```

## 18.2 Shutdown Request

The bridge may invoke the reserved framework action:

`system.shutdown`

This action must be restricted to authorized callers.

## 18.3 Shutdown Deadline

Shutdown must have a configurable deadline.

When the deadline expires, the bridge may escalate to process termination according to platform-specific policies.

## 18.4 Active Jobs

The shutdown policy shall define whether active jobs are:

- Allowed to finish.
- Cancelled.
- Marked interrupted.
- Transferred to a supported durable worker.

Transfer is permitted only where an actual durable execution mechanism exists.

## 18.5 Unexpected Electron Termination

The design must account for cases where Electron crashes or is forcibly terminated before graceful shutdown is possible.

Python process ownership and orphan cleanup require explicit platform-specific handling.

---

# 19. Electron IPC Security

## 19.1 Trust Boundaries

The renderer is not trusted to perform arbitrary operating-system operations.

The main process shall validate access to backend capabilities.

## 19.2 Context Isolation

The recommended Electron configuration uses:

- Context isolation enabled.
- Node integration disabled in the renderer.
- A restricted preload API.
- Explicit IPC handlers.

## 19.3 Action Allowlisting

The Electron application should expose approved business actions or approved action namespaces.

The bridge must not turn arbitrary renderer strings into shell commands.

## 19.4 IPC Caller Validation

Main-process IPC handlers should verify the originating web contents and expected frame or window context.

Unexpected senders must be rejected.

## 19.5 Event Exposure

Only approved backend events should be forwarded to renderer subscribers.

Sensitive diagnostic events should remain inside the main process or authorized diagnostics facilities.

## 19.6 Filesystem and Executable Paths

Renderer-supplied paths must not be automatically trusted.

Access to local files and executable configuration must follow explicit validation and authorization policies.

## 19.7 Security Boundary

The bridge is a technical communication component, not a general-purpose unrestricted remote execution service.

---

# 20. Large Artifact Integration

## 20.1 Principle

Large binary artifacts shall not be embedded in normal CLI JSON responses.

## 20.2 Artifact References

Python may return managed artifact descriptors.

Example:

```json
{
  "artifact_id": "artifact-001",
  "type": "file",
  "path": "outputs/generated.wav",
  "media_type": "audio/wav"
}
```

## 20.3 Artifact Access

The Electron main process shall validate artifact references before exposing files to the renderer.

The design must account for:

- Authorized storage locations.
- Canonical path resolution.
- Symbolic links.
- File lifetime.
- Cleanup.
- Media handling.
- Application-specific access policies.

## 20.4 Renderer Consumption

Applications may expose approved local resources through secure mechanisms.

The renderer must not gain unrestricted filesystem access merely because Python returned a path.

## 20.5 Artifact Lifecycle

The framework should support identifying whether an artifact is:

- Temporary.
- Persistent.
- Application-owned.
- Job-owned.

The application determines business retention policies.

---

# 21. Application-Specific Electron Integration

## 21.1 Application Ownership

Every consuming application defines its own action semantics and UI.

It does not implement its own transport protocol.

## 21.2 Typed Application Client

A consuming application may wrap the generic bridge in a typed client.

Example:

```typescript
class VoiceClient {
  constructor(
    private bridge: AdharaSutraBridge
  ) {}

  async generate(
    text: string,
    voiceId: string
  ) {
    return this.bridge.execute(
      "voice.generate",
      {
        text,
        voice_id: voiceId
      }
    );
  }
}
```

This wrapper represents application-specific action semantics.

It must not recreate process or protocol management.

## 21.3 Generated Types

The framework should support generating TypeScript request and response types from application action schemas.

This is a proposed enhancement.

Generated types must be traceable to authoritative action contracts.

## 21.4 UI Framework Independence

The bridge shall not require React, Vue, Angular, or another renderer UI framework.

It should remain usable with any supported Electron renderer architecture.

---

# 22. Development Environment Integration

## 22.1 Development Mode

During development, Electron may launch the application through a local Python environment.

Example conceptual configuration:

```json
{
  "python": {
    "mode": "development",
    "executable": ".venv/bin/python",
    "module": "my_application"
  }
}
```

This Unix-style executable path is illustrative. Windows development configuration requires a platform-appropriate path.

## 22.2 Development Benefits

The bridge should support:

- Visible backend logs.
- Backend readiness reporting.
- Action debugging.
- Configurable startup parameters.
- Controlled process restart.

## 22.3 Development Safety

Development-only capabilities must not be unintentionally exposed in production packages.

## 22.4 Hot Reloading

Frontend hot reloading and Python backend restarting should be independently configurable.

The bridge should not restart the backend unnecessarily when only renderer code changes.

---

# 23. Production Packaging Architecture

## 23.1 Packaging Goal

A packaged Electron application must reliably locate and launch its Python backend without relying on an undeclared development environment.

## 23.2 Supported Packaging Approaches

### Approach A — Bundled Python Environment

Package a Python interpreter and required application dependencies.

Advantages:

- Closely matches Python execution semantics.
- Supports ordinary package layouts.

Tradeoffs:

- Larger distribution.
- Dependency bundling complexity.
- Platform-specific runtime management.

### Approach B — Frozen Python Executable

Compile or bundle the Python application into a standalone executable using an appropriate packaging tool.

Advantages:

- Simplifies launch discovery.
- May reduce dependency on a separate interpreter layout.

Tradeoffs:

- Compatibility and packaging issues with native dependencies.
- Potential startup overhead.
- Platform-specific build requirements.

### Approach C — Externally Installed Runtime

Use a separately installed Python environment.

This should be treated as an explicitly supported deployment mode rather than the default assumption for end-user desktop packages.

## 23.3 Proposed Direction

Support bundled and frozen runtime strategies through a common runtime manifest and executable resolver.

Choose the preferred default only after packaging prototypes are validated against representative applications.

## 23.4 Platform Packaging

Production validation should cover:

- Windows.
- Linux.
- macOS.

Where supported, packaging must account for:

- Executable paths.
- Resource locations.
- File permissions.
- Native dependencies.
- Code signing requirements.
- Platform process termination.
- Installer and update behavior.

---

# 24. Electron Package Structure

A consuming application may use:

```text
my-application/
├── electron/
│   ├── src/
│   │   ├── main/
│   │   │   ├── index.ts
│   │   │   ├── bridge.ts
│   │   │   └── ipc.ts
│   │   │
│   │   ├── preload/
│   │   │   └── index.ts
│   │   │
│   │   └── renderer/
│   │       ├── components/
│   │       ├── pages/
│   │       └── services/
│   │
│   ├── resources/
│   │   └── runtime-manifest.json
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── src/
│   └── my_application/
│       ├── app.py
│       ├── application/
│       ├── domain/
│       └── infrastructure/
│
└── tests/
```

The shared bridge is installed as a dependency rather than copied into each application.

---

# 25. Platform-Specific Considerations

## 25.1 Windows

The design must account for:

- Windows executable extensions.
- Process creation behavior.
- Child-process termination.
- Paths containing spaces.
- Packaged runtime locations.
- Native DLL dependencies.
- Installer-specific resource paths.

## 25.2 Linux

The design must account for:

- Executable permissions.
- Process signals.
- Child-process cleanup.
- Distribution-dependent runtime dependencies.
- AppImage or other supported package layouts.
- Symbolic links.

## 25.3 macOS

The design must account for:

- Application bundle layout.
- Executable permissions.
- Code signing.
- Notarization requirements.
- Runtime resource paths.
- Architecture compatibility.
- Child-process behavior.

## 25.4 Cross-Platform Abstraction

Platform-specific code should remain behind the bridge's runtime resolver and process-management interfaces.

Application business logic should not depend on platform-specific launch behavior.

---

# 26. Error Model

The bridge must distinguish errors originating from different layers.

| Error category | Example |
|---|---|
| Runtime discovery | Python executable missing |
| Process startup | Python failed to launch |
| Handshake | Unsupported protocol |
| Transport | Broken pipe |
| Protocol | Invalid response envelope |
| Request | Unknown action |
| Application | Domain validation failure |
| Connector | External dependency unavailable |
| Job | Job execution failure |
| Timeout | Caller stopped waiting |
| Cancellation | Cancellation unsupported |
| Shutdown | Backend failed to terminate |

## 26.1 Application Errors

A structured Python error response should become a typed application/remote error in TypeScript.

## 26.2 Transport Errors

Transport failures must remain distinguishable from application errors.

## 26.3 Unknown Outcomes

If a request may have executed but no response was received, the bridge should expose that uncertainty.

It must not falsely classify the operation as safely retryable.

---

# 27. Compatibility and Versioning

## 27.1 Independent Versions

The architecture distinguishes:

- Electron bridge package version.
- AdharaSutra Python runtime version.
- CLI protocol version.
- Consuming application version.
- Application action contract version.

## 27.2 Compatibility Negotiation

Persistent sessions shall negotiate supported protocol versions during handshake.

## 27.3 Version Mismatch

Unsupported combinations must fail explicitly.

## 27.4 Type Compatibility

Generated TypeScript types should correspond to versioned action schemas.

## 27.5 Framework Upgrade

Applications should be able to upgrade bridge and runtime components without rewriting business logic, provided relevant contracts remain compatible.

---

# 28. Migration From Existing Electron Applications

## 28.1 Objective

Existing Electron applications may contain custom Python subprocess communication.

The migration approach must preserve current behavior while introducing the shared bridge.

## 28.2 Migration Stages

### Stage 1 — Inspect

Identify:

- Python process startup.
- CLI command construction.
- Electron IPC handlers.
- stdout parsing.
- stderr handling.
- Progress handling.
- Error handling.
- Cancellation.
- Shutdown behavior.

### Stage 2 — Baseline

Capture existing action contracts and behavioral tests.

### Stage 3 — Introduce Bridge

Use the shared bridge in Electron main.

### Stage 4 — Add Compatibility Layer

Map existing Electron operations to registered AdharaSutra actions.

### Stage 5 — Migrate Protocol

Replace custom communication with the unified structured protocol.

### Stage 6 — Migrate Events and Jobs

Move progress, cancellation, and job tracking to standard framework facilities.

### Stage 7 — Remove Legacy Transport

Remove obsolete custom communication code after regression verification.

### Stage 8 — Verify

Run protocol, Electron, application, and packaged-runtime tests.

## 28.3 Compatibility Requirement

Existing application business behavior must remain unchanged unless explicitly authorized.

Migration should not require rewriting domain algorithms simply to adopt the bridge.

---

# 29. Testing Strategy

## 29.1 Unit Tests

Validate:

- Runtime resolver.
- Process manager.
- Protocol parser.
- Serializer.
- Request correlation.
- Event dispatcher.
- Timeout manager.
- Error mapping.
- Subscription cleanup.

## 29.2 Protocol Contract Tests

Validate compatibility against the Python protocol implementation.

Required scenarios:

- Valid request.
- Valid response.
- Error response.
- Progress events.
- Job acceptance.
- Cancellation.
- Version mismatch.
- Malformed messages.

## 29.3 Process Integration Tests

Use a controlled Python test application.

Validate:

- Startup.
- Handshake.
- Concurrent requests.
- Long-running operations.
- Process crash.
- Restart.
- Shutdown.

## 29.4 Electron Integration Tests

Use a real Electron main/preload/renderer test environment.

Validate:

- IPC boundaries.
- Approved action invocation.
- Event forwarding.
- Subscription cleanup.
- Renderer destruction.
- Window recreation.
- Backend lifecycle.

## 29.5 Security Tests

Validate:

- Unauthorized IPC senders.
- Invalid action identifiers.
- Unexpected renderer payloads.
- Unsafe executable paths.
- Artifact path traversal.
- Malformed protocol messages.

## 29.6 Packaging Tests

Test actual packaged applications.

Validation must not be limited to development-mode execution.

---

# 30. Performance Requirements

The Electron bridge should satisfy approved protocol overhead targets.

Proposed measurements:

| Metric | Proposed target |
|---|---|
| Bridge request overhead p95 | ≤ 20 ms in a warmed runtime |
| Progress event delivery p95 | ≤ 50 ms |
| Protocol message size | Default maximum 1 MiB |
| Request concurrency | Configurable |
| Event buffering | Bounded |
| Startup timeout | Configurable |
| Graceful shutdown timeout | Configurable |

These are preliminary engineering targets.

Actual acceptance thresholds require benchmark validation.

Performance measurements should distinguish Electron IPC, bridge processing, Python protocol handling, and application execution.

---

# 31. Electron Integration Verification Rules

The architecture verifier should detect applicable violations.

| Rule ID | Rule |
|---|---|
| EI-VER-001 | Electron main owns Python process creation |
| EI-VER-002 | Renderer does not directly execute Python |
| EI-VER-003 | Renderer uses approved preload APIs |
| EI-VER-004 | Python communication uses the shared bridge |
| EI-VER-005 | Bridge uses the supported protocol version |
| EI-VER-006 | Application does not implement a competing Python communication protocol |
| EI-VER-007 | stdout protocol framing is preserved |
| EI-VER-008 | stderr diagnostics are handled separately |
| EI-VER-009 | Request correlation is enforced |
| EI-VER-010 | Event subscriptions have cleanup mechanisms |
| EI-VER-011 | Cancellation uses standard protocol operations |
| EI-VER-012 | Process failures invalidate pending requests |
| EI-VER-013 | Unsupported protocol combinations are rejected |
| EI-VER-014 | Packaged runtime paths are configured |
| EI-VER-015 | Unsafe renderer process-execution access is prohibited |
| EI-VER-016 | Artifact paths follow defined access restrictions |

Some requirements need runtime tests or review and cannot be proven through source inspection alone.

---

# 32. End-to-End Scenarios

## Scenario EI-S01 — Normal Request

**Given** an Electron application has a ready Python runtime,

**When** the renderer invokes an approved action,

**Then** the preload forwards the request through main-process IPC.

**And** the bridge sends a valid CLI request.

**And** the response is correlated and returned to the requesting renderer.

## Scenario EI-S02 — HTTP-Based Backend

**Given** an action uses a ComfyUI-style HTTP integration,

**When** Electron invokes the action,

**Then** the bridge uses the normal CLI protocol.

**And** no Electron-side HTTP integration is required for that business action.

## Scenario EI-S03 — External CLI Backend

**Given** an action uses an audio.cpp-style executable,

**When** Electron invokes the action,

**Then** the bridge uses the same CLI protocol.

**And** Python manages external process execution through AdharaSutra.

## Scenario EI-S04 — Long-Running Job

**Given** an action starts a managed job,

**When** the job reports progress,

**Then** the bridge forwards the appropriate events to authorized subscribers.

**And** the original job-submission request remains completed after acknowledgment.

## Scenario EI-S05 — Cancellation

**Given** a running job,

**When** Electron requests cancellation,

**Then** the bridge sends the standard cancellation request.

**And** reports acknowledgment separately from confirmed termination.

## Scenario EI-S06 — Python Crash

**Given** Python terminates unexpectedly during a request,

**When** the bridge detects process exit,

**Then** pending requests are rejected with transport-level failures.

**And** the bridge does not report successful execution.

## Scenario EI-S07 — Renderer Reload

**Given** the renderer reloads while the Python runtime remains active,

**When** the new renderer initializes,

**Then** it can reconnect through the main-process bridge.

**And** stale renderer subscriptions are removed.

## Scenario EI-S08 — Protocol Mismatch

**Given** an incompatible bridge and Python runtime,

**When** handshake occurs,

**Then** the session is rejected.

**And** normal business actions do not execute.

## Scenario EI-S09 — Packaged Application

**Given** a packaged Electron application,

**When** the application launches,

**Then** the main process resolves the bundled or configured Python runtime.

**And** launches it without relying on an undeclared development environment.

## Scenario EI-S10 — Controlled Shutdown

**Given** Electron is closing,

**When** the shutdown procedure begins,

**Then** the bridge stops accepting new work.

**And** requests Python shutdown.

**And** applies configured deadlines and cleanup policies.

---

# 33. Architecture Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| EI-D01 | Electron communication | CLI protocol |
| EI-D02 | Shared integration | TypeScript bridge |
| EI-D03 | Python process owner | Electron main |
| EI-D04 | Renderer access | Restricted preload API |
| EI-D05 | Default process mode | Persistent CLI |
| EI-D06 | Request tracking | Correlation registry |
| EI-D07 | Event handling | Bridge event dispatcher |
| EI-D08 | Job tracking | Python-owned job lifecycle |
| EI-D09 | Cancellation | Standard framework action |
| EI-D10 | Startup readiness | Protocol handshake |
| EI-D11 | Crash recovery | Configurable bounded restart |
| EI-D12 | Automatic replay | Disabled unless explicitly safe |
| EI-D13 | Runtime discovery | Configuration and packaged manifest |
| EI-D14 | Large artifacts | Managed file references |
| EI-D15 | Cross-platform logic | Isolated platform adapters |
| EI-D16 | Protocol schemas | Shared versioned contracts |
| EI-D17 | UI framework coupling | None |
| EI-D18 | Production packaging | Bundled or frozen Python |

These remain design proposals until reviewed and finalized.

---

# 34. Outstanding Questions

## EI-OQ-001 — Default Python Packaging Strategy

Should packaged Electron applications default to a bundled Python environment or a frozen executable?

**Recommendation:** Validate both through production prototypes before selecting a default.

## EI-OQ-002 — Multiple Python Runtime Instances

Should one Electron application support multiple independent AdharaSutra Python processes?

**Recommendation:** Start with one managed runtime per application and permit explicit additional instances only where justified.

## EI-OQ-003 — Background Job Persistence

Should an Electron restart be able to reconnect to previously running durable jobs?

**Recommendation:** Support this only when Python has an actual durable execution service and stable job-status API.

## EI-OQ-004 — Automatic Process Restart

Should the bridge restart Python automatically after a crash?

**Recommendation:** Support configurable bounded restart, but never automatically replay unknown-outcome business actions.

## EI-OQ-005 — Type Generation

Should the bridge generate TypeScript action clients from Python action schemas?

**Recommendation:** Include this as a high-value developer feature after protocol contracts stabilize.

## EI-OQ-006 — Multiple Renderer Windows

Should the bridge expose per-window authorization, event routing, and subscription ownership?

**Recommendation:** Yes. The bridge should support multiple renderers without leaking requests or events between unauthorized consumers.

## EI-OQ-007 — Backend Logging Presentation

Should applications expose Python stderr directly to users?

**Recommendation:** No. Provide controlled diagnostics with redaction and bounded retention.

## EI-OQ-008 — Artifact Access

Should the bridge supply a dedicated artifact-serving mechanism?

**Recommendation:** Prefer explicit, validated artifact access rather than unrestricted local paths. The exact transport should be finalized in the artifact-management design.

## EI-OQ-009 — Runtime Readiness Feedback

How should Electron display backend initialization and external dependency readiness?

**Recommendation:** Keep runtime readiness distinct from optional connector health.

## EI-OQ-010 — Bridge Distribution

Should the bridge package remain generic or include optional Electron helper modules?

**Recommendation:** Keep the core bridge generic, with optional helpers for IPC registration, packaging, and typed application clients.

---

# 35. Functional Requirements Traceability

| Functional requirement group | Integration responsibility |
|---|---|
| FR-ELC | Shared Electron communication |
| FR-CLI | Protocol and routing integration |
| FR-RUN | Runtime lifecycle |
| FR-JOB | Job status, progress and cancellation |
| FR-STATE | State-event delivery |
| FR-ERR | Error normalization |
| FR-LOG | Diagnostic capture |
| FR-CFG | Runtime configuration |
| FR-SEC | IPC and process security |
| FR-PKG | Python runtime packaging |
| FR-TEST | Contract and integration tests |
| FR-MIG | Existing Electron migration |

---

# 36. Non-Functional Requirements Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-PERF | Persistent runtime and efficient protocol handling |
| NFR-RES | Bounded queues and resource cleanup |
| NFR-REL | Process monitoring and explicit failure semantics |
| NFR-AVAIL | Startup readiness and controlled recovery |
| NFR-SCALE | Concurrent request correlation |
| NFR-SEC | Main-process ownership and restricted IPC |
| NFR-PORT | Cross-platform runtime resolution |
| NFR-TEST | Bridge and Electron integration tests |
| NFR-COMP | Protocol compatibility negotiation |
| NFR-OBS | Diagnostic and request correlation |
| NFR-OPS | Production runtime packaging |
| NFR-MIG | Incremental bridge adoption |

---

# 37. Acceptance Criteria

The Electron integration design may be approved when:

- [ ] Electron main, preload, and renderer responsibilities are defined.
- [ ] The shared bridge owns Python communication.
- [ ] Python runtime discovery supports development and production.
- [ ] Process lifecycle states are defined.
- [ ] Startup and handshake behavior are unambiguous.
- [ ] Persistent and one-shot modes are supported conceptually.
- [ ] Request correlation is defined.
- [ ] Out-of-order responses are supported.
- [ ] Event subscriptions and cleanup are defined.
- [ ] Job acknowledgment and completion are distinct.
- [ ] Cancellation semantics are accurate.
- [ ] Timeout ownership is explicit.
- [ ] Process crashes invalidate pending requests.
- [ ] Recovery policy does not replay unsafe actions.
- [ ] Shutdown and orphan-process handling are addressed.
- [ ] IPC authorization and renderer restrictions are defined.
- [ ] Artifact access does not expose unrestricted filesystem access.
- [ ] Protocol compatibility is validated.
- [ ] Platform-specific behavior is isolated.
- [ ] Production packaging strategies are documented.
- [ ] Existing application migration is feasible.
- [ ] Relevant security and packaging tests are planned.
- [ ] Critical unresolved decisions are closed or explicitly deferred.

---

# 38. Final Architecture Summary

AdharaSutra provides a common Electron integration architecture through a reusable TypeScript bridge.

Electron renderer applications communicate through restricted preload APIs.

The Electron main process owns the Python runtime and manages process lifecycle through the bridge.

The bridge handles:

- Executable resolution.
- Python startup.
- Protocol handshake.
- Request serialization.
- Response correlation.
- Event subscriptions.
- Job-client operations.
- Cancellation messaging.
- Timeouts.
- Process failure detection.
- Restart policy.
- Controlled shutdown.

Python uses the AdharaSutra runtime to execute registered business actions and access framework-managed infrastructure.

The Electron integration does not depend on which external connectors an application uses.

This separation enables multiple independent applications to share one standardized communication implementation while retaining their own business behavior and user interfaces.

The fundamental guarantee remains:

**One Electron bridge. One CLI communication protocol. Multiple independent Python applications.**

---

# 39. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending architecture review

**Next Document:** `docs/design/connector-framework.md`

The next document will define the shared connector infrastructure and individual connector contracts for HTTP, WebSocket, external CLI executables, SQLite, and filesystem operations, including registration, lifecycle, error mapping, health checks, configuration, test doubles, and service-specific adapters.

---

**AdharaSutra — Build once. Standardize everywhere.**
