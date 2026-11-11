---
type: Concept
title: Connector framework
description: Integration boundaries and resource ownership for external systems.
status: draft
tags: [connectors, architecture]
---

Connectors provide reusable infrastructure for HTTP, WebSocket, external CLI,
SQLite and filesystem operations. Applications retain service-specific business
logic. A registry resolves connectors by stable identifier, detects duplicate
registrations and validates dependencies. Applications and optional packages
can register custom connectors and substitute test doubles.

Connectors receive validated configuration and follow initialization, readiness,
health and shutdown conventions. The framework maps errors into consistent
categories while retaining useful diagnostics. Unused integrations should not
force unrelated dependencies on an application.

HTTP operations support timeouts and policy-controlled retries that account for
idempotency. External processes use argument arrays, capture output and exit
status, and follow explicit timeout, cancellation and cleanup policies. A change
in external transport must not change the Electron-facing CLI contract.

The exact common interfaces, lifecycle transitions, optional dependency layout,
and connector-specific guarantees remain to be reconciled and approved. See the
[connector requirements](../../docs/requirements/functional-connector-framework-requirements.md),
[HTTP requirements](../../docs/requirements/functional-http-connector-requirements.md),
and [external CLI requirements](../../docs/requirements/functional-external-cli-connector-requirements.md).
