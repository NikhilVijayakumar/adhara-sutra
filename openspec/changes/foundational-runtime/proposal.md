# Foundational runtime and CLI protocol

## Why

Applications need a common runtime and action protocol before the framework can
support connectors, Electron integration, and migration. The source requirements
and architecture remain proposed; this change is a draft for review.

## What Changes

- Specify application bootstrap, lifecycle, and action registration.
- Specify validation, routing, structured responses, and CLI execution modes.
- Trace each drafted scenario to requirement IDs; see the
  [implementation status index](../../../docs/requirements/status.md) for coverage.

## Capabilities

### New Capabilities

- `application-runtime`: initialization, lifecycle, and application extensions.
- `cli-protocol`: action routing, validation, process channels, and responses.
- `connector-framework`: connector lifecycle, registration, and process safety.
- `state-and-jobs`: state boundaries and job execution ownership.
- `architecture-governance`: evidence-based verification and reviewable migration.
- `security-and-diagnostics`: trust boundaries and sensitive diagnostics.
- `testing-and-packaging`: contract-test support and packaged runtime discovery.
- `configuration-lifecycle`: configuration validation, startup and shutdown.
- `electron-bridge`: process ownership, readiness, and communication failure.

## Impact

This is a proposed specification. An initial runtime and CLI protocol are
implemented, but the change is not complete or approved; its other capabilities
remain largely unimplemented. See [implementation status](../../../docs/requirements/status.md).
Further work depends on
reviewing the [runtime](../../../docs/requirements/functional-application-runtime-requirements.md),
[CLI](../../../docs/requirements/functional-cli-framework-requirements.md), and
[Electron](../../../docs/requirements/functional-electron-communication-requirements.md)
requirements and [CLI protocol knowledge](../../../knowledge/concepts/cli-protocol.md).
Open questions include exact envelope fields and versions, lifecycle transition
rules, execution and cancellation semantics, and compatibility policies.
