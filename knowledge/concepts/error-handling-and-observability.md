---
type: Concept
title: Error handling and observability
description: Proposed error taxonomy, propagation boundaries, structured logging, correlation, redaction, and diagnostics model.
status: draft
tags: [errors, observability, logging, diagnostics]
---

# Error taxonomy and codes

AdharaSutra proposes one framework-owned technical error model plus application-owned domain errors. A
category names the kind of failure (protocol, validation, configuration, lifecycle, runtime, action,
connector, process, persistence, state, job, cancellation, timeout, security, resource, internal);
a code names a specific failure contract, formatted `CATEGORY_SPECIFIC_CONDITION`
(`PROTOCOL_UNSUPPORTED_VERSION`, `CONNECTOR_UNAVAILABLE`, `STATE_VERSION_CONFLICT`,
`JOB_QUEUE_FULL`). Codes are stable within the compatibility contract and never silently redefined;
a central catalog records code, category, description, typical origin, retryability guidance,
exposure policy, protocol status and compatibility notes. Applications define domain errors
(`VOICE_PROFILE_NOT_FOUND`) that reuse the shared envelope when exposed through the protocol.

# Error context and outcome classification

The proposed error fields are `code`, `category`, `message` (safe, human-readable), `retryable`
(true/false/null — unknown), `details` (approved structured metadata), `correlation_id`, `cause`
(internal original-exception reference) and `severity`. Python exception chaining preserves causes
for controlled internal diagnostics only — never automatically serialized outward. Once classified,
an error's code and category stay immutable as it propagates; higher layers may map it into a
distinct domain or protocol error only under an explicit boundary contract. `retryable: true` is
guidance, not a promise that automatic retry is desirable; the framework may implement technical
retries, but the application owns domain-level retry eligibility and idempotency. Outcomes must be
distinguished: confirmed success, confirmed failure, cancellation requested, confirmed cancellation,
timeout, interrupted execution, and unknown — uncertainty is preserved, never converted to failure
merely because a response was lost.

# Propagation across boundaries

Errors propagate through defined boundaries until a component handles (resolves or applies a
documented recovery policy) or translates (re-represents for another boundary) them:
external dependency → low-level exception → connector mapping → application adapter → use case →
action execution boundary → framework normalization → CLI error envelope → Electron bridge → UI.
Not every error crosses every layer (invalid requests fail at protocol validation). Error ownership
sits with each layer: domain owns business rules, connectors own technical transport failures, job
manager owns execution lifecycle, lifecycle manager owns startup/shutdown, CLI runtime owns the
standard error response, the bridge owns typed transport errors, the renderer owns presentation.
Boundary guarantees: action failures must not terminate the persistent runtime; job failures update
job state and publish terminal events, never success; a failed write is never reported as committed;
security failures are reported without leaking validation details; cleanup failures never erase the
original failure.

# Expected, unexpected, and fatal errors

Expected errors (invalid payload, missing config, unavailable service, busy database) become
classified errors. Unexpected exceptions at a request boundary become a safe internal-error
response when runtime integrity is intact, with the full exception logged internally — never
silently converted to success or default values. Fatal failures (transport corruption, critical
lifecycle corruption, indispensable infrastructure failure, unsafe-to-continue state) may trigger
controlled shutdown. Severity (debug, info, warning, error, critical) is diagnostic impact,
separate from category: expected user validation is not necessarily ERROR-logged, ordinary
cancellations are not critical, and recovery is only claimed after post-recovery checks pass.

# Protocol and Electron serialization

The CLI error envelope carries `code`, `message`, `retryable` and optional `details`, consistent
with the CLI protocol concept. The proposed serializer validates the code, produces a safe message,
includes only approved details, preserves request correlation, removes sensitive internal context,
never serializes arbitrary exception objects, and on its own failure emits a minimal safe
internal-error response rather than recursing. Every accepted request gets one attempted terminal
response; process crashes may prevent delivery. The Electron bridge proposes typed errors for
remote application errors, protocol errors, transport errors, process startup/termination errors,
client timeouts, cancellation outcomes and compatibility errors. A broken pipe or unexpected Python
exit is a transport error, distinct from business failure — the bridge must preserve uncertainty
about side-effecting operations. UI presentation (inline message, retry prompt, fatal screen) is the
consuming application's decision.

# Structured logging model

Logging is centralized in the framework on Python's standard `logging`, with structured JSON
formatting via small adapters — no heavyweight observability library required. Records carry
`timestamp` (ISO 8601 UTC proposed), `level`, `logger`, `message`, `application`, `component`, plus
optional correlation fields. Proposed level policy: INFO in development (DEBUG opt-in), INFO or
WARNING in production, sensitive payloads off by default. Destinations: stderr (default
diagnostic channel), rotating local log files, and test capture handlers, with optional syslog and
telemetry sinks; multiple sinks may be configured. When the CLI protocol is active, stdout carries
protocol messages only — application and framework logging must never write there. Logging is
bounded: configurable async queue limits, a documented backpressure policy that preserves critical
records and may drop or aggregate repetitive low-priority ones, retention by size/count/age/budget,
dropped-record counters, and flush-on-graceful-shutdown; buffered logs may not survive abrupt
termination. Logger namespaces identify ownership (`adharasutra.connectors.http`,
`application.vani.audio`); applications acquire framework-configured loggers and select level,
sinks, format and retention within supported policy.

# Request, job, and process correlation

Correlation follows an execution from Electron request through CLI request, application action,
connector operation or job, execution attempt, process execution ID, to the external dependency.
Identifiers — request, session, job, attempt, process execution, connector, correlation — follow
documented uniqueness rules and are never authentication credentials. The framework propagates
them through action execution, async tasks, job submission, connector calls, process execution,
error handling and logging; `contextvars` is the candidate mechanism, with explicit handling for
context copied into background tasks, threads and subprocesses (no automatic propagation) and for
external correlation headers only where the remote contract permits.

# Sensitive-data redaction

Redaction targets access tokens, passwords, API keys, authentication headers, private
credentials, confidential user content, sensitive environment variables and secret configuration
fields. Proposed mechanisms: schema-aware sensitive fields, explicit redaction markers, known
sensitive-header filtering, structured record filtering, safe exception formatting and sanitized
diagnostic exports — applied before records reach external sinks. Raw application payloads are not
logged by default, and exception messages are not assumed safe for disclosure. Pattern-based
redaction cannot guarantee completeness of arbitrary text; the preferred strategy is never
collecting unnecessary sensitive content in the first place.

# Health, diagnostics, and developer commands

Health (operational condition) stays separate from readiness (ability to accept work). Proposed
health statuses: healthy, degraded, unavailable, unknown, not checked. Runtime readiness follows
required configuration, lifecycle and protocol initialization; a connector can be initialized while
its remote dependency is unavailable; applications may expose capability-level readiness. Checks
are on-demand by default (periodic optional), must not run expensive operations or cause side
effects, distinguish check time from report time, and are exposed via the reserved `system.health`
action. Diagnostics come in summary, detailed, and redacted support-export modes; reports must
distinguish checked from unchecked information, and runtime evidence must never be presented as
architecture-verification evidence. Lightweight metrics (request/error/duration counters, job
counts, connector errors, dropped log records) are exposed through diagnostics with bounded label
cardinality; metrics and tracing are optional, with OpenTelemetry an optional adapter, never a
mandatory dependency. Proposed developer commands: `adhara doctor` (configuration and environment),
`adhara inspect` (implementation structure), `adhara verify` (architecture conformance) — sharing
evidence without conflating responsibilities. Runtime log-level adjustment, if supported, goes
through an authorized diagnostic action only.

# Alternatives considered

Proposed directions: framework-owned technical taxonomy with application-owned domain errors;
stable versioned code catalog; tri-state retryability and explicit unknown outcomes; cause
preservation internal-only; safe structured public envelopes; standard `logging` with JSON adapters;
stderr as default diagnostic channel with protocol-only stdout; optional rotating files; context
correlation hierarchy; schema-aware redaction; health separate from readiness; optional bounded
metrics and tracing; deterministic verification rules (registered codes, no diagnostics on stdout,
no raw exceptions in public serialization). Deferred: distributed monitoring backends, cloud
telemetry, centralized log servers, automatic log upload, LLM-based root-cause analysis, mandatory
OpenTelemetry, recording every function call, and automatic retry/recovery of every operation.
Migration from existing applications is adapter-first and incremental: compatibility adapters for
legacy exception classes, routing existing loggers into framework configuration, moving stdout
writers off the protocol stream, then removing duplicated infrastructure.

# Open questions

- EO-OQ-001 — One base exception with registered codes, or multiple typed subclasses?
- EO-OQ-002 — Register error codes dynamically, or define them through a versioned catalog?
- EO-OQ-003 — Should applications register error mappers explicitly?
- EO-OQ-004 — Python standard logging, or a third-party structured logging system?
- EO-OQ-005 — Should all environments use JSON logs?
- EO-OQ-006 — Should correlation identifiers be automatically injected into logs?
- EO-OQ-007 — When should stack traces appear in diagnostic output?
- EO-OQ-008 — Should applications add arbitrary detail fields to public errors?
- EO-OQ-009 — What default log retention should persistent applications use?
- EO-OQ-010 — Should OpenTelemetry support be included in the first release?
- EO-OQ-011 — Should the framework periodically check connector health?
- EO-OQ-012 — Should AdharaSutra provide a built-in support bundle generator?
- EO-OQ-013 — Should a failed logging sink ever trigger application shutdown?
- EO-OQ-014 — Should Electron dynamically enable detailed backend logging?
- EO-OQ-015 — Should the framework generate localized user-facing error messages?

See [error handling requirements](../../docs/requirements/functional-error-handling-requirements.md),
[logging and diagnostics requirements](../../docs/requirements/functional-logging-and-diagnostics-requirements.md),
and [observability requirements](../../docs/requirements/non-functional-observability-requirements.md).
