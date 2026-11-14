# AdharaSutra Electron bridge

A dependency-free Node/Electron main-process client for the AdharaSutra CLI
protocol. It spawns one Python application in persistent mode and exchanges
newline-delimited JSON over stdin/stdout.

```js
import { Bridge, BridgeError } from "@nikhi/adhara-bridge";

const bridge = new Bridge({
  command: "python",
  args: ["-m", "my_app", "--persistent"],
  env: { PYTHONPATH: "/path/to/my_app/src" },
});

bridge.on("event", (event) => {
  // { kind: "event", request_id, job_id?, event, data }
  console.log(event.event, event.data);
});
bridge.on("stderr", (line) => {
  // The Python runtime writes structured JSON diagnostics here.
  console.error(line);
});
bridge.on("exit", ({ code, signal, expected }) => {
  if (!expected) console.error("backend exited", code, signal);
});

await bridge.start(); // spawns the process and completes system.hello
const { message } = await bridge.request("greeting.create", { name: "Ada" });

const { job_id } = await bridge.request("report.submit", { month: "2026-11" });
const events = []; // progress events for this job carry the same job_id
bridge.on("event", (event) => event.job_id === job_id && events.push(event));

const { status } = await bridge.jobStatus(job_id); // null if the ID is unknown

const outcome = await bridge.cancel(job_id);
// { job_id, cancelled: true|false, status: { state, ... } | null }

await bridge.close();
```

`request()` resolves with the response's `data` and rejects with a `BridgeError`
for protocol or action failures. The error carries the stable `code`,
`category`, `retryable`, optional `details`, and the full `response` envelope.
Use `health()` for readiness and connector health and `help()` for registered
actions and jobs. `jobStatus(jobId)` reads the existing job snapshot; the
application owns job submission, listing, and any access authorization.

## Events and ordering

Events emitted by an action during its request precede its response. A submitted
job can emit events after the submission response; correlate its progress by
`job_id`, rather than assuming an order relative to that response. The bridge
delivers stdout messages in order. Distinguish events from responses with `kind`.
Malformed lines and uncorrelated responses are reported on `protocolError`.

## Cancellation and timeouts

`cancel(jobId)` sends `system.cancel`. It targets managed jobs only; the current
persistent session executes requests sequentially, so an action that is still
running cannot be cancelled until it returns. The result reports whether
cancellation was accepted (`cancelled`) and the job's current status; a job whose
operation cannot be interrupted may still finish normally. Pass
`defaultTimeoutMs` or `{ timeoutMs }` to reject a pending request. `BRIDGE_TIMEOUT`
includes `request_id`, `action`, `outcome: "unknown"`, and
`cancellation_requested: false` in its details. The timeout does not request
cancellation, stop the Python work, or retry it. A later response for the timed-out
request is currently emitted as an uncorrelated `protocolError`.

If the job ID is known, use `jobStatus(jobId)` to inspect it. If a job submission
response was lost, reconcile it using the application's own operation identity or
other application-specific mechanism before resubmitting.

## Failure handling

If the backend exits or its process fails, every pending request rejects with
`BRIDGE_PROCESS_EXITED` or `BRIDGE_PROCESS_FAILED`, and the bridge emits `exit`
or `processError`. `start()` rejects when the process cannot spawn, the handshake
fails, or the backend does not support protocol `1.0`. A backend that is not in
persistent mode exits after the handshake; keep it open with the application's
persistent flag.

## Security boundary

The command and arguments are fixed when the bridge is constructed. There is no
API that accepts a command, shell string, or path per request: renderer input
can only become an action name and payload. Use `shell: false` semantics (the
default here), keep the bridge in the Electron main process, expose a narrow
preload/IPC surface, and allowlist the actions the renderer may call. The bridge
does not evaluate shell strings and does not forward the renderer's environment.

## Limitations

- One backend process per bridge; the persistent session is sequential.
- Cancellation covers jobs, not in-flight requests.
- The bridge does not restart a crashed backend automatically.
- The package ships plain ESM JavaScript plus type declarations; no build step.
