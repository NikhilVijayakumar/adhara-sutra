---
type: Concept
title: Security, reliability, and observability
description: Trust boundaries, failure handling, and operational evidence.
status: draft
tags: [security, reliability, observability]
---

Protocol input, Electron IPC, filesystem access, subprocess execution and
external networks cross trust boundaries. The framework validates inputs, limits
exposed operations, avoids shell interpretation for ordinary process execution,
protects credentials, and redacts sensitive diagnostics. Electron's main process
owns Python process management; a restricted preload exposes approved operations.
Subprocess management alone must not be represented as sandboxing.

Managed resources have explicit owners, limits, cleanup and recovery policies.
Timeout, cancellation and an unknown remote outcome are distinct from confirmed
success or failure. Retry policy considers idempotency. Health is separate from
readiness. Protocol stdout remains separate from stderr diagnostics. Correlation
across requests, jobs and processes supports diagnosis; advanced telemetry is
optional and must not require a cloud service.

See [security requirements](../../docs/requirements/non-functional-security-requirements.md),
[reliability requirements](../../docs/requirements/non-functional-reliability-requirements.md),
and [observability requirements](../../docs/requirements/non-functional-observability-requirements.md).
