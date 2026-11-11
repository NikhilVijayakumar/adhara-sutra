---
type: Concept
title: Configuration and lifecycle
description: Configuration precedence, runtime composition, readiness and cleanup.
status: draft
tags: [configuration, lifecycle, runtime]
---

AdharaSutra (proposed) owns configuration loading, merging, validation and diagnostics, and coordinates initialization, readiness and shutdown; applications define their own settings, schemas, services and business behavior. The central guarantee: every managed component has an explicit configuration, dependency relationship, lifecycle owner and cleanup policy. The core configuration and lifecycle foundation must remain usable without optional HTTP, WebSocket, SQLite or job-management dependencies.

# Configuration sources and precedence

Proposed sources, lowest to highest precedence: framework defaults, application defaults, base configuration file, environment-specific file, environment variables, explicit runtime or CLI overrides. YAML is the proposed primary file format (JSON/TOML via explicit loaders); the exact precedence and default format are proposed, not approved. Framework defaults stay conservative and never silently enable expensive optional infrastructure. Environment variables follow a deterministic namespace convention (e.g. `ADHARA_RUNTIME_MODE`); explicit overrides come only from trusted startup configuration, never unrestricted Electron renderer code. Unknown keys are rejected in strict production validation unless an extension namespace declared them. Named environments (development, test, production) are selected explicitly through trusted startup configuration and must not mix dev paths, production credentials, test-only dependencies or debug policies.

Proposed merge policy: nested mappings merge recursively where schema permits; scalars are replaced; lists are replaced, never implicitly concatenated (concatenation risks duplicated connectors or permissions). Missing, explicit null, default and required-but-missing values must be distinguishable; explicit null must not silently mean "remove". Invalid higher-precedence overrides must fail validation rather than silently fall back to lower-precedence values.

# Validation and error reporting

Validation runs in stages — parse syntax, merge, check types and required fields, cross-field constraints, resolve paths and secret references, validate capability dependencies — before dependent components initialize. Cross-field examples: persistent state requires a persistence adapter; persistent CLI mode requires compatible protocol settings; an enabled connector requires its dependencies. Production may validate stricter than development (e.g. no silent dependence on a development virtual environment). Validation errors identify the configuration key, failure category, expected constraint, source location and safe remediation guidance; diagnostics identify which source supplied each effective value without revealing sensitive values. Proposed error codes include `CONFIG_VALIDATION_FAILED`, `CONFIG_UNKNOWN_KEY`, `CONFIG_OVERRIDE_INVALID` and `CONFIG_SECRET_UNAVAILABLE`, to be reconciled with the framework-wide error catalog.

# Configuration snapshots and secrets

The runtime uses one immutable, validated configuration snapshot per instance; business actions must not mutate it, and a changed file on disk does not imply the running application adopted it. Components receive typed slices of their required configuration, not unrestricted access to all secrets. Secrets are declared as references (resolved via protected sources such as environment variables or OS credential stores) only when required by authorized components, and are redacted from logs, configuration dumps, error envelopes, Electron events and diagnostics. The framework prevents accidental exposure; it cannot guarantee secrecy against malicious code running inside the same process. Live reloading is deferred: settings would first need reconfiguration categories (immutable, restart-required, component-restart, dynamically reconfigurable) with validation, affected-component, in-flight-operation, ordering and rollback semantics.

# Application bootstrap

Proposed bootstrap sequence: create application definition → load configuration sources → merge and validate → resolve environment and secrets → register capabilities → build dependency graph → validate composition → initialize required components → restore required persistent state → initialize application services → initialize CLI runtime → evaluate readiness. Actual ordering of restoration, services and connectors follows the validated dependency graph; independent components may initialize concurrently where safe, without unnecessary serialization. Initialization policies are eager, lazy (first-use, safe under concurrent first use, one instance per scope) or conditional; invalid combinations (e.g. a required eager service depending on an unavailable component) are rejected. Cycles and missing dependencies produce structured composition errors before affected services start. Bootstrap must not execute unrelated business actions, start optional connectors without declared need, ignore invalid configuration, suppress required initialization failures, or depend on Electron for standalone CLI operation.

# Partial startup failure

If a component fails after others have initialized, the framework stops initialization, closes already-started components in reverse dependency order, records the failure and reports startup failure; readiness stays false. Cleanup failures must not overwrite the original initialization failure — both are retained in controlled diagnostics. Initialization is not retried indefinitely; bounded retry policies require side-effect consideration. Cleanup cannot guarantee reversal of external side effects; application-specific compensation is required for durable effects created during initialization.

# Lifecycle states and transitions

Proposed states: created → configuring → initializing → ready → running → stopping → stopped, plus failed. Invalid transitions are rejected; readiness is never reported before required initialization completes; once stopping begins, ordinary new work is not admitted; fatal failures are not hidden by later nonfatal events; transitions are observable through diagnostics and events. Proposed policy: preserve fatal-failure information separately from cleanup state so failure evidence is not lost (whether FAILED is externally final remains open). Managed components follow a minimal start/close contract, with optional readiness, health, reconfiguration, failure-notification and shutdown-preparation capabilities; lightweight components without external resources are not forced to implement empty lifecycle operations. Lifecycle hooks (before_start, after_configuration, before_ready, after_ready, before_shutdown, after_shutdown, on_failure) are framework-executed with explicit registration, ordering, timeout and error policies; hooks must not bypass service composition or start unmanaged resources, and critical hook failures may abort startup.

# Start and stop ordering

Components initialize dependency-aware (topological); a connector not required by the application never becomes an obligatory startup dependency, and unused optional modules are not installed or initialized merely because the framework supports them. Shutdown releases components in an order respecting dependencies and active resource ownership: connectors are not closed before their dependent active operations are completed, cancelled or released. Application-scoped resources live for the runtime's lifetime; request-scoped resources are cleaned when their execution context completes; job-scoped resources belong to the Job Manager. A longer-lived service must not retain unsafe references to shorter-lived services (scope violations should be detected where possible).

# Readiness, health and runtime failure

Readiness ("can this application accept this operation?") is distinct from health ("is this component functioning per its checks?"). The runtime reports ready when required configuration is valid, required services are initialized, mandatory dependencies satisfy their readiness policies, the CLI transport can process supported requests, and shutdown has not begun. An optional connector failure need not break overall readiness — capability-level readiness (e.g. voice_generation READY, image_generation DEGRADED) avoids treating every optional failure as total failure, and readiness changes are exposed through diagnostics and approved events. Failures are classified by impact: request failure (fails the request), component failure (degrades a capability), required-service failure (may make the runtime unready), fatal runtime failure (controlled shutdown), process termination (external bridge detects loss). Expected operation failures must not terminate unrelated healthy operations; fatal infrastructure failures may require shutdown when safe continuation cannot be guaranteed.

# Graceful shutdown and signals

Triggers: one-shot completion, Electron shutdown, authorized `system.shutdown`, operating-system termination signal, fatal runtime failure, or explicit application lifecycle request. Proposed sequence: mark STOPPING → stop new request admission → apply active-request and job shutdown policies → wait within defined deadlines → release job and request resources → close application services → close connectors and state stores → flush diagnostics → close protocol transport → mark STOPPED; exact order derives from dependencies and resource ownership. Active requests complete, are cancelled, or fail with a shutdown error per mode- and operation-dependent policy; committed persistent state is never deleted during ordinary shutdown. Deadlines are configurable; if graceful shutdown cannot complete, the owner may escalate to platform-supported termination. Repeated shutdown requests must not run unsafe duplicate cleanup. Forced termination can leave outcomes unknown — the framework must not claim successful completion merely because termination was requested.

# Error contracts during startup and shutdown

Errors preserve a stable category, affected component, lifecycle phase, correlation metadata, safe human-readable explanation and internal diagnostic cause. Proposed lifecycle codes include `LIFECYCLE_INVALID_TRANSITION`, `LIFECYCLE_INITIALIZATION_FAILED`, `LIFECYCLE_NOT_READY`, `LIFECYCLE_SHUTTING_DOWN`, `LIFECYCLE_SHUTDOWN_FAILED`, `LIFECYCLE_CLEANUP_FAILED` and `LIFECYCLE_TIMEOUT`; composition codes include `SERVICE_NOT_REGISTERED`, `SERVICE_DEPENDENCY_MISSING`, `SERVICE_DEPENDENCY_CYCLE` and `CAPABILITY_UNAVAILABLE`. Startup diagnostics identify the initialization phase, failed component, dependency chain, failure category, cleanup status and safe remediation. Shutdown failures (job cancellation, process termination, connector close, persistence or log flush, timeouts) are aggregated without halting remaining cleanup, and the final process outcome reflects fatal shutdown failures per the approved exit-code policy. The lifecycle manager makes a best effort to clean up managed resources, but cannot guarantee cleanup after abrupt OS termination or unrecoverable process failure.

# Runtime modes and Electron

One-shot mode initializes only the resources the requested action requires, executes it, returns a terminal response and exits; state is volatile unless explicitly persisted, exit codes follow the CLI protocol policy, and a one-shot process must not acknowledge a background job as continuing unless a real separate execution owner exists. Persistent mode (for Electron-backed applications) initializes reusable resources once and retains them across requests, maintaining request isolation and enforcing concurrency limits; session readiness is established only after required initialization and the CLI handshake succeed. Electron main owns the Python backend: unexpected Python termination invalidates pending requests as transport-level failures; restart follows a bounded configured policy without replaying non-idempotent business actions; renderer reload must not restart the runtime; packaged production paths resolve independently of development assumptions. A restarted process is a new runtime instance whose in-memory state is rebuilt or restored per explicit policies.

# Alternatives considered

- Rejected initially: distributed configuration service, Kubernetes-style orchestration, service-discovery cluster, runtime dependency installation, automatic secret synchronization, mandatory live reload, workflow orchestration engine, complex dependency-injection container, mandatory startup of all connectors, automatic recovery from every fatal failure.
- TOML vs YAML as the default format; Pydantic vs dataclasses vs a validation abstraction — the public contract should not bind application domain code to one library.
- Custom dependency-injection container vs explicit registration, factories and dependency resolution (recommended: the latter).
- Async-only lifecycle hooks vs allowing simple synchronous components through adapters (recommended: both).
- Reloading corrected configuration after failed startup without restart vs process restart (recommended: restart — simpler and more predictable).

# Open questions

- CL-OQ-001 — Configuration format: should YAML be the default, or TOML preferred for Python-centric applications?
- CL-OQ-002 — Configuration schema technology: Pydantic, dataclasses, or an abstraction supporting multiple validation technologies?
- CL-OQ-003 — Dependency injection: should the framework implement a custom dependency-injection container?
- CL-OQ-004 — Lifecycle async model: should all managed components expose asynchronous lifecycle hooks?
- CL-OQ-005 — Readiness granularity: overall readiness only, or also capability-level readiness?
- CL-OQ-006 — Live configuration reloading: should configuration files be watched automatically?
- CL-OQ-007 — Service initialization concurrency: should independent components initialize concurrently by default?
- CL-OQ-008 — Shutdown deadline defaults: what deadlines should apply to requests, jobs, connectors and overall shutdown?
- CL-OQ-009 — Lifecycle hook ordering: explicit priorities or dependency declarations?
- CL-OQ-010 — Configuration error recovery: reload corrected configuration after failed startup without restarting the process?
- CL-OQ-011 — Multiple runtime instances: should one Python process host multiple AdharaSutra applications?
- CL-OQ-012 — Secret provider interface: which credential providers should be included initially?
- CL-OQ-013 — Runtime diagnostics exposure: should Electron be allowed to retrieve the effective configuration?
- CL-OQ-014 — Failure recovery: should critical components support automatic reinitialization after runtime failure?

See [configuration requirements](../../docs/requirements/functional-configuration-requirements.md), [runtime requirements](../../docs/requirements/functional-application-runtime-requirements.md), and [dependency management requirements](../../docs/requirements/functional-dependency-and-service-management-requirements.md).
