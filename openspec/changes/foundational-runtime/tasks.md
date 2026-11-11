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
