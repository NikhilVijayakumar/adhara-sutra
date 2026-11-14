---
type: Concept
title: Architecture and boundaries
description: Proposed framework, application, and Electron boundaries.
status: draft
tags: [architecture, boundaries]
---

# Proposed boundaries

## Current implementation and review boundary (2026-11-13)

Current package paths are `nikhi.adhara_sutra`, not the illustrative layout below.
Persistent requests are sequential; short actions can submit async background jobs.
Jobs run concurrently on the event loop and sync handlers run inline with a registration
warning. Timeouts and cancellation are cooperative. HttpClient is synchronous; SQLite
is optional and thread-owned. Persistence stores job metadata, not durable execution.
The fixed-command Node bridge exposes `jobStatus` and job cancellation. Business
submission, listing, and authorization stay application-owned. Generated minimal/cli
profiles share selection with verification and migration; DDD/Electron/AI remain candidates.

The remaining sections preserve draft design context and alternatives. In particular,
their concurrent-request and proposed service-lifetime descriptions are not current
API promises. Current API/wire shapes are in the maintained
[protocol reference](../docs/protocol-reference.md) and runtime source. The
[independent review](../docs/architecture-review-2026-11-13.md) explains confirmed
gaps and recommended targets, tracked by
[the architecture integrity change](../openspec/changes/architecture-integrity-review/proposal.md).
Shared profile selection, job status, captured source identity, and completion gates
are implemented as tracked there. Async HTTP and Node-owned backend discovery remain
conditional integration work; the runtime/tooling import boundary remains deferred.

## Historical draft design context

AdharaSutra is the proposed foundational runtime for independent Python applications.
Applications use its public interfaces and register their own business behavior; the
framework manages runtime and infrastructure without importing application modules;
Electron talks to Python only through a versioned CLI process protocol; connectors
access external services and resources. The framework owns the application foundation,
applications own their business capabilities (SA-001–SA-003), and development tooling
is never required to execute an already-packaged application (SA-004). Five subsystems
are proposed: core runtime, communication runtime, infrastructure runtime, architecture
tooling, and application development and migration tooling. Discovery, verification,
scaffolding, and migration should share consistent rules, with deterministic evidence
as the basis for mandatory checks and unsupported checks kept visible.

# Component responsibilities

- Framework-owned: application initialization, configuration loading and validation, service and connector registration and lifecycle, request validation and routing, execution contexts, response and event serialization, technical error normalization, logging, state and job infrastructure, external process management, and shutdown coordination.
- Application-owned: business entities and models, domain services and policies, use cases, action handlers, workflows and validation, state schemas, domain repositories, service-specific integration adapters, and business error definitions.
- An application extends AdharaSutra by registering capabilities — it must not build another application framework around it or recreate its communication, lifecycle, or infrastructure mechanisms.

# Dependency rules

The proposed default for complex applications is DDD/hexagonal: interfaces call the
application layer, which calls the domain; infrastructure implements contracts the
application or domain layers define; composition happens at the outer boundary.

- Allowed: Domain → Domain only; Application → Domain plus application-defined ports; Infrastructure → application ports and domain models where necessary; Interfaces → application services and request/response models. The composition root is the one intentional exception — wiring all layers is its job.
- Prohibited: domain importing infrastructure, Electron, CLI transport, HTTPX, or raw subprocess management; application importing concrete infrastructure; infrastructure importing interface-layer handlers; actions implementing protocol framing. Domain code stays testable as plain unit tests.
- Framework rules: high-level contracts never depend on low-level implementations; core never imports optional connectors, application business modules, or development tooling; circular imports between framework modules are prohibited.
- Forbidden: CLI protocol importing application handlers; connectors importing consuming application domains; runtime modules importing project-specific adapters such as audio.cpp; the verifier importing or executing application code during static analysis.
- Permitted: CLI transport → core contracts plus CLI protocol; connectors → connector base plus configuration; state → core contracts plus persistence ports (never SQLite directly); jobs → core plus state/event interfaces; migration → discovery, verification, and reporting models.

# Proposed module structure

One Python distribution (a modular monolith) with internal module boundaries and optional
dependency groups is proposed; separate distributions (adharasutra-http, -process, -sqlite,
-architecture, -migration, -scaffold) are extracted only when justified — stable interfaces,
dependency isolation, or release cadence. The Electron bridge remains a separate TypeScript
package (different runtime).

- `adharasutra.core` — application kernel, context, bootstrap, lifecycle, service registry and composition, configuration, errors, shared types.
- `adharasutra.cli` — protocol models and validation, one-shot and persistent transports, action registry, dispatcher, session manager, request correlation.
- `adharasutra.connectors` — connector base, registry, and health plus HTTP, WebSocket, external-process, SQLite, and filesystem connectors (no custom ORM).
- `adharasutra.state` — stores, scopes, subscriptions, concurrency, persistence ports.
- `adharasutra.jobs` — manager, scheduler, lifecycle, progress, cancellation, recovery.
- `adharasutra.events` — dispatcher, models, subscriptions; in-process only, no distributed broker initially.
- `adharasutra.observability` — logging, diagnostics, correlation; protocol on stdout, diagnostics on stderr.
- `adharasutra.tooling` — scaffold, discovery, verification, migration, reporting (development only).
- `adharasutra.developer_cli` — proposed `adhara new/inspect/verify/migrate/doctor` commands, separate from the application runtime CLI.
- `@adharasutra/electron-bridge` — Electron-side protocol serialization, request tracking, cancellation, crash detection, compatibility negotiation.

Every application requires the core runtime, configuration, lifecycle, CLI protocol,
action router, and basic logging. Everything else is opt-in per profile — a minimal
CLI application must not require SQLite, jobs, or unrelated connectors; persistent
sessions and the job engine become recommended for Electron-CLI and AI-worker profiles.

# Runtime process topology

- The Electron renderer owns presentation and user interaction only — no process spawning or backend protocol parsing. A restricted preload exposes an allowlisted API; the Electron main process owns Python runtime discovery, process creation and ownership, IPC authorization, shutdown coordination, and bridge lifecycle.
- The shared bridge negotiates protocol compatibility, correlates requests, and handles timeouts, cancellation, progress-event streaming, and Python crash reporting.
- Python speaks UTF-8 newline-delimited JSON: stdin carries requests, stdout carries protocol messages, stderr carries diagnostics — one message per line. The framework owns the envelope structure (requests, responses, events, errors, cancellation, session control); the application owns action and payload semantics.
- One-shot CLI: a process per command that terminates after returning its result — simple lifecycle, no in-memory state between invocations, startup overhead per request.
- Persistent CLI: one Python process serves many requests with event streaming, concurrent async actions, persistent connections, and centralized state/job coordination — the proposed default for Electron-backed apps, one-shot remaining for standalone commands, diagnostics, and automation. In-memory state never survives process termination; persistence requires a configured backend.
- Deployment models: standalone CLI; Electron with bundled Python (environment or frozen executable — packaging open); Electron with externally installed dependencies (ComfyUI, LM Studio, audio.cpp) that must be locatable, configurable, and diagnosable; Windows, Linux, macOS with platform-specific process management isolated behind framework interfaces.

# Extension points

Applications extend through registration, never by modifying framework internals:
business actions, application services, domain interfaces and ports, integration
adapters, state schemas, job handlers, and lifecycle hooks. Conceptual shapes
(`Application(name, version)`, `@app.action(...)`, `app.register_service(...)`) are proposals.

- The framework owns request parsing, validation, action lookup, execution context, error translation, serialization, and progress delivery; the handler owns behavior, business validation, and workflow decisions.
- Proposed service lifetimes: application, session, request, job — explicit registration and composition, with no general-purpose DI container unless requirements justify it.
- Service-specific adapters (ComfyUI, LM Studio, audio.cpp) translate domain operations onto framework connectors and may ship as optional plugins. Shell interpretation is disabled by default in the process connector; large outputs move as artifact file references, not inline protocol payloads.
- Internal events do not automatically become Electron protocol events; the CLI event adapter decides external exposure.

# Alternatives considered

- Framework inheritance vs composition and registration — registration chosen: clearer extension points, less coupling, easier testing, friendlier to independently developed applications.
- Local HTTP server (e.g. FastAPI) vs CLI process communication between Electron and Python — CLI chosen: no extra local server, terminal and automation support, one common bridge across applications.
- Persistent vs one-shot CLI — both supported; persistent preferred for repeated interactive desktop operations.
- Unified connector interface vs specialized interfaces — shared lifecycle plus connector-specific capabilities; a generic connector must not hide database transactions or process streaming.
- One vs many Python packages — modular monolith first, extraction only when justified.
- In-process and managed-subprocess jobs vs durable external workers — the former first; durable workers are a future extension, and a job record in SQLite is not durable execution by itself.
- Strict DDD layering vs simplicity — multiple architecture profiles (minimal, cli, ddd, electron-cli, ai-worker) composing capabilities over one shared runtime; small utilities are not forced into empty DDD layers.
- Shared application context vs explicit injection — context at framework boundaries, explicit dependencies in business services, avoiding an unrestricted service locator.
- Python state vs Electron UI state — presentation-only state stays in Electron; authoritative, shared, persisted, or job-coordinated state lives in Python.

See [runtime requirements](../docs/requirements/functional-application-runtime-requirements.md),
[architecture governance](concepts/architecture-governance.md), and the
[requirements index](../docs/requirements/README.md).
