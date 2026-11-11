---
type: Product
title: AdharaSutra product and scope
description: Purpose, users, and boundaries of the proposed framework.
status: draft
tags: [product, scope]
---

# Purpose

AdharaSutra is a proposed unified, reusable, architecture-driven, CLI-first Python
application framework. It aims to let developers and coding agents create, operate,
extend, verify, and migrate applications without repeatedly implementing foundational
infrastructure. Philosophy: **build business capabilities, not repeated infrastructure.**

# Problem

Multiple Python applications — especially Electron-integrated ones — each duplicate
conceptually identical infrastructure: CLI parsing and dispatch, Electron–Python
communication, HTTP clients, subprocess execution, SQLite, configuration, state and
jobs, progress/errors/cancellation, lifecycle, and testing — breeding inconsistency,
maintenance cost, and migration difficulty where infrastructure and business logic
intertwine.

# Core identity

An opinionated framework — the foundational runtime and architectural conventions
applications are built on, not a helper library. It aims to own bootstrap and
lifecycle; CLI communication and action routing; unified Electron–Python contracts;
state, jobs, HTTP/WebSocket/external-CLI/SQLite/filesystem integrations, configuration,
logging and errors, conventions, scaffolding, discovery, deterministic verification,
incremental migration, and testing. Applications own domain models, rules, workflows,
validation, state, and persistence; the framework must not couple to any domain.

# Architectural principles

- **5.1 Framework-first development** — applications build on AdharaSutra, which defines structure, lifecycle, extension points, and conventions.
- **5.2 Business logic independence** — business rules are developed, tested, and maintained within consuming applications.
- **5.3 Unified communication** — one consistent, versioned CLI protocol for every Electron app, regardless of the integration behind it.
- **5.4 Infrastructure abstraction** — standardize integrations without hiding technology capabilities; share configuration, lifecycle, error, and testing conventions.
- **5.5 Predictable architecture** — documented structure with enforceable module boundaries, understandable without reverse engineering.
- **5.6 Deterministic verification** — compliance is checked by deterministic rules; LLMs may assist, but mandatory requirements never depend on subjective LLM approval.
- **5.7 Incremental adoption** — existing applications adopt gradually, preserving behavior over unnecessary rewrites.
- **5.8 Extensibility without unnecessary complexity** — plugins, connectors, and architecture profiles, but no abstractions without demonstrated need.
- **5.9 Agent-friendly engineering** — structured, evidence-backed documentation portable across development tools, not tied to one agent or model provider.
- **5.10 Maintainability and compatibility** — public interfaces, protocols, architecture rules, and migration formats follow explicit versioning policies.

# CLI-first communication

Electron reaches Python through standardized process communication; the framework
handles routing, validation, serialization, events, errors, and process lifecycle.
Applications register actions at defined extension points; external dependencies go
through connectors (HTTP/WebSocket to ComfyUI, HTTP to LM Studio, external CLI to
audio.cpp, SQLite). The Electron-facing contract never changes with the integration — central to the framework's identity.

# Application development vision

New applications are generated with predefined architecture, communication,
configuration, testing, and connectors, needing only business-specific implementation.
Existing applications are analyzed — structure, execution model, dependencies, state,
integration boundaries — and given an actionable migration plan while functionality
stays operational; applications share conventions yet keep independent capabilities, dependencies, and release lifecycles.

# Discovery and verification vision

Architecture should be observable and verifiable, not merely documented: discover
existing architecture, map modules and entry points, inspect CLI/Electron patterns,
identify integrations, verify profile compliance, produce evidence-backed findings,
flag unsupported checks, recommend remediation, and track conformance. The same rules
guide creation, verification, and migration; passing means the checks actually performed passed, not general correctness.

# Migration vision

A core capability: existing applications converge toward the same standards as newly
generated ones. The workflow understands the implementation, baselines behavior,
compares against the target architecture, identifies gaps and risks, generates
actionable tasks, introduces infrastructure incrementally, preserves functionality
and data, verifies each stage, and removes obsolete infrastructure after validation — transparent, reviewable, reversible where feasible.

# Developer and coding-agent experience

Coding agents learn conventions from standardized documentation and framework
reports: structure, component responsibilities, integration points, violations,
source evidence, required changes, acceptance criteria, and verification procedures.
Agent-assisted analysis enhances deterministic tooling; the core framework must function without an LLM.

# Documentation-driven design

Design and documentation precede large-scale implementation: define the vision,
establish functional and non-functional requirements, design the architecture,
define contracts, evaluate tradeoffs, validate usage and migration scenarios, and
refine decisions into a stable baseline. Documentation must stay aligned with the actual implementation.

# Goals and non-goals

Goals: one reliable foundation shared across independent applications; new apps start
from established architecture; existing apps adopt incrementally without losing
working business logic; predictable structure for developers and coding agents.
Non-goals: owning application business rules or domains; requiring Electron, a local
HTTP server, or an LLM for the core runtime; complete rewrites; verification implying
complete correctness — reports state what was actually checked.

See [requirements](../docs/requirements/README.md).
