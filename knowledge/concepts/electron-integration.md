---
type: Concept
title: Electron integration
description: Process boundaries, bridge ownership, protocol flows, security model, failure handling and packaging for Electron applications driving AdharaSutra Python backends.
status: draft
tags: [electron, protocol, security]
---

Proposed integration: a TypeScript bridge in the Electron main process manages a Python application runtime
over the versioned AdharaSutra CLI protocol (NDJSON on the child's stdin/stdout, stderr for diagnostics) —
one reusable, secure mechanism for consuming applications that keep their own UI and workflows.

# Process boundaries

Flow: the renderer calls an approved preload API, preload forwards over Electron IPC, main validates the
caller and operation and invokes the bridge, the bridge serializes a CLI request, Python dispatches to
application actions, and correlated responses or events return to the renderer. The renderer never touches
Python streams, processes or OS commands; the preload exposes only approved operations (conceptually
`execute`, `cancelJob`, `onEvent`) and blocks Node internals; the main process owns IPC registration,
renderer authorization, backend lifecycle, readiness and shutdown coordination.

# Bridge package boundaries

The proposed `@adharasutra/electron-bridge` package (TypeScript, Electron main/Node) is technical and
application-independent: process manager, executable resolver, protocol client (serialization, parsing,
framing, compatibility), request correlation and timeouts, event dispatcher, job client and cancellation,
error mapping, per-platform adapters. It contains no action handlers or business logic and is indifferent
to which connector an action uses. Applications may wrap it in typed clients or generated TypeScript
action types (proposed) without recreating process or protocol management; it requires no UI framework
and is installed as a dependency, not copied.

# Protocol and request/response flows

All Electron-to-Python communication uses the versioned CLI protocol over stdio; applications must not
implement competing transports. The recorded rationale is connector independence: whether an action is
backed by a ComfyUI-style HTTP service, an audio.cpp-style executable, LM Studio or SQLite, Electron sees
the same `bridge.execute(action, payload)`; external-system integration lives on the Python side. The
protocol is owned by AdharaSutra, versioned independently of bridge package, Python runtime, application
and action contracts (see the [CLI protocol concept](cli-protocol.md)); persistent sessions negotiate
versions at handshake and unsupported combinations fail explicitly.

Requests carry `kind`, `protocol_version`, `request_id`, `action`, `payload`; responses carry `success`,
`data`, `error`, correlated by `request_id` so concurrent requests may complete out of order (unrecognized
or duplicate terminal responses are protocol anomalies). Persistent mode is the recommended default — one
runtime multiplexes requests and keeps connectors, pools, SQLite connections and application state
initialized — while one-shot mode (spawn, one request, exit) serves diagnostics and short-lived commands
without surviving state or jobs. Events flow through a dispatcher with filtering by request/job/event
name, arrival-order preservation, bounded buffering and coalescing of low-value progress; terminal job
events are never dropped and progress is never invented. Job acceptance is distinct from job completion —
job lifecycle belongs to Python's job subsystem, and closing a renderer does not cancel jobs unless the
application defines that ownership; the initial protocol does not replay events, so late subscribers use a
job-status query. Cancellation uses the standard `system.cancel` action, distinguishing acknowledgment from
confirmed termination and handling completion-first races.

# Python process lifecycle ownership

The Electron main process owns every Python process the bridge starts, each with a defined owner and
cleanup policy. Proposed states: STOPPED → STARTING → INITIALIZING → HANDSHAKING → READY → RUNNING, plus
FAILED and STOPPING; READY requires initialization plus protocol handshake — the authoritative readiness
signal; ordinary requests wait for it. Startup resolves the runtime, validates the launch configuration,
spawns, attaches stream handlers, sends `system.hello` and validates the handshake under a configurable
timeout, cleaning up the owned process on failure. Discovery follows an explicit ordered configuration —
application configuration, packaged runtime manifest, approved development configuration, then explicitly
enabled system discovery; `PATH` is not assumed in production, and manifest paths resolve from approved
resource roots, not untrusted working directories. Shutdown stops new UI requests, notifies Python
(reserved `system.shutdown`, authorized callers only), lets it finish, cancel or transfer jobs and close
connectors under a configurable deadline that escalates to platform-specific forced termination; early
Electron termination requires explicit orphan cleanup.

# Failure and reconnection handling

Crash detection covers unexpected exit, exit without terminal response, closed stdout, unavailable stdin
and unrecoverable parsing. On termination the session is marked unavailable, pending requests are rejected
with transport-level errors, unknown remote outcomes are preserved, resources are released and a failure
notification is emitted; bounded, sanitized recent stderr is retained for diagnosis. Proposed restart
policies — disabled, manual, on crash, limited retry — defaulting for interactive applications to bounded
restart with backoff but no automatic replay: a side effect may already have happened, so replay needs an
explicit idempotency contract. Restart creates a new protocol session (state survives only via configured
persistent storage; job recovery is Python's concern). Renderer reload reconnects through the still-running
main-process bridge, with stale subscriptions removed. Bridge timeouts are client-side only: a local
timeout does not stop remote Python work, unknown remote status is preserved, and non-idempotent actions
are never automatically retried.

# IPC surface restrictions and security model

The renderer is not trusted for arbitrary OS operations; the main process validates access. Proposed
baseline: context isolation enabled, Node integration disabled in the renderer, a restricted preload API,
and explicit IPC handlers that verify the originating web contents and frame context. Applications expose
approved actions or namespaces; the bridge never turns renderer strings into shell commands — it is not a
remote-execution service. Only approved events reach renderer subscribers, sensitive diagnostics stay in
the main process, and renderer-supplied filesystem and executable paths follow explicit validation. Large
binaries never ride in JSON responses: Python returns managed artifact descriptors, the main process
validates references before exposing files, and the renderer gains no unrestricted filesystem access.

# Packaging implications

Supported strategies: a bundled Python interpreter plus dependencies (faithful semantics, larger
distribution); a frozen executable (simpler launch discovery, but native-dependency and per-platform build
issues); or an explicitly configured external runtime. Bundled and frozen share the runtime manifest and
executable resolver; the default is deferred until prototypes are validated. Development mode launches a
configured local environment with visible logs, readiness reporting and controlled restart; dev-only
capabilities must not leak into production, and renderer hot reload and backend restart are independently
configurable. Platform differences (paths, signals, permissions, bundles, signing, termination) stay
behind the bridge's resolver. Validation must test actually packaged applications, not only dev mode.

# Open questions

- EI-OQ-001 — Bundled Python environment or frozen executable as the packaged default? Validate both through production prototypes before choosing.
- EI-OQ-002 — Should one Electron application support multiple independent AdharaSutra Python processes? Start with one managed runtime; permit explicit instances only when justified.
- EI-OQ-003 — Should an Electron restart reconnect to previously running durable jobs? Only when Python has a real durable execution service and stable job-status API.
- EI-OQ-004 — Should the bridge restart Python automatically after a crash? Configurable bounded restart, but never automatically replay unknown-outcome actions.
- EI-OQ-005 — Should the bridge generate TypeScript action clients from Python action schemas? High-value feature after protocol contracts stabilize.
- EI-OQ-006 — Should the bridge expose per-window authorization, event routing and subscription ownership? Yes, without leaking between unauthorized consumers.
- EI-OQ-007 — Should applications expose Python stderr directly to users? No — controlled diagnostics with redaction and bounded retention.
- EI-OQ-008 — Should the bridge supply a dedicated artifact-serving mechanism? Prefer explicit, validated artifact access; finalize the transport in the artifact design.
- EI-OQ-009 — How should Electron display backend initialization and external dependency readiness? Keep runtime readiness distinct from optional connector health.
- EI-OQ-010 — Should the bridge package remain generic or include optional Electron helper modules? Keep the core generic; optional helpers for IPC registration, packaging and typed clients.

See [Electron communication requirements](../../docs/requirements/functional-electron-communication-requirements.md) and [CLI requirements](../../docs/requirements/functional-cli-framework-requirements.md).
