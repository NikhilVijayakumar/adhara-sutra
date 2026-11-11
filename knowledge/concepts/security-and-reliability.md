---
type: Concept
title: Security and reliability
description: Proposed trust boundaries, hardening, failure taxonomy, and recovery policies across the AdharaSutra runtime.
status: draft
tags: [security, reliability, trust-boundaries]
---

# Central principle

Every privileged operation would carry an explicit trust boundary, an authorized path, and a defined
failure policy; every managed resource an owner, bounded policy, and verifiable cleanup. The framework
owns technical controls, applications business authorization, deployment OS permissions.

# Trust boundaries and threat model

Ten boundaries: renderer→preload, preload→Electron main, main→Python runtime, protocol→actions, use
cases→connectors, runtime→executables/filesystem/SQLite/HTTP, tooling→repositories. Authorization
never propagates downstream; the same-user Python child is structure, not isolation. Threats —
renderer input, untrusted responses, subprocess output — map to allowlists, validation, size limits.

# Electron hardening

Context isolation on, renderer Node integration off, sandbox where compatible, minimal preload
exports, IPC allowlists, controlled navigation, CSP. Electron main owns Python process creation
and backend lifecycle; renderers never spawn Python, run shell commands, or touch credentials.
IPC validates sender, origin, operation, schema, permissions; dynamic channels prohibited.

# Input and protocol validation

External inputs are validated at the boundary before privileged operations (defense in depth);
untrusted input never controls executable paths, shell commands, or module imports. CLI messages
are checked for UTF-8, JSON, size (proposed 1 MiB), version, kind, fields, and payload schema;
stdout stays protocol-only; request IDs are correlation, not identity; no `eval`, `exec`, or imports.

# Subprocess execution and termination

Shell interpretation is disabled by default; the Process Connector passes structured argument
arrays, with executables from registered identities or trusted configuration — never renderer
input. Subprocesses inherit launcher privileges; OS sandboxing is optional deployment capability.
Every process has an owner; termination runs graceful → grace → escalation → confirmed state.

# Filesystem, artifacts, network, and secrets

Applications declare filesystem roots; paths cannot escape via traversal or symlinks, and critical
writes use temporary-file-and-replace. Artifacts use opaque managed identifiers — never client
paths or CLI-JSON embedding. HTTPS keeps TLS verification on, SSRF covers redirects and DNS,
localhost is not trust. Secrets are references, not values; redaction precedes external sinks.

# Failure taxonomy, retry, and idempotency

Failures are recoverable (temporary HTTP unavailability, invalid input, one job failing) or
potentially fatal (corrupted protocol state, failed critical initialization, unavailable
persistence). Outcomes are classified and isolated to the smallest safe domain, distinguishing
success, failure, interruption, cancellation, timeout, unknown; retries are idempotency-aware.

# Readiness, degradation, recovery, and cleanup

Readiness is reported only after mandatory startup conditions, including protocol handshake;
optional-component failure may degrade rather than fail startup; partial initialization cleans
up preserving the primary error. Crash recovery reconciles interrupted jobs and validates
artifacts before readiness; shutdown is bounded, idempotent, never promising clean forced kills.

# Alternatives considered

Proposed: secure defaults, restricted renderer privileges, bridge allowlists plus application
domain authorization, registered executables, secret references, idempotency-aware retries,
read-only tooling. Deferred: OS sandboxes, encryption at rest, automatic retries, audit logs.

# Open questions

- SR-OQ-001 — Should every AdharaSutra application use the same default security profile?
- SR-OQ-002 — Should renderer sandboxing be mandatory?
- SR-OQ-003 — Should the bridge implement authorization or delegate it entirely to the application?
- SR-OQ-004 — Should AdharaSutra provide a standard action-authorization interface?
- SR-OQ-005 — Should every external executable require registration?
- SR-OQ-006 — Should AdharaSutra provide an operating-system sandbox abstraction?
- SR-OQ-007 — Should all application filesystem access use AdharaSutra wrappers?
- SR-OQ-008 — Should artifact access use opaque IDs, signed references, or both?
- SR-OQ-009 — Should persistent state and SQLite databases be encrypted automatically?
- SR-OQ-010 — Which secret providers should be implemented initially?
- SR-OQ-011 — Should the HTTP Connector enforce destination allowlists?
- SR-OQ-012 — Should retries be enabled automatically for all connectors?
- SR-OQ-013 — Should circuit breakers be part of the initial connector framework?
- SR-OQ-014 — What initial queue, process, and memory limits should apply?
- SR-OQ-015 — Should AdharaSutra provide tamper-evident audit logs?
- SR-OQ-016 — Should the runtime automatically restart failed jobs?
- SR-OQ-017 — Should the framework reattach to processes surviving a Python crash?
- SR-OQ-018 — Should durable workers be mandatory for Electron applications?
- SR-OQ-019 — Which architecture security rules should be nonwaivable?
- SR-OQ-020 — Should dependency vulnerability scanning be a release requirement?
- SR-OQ-021 — Should downloaded or generated artifacts receive automatic checksums?
- SR-OQ-022 — When should threat models be reviewed?
- SR-OQ-023 — Should localhost HTTP services be treated as trusted?
- SR-OQ-024 — Should every security rule require executable tests?
- SR-OQ-025 — Should the final architecture baseline include a formal threat register?

See [security-related functional requirements](../../docs/requirements/functional-security-related-functional-requirements.md),
[security requirements](../../docs/requirements/non-functional-security-requirements.md), and
[reliability requirements](../../docs/requirements/non-functional-reliability-requirements.md).
