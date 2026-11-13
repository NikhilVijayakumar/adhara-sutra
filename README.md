# AdharaSutra (आधारसूत्र)

**Documentation:** [Requirements](docs/requirements/README.md) · [OpenSpec changes](openspec/README.md) · [Knowledge](knowledge/index.md)

The initial runtime is available as `nikhi.adhara_sutra`. For a working example,
run `PYTHONPATH=src python3 examples/basic_app.py` and send a newline-terminated
request such as `{"kind":"request","protocol_version":"1.0","request_id":"1","action":"greeting.create","payload":{"name":"world"}}`.
Use `--persistent` to keep the process open; the first request must call
`system.hello`. Persistent requests currently execute sequentially. With the
package installed, `adhara run examples/basic_app.py` (or a module name) loads
the application's `app`, `application`, or `create_app()` and serves the same
protocol; `adhara version` prints the framework version. `adhara doctor [target]
[--json] [--output FILE]` reports framework, interpreter, dependency, and
configuration diagnostics with remediation, and, when a target is given, the
application's registered actions, jobs, and services without printing
configuration values. Package releases follow
Semantic Versioning. The CLI protocol has its own `PROTOCOL_VERSION` (`1.0`),
advertised by `system.hello` and validated before dispatch; the Electron bridge
exports the same constant and refuses a backend that does not support it. Report
formats carry independent `schema_version` and profile versions. Tests can use
`ApplicationTestClient(app)` as an async context manager to start the runtime
and `await client.call(action, payload)` (or `.dispatch` for the full envelope)
without the CLI transport. `adhara inspect [path] [--json] [--output FILE]`
statically analyzes a project and reports its entry points, actions, jobs,
services, integrations, dependencies, state and job access, and Electron
boundaries. Every finding cites file and line evidence and is marked observed
or inferred; reports carry a schema version and the Git revision when available.
`adhara verify [path] [--json] [--output FILE] [--strict]` evaluates the
versioned architecture profile against that discovery and reports each check as
pass, fail, needs review, or not checked, with evidence and remediation. It
exits 0 without failures, 1 with failures (or with needs-review checks under
`--strict`), and 2 for an invalid invocation, so it can run in CI.
`adhara migrate [path] [--strategy adapter-first|incremental|rebuild] [--status FILE]
[--json] [--output FILE]` combines discovery and verification into a structured
migration plan: actionable findings with evidence and recommendations, and
independently verifiable tasks with verification and rollback guidance. The plan
preserves existing business behavior, CLI and Electron contracts, and persistent
data, and changes no source files. A status file maps task ids to `pending`,
`in_progress`, `done`, `deferred`, or `blocked` for progress reporting.
`Application.run()` returns the process exit code, so entry points should
`raise SystemExit(app.run(...))`: 0 success (or a cleanly ended persistent
session), 2 no request was received, 3 initialization failed, 4 an action
failed, 6 an interrupt (cancellation), 7 a connector or dependency failure, 8 a
protocol failure, 10 an internal failure. Code 5 (timeout) is reserved for that
capability. Action failures do not end a persistent session. Handlers emit
correlated progress events with `context.emit(event, data)`; each event is a
newline-delimited `{"kind": "event", ...}` envelope written before the request's
terminal response. The `system.hello` response reports the application name and
version, the framework version, and the supported protocol versions. Send
`system.help` to list registered actions with their descriptions and schema
hooks; an unknown action reports the available action names. Protocol
error objects carry a stable `category` (protocol, validation, action,
lifecycle, connector, internal) alongside `code`, `message`, `retryable`, and
optional `details`. See [docs/protocol-reference.md](docs/protocol-reference.md)
for the maintained protocol reference covering messages, events, errors,
sessions, version compatibility, and exit codes.
Application names are unique among live `Application` objects in a process.
Invalid definitions raise `ApplicationDefinitionError`, a `ValueError` with
`code` and `field` attributes; a name can be reused after its object is released.
For bootstrap, pass a synchronous `validate_config` callback to `Application`;
raise `ValueError` or `TypeError` to reject configuration. Register services or
connectors with `app.service(name, factory, depends_on=(... ,))`. Factories
return synchronous or asynchronous context managers and receive the application
context. Dependencies start first and resources close in reverse startup order.
Unknown or cyclic dependencies and invalid configuration raise `BootstrapError`
before any service starts. The original exception is available as `__cause__`.
Configuration merges, lowest priority first: the `config` mapping, a JSON object
from `config_file=` or `ADHARA_CONFIG_FILE`, `ADHARA_CONFIG_<KEY>` environment
variables (lowercased top-level keys, values parsed as JSON when possible), and
`app.override_config({...})` before startup. Validation runs on the merged
mapping. An unreadable, malformed, or non-object config file aborts startup with
its path in the error. Credentials can come from `ADHARA_CONFIG_*` variables or a
config file, so they need not be embedded in application source; connectors
accept them as headers or environment values.
Diagnostics are structured JSON written to stderr; `Application.run()` installs
the handler automatically and `configure_logging()` is available for custom
entry points. The level defaults to `ADHARA_LOG_LEVEL` (INFO when unset) and can
be set programmatically. Each record carries `timestamp`, `level`, `logger`, and
`message`, plus `request_id` and `action` while a request is being handled and
`exception` for tracebacks. stdout stays reserved for protocol messages.
Log messages, exception text, protocol error messages and details, and generated
reports redact values under keys such as `password`, `token`, `secret`, and
`api_key`, including quoted or bare `key=value` assignments and bearer headers,
replacing them with `[REDACTED]`. Framework log records are redacted before any
handler formats them, including the default one. Redaction is pattern-based, so a
secret written in an unusual format can still pass through.
Handlers share process state through `context.state`, share state within a
persistent session through `context.session_state`, and get a fresh
`context.request_state` per request. Applications define the keys and values;
service factories receive the same process state at startup. `context.state_lock`
is one `asyncio.Lock` per application, shared by request and job contexts; use it
to serialize compound process-state updates when jobs run concurrently. Plain
state mappings are otherwise unsynchronized, so the application owns any other
coordination it needs. Independent `Application` instances do not share state,
configuration, jobs, or services. Subscribe to process-state changes with
`unsubscribe = context.state.subscribe(listener, key="name")`; omit `key` to
observe all keys. Synchronous listeners receive `(operation, key, value)`, with
`operation` equal to `"set"` or `"delete"`; deletions include the removed value.
Notifications follow top-level mutations, not in-place edits of nested values.
Listener failures are logged and do not undo changes. Call `unsubscribe()` when
the subscription is no longer needed.

Background jobs are registered with `@app.job(name, timeout=...)` and submitted
from a handler with `context.jobs.submit(name, payload)`, which returns an
identifier. Job handlers receive `(payload, context)`; events they emit carry the
`job_id`, and their log records are correlated with it. Use
`context.jobs.status(id)`, `.list()`, `.cancel(id)`, and `.wait(id)` to inspect
execution. Send `system.cancel` with `{"job_id": ...}` to cancel a managed job;
the result reports whether cancellation was accepted, its phase (`requested`,
`completed`, `unsupported`, or `failed`), and the current status. A full queue
rejects new work with the retryable `JOB_QUEUE_FULL` error instead of growing
without bound.
Jobs run in-process with bounded concurrency (`max_concurrent_jobs`, default 4)
and a bounded waiting queue (`max_queued_jobs`, default 64); timeouts apply to
async handlers. Stopping the application cancels active jobs before services
close, so jobs never outlive their owning process, and shutdown waits at most
`shutdown_timeout` seconds (default 10) for cancellation and cleanup; external
commands accept a `kill_timeout` grace period before forced termination.
Persistence and recovery across processes are not yet provided.

Connectors are services: register them with `app.service`, resolve them with
`context.get_service`, and replace them with a test double by registering the
double in place of the live factory. A service with a callable `health()`
(synchronous or asynchronous, truthy when available) is reported by
`system.health` after startup as `{"status": "ok"|"degraded", "state": ...,
"services": {...}}`. Raise `ConnectorError(message, retryable=..., details=...)`
for an expected upstream failure: the response reports code `CONNECTOR_FAILURE`,
category `connector`, the retryability flag, and optional details, and one-shot
execution exits 7 while a persistent session continues.

Applications can map exceptions raised by action handlers with
`app.map_error(DomainError, code="ACTION_VALIDATION_FAILED", message="Invalid request")`
before startup. Supported codes are `ACTION_VALIDATION_FAILED`, `ACTION_NOT_FOUND`,
`CONNECTOR_FAILURE`, and `RUNTIME_EXECUTION_FAILED`; `retryable` defaults to
false. The most specific registered exception class wins. The public response
uses the configured message, while diagnostics retain the original exception.

The optional HTTP connector (`pip install nikhi-adhara-sutra[http]`) wraps one
reused `httpx` client: register `HttpClient(base_url=..., timeout=...)` as a
service, call `get`/`post`/`put`/`patch`/`delete`/`head`, and read `status`,
`headers`, `body`, `.text()`, or `.json()`. `raise_for_status()` raises a
`ConnectorError` for non-success statuses, marking only server, timeout, and
rate-limit statuses as retryable; transient network failures and timeouts are
retryable connector errors. The client closes when the application stops. For Basic
authentication pass `auth=(username, password)`; for bearer tokens pass an
`Authorization` header. Obtain credentials from environment variables or the
application's configuration rather than embedding them in source code. Use HTTPS
to protect credentials in transit. Set `max_retries` (default 0) and
`retry_delay` in seconds (default 0) to retry transient network failures and
HTTP 408, 429, 500, 502, 503, or 504 responses. Automatic retries apply only to
GET, HEAD, and OPTIONS; the final response or error is returned after exhaustion.
The delay is fixed and applies between attempts. For incremental response bodies,
use `with client.stream("GET", url) as response:` and iterate over
`response.iter_bytes()`. The stream exposes `status`, `headers`, `url`, `ok`,
and `raise_for_status()`; leaving the context closes the response even if it was
only partly consumed. Streaming requests are not automatically retried.

SQLite is available as `SQLiteDatabase(path=...)`: register it as a service and
use `execute`, `executemany`, `query`, `query_one`, and `transaction()` for
explicit commit or rollback. Foreign keys are enabled, and one connection is
owned by the thread that starts the application, so cross-thread use is
rejected. `db.migrate([(1, create_schema), (2, upgrade_schema)])` applies
application-defined migration callables in strictly increasing positive version
order, recording versions in `adhara_schema_migrations`. Supply the complete
history on every run; mismatched history is rejected. Pending migrations and
their records commit together or roll back together. Callables receive `db` and
must not manage transactions themselves. Run migrations outside a transaction.
`db.integrity_check()` returns SQLite's integrity messages (`["ok"]` for a
healthy database), and `db.backup(path)` creates a consistent backup at a new
file path without overwriting an existing file. To recover, stop applications
using the database, preserve the damaged files, restore a verified backup to
the database path, and check its integrity before resuming service.

For explicitly persisted state, register `SQLiteState(db, namespace)` as a
service dependent on the database (wrap it with `contextlib.nullcontext` in
the service factory). It is a mutable mapping with string keys and JSON values,
stored separately per namespace. Retrieved values are snapshots: assign changed
values back to persist them. Operations use the database's thread ownership and
transaction policy; use `db.transaction()` for grouped changes. Persistent
state is separate from `context.state` and remains available after restart.
Applications can build their own repositories on
the managed connection; [the repository example](examples/sqlite_repository.py)
shows dependency ordering, parameterized statements, and transactions.

External commands run through `ExternalCommand(executable, search_path=...)`:
`await run(args, timeout=..., input=..., cwd=..., env=..., on_output=...)`
passes a structured argument array without a shell (a command string or
non-string argument is rejected), streams stdout and stderr
lines to `on_output(stream, chunk)`, and returns `CommandResult` with the exit
status, captured output, and duration. `raise_for_status()` raises a
non-retryable `ConnectorError` for a non-zero exit. Timeouts and cancellation
terminate the process tree and report retryable errors; stopping the application
also terminates any command still running. Register an output parser with
`command.register_parser(name, parser)` and call `command.parse(name, result)`
on a `CommandResult`; the parser receives the captured output and exit status,
and its return value or exception passes through to the caller. Interactive
process sessions are not yet provided.

`AppDirectories.for_app(name)` resolves application data, configuration, cache,
log, and temporary directories using platform conventions (or a `base` directory
for a portable layout); `ensure()` creates them and `temporary()` yields an
application-scoped temporary directory that is removed on exit, including on
error. `PathBoundary(*roots)` resolves framework-managed paths against configured
roots and rejects traversal, escaping symbolic links, and sibling-prefix paths
with `PathViolation`; `open()`, `read_text()`, `write_text()`, `read_json()`,
and `write_json()` apply the same check. Text and JSON use UTF-8 by default;
write helpers require the parent directory to exist and propagate errors.
`ArtifactStore(directory).put(binary_stream, media_type=...)` copies data in
chunks and returns a JSON-compatible reference containing an opaque artifact ID,
size, and media type. Use `store.open(id)` to read it and `store.delete(id)` to
remove it. Applications own access control, retention, and cleanup, and should
keep the store directory private. Path checks resolve symbolic links at the time
of the check and do not protect against concurrent path changes.

The Electron/Node main-process bridge lives in [bridge/](bridge/README.md). It
spawns one persistent backend, performs the `system.hello` handshake, correlates
responses, forwards events, and rejects pending work when the backend exits. The
package exposes `start()`, `request(action, payload, {timeoutMs})`,
`cancel(jobId)`, `health()`, `help()`, and `close()`, plus `event`, `stderr`,
`exit`, `protocolError`, and `processError` events. Its command and arguments are
fixed at construction, held privately, and spawned without a shell, so renderer
input can only become an action name and payload. A running request cannot be cancelled because the persistent session is
sequential; cancellation targets managed jobs.

**A CLI-First Python Application Framework**

*Build once. Standardize everywhere.*

**Status:** Architecture & Design — Proposed  
**Version target:** 0.1.0  
**Language:** Python 3.12+  
**Primary integration:** Electron ↔ Python CLI  
**Architecture:** Opinionated, DDD-compatible, Hexagonal / Ports & Adapters  
**License:** MIT (proposed)

---

## 1. Overview

**AdharaSutra** is a reusable, opinionated Python application framework designed to provide a consistent foundation for building, operating, verifying, and migrating CLI-first applications.

Its primary purpose is to eliminate repeated infrastructure and architectural boilerplate across Python applications, particularly applications that use Electron as their frontend.

AdharaSutra owns the application runtime, CLI communication protocol, infrastructure integrations, state management, configuration, lifecycle, architectural conventions, verification, and migration tooling.

Applications built on AdharaSutra implement their own business logic, domain models, application actions, and workflows without recreating these foundational capabilities.

### Core principle

> AdharaSutra defines how applications are built and executed. Applications define what they do.

The framework must remain independent of application-specific business logic.

### Primary objectives

1. Establish a unified architecture for all Python applications.
2. Standardize Electron-to-Python communication through a CLI protocol.
3. Provide reusable HTTP, CLI, WebSocket, SQLite, and filesystem infrastructure.
4. Centralize application state, job execution, lifecycle, and error handling.
5. Generate new applications using predefined architecture templates.
6. Analyze existing applications and document their current implementation.
7. Deterministically verify conformance with architecture standards.
8. Generate actionable migration plans for existing applications.
9. Support incremental migration without breaking working functionality.
10. Enable Claude Code, Codex, OpenCode, and other coding agents to understand and maintain applications through shared reports and specifications.

---

## 2. Design Philosophy

AdharaSutra follows the principles below.

### 2.1 Framework-first architecture

Every application uses AdharaSutra as its underlying application framework.

The framework provides:

- Application initialization and bootstrap
- Runtime lifecycle
- CLI parsing and execution
- Action routing and registration
- Request/response serialization
- State management infrastructure
- Job orchestration
- External communication adapters
- Database facilities
- Configuration management
- Logging and error handling
- Architectural conventions
- Verification and migration capabilities

Applications provide:

- Domain models
- Business rules
- Application services
- Use cases and action handlers
- Application-specific workflows
- Domain-specific persistence operations
- External service mappings where required

### 2.2 Zero application business logic

AdharaSutra must not contain business rules belonging to any consuming application.

For example, the framework must not know how to:

- Generate speech
- Construct a comic panel
- Generate an image
- Execute an AI inference workflow
- Process an audio file
- Manage a film-production scene

Instead, it provides the capabilities necessary for applications to implement these operations.

### 2.3 Uniform Electron communication

All Electron applications communicate with Python through the same versioned CLI protocol.

Electron must not require different integration approaches based on the external dependency used by Python.

For example:

- Electron → AdharaSutra → HTTP → ComfyUI
- Electron → AdharaSutra → HTTP → LM Studio
- Electron → AdharaSutra → subprocess → audio.cpp
- Electron → AdharaSutra → SQLite
- Electron → AdharaSutra → filesystem

The Electron-facing communication contract remains consistent.

### 2.4 Infrastructure ownership

Applications should use framework-provided facilities for common infrastructure rather than implementing their own copies.

The framework manages the technical mechanisms.

Applications configure the mechanisms and provide domain-specific behavior.

### 2.5 Architecture as an enforceable contract

Architecture conventions are not merely documentation.

AdharaSutra provides deterministic verification rules that can be executed locally, during migration, and in CI/CD.

The same architecture specification drives:

- Project generation
- Implementation verification
- Migration gap analysis
- Architecture reporting
- Continuous enforcement

### 2.6 Incremental adoption

Existing applications must be able to adopt AdharaSutra without a complete rewrite.

Migration must preserve functioning business logic, data, external integrations, and public behavior unless changes are explicitly authorized.

---

## 3. High-Level Architecture

```text
┌────────────────────────────────────────────┐
│             Electron Application           │
│                                            │
│  Renderer UI                               │
│       │                                    │
│       ▼                                    │
│  Electron IPC / Main Process               │
│       │                                    │
│       ▼                                    │
│  AdharaSutra Electron Bridge               │
└────────────────────┬───────────────────────┘
                     │
                     │ Standard CLI Protocol
                     │ stdin / stdout / stderr
                     ▼
┌────────────────────────────────────────────┐
│                AdharaSutra                 │
│                                            │
│  CLI Protocol & Action Router              │
│              │                             │
│              ▼                             │
│  Application Runtime & Lifecycle           │
│              │                             │
│    ┌─────────┼────────────┐                │
│    ▼         ▼            ▼                │
│  State     Jobs       Configuration        │
│    │         │            │                │
│    └─────────┼────────────┘                │
│              ▼                             │
│       Application Extensions               │
│              │                             │
│              ▼                             │
│      Application Business Logic            │
│              │                             │
│              ▼                             │
│         Connector Registry                 │
│                                            │
│  HTTP | CLI | SQLite | WebSocket | Files   │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│            External Dependencies           │
│                                            │
│  ComfyUI        HTTP / WebSocket           │
│  LM Studio      HTTP                       │
│  audio.cpp      CLI / Subprocess           │
│  SQLite         Database                   │
│  Other Tools    Supported Connectors       │
└────────────────────────────────────────────┘
```

### Architectural dependency direction

Application code imports AdharaSutra's public interfaces and facilities.

The framework must not directly import application-specific modules.

The framework may invoke registered application handlers through explicitly defined extension points.

Domain logic must remain independent of Electron, CLI parsing, HTTPX, subprocess management, and database connection implementations.

---

## 4. Framework Capabilities

### 4.1 Core Application Runtime

The runtime is responsible for managing the lifecycle of an application.

Responsibilities include:

- Application initialization
- Configuration loading
- Dependency registration
- Connector initialization
- Action registration
- State initialization
- Job manager initialization
- Resource cleanup
- Graceful termination
- Error propagation

Proposed application API:

```python
from adharasutra import Application

app = Application(
    name="my-application",
    version="1.0.0",
)

app.run()
```

The framework initializes the required infrastructure before accepting application requests.

### 4.2 Application Lifecycle

The framework defines standard lifecycle states.

```text
CREATED
   │
   ▼
INITIALIZING
   │
   ▼
READY
   │
   ▼
RUNNING
   │
   ▼
STOPPING
   │
   ▼
STOPPED
```

Failure transitions must be explicitly defined.

Applications may register startup and shutdown hooks.

The runtime is responsible for initializing resources in dependency order and releasing them safely.

---

## 5. Unified CLI Framework

The CLI is the primary communication interface between Electron and Python.

Applications do not implement separate command-parsing systems.

They register application actions with AdharaSutra.

### 5.1 Responsibilities

The CLI framework provides:

- Command parsing
- Action registration
- Request validation
- Response serialization
- Structured event streaming
- Standard error responses
- Exit-code management
- Input handling
- Long-running process support
- Cancellation
- Request correlation
- Protocol versioning
- Session management

### 5.2 Standard Application Actions

Application actions are registered through framework APIs.

Illustrative example:

```python
from adharasutra import Application

app = Application(name="vani")

@app.action("voice.generate")
async def generate_voice(payload, context):
    service = context.services.get("voice_service")
    return await service.generate(payload)

app.run()
```

The handler supplies business behavior.

AdharaSutra owns the command routing, input validation, execution lifecycle, and response protocol.

### 5.3 CLI Execution Modes

AdharaSutra must support two CLI execution models.

#### One-shot execution

Electron starts a Python process for a command and receives its result.

Suitable for:

- Short-running operations
- Health checks
- Configuration queries
- Batch commands
- Automation
- Diagnostics

#### Persistent CLI session

Electron starts a long-lived Python process.

Multiple requests are exchanged through a structured message protocol.

Suitable for:

- Stateful application sessions
- Long-running processing
- Progress events
- Shared in-memory resources
- Job cancellation
- Repeated operations

Both modes must use the same logical request and response schemas.

The framework must define how each mode handles process termination, cancellation, timeouts, and lost connections.

---

## 6. Electron Communication Contract

### 6.1 Communication Policy

Electron-to-Python application communication uses CLI-based process communication.

No HTTP server is required between Electron and AdharaSutra.

HTTP clients are used only where needed for external services.

### 6.2 Transport

Supported process channels:

| Channel | Responsibility |
|---|---|
| stdin | Structured requests and cancellation messages |
| stdout | Structured responses and events |
| stderr | Diagnostic logging |
| Exit code | Final process status |

Persistent communication uses newline-delimited JSON (NDJSON).

Every protocol message must be a valid JSON object contained on one line.

Normal logs must not be written to stdout while the structured protocol is active.

### 6.3 Request Envelope

```json
{
  "protocol_version": "1.0",
  "request_id": "req-001",
  "action": "voice.generate",
  "payload": {
    "text": "Hello",
    "voice_id": "voice-1"
  }
}
```

The framework validates the envelope.

Application-specific payload schemas are registered by the application.

### 6.4 Response Envelope

```json
{
  "protocol_version": "1.0",
  "request_id": "req-001",
  "success": true,
  "data": {
    "job_id": "job-123",
    "status": "accepted"
  },
  "error": null
}
```

A job accepted for asynchronous execution is not equivalent to a completed job.

The framework must distinguish accepted, running, completed, failed, and cancelled operations.

### 6.5 Error Envelope

```json
{
  "protocol_version": "1.0",
  "request_id": "req-001",
  "success": false,
  "data": null,
  "error": {
    "code": "CONNECTOR_UNAVAILABLE",
    "message": "Required external service is unavailable",
    "retryable": true
  }
}
```

Errors must use standardized codes.

Internal tracebacks and secrets must not be exposed in frontend-facing messages.

### 6.6 Event Envelope

```json
{
  "protocol_version": "1.0",
  "request_id": "req-001",
  "event": "job.progress",
  "data": {
    "job_id": "job-123",
    "percent": 65
  }
}
```

The framework defines common events:

- `job.started`
- `job.progress`
- `job.completed`
- `job.failed`
- `job.cancelled`
- `connector.status_changed`
- `application.state_changed`

Applications may define additional events using documented namespaces.

### 6.7 Protocol Requirements

The protocol must support:

- Request correlation
- Structured errors
- Progress reporting
- Cancellation
- Version negotiation
- Message ordering per request
- Large-input handling
- Process termination handling
- Optional heartbeats
- Protocol compatibility tests

Large binary data must not be embedded directly into ordinary JSON messages.

Use controlled file references or other explicitly supported transfer mechanisms.

---

## 7. Electron Bridge Package

A companion TypeScript package is proposed.

**Package name:** `@adharasutra/electron-bridge`  
**Status:** Proposed

It provides a reusable Electron integration layer.

### Responsibilities

- Discover and launch the Python application executable
- Manage Python child processes
- Send structured requests
- Parse structured responses
- Correlate requests and responses
- Subscribe to events
- Forward progress notifications
- Handle timeouts and cancellation
- Restart or reconnect according to policy
- Manage startup and shutdown
- Validate protocol compatibility

### Example

```typescript
const result = await pythonBridge.execute(
  "voice.generate",
  {
    text: "Hello",
    voice_id: "voice-1"
  }
);
```

Every application uses the same bridge interface.

Only action names and payloads differ.

### Electron Security

Process launching must occur in the Electron main process.

The renderer should access an allowlisted API exposed through preload.

The framework must not permit untrusted renderer input to become arbitrary shell commands.

---

## 8. Connector Framework

AdharaSutra provides a standardized infrastructure layer for connecting applications to external systems.

### 8.1 Goals

- Avoid duplicate infrastructure implementations
- Centralize connection lifecycle management
- Standardize timeouts and errors
- Support dependency replacement
- Simplify testing
- Preserve the Electron-facing contract
- Provide consistent configuration

### 8.2 Connector Categories

| Connector | Typical use |
|---|---|
| HTTP | REST APIs, inference services |
| WebSocket | Streaming and live events |
| CLI | External executables |
| SQLite | Local persistence |
| Filesystem | Local files and directories |
| Custom | Additional integration types |

### 8.3 Connector Lifecycle

Every managed connector must expose appropriate lifecycle operations:

```python
class Connector:
    async def connect(self):
        ...

    async def health(self):
        ...

    async def close(self):
        ...
```

This is a conceptual interface.

The framework must define separate capability contracts for different connector types.

A database connector should expose transaction and query facilities rather than being forced into a generic HTTP-style action interface.

### 8.4 HTTP Connector

Recommended implementation: HTTPX.

Responsibilities:

- Base URL management
- Connection reuse
- Request timeouts
- Retry policy
- Authentication configuration
- Header management
- Structured error mapping
- Response validation
- Resource cleanup

Application-specific HTTP endpoints and domain mappings belong to the consuming application or optional integration plugins.

### 8.5 External CLI Connector

Responsibilities:

- Executable discovery
- Argument construction
- Environment configuration
- Process creation
- stdin/stdout/stderr handling
- Streaming output
- Timeouts
- Cancellation
- Process-tree termination
- Exit-code interpretation
- Temporary-file cleanup

Subprocess execution must use safe argument arrays instead of dynamically constructed shell commands wherever possible.

### 8.6 SQLite Connector

Responsibilities:

- Connection lifecycle
- Schema migration infrastructure
- Transaction management
- Concurrency policy
- Database error handling
- Connection cleanup
- Backup support

Applications define their own tables, repositories, queries, and domain data.

The framework must not impose application-specific schemas.

### 8.7 Integration Plugins

Service-specific integrations may be packaged independently.

Potential plugins include:

```text
adharasutra-comfyui
adharasutra-lmstudio
adharasutra-audiocpp
```

These names are proposed.

Applications install only the connectors and plugins they require.

---

## 9. External Integration Examples

### 9.1 ComfyUI

```text
Electron
   │
   ▼
AdharaSutra CLI
   │
   ▼
Application Image Action
   │
   ▼
ComfyUI Integration
   │
   ▼
HTTP / WebSocket Connector
   │
   ▼
ComfyUI
```

The framework manages HTTP connections, timeouts, and execution infrastructure.

The application owns image-generation workflow selection and interpretation.

### 9.2 LM Studio

```text
Electron
   │
   ▼
AdharaSutra CLI
   │
   ▼
Application Inference Action
   │
   ▼
LM Studio Integration
   │
   ▼
HTTP Connector
   │
   ▼
LM Studio
```

The framework provides networking infrastructure.

The application defines its prompts, inference requirements, output handling, and model-related business logic.

### 9.3 audio.cpp

```text
Electron
   │
   ▼
AdharaSutra CLI
   │
   ▼
Application Audio Action
   │
   ▼
audio.cpp Integration
   │
   ▼
External CLI Connector
   │
   ▼
audio.cpp executable
```

The framework manages the subprocess.

The application or integration plugin defines audio.cpp-specific arguments, output parsing, and supported operations.

### Fundamental guarantee

Changing an external integration from HTTP to CLI, or vice versa, must not require changing the standard Electron communication protocol.

Application-level action schemas may evolve only through the framework's documented compatibility and versioning mechanisms.

---

## 10. State Management

AdharaSutra provides shared state-management infrastructure.

It must not define the business state of consuming applications.

### 10.1 State Categories

| Category | Description |
|---|---|
| Runtime state | Application lifecycle and readiness |
| Session state | Active requests and connections |
| Connector state | Availability and health |
| Job state | Execution status and progress |
| Persistent state | Durable values stored through adapters |
| Application state | Application-defined state schemas |

### 10.2 State Store

The framework should support:

- Get and update operations
- Typed values
- Subscription and change notification
- State initialization
- Persistence adapters
- Concurrency control
- State cleanup
- Explicit ownership

Illustrative API:

```python
state = context.state

await state.set("processing.active", True)

active = await state.get("processing.active")
```

### 10.3 Persistent and Ephemeral State

The framework must distinguish between:

- In-memory state belonging to one process
- Session state belonging to a persistent CLI connection
- Persistent state stored in SQLite or another backend
- Background job state owned by a worker

An ordinary CLI process that exits cannot retain in-memory application state.

The framework must explicitly define the state ownership and persistence semantics of each execution mode.

---

## 11. Job Execution Engine

AdharaSutra provides job-management infrastructure for long-running operations.

### Responsibilities

- Job creation
- Job identifiers
- Lifecycle tracking
- Progress reporting
- Cancellation
- Timeouts
- Result handling
- Failure reporting
- Resource cleanup
- Optional persistence
- Concurrency control

### Job Lifecycle

```text
PENDING
   │
   ▼
RUNNING
   │
   ├────────► COMPLETED
   │
   ├────────► FAILED
   │
   └────────► CANCELLED
```

Applications define the operation to execute.

The framework defines how the job is scheduled, monitored, and managed.

### Background Execution

Returning a job ID must not imply that work will continue after the CLI process exits.

Durable or detached execution requires a defined worker or persistent runtime responsible for executing and recovering jobs.

---

## 12. Application Architecture

AdharaSutra provides an opinionated architecture compatible with DDD and Hexagonal Architecture.

### Default Generated Structure

```text
my-application/
├── pyproject.toml
├── README.md
├── config/
│   └── application.yaml
├── src/
│   └── my_application/
│       ├── app.py
│       ├── bootstrap.py
│       │
│       ├── domain/
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── services/
│       │   └── events/
│       │
│       ├── application/
│       │   ├── actions/
│       │   ├── commands/
│       │   ├── queries/
│       │   ├── handlers/
│       │   └── ports/
│       │
│       ├── infrastructure/
│       │   ├── connectors/
│       │   ├── repositories/
│       │   └── persistence/
│       │
│       └── interfaces/
│           └── cli/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contracts/
│   └── architecture/
│
└── openspec/
```

### Layer Responsibilities

**Domain**

Contains domain entities, value objects, domain rules, and domain services.

Must not depend on Electron, CLI frameworks, HTTP implementations, or persistence implementations.

**Application**

Contains use cases, commands, queries, handlers, and ports.

Coordinates domain behavior.

**Infrastructure**

Contains implementations of external dependencies, repositories, and infrastructure adapters.

Uses AdharaSutra's shared facilities.

**Interfaces**

Registers application actions and connects external requests to application use cases.

Uses the framework's CLI registration system rather than implementing a separate communication runtime.

### Dependency Rules

```text
Interfaces ─────► Application ─────► Domain
                     ▲
                     │
               Infrastructure
```

Infrastructure implements application-defined ports.

Composition occurs at the application bootstrap boundary.

### Architecture Profiles

AdharaSutra should support:

| Profile | Purpose |
|---|---|
| `minimal` | Small Python utilities |
| `cli` | Standalone CLI applications |
| `ddd` | Domain-driven applications |
| `electron-cli` | Electron applications using Python CLI |
| `ai-worker` | Long-running local AI workloads |

The framework provides the runtime across profiles.

Profiles determine generated conventions and applicable architecture verification rules.

---

## 13. Application Scaffolding

AdharaSutra provides a project generator.

### Commands

```bash
adhara new my-application
adhara new my-application --profile cli --connectors http,sqlite
```

The implemented `minimal` and `cli` profiles generate packaging, a working
bootstrap and entry point, an example action and test, documentation, and the
selected `http`, `sqlite`, or `external` connector services. Generation refuses
to overwrite existing files unless `--force` is set.

### Generated Artifacts

The generator creates:

- Standard `src/` project structure
- Python packaging configuration
- Application bootstrap and module entry point
- Example action handler
- Selected connector services
- Example test using `ApplicationTestClient`
- Project README and `.gitignore`
- CLI registration, for the `cli` profile

Generated projects are valid, testable, and pass `adhara verify` immediately
after dependency installation. Additional profiles (DDD, Electron CLI, AI worker),
configuration and state templates, OpenSpec setup, and CI configuration remain
future work.

---

## 14. Architecture Discovery Engine

AdharaSutra must support inspecting existing Python applications to understand how they are implemented.

This capability is useful for:

- Migrating legacy applications
- Onboarding coding agents
- Understanding unfamiliar repositories
- Detecting duplicated infrastructure
- Documenting architecture
- Identifying migration dependencies

### Proposed Command

```bash
adhara inspect ./existing-application
```

### Discovery Responsibilities

The engine should inspect:

- Project folders and modules
- Python entry points
- CLI registrations and commands
- Electron IPC integration
- Python subprocess execution
- External HTTP clients
- WebSocket usage
- SQLite connections
- State ownership
- Job management
- Configuration mechanisms
- Application dependencies
- Runtime lifecycle
- Test coverage
- Packaging and build scripts

### Current Implementation Report

The discovery engine generates an evidence-backed representation of the existing system.

Proposed structure:

```text
architecture/
└── current/
    ├── overview.md
    ├── module-inventory.json
    ├── dependency-graph.json
    ├── cli-commands.json
    ├── electron-ipc.json
    ├── connectors.json
    ├── state-and-storage.md
    └── findings.json
```

Reports must identify:

- Observed behavior
- Relevant source files
- Source line references
- Inferred architecture
- Known limitations
- Unverified behavior

The engine must not represent inferred behavior as confirmed fact.

---

## 15. Deterministic Architecture Verification

Architecture verification is a primary framework capability.

The framework must verify whether an application conforms to its selected architecture profile.

### Proposed Command

```bash
adhara verify ./my-application
```

Additional modes:

```bash
adhara verify . --level static

adhara verify . --level full

adhara verify . --format json

adhara verify . --explain
```

### Verification Categories

| Category | Verification |
|---|---|
| Structure | Required folders and metadata |
| Dependencies | Forbidden imports and layer boundaries |
| Framework adoption | Required framework entry points |
| CLI | Protocol and action registration |
| Electron | Approved CLI communication boundary |
| HTTP | Framework connector policy |
| External CLI | Framework process runner policy |
| SQLite | Framework database policy |
| State | State ownership and management rules |
| Jobs | Lifecycle and cancellation contracts |
| Configuration | Validated application configuration |
| Testing | Required architecture and contract tests |
| Security | Selected static and runtime safety rules |

### Deterministic First

Mandatory architecture rules must be verified deterministically wherever feasible.

Recommended technologies:

- Import Linter
- Grimp
- Python AST
- LibCST
- pytest
- JSON Schema or Pydantic
- Ruff

These are implementation candidates, not mandatory dependencies for every application.

### Verification Status

Every rule must report one of:

- `PASS`
- `FAIL`
- `NEEDS_REVIEW`
- `NOT_CHECKED`

Passing a static check must not be interpreted as proof of untested runtime behavior.

### Example Finding

```json
{
  "rule_id": "ARCH-HTTP-001",
  "status": "FAIL",
  "severity": "error",
  "file": "src/app/services/client.py",
  "line": 42,
  "message": "Direct HTTP client usage is prohibited",
  "expected": "Use AdharaSutra HTTP connector",
  "remediation": "Replace direct client initialization"
}
```

### Architecture Configuration

Proposed `architecture.yaml`:

```yaml
schema_version: "1.0"

architecture:
  profile: ddd
  framework_required: true

layers:
  domain:
    forbidden_imports:
      - infrastructure
      - interfaces
      - httpx
      - sqlite3
      - typer

  application:
    forbidden_imports:
      - infrastructure
      - interfaces

cli:
  protocol_version: "1.0"
  framework_router_required: true

connectors:
  external_http: framework-managed
  external_cli: framework-managed
  sqlite: framework-managed

verification:
  fail_on: error
  require_contract_tests: true
```

The architecture specification must be versioned.

Project-specific exceptions must be explicit, documented, and reviewable.

---

## 16. LLM-Assisted Architecture Analysis

AdharaSutra is deterministic-first but may support optional LLM-assisted analysis.

### Deterministic Responsibilities

- Folder validation
- Dependency checking
- Schema validation
- Contract verification
- Known API usage detection
- Rule evaluation
- Runtime tests
- CI enforcement

### Optional LLM Responsibilities

- Interpreting complex legacy architecture
- Identifying likely misplaced business logic
- Explaining architectural tradeoffs
- Suggesting migration approaches
- Proposing refactoring steps
- Reviewing unclear module responsibilities
- Generating migration documentation

### Fundamental Rule

> LLM analysis may recommend architectural changes, but it must not override deterministic verification results.

LLM findings must be labeled advisory unless independently verified.

The core framework must function without an LLM provider.

---

## 17. Existing Application Migration

AdharaSutra must support incremental migration of applications that already have working Python backends, CLI commands, Electron integrations, and external dependencies.

Migration must not require complete application rewrites.

### Migration Goals

1. Preserve existing business functionality.
2. Preserve existing data.
3. Preserve supported CLI behavior during transition.
4. Replace duplicated infrastructure.
5. Introduce the AdharaSutra runtime.
6. Standardize Electron communication.
7. Align application structure with the selected architecture profile.
8. Verify compliance after migration.

### Proposed Commands

```bash
adhara migrate analyze ./existing-app

adhara migrate plan ./existing-app

adhara migrate apply ./existing-app --phase cli

adhara migrate verify ./existing-app

adhara migrate status ./existing-app
```

All commands are proposed design targets.

### Migration Stages

#### Stage 1: Discovery

Inspect the existing application.

Identify CLI commands, business modules, connectors, state, configuration, and Electron communication.

#### Stage 2: Baseline

Record current behavior and tests.

Capture CLI outputs, database assumptions, and integration behavior.

#### Stage 3: Gap Analysis

Compare the current implementation with the target architecture.

Identify violations and missing framework adoption points.

#### Stage 4: Migration Planning

Generate structured migration tasks and compatibility requirements.

#### Stage 5: Framework Adoption

Introduce AdharaSutra as the application runtime.

Register existing business functionality through framework actions.

#### Stage 6: Infrastructure Migration

Replace duplicated HTTP, subprocess, SQLite, logging, and configuration implementations.

#### Stage 7: State and Job Migration

Move state and job lifecycle management into framework facilities where applicable.

#### Stage 8: Architecture Alignment

Restructure application modules while preserving behavior.

#### Stage 9: Verification

Run deterministic architecture checks, contract tests, and regression tests.

#### Stage 10: Cleanup

Remove obsolete infrastructure only after verification succeeds.

### Migration Strategies

Supported strategies:

- Adapter-first
- Incremental refactoring
- Controlled rebuild

Incremental refactoring should be the default strategy.

---

## 18. Migration Report

The migration engine must produce actionable reports suitable for human developers and coding agents.

### Report Structure

```text
architecture/
└── migration/
    ├── gap-analysis.md
    ├── migration-plan.md
    ├── migration-tasks.json
    ├── compatibility-map.json
    ├── verification-plan.md
    └── migration-manifest.json
```

### Required Finding Information

Every migration finding should contain:

- Unique finding ID
- Architecture rule ID
- Current implementation
- Expected implementation
- Source evidence
- Affected files
- Recommended changes
- Migration dependencies
- Regression risk
- Acceptance criteria
- Verification commands
- Migration status

### Example Migration Task

```yaml
id: MIG-CLI-003

title: Migrate external process execution

current:
  component: audio_runner
  implementation: custom_subprocess

target:
  connector: adharasutra.cli

requirements:
  - preserve_existing_arguments
  - preserve_error_handling
  - preserve_output_formats
  - support_cancellation

verification:
  - architecture_contract
  - cli_integration_tests
  - electron_regression_tests
```

Reports must clearly distinguish observed facts, confirmed violations, assumptions, and recommended fixes.

---

## 19. Verification-Driven Migration

The migration workflow must reuse the Architecture Discovery and Verification engines.

```text
Existing Application
        │
        ▼
Architecture Discovery
        │
        ▼
Current Implementation Report
        │
        ▼
Deterministic Verification
        │
        ▼
Architecture Gap Report
        │
        ▼
Migration Plan
        │
        ▼
Coding Agent / Developer
        │
        ▼
Incremental Implementation
        │
        ▼
Deterministic Reverification
        │
        ▼
Regression Testing
        │
        ▼
Migration Completion
```

### Automated Fixes

The migration engine may provide deterministic codemods for known, safe transformations.

Complex architectural refactoring must remain reviewable.

The framework must never silently rewrite or delete business logic.

### Baseline Support

Existing applications may initially contain many architecture violations.

Migration should support a recorded baseline so that:

- Existing violations are tracked.
- New violations are blocked.
- Resolved violations are removed from the baseline.
- Migration progress can be measured.
- Approved exceptions remain visible.

---

## 20. Agent-Friendly Architecture Reports

AdharaSutra must support Claude Code, Codex, OpenCode, and other compatible coding agents.

The framework should not require a different report format for every agent.

### Common Outputs

- Human-readable Markdown
- Machine-readable JSON
- Evidence-backed file references
- Architecture rule identifiers
- Migration tasks
- Verification commands
- Source revision information

### Report Freshness

Every report must record:

- Source Git commit
- Relevant working-tree hashes
- Framework version
- Architecture profile version
- Analyzer version
- Generation timestamp
- Verification coverage

Agents must refresh stale analysis when source files change.

### Agent Workflow

```text
1. Read Current Implementation Report
2. Read Architecture Requirements
3. Read Migration Gap Report
4. Inspect Referenced Source Files
5. Create or Update OpenSpec Change
6. Implement One Migration Unit
7. Run Deterministic Verification
8. Run Regression Tests
9. Record Evidence
10. Continue with Remaining Tasks
```

The reports provide context, while source code remains authoritative.

---

## 21. OpenSpec Integration

AdharaSutra is designed to work with specification-driven development.

OpenSpec integration should be optional but directly supported.

### Workflow

```text
Proposal
   ↓
Specifications
   ↓
Design
   ↓
Architecture Decisions
   ↓
Tasks
   ↓
Implementation
   ↓
Verification
   ↓
Archive
```

### Proposed Command

```bash
adhara migrate plan ./vani --openspec
```

### Generated OpenSpec Artifacts

```text
openspec/
└── changes/
    └── adopt-adharasutra/
        ├── proposal.md
        ├── specs/
        │   ├── cli-contract/
        │   ├── connector-adoption/
        │   └── architecture-conformance/
        ├── design.md
        ├── tasks.md
        └── migration-manifest.json
```

Generation must respect the consuming repository's installed OpenSpec schema and conventions.

The integration should avoid overwriting existing changes, specifications, or project-specific workflow rules.

### Verification Requirements

Each migration task must have objective acceptance criteria.

Architecture compliance and application behavior should be verified separately.

---

## 22. Cross-Agent Development

AdharaSutra should remain compatible with multiple coding-agent harnesses.

Primary targets:

- Claude Code
- Codex
- OpenCode

Additional compatible agents may be supported through shared files and documented commands.

### Recommended Agent Skills

```text
adharasutra-skills/
├── create-application/
├── inspect-architecture/
├── verify-architecture/
├── migrate-application/
├── implement-action/
├── integrate-http-service/
├── integrate-external-cli/
├── configure-state/
└── verify-migration/
```

Skills should provide workflows and instructions.

The framework executable remains responsible for deterministic behavior.

Agent-specific wrappers must not introduce separate architecture standards.

---

## 23. Testing Strategy

AdharaSutra must provide testing utilities and enforceable contract tests.

### Testing Layers

| Test type | Purpose |
|---|---|
| Unit | Framework components |
| Contract | CLI protocol and connectors |
| Integration | External dependencies |
| Architecture | Layering and conventions |
| Migration | Existing-project compatibility |
| Regression | Preserve application behavior |
| Electron | Main-process CLI integration |
| Packaging | Verify packaged application runtime |

### Framework Testing Requirements

The framework must test:

- Request validation
- Response serialization
- Protocol compatibility
- CLI command routing
- Event streaming
- Error mapping
- Process execution
- Cancellation
- Timeouts
- Connector lifecycle
- State persistence
- Job management
- Architecture verification
- Migration transformations

### External Dependency Testing

Framework tests must not always require real ComfyUI, LM Studio, or audio.cpp installations.

Use mock connectors, test doubles, and controlled subprocess fixtures.

Separate optional live integration tests from core framework tests.

### Acceptance Criteria

A new generated application should pass architecture and basic CLI contract tests immediately.

A migrated application must pass its migration acceptance criteria and required behavioral regression tests.

---

## 24. Security Requirements

AdharaSutra must establish safe defaults.

### Process Security

- Avoid shell interpolation of untrusted arguments.
- Use executable allowlists where appropriate.
- Validate executable paths.
- Control environment variable exposure.
- Support process timeouts and cancellation.
- Clean up child processes.

### Input Security

- Validate protocol payloads.
- Enforce message-size limits.
- Validate file paths and allowed directories.
- Reject unsupported protocol versions.
- Prevent arbitrary command execution through action names.

### Data Security

- Avoid logging secrets.
- Protect configuration credentials.
- Handle temporary files safely.
- Support SQLite backups and recovery.
- Define appropriate local-file permissions.

### Electron Security

- Run Python process management in the Electron main process.
- Expose restricted operations through preload.
- Avoid enabling unrestricted renderer access to system resources.
- Validate action identifiers and payloads.

### Connector Security

- Apply appropriate network timeouts.
- Validate remote endpoint configuration.
- Protect authentication details.
- Use explicit retry policies.
- Avoid indiscriminate retries of non-idempotent operations.

---

## 25. Logging and Observability

The framework must provide consistent diagnostic facilities.

### Logging

Support:

- Structured logs
- Log levels
- Request correlation IDs
- Job identifiers
- Connector identifiers
- Configurable destinations
- Sensitive-data redaction

Logs must not corrupt structured CLI output.

### Diagnostics

Proposed commands:

```bash
adhara doctor .

adhara inspect .

adhara verify .
```

Diagnostics should report:

- Framework installation
- Configuration validity
- CLI protocol status
- Connector readiness
- Architecture status
- Dependency availability
- Runtime errors

### Observability

Initial observability should be lightweight.

Advanced metrics or tracing should remain optional.

---

## 26. Configuration Management

AdharaSutra provides centralized configuration facilities.

### Supported Sources

- Framework defaults
- Application configuration files
- Environment variables
- CLI overrides
- Explicit runtime configuration

Precedence rules must be documented.

### Proposed Configuration

```yaml
application:
  name: vani
  version: 1.0.0

runtime:
  mode: persistent-cli

protocol:
  version: "1.0"

connectors:
  http:
    enabled: true

  cli:
    enabled: true

  sqlite:
    enabled: true
    database: data/application.db

jobs:
  max_concurrent: 2

logging:
  level: INFO
  destination: stderr
```

Configuration must be validated before runtime initialization.

Secrets should be supplied through appropriately protected sources rather than committed configuration files.

---

## 27. Package Organization

AdharaSutra should use a modular structure.

### Proposed Repository

```text
adhara-sutra/
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
│
├── packages/
│   ├── adharasutra-core/
│   ├── adharasutra-cli/
│   ├── adharasutra-state/
│   ├── adharasutra-jobs/
│   ├── adharasutra-connectors/
│   ├── adharasutra-architecture/
│   ├── adharasutra-migration/
│   └── adharasutra-scaffold/
│
├── integrations/
│   ├── comfyui/
│   ├── lmstudio/
│   └── audiocpp/
│
├── electron/
│   └── electron-bridge/
│
├── templates/
│   ├── minimal/
│   ├── cli/
│   ├── ddd/
│   ├── electron-cli/
│   └── ai-worker/
│
├── skills/
│   ├── create-application/
│   ├── inspect-architecture/
│   ├── verify-architecture/
│   └── migrate-application/
│
├── examples/
│   ├── basic-cli/
│   ├── electron-app/
│   └── external-integration/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contracts/
│   └── migration/
│
├── docs/
│   ├── architecture/
│   ├── protocol/
│   ├── connectors/
│   ├── migration/
│   └── verification/
│
└── openspec/
```

This is the target logical structure.

The initial implementation may use a single Python distribution with internal modules to reduce packaging complexity.

Separate distributions should be introduced when dependency isolation or independent releases justify them.

---

## 28. Packaging and Distribution

### Python

Proposed package:

```text
adharasutra
```

Proposed command:

```bash
adhara
```

Proposed Python API:

```python
from adharasutra import Application
```

### Electron

Proposed npm package:

```text
@adharasutra/electron-bridge
```

### Distribution Goals

- PyPI-compatible Python packages
- npm-compatible Electron bridge
- GitHub-hosted source repositories
- Automated releases
- Semantic versioning
- Reproducible builds
- Documented compatibility matrix

### Versioning

The framework, CLI protocol, architecture profiles, and report schemas must be versioned independently where appropriate.

Breaking changes must have documented migration paths.

### Electron Packaging

The framework should provide reusable packaging recipes for Python-backed Electron applications.

It must account for:

- Python runtime distribution
- Executable discovery
- Application resource paths
- Packaged dependency locations
- Platform differences
- External executable requirements
- Startup diagnostics
- Production smoke tests

The framework must not assume that a Python development environment exists on the end user's machine.

---

## 29. Continuous Integration

AdharaSutra should provide reusable CI templates.

### Required Checks

- Python unit tests
- CLI protocol tests
- Architecture verification
- Static analysis
- Type checking
- Package build validation
- Migration fixture tests
- Dependency compatibility
- Electron bridge contract tests

### Proposed CI Workflow

```yaml
name: Architecture Verification

on:
  pull_request:
  push:
    branches:
      - main
      - develop

jobs:
  verify:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync --locked --group dev

      - name: Verify architecture
        run: uv run adhara verify . --level static

      - name: Run tests
        run: uv run pytest
```

This workflow is illustrative and requires implemented CLI commands, configured dependencies, and selected action versions.

### Architecture Drift Prevention

CI should detect newly introduced violations.

Existing applications may use a migration baseline during incremental adoption.

New violations should fail CI according to the configured severity policy.

---

## 30. Development Roadmap

### Phase 1 — Core Framework and CLI Protocol

Deliverables:

- Application runtime
- Configuration system
- Action registration
- CLI router
- Request/response schemas
- Structured errors
- Logging
- Basic lifecycle
- Contract tests

**Goal:** Build an application with no custom CLI infrastructure.

### Phase 2 — Connector Infrastructure

Deliverables:

- HTTP connector
- CLI subprocess connector
- SQLite connector
- WebSocket connector
- Connector registry
- Health and lifecycle support
- Test doubles

**Goal:** Applications use standard infrastructure instead of duplicated integration code.

### Phase 3 — State and Job Engine

Deliverables:

- State store
- Persistent-state facilities
- Job lifecycle
- Progress events
- Cancellation
- Concurrency control
- Persistent CLI sessions

**Goal:** Provide consistent execution and state management.

### Phase 4 — Electron Bridge

Deliverables:

- Shared TypeScript package
- Process lifecycle
- Protocol communication
- Event subscriptions
- Cancellation
- Error mapping
- Electron integration tests

**Goal:** Every Electron application communicates with Python through the same interface.

### Phase 5 — Architecture Discovery and Verification

Deliverables:

- Source discovery
- Import graph analysis
- Architecture rules
- Static verification
- Runtime contract verification
- Implementation reports
- JSON findings
- CI integration

**Goal:** Understand and deterministically verify application architecture.

### Phase 6 — Migration Engine

Deliverables:

- Legacy application analysis
- Gap analysis
- Migration reports
- Compatibility mappings
- Migration task generation
- Safe codemods
- Migration baseline
- Verification-driven migration

**Goal:** Move existing applications to AdharaSutra incrementally.

### Phase 7 — Scaffolding and OpenSpec

Deliverables:

- Project generator
- Architecture profiles
- OpenSpec templates
- Cross-agent skills
- Development recipes
- Example applications

**Goal:** Make new application creation consistent and repeatable.

### Phase 8 — Packaging and Production Hardening

Deliverables:

- PyPI publishing
- npm bridge publishing
- Release automation
- Packaged Electron testing
- Security validation
- Compatibility documentation
- Stable public API

**Goal:** Establish AdharaSutra as a reliable foundation for production applications.

These phases describe a target sequence. Dependencies between phases may require building thin versions of later components earlier—for example, the Electron protocol should be validated with a basic bridge during Phase 1.

---

## 31. Non-Goals

AdharaSutra is not intended to:

- Contain consuming applications' business logic.
- Replace Electron as the desktop UI technology.
- Require FastAPI or another HTTP server between Electron and Python.
- Reimplement HTTPX, SQLite, Typer, or established Python libraries without a clear need.
- Force every application to use every connector.
- Mandate complete DDD layering for small utilities.
- Automatically rewrite complex legacy business logic without review.
- Use an LLM as the authoritative architecture compliance checker.
- Guarantee business correctness solely through architecture verification.
- Require ComfyUI, LM Studio, or audio.cpp for the core runtime.

---

## 32. Definition of Done

### Framework Runtime

- Applications can initialize using AdharaSutra.
- The framework manages CLI routing and lifecycle.
- External connectors can be registered.
- Structured responses and errors follow the common protocol.
- State and jobs follow documented lifecycle rules.
- Core runtime tests pass.

### New Applications

- Project scaffolding generates a valid application.
- The application uses AdharaSutra as its runtime.
- Business logic remains application-specific.
- Architecture verification passes.
- CLI contract tests pass.

### Existing Applications

- Current implementation is documented.
- Architecture gaps are identified.
- Migration tasks are generated.
- Existing behavior is preserved.
- Shared infrastructure replaces duplicated implementations.
- The Electron CLI contract is maintained or compatibly migrated.
- Architecture verification passes.
- Required regression tests pass.

### Coding-Agent Integration

- Architecture reports contain source evidence.
- Migration plans contain actionable tasks.
- Reports use common formats across agents.
- Stale reports can be detected.
- OpenSpec artifacts can be generated where enabled.
- Deterministic verification determines mandatory compliance.

---

## 33. Guiding Architectural Rules

1. AdharaSutra is the foundational runtime for consuming applications.
2. Application business logic must remain outside the framework.
3. Electron communicates with Python through the unified CLI protocol.
4. External integrations must not dictate the Electron communication interface.
5. The framework manages common infrastructure mechanisms.
6. Applications define domain behavior and integration-specific operations.
7. Framework interfaces must support mocking and testing.
8. Architecture conventions must be deterministic and enforceable where possible.
9. Migration must preserve verified existing behavior.
10. Every migration change must have evidence and acceptance criteria.
11. Architecture reports must distinguish facts, assumptions, and recommendations.
12. The core framework must remain usable without any LLM.
13. New and existing applications must converge on the same architecture standard.
14. Framework upgrades must account for protocol, schema, and behavioral compatibility.
15. Complexity should be introduced only when justified by concrete requirements.

---

## 34. Example End-to-End Workflow

### Create a New Application

```bash
adhara new my-app \
  --profile electron-cli \
  --architecture ddd

cd my-app

adhara verify .
```

Implement application-specific actions and business logic.

The framework handles CLI routing, protocol communication, state, and infrastructure.

### Inspect an Existing Application

```bash
adhara inspect ./existing-app
```

Review the generated current implementation report.

### Verify Architecture

```bash
adhara verify ./existing-app \
  --level full \
  --format json
```

Review violations, source evidence, and unsupported checks.

### Generate Migration Plan

```bash
adhara migrate plan ./existing-app \
  --openspec
```

Use the generated plan with Claude Code, Codex, OpenCode, or a human developer.

### Implement and Reverify

After each migration unit:

```bash
adhara verify ./existing-app

adhara migrate status ./existing-app
```

Run the relevant application regression and Electron integration tests.

Continue until the applicable architecture requirements are satisfied.

---

## 35. Long-Term Vision

AdharaSutra aims to become a common foundation across Python-backed desktop applications.

A developer or coding agent should be able to enter any AdharaSutra application and quickly determine:

- How the application starts
- How Electron communicates with Python
- Where its business logic belongs
- How external dependencies are accessed
- How state and jobs are managed
- How application errors are reported
- Which architecture rules apply
- Whether the implementation complies
- What needs to change during migration
- How to verify changes

The framework should make application development more consistent, reduce repeated engineering effort, and provide a verifiable architecture that remains understandable across projects and coding agents.

---

## Project Identity

**Name:** AdharaSutra  
**Sanskrit:** आधारसूत्र  
**Meaning:** Foundation or supporting principle  
**Category:** Python Application Framework  
**Primary Interface:** CLI  
**Primary Frontend Integration:** Electron  
**Design:** Framework-first, business-logic independent  
**Architecture:** DDD-compatible, Hexagonal, Modular  
**Verification:** Deterministic-first  
**Migration:** Incremental and evidence-driven

**AdharaSutra — Build once. Standardize everywhere.**

---

## License

MIT License — proposed.

A `LICENSE` file should be added when the repository is initialized and the license is finalized.
