---
type: Concept
title: Architecture and boundaries
description: Proposed framework, application, and Electron boundaries.
status: draft
tags: [architecture, boundaries]
---

# Proposed boundaries

Applications depend on the framework's public interfaces and register their
own business behavior. The framework manages runtime and infrastructure without
depending directly on application-specific modules. Electron uses a versioned
CLI process protocol; connectors access external services and resources.

Architecture discovery, verification, scaffolding, and migration should share
consistent rules. Deterministic evidence is the basis for mandatory checks;
unsupported checks and uncertainty must remain visible.

Sources: [system architecture](../docs/raw/system-architecture.md),
[application architecture](../docs/raw/application-architecture.md),
[module architecture](../docs/raw/module-architecture.md), and
[architecture verification](../docs/raw/architecture-verification.md).
