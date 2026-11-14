# CLI Protocol Reference

This is the maintained reference for the AdharaSutra CLI protocol: message
shapes, built-in actions, errors, sessions, versions, and process exit codes.

The protocol is versioned independently of the framework package. The current
protocol version is `1.0`, exported as `nikhi.adhara_sutra.PROTOCOL_VERSION`;
`SUPPORTED_PROTOCOL_VERSIONS` lists every version the runtime accepts.

## Transport

- Newline-delimited JSON over standard input and standard output.
- One JSON object per line. A line larger than 1 MiB or one that does not end in
  a newline is a protocol failure.
- Standard output carries protocol messages only. Diagnostics go to standard
  error as structured JSON when `configure_logging()` is installed.
- Requests are processed sequentially in a persistent session. Jobs may run
  concurrently inside the process.

## Messages

Every message is a JSON object with a `kind` field.

### Request

```json
{
  "kind": "request",
  "protocol_version": "1.0",
  "request_id": "req-1",
  "action": "orders.create",
  "payload": {"sku": "ABC", "quantity": 2}
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `kind` | yes | Must be `"request"`. |
| `protocol_version` | yes | Must be one of `SUPPORTED_PROTOCOL_VERSIONS`. |
| `request_id` | yes | Non-empty string chosen by the caller; echoed in the response and events. |
| `action` | yes | Registered action name, or a `system.*` action. |
| `payload` | yes | JSON object. Validators may transform it before the handler runs. |

Unknown fields are ignored. Action names match
`^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*$` and may not start with
`system.` or `protocol.`.

### Response

```json
{
  "kind": "response",
  "protocol_version": "1.0",
  "request_id": "req-1",
  "success": true,
  "data": {"id": "ord-7"},
  "error": null
}
```

A failed request has `success: false`, `data: null`, and an error object.

### Event

Actions can emit events with `context.emit(name, data)` while processing a request;
those events precede that action's response and carry its `request_id`. A submitted
job runs independently and its events can arrive after the submission response. Job
events carry `job_id` and currently have a null `request_id`; correlate them by job ID.

```json
{
  "kind": "event",
  "protocol_version": "1.0",
  "request_id": "req-1",
  "job_id": "7f2c...",
  "event": "progress",
  "data": {"completed": 3, "total": 10}
}
```

## Built-in actions

| Action | Payload | Result |
| --- | --- | --- |
| `system.hello` | `{}` | `protocol_version`, `supported_protocol_versions`, `framework_version`, application `name` and `version`. |
| `system.help` | `{}` | `framework_version`, registered `actions` metadata, registered `jobs` metadata. |
| `system.health` | `{}` | `status` (`ok` or `degraded`), lifecycle `state`, and per-service `services` status. Requires a ready or running application. |
| `system.jobs.get` | `{"job_id": "..."}` | `job_id` and its `status` snapshot, or `null` for an unknown job. Requires a ready or running application. |
| `system.cancel` | `{"job_id": "..."}` | `job_id`, `cancelled` (whether cancellation was accepted), `cancellation` (`requested`, `completed`, `unsupported`, or `failed`), and the current `status` snapshot, or `null` for an unknown job. Requires a ready or running application. |

`system.help` actions carry `name`, `description`, `input_schema`, and
`output_schema` flags. Jobs carry `name`, `description`, and `timeout`.

## Errors

```json
{
  "code": "ACTION_VALIDATION_FAILED",
  "category": "validation",
  "message": "Invalid action payload",
  "retryable": false,
  "details": "quantity must be positive"
}
```

| Code | Category | Retryable | Meaning |
| --- | --- | --- | --- |
| `PROTOCOL_INVALID_MESSAGE` | `protocol` | no | Malformed envelope, missing field, oversized or incomplete line. |
| `PROTOCOL_INVALID_STATE` | `protocol` | no | Persistent session used before the `system.hello` handshake. |
| `PROTOCOL_UNSUPPORTED_VERSION` | `protocol` | no | `protocol_version` is not supported. |
| `ACTION_VALIDATION_FAILED` | `validation` | no | Payload validator rejected the input, or `system.cancel` omitted `job_id`. |
| `ACTION_OUTPUT_INVALID` | `validation` | no | The output hook or result could not be serialized. |
| `ACTION_NOT_FOUND` | `action` | no | Unknown action; `details.available_actions` lists registered names. |
| `RUNTIME_NOT_READY` | `lifecycle` | no | The application is not ready or running. |
| `CONNECTOR_FAILURE` | `connector` | from the error | A connector or external dependency failed. |
| `CONNECTOR_TIMEOUT` | `connector` | yes | A connector operation timed out; one-shot execution exits `5`. |
| `RUNTIME_EXECUTION_FAILED` | `internal` | unknown | An unexpected handler failure. |
| `JOB_QUEUE_FULL` | `lifecycle` | yes | The bounded job queue is at capacity. |

Messages and details are redacted before serialization: values under sensitive
keys and `key=value` or authorization-header assignments become `[REDACTED]`.
Internal tracebacks are not returned to callers.

## Sessions

One-shot execution reads one request, writes one response, and exits. A clean
persistent session reads requests until standard input closes. The first
persistent request must be `system.hello`; later requests are dispatched in
order. An action failure returns an error and keeps the session alive. A protocol
failure ends the session with exit code `8`.

The Electron/Node bridge uses the same protocol. It spawns one persistent
backend, performs the handshake, and refuses a backend that does not advertise
the bridge's protocol version.

## Version compatibility

- Package releases follow Semantic Versioning.
- The protocol version is independent of the application version.
- `system.hello` advertises the current protocol version and every supported
  version.
- Requests with any other `protocol_version` are rejected before dispatch.
- Machine-readable reports carry their own `schema_version`; verification
  reports also carry the architecture profile version.
- The Electron bridge exports `PROTOCOL_VERSION` and fails startup with
  `BRIDGE_PROTOCOL_UNSUPPORTED` when the backend does not support it.

`system.jobs.get` requires a non-empty string `job_id`; malformed IDs return
`ACTION_VALIDATION_FAILED` with details `job_id`. Applications own submission,
job listing, and access authorization for their exposed actions and bridge.

## Job terminal outcomes

Job status snapshots include a local `persistence` object. Its status is `pending`
while a stored job is active, `disabled` without a store, `saved` after a successful
terminal save or recovery, and `failed` with error code `JOB_PERSISTENCE_FAILED`
when the terminal save fails. A failed save does not change the actual local execution
outcome, but that outcome may not survive a restart; the diagnostic field itself is
not a durable database column. A failed running-state save prevents handler execution.

Job results must be JSON-compatible and cannot contain non-finite numbers. Invalid
results produce `JOB_OUTPUT_INVALID`; use an ArtifactStore reference for binary or
large data. A terminal save is attempted before waiters are released, and waiters are
still released if that save fails.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, or a cleanly ended persistent session. |
| `2` | No request was received, or an invalid invocation. |
| `3` | Initialization failed. |
| `4` | An action failed. |
| `5` | A connector operation timed out. |
| `6` | Interrupt or cancellation. |
| `7` | A connector or dependency failed. |
| `8` | A protocol failure. |
| `10` | An internal failure. |

In a persistent session, action and connector failures do not end the process;
they end a one-shot invocation with the matching code.

## Example exchange

```text
--> {"kind":"request","protocol_version":"1.0","request_id":"1","action":"system.hello","payload":{}}
<-- {"kind":"response","protocol_version":"1.0","request_id":"1","success":true,"data":{"protocol_version":"1.0","supported_protocol_versions":["1.0"],"framework_version":"0.1.0","name":"demo","version":"1.0"},"error":null}
--> {"kind":"request","protocol_version":"1.0","request_id":"2","action":"orders.create","payload":{"sku":"ABC"}}
<-- {"kind":"event","protocol_version":"1.0","request_id":"2","event":"progress","data":{"completed":1,"total":1}}
<-- {"kind":"response","protocol_version":"1.0","request_id":"2","success":true,"data":{"id":"ord-7"},"error":null}
```

## Related documentation

- [README](../README.md) for application, connector, state, job, and report usage.
- [Electron bridge](../bridge/README.md) for the Node API.
- [Requirements index](requirements/status.md) for requirement coverage.
