# Tasks

Work on one requirement at a time: finish its implementation and practical
verification, update the requirement index, then select the next. Existing
partial work on other requirements remains recorded but is not active work.

## Active task

- [x] Complete and practically verify FR-RUN-001, framework-based application creation, against its acceptance criteria. Checked creation, startup and shutdown, invalid version, duplicate name, and name reuse after release.
- [x] Complete and practically verify FR-RUN-002, application bootstrap: validate configuration, start named service and connector dependencies in order, reject missing or cyclic dependencies, and clean up after partial failure.
- [x] Complete and practically verify FR-RUN-003, application lifecycle: managed states and transitions (including `running` during serving), invalid transitions rejected, lifecycle events observable via `on_lifecycle`, and shutdown releasing resources.
- [x] Complete and practically verify FR-RUN-004, application extension points: actions and services register via public API without framework modification, services use framework facilities, no framework dependency on consuming modules, handlers testable independently of CLI transport (direct dispatch and plain calls).
- [x] Complete and practically verify FR-RUN-006, runtime execution modes: one-shot `serve` executes a request and terminates; persistent `serve` processes multiple requests (handshake + actions) with consistent action semantics; runtime resources are started/stopped per serve session.
- [x] Complete and practically verify FR-RUN-005, application context: per-request context with isolated metadata (`request_id`, `action`), access to registered services/config, and clear `get_service` errors for unregistered capabilities.
- [x] Complete and practically verify FR-CLI-001, centralized CLI routing: actions invoked by identifier, unknown actions return standardized `ACTION_NOT_FOUND`, duplicate registrations rejected, routing contains no application-specific business logic.
- [x] Complete and practically verify FR-CLI-002, action registration: identifier validation, input/output schema hooks, sync and async handlers, and `list_actions()` discovery metadata.
- [x] Complete and practically verify FR-CLI-003, input validation: protocol envelopes rejected, payload validation errors structured with affected-field details before handler execution.
- [x] Complete and practically verify FR-CLI-004, structured output: valid success/error response envelopes with app data, and diagnostics separated from protocol stdout.
- [x] Complete and practically verify FR-CFG-003, configuration validation: `validate_config` runs before dependent services initialize and rejects invalid config.
- [x] Complete and practically verify FR-DI-001/002/003/004, service registration/resolution/lifecycle/validation: `app.service` registration with dependencies, dependency-ordered startup, context-managed cleanup, and detectable missing/circular dependency errors.
- [x] Complete and practically verify FR-DI-005/006, test replacement and optional dependencies: services replaceable with test implementations; unused capabilities not required.
- [x] Complete and practically verify FR-ERR-001/004/005, standard error model/serialization/sensitive-info protection: structured error envelopes with code/message/retryable/details and request correlation; frontend-facing errors follow protocol; internal details not exposed in responses.
- [x] Complete and practically verify FR-CFG-001/005, central configuration and application-specific settings: app config provided/accessible via centralized context; `validate_config` supports app-defined schemas and normalized config.
- [x] Complete and practically verify FR-CLI-005, one-shot CLI execution: a stdin request is dispatched, a structured response is returned, and the process exits with a documented status. Checked success (0), unknown action (4), invalid JSON and unsupported version (8), empty input (2), action failure (4), and initialization failure (3); persistent action failures do not force a nonzero exit.
- [x] Complete and practically verify FR-CLI-006, persistent CLI execution: multiple requests run in one process lifetime, responses correlate by `request_id`, handlers emit correlated events that precede the terminal response, and EOF or a malformed frame ends the session with documented cleanup and exit status.
- [x] Complete and practically verify FR-CLI-009, CLI version information: `system.hello` reports the application name and version, the framework version, and the supported protocol versions in both one-shot and persistent sessions.
- [x] Complete and practically verify FR-ERR-002, error classification: every protocol error now carries a stable `category` (protocol, validation, action, lifecycle, internal) derived from its code; checked each category and confirmed the mapping is stable across requests.
- [x] Complete and practically verify FR-ERR-003, error propagation: handler, validation, and startup failures keep their original exception as the cause and are logged with the traceback while responses stay safe; a shutdown failure no longer replaces an error already propagating.
- [x] Complete and practically verify FR-LOG-001..004, structured diagnostics: `configure_logging()` installs a JSON stderr handler that `run()` uses, request scope is tracked with a context variable so records carry `request_id`/`action`, tracebacks are preserved, stdout stays protocol-only, and records logged outside a request have empty correlation. Job correlation follows when jobs exist.
- [x] Complete and practically verify NFR-SEC-003 and FR-SEC-001, input validation: malformed envelopes, unsupported versions, missing or invalid identifiers and payloads, unknown actions, rejected payloads, invalid JSON, non-finite numbers, oversized or incomplete frames, and premature persistent requests are all rejected with structured errors before any handler runs; handshake negotiation only succeeds on a valid hello.
- [x] Complete and practically verify FR-CLI-008 and FR-CLI-010, CLI discovery and standard input: `system.help` returns machine-readable action metadata (name, description from the handler docstring, schema hooks) in both modes; unknown actions report the available names; requests are read from stdin as newline-delimited JSON. Verified the standard request/response envelopes and marked FR-ELC-001..004 complete.
- [x] Complete and practically verify FR-LOG-005, configurable log levels: `ADHARA_LOG_LEVEL` sets the default level, an explicit `configure_logging(level=...)` wins, invalid values fall back to INFO, and stdout stays protocol-only. Marked NFR-OBS-001/005 complete and NFR-OBS-002 partial (job correlation pending).
- [x] Add interrupt handling: an interrupt during serving releases managed resources, logs "Application interrupted", and exits with the cancellation status 6. FR-RUN-007 and FR-CLI-007 remain partial until jobs, subprocesses, timeouts, and dependency failures exist.
- [x] Complete and practically verify FR-STATE-001/002/003, state facilities: handlers share process state through `context.state`, share state within a persistent session through `context.session_state`, and receive a fresh `context.request_state` per request; applications define keys and values and service factories can seed process state. Marked FR-STATE-005 partial until persistent state exists.
- [ ] Select and complete the next requirement, updating the status index after verification.

## Review and design

- [ ] Review the traced requirements, reconcile source documents, and resolve open questions.
- [ ] Agree on lifecycle transitions, protocol schemas, error handling, and compatibility rules.
- [ ] Record durable architecture decisions and update the draft specifications.

## Implementation and verification

- [x] Create an installable Python package and a small consuming example.
- [x] Add initial action registration, managed services, and sequential one-shot and persistent JSON-line request handling.
- [x] Build and install the package locally; exercise the persistent handshake, a successful action, and unknown-action handling.
- [ ] Implement the approved runtime and action registration interfaces.
- [ ] Implement request validation, CLI routing, and response serialization.
- [ ] Complete lifecycle and validation behavior, including partial-startup cleanup and error reporting.
- [ ] Verify remaining one-shot and persistent behavior and channel separation through practical integration checks.
- [ ] Implement and verify the remaining proposed connector, state, job, Electron, security, architecture and packaging capabilities as applicable.
- [ ] Document verification results and unresolved requirements before archiving.
