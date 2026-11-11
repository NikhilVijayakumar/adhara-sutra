# AdharaSutra — Framework Vision

**Project:** AdharaSutra (आधारसूत्र)  
**Category:** CLI-First Python Application Framework  
**Document:** `docs/design/vision.md`  
**Status:** Draft — Pending Architecture Review  
**Version:** 0.1.0

---

## 1. Vision Statement

**AdharaSutra aims to become a unified, reusable, architecture-driven Python application framework that enables developers and coding agents to create, operate, extend, verify, and migrate applications without repeatedly implementing foundational infrastructure.**

The framework establishes a consistent application foundation that manages runtime execution, CLI communication, state, external integrations, configuration, lifecycle, and architectural standards.

Applications built on AdharaSutra focus primarily on implementing their business capabilities while inheriting the framework's standardized infrastructure and development conventions.

Its central philosophy is:

**Build business capabilities, not repeated infrastructure.**

## 2. The Problem We Want to Solve

Developing multiple Python applications, especially those integrated with Electron and local tools, introduces recurring engineering problems.

Each application often independently implements:

- CLI command parsing and action dispatch.
- Communication between Electron and Python.
- HTTP clients for external services.
- Subprocess execution for external command-line tools.
- SQLite connections and persistence infrastructure.
- Application configuration and environment management.
- State and background job management.
- Progress reporting, errors, cancellation, and logging.
- Application startup and shutdown.
- Project architecture and directory conventions.
- Testing and verification infrastructure.

Although applications have different business purposes, much of this infrastructure is conceptually identical.

Duplicating it creates inconsistencies, unnecessary maintenance, divergent communication protocols, and additional work when adopting new architectural standards.

Existing applications also become difficult to migrate because their infrastructure and business logic may be intertwined.

AdharaSutra exists to solve these problems at the framework level.

## 3. Our Desired Future

We envision an ecosystem where multiple independent applications share the same reliable technical foundation.

A new application should begin with an established architecture rather than an empty project requiring repeated technical decisions.

An existing application should be able to adopt the framework incrementally without losing its working business logic.

A developer or coding agent should be able to enter an AdharaSutra application and quickly understand:

- How it is structured.
- How it starts and executes.
- How commands reach business logic.
- How Electron communicates with Python.
- How it connects to external systems.
- How its state and jobs are managed.
- Which architectural standards apply.
- Whether its implementation follows those standards.
- What changes are required to bring it into compliance.

The framework should make these behaviors predictable across applications.

## 4. Core Framework Identity

AdharaSutra is an **opinionated, CLI-first Python application framework**.

It is not merely a collection of helper functions or a CLI argument-parsing library.

It provides the foundational application runtime and architectural conventions upon which consuming applications are developed.

The framework owns common technical responsibilities.

Consuming applications own their business logic.

### Framework responsibilities

AdharaSutra aims to provide:

1. Application bootstrap and runtime lifecycle.
2. Standard CLI communication and action routing.
3. Unified Electron-to-Python communication contracts.
4. State management infrastructure.
5. Background job and process management.
6. HTTP, WebSocket, external CLI, SQLite, and filesystem integrations.
7. Configuration and dependency management.
8. Logging, error handling, and observability.
9. Standard project architecture and directory conventions.
10. Application scaffolding and reusable templates.
11. Architecture discovery and implementation reporting.
12. Deterministic architecture verification.
13. Incremental migration of existing applications.
14. Testing, diagnostics, and compatibility facilities.

### Application responsibilities

Each consuming application provides:

- Domain models and business rules.
- Application-specific use cases and actions.
- Domain workflows.
- Business validation.
- Application-specific state definitions.
- Domain persistence operations.
- External service-specific behavior where necessary.

The framework must not become coupled to any individual application's domain.

## 5. Our Architectural Principles

### 5.1 Framework-first development

Applications should be built upon AdharaSutra rather than independently implementing foundational infrastructure.

The framework defines the application structure, runtime lifecycle, extension points, and infrastructure conventions.

### 5.2 Business logic independence

AdharaSutra must remain independent of application-specific business rules.

Business logic should be developed, tested, and maintained within consuming applications.

### 5.3 Unified communication

All Electron applications should communicate with their Python backends using one consistent, versioned CLI protocol.

The communication mechanism must not change based on whether a Python action uses HTTP, a local executable, or a database.

### 5.4 Infrastructure abstraction

The framework should standardize technical integration mechanisms without hiding important capabilities of individual technologies.

HTTP requests, external CLI execution, and database transactions may require different interfaces, but they should share consistent configuration, lifecycle, error-handling, and testing conventions.

### 5.5 Predictable architecture

Applications should follow a documented architectural structure with enforceable module boundaries and dependency rules.

Architecture should be understandable to developers and coding agents without requiring extensive reverse engineering.

### 5.6 Deterministic verification

Architecture compliance should be checked through deterministic rules and tests wherever feasible.

LLMs may assist with interpretation, refactoring, and migration planning, but mandatory machine-verifiable requirements should not depend on subjective LLM approval.

### 5.7 Incremental adoption

Existing applications must be able to adopt AdharaSutra gradually.

Migration should favor preservation of existing behavior over unnecessary rewrites.

### 5.8 Extensibility without unnecessary complexity

The framework should support plugins, connectors, and configurable architecture profiles.

However, extensibility must not introduce excessive abstractions, mandatory dependencies, or complexity without demonstrated need.

### 5.9 Agent-friendly engineering

The framework should produce structured, evidence-backed documentation and reports that coding agents can use consistently.

Architectural understanding must be portable across development tools rather than tied to a particular agent or model provider.

### 5.10 Maintainability and compatibility

Framework changes should consider their effects on existing applications.

Public interfaces, communication protocols, architecture rules, and migration formats should follow explicit compatibility and versioning policies.

## 6. CLI-First Application Communication

AdharaSutra adopts the CLI as the primary interface between Electron and Python applications.

Electron communicates with the Python runtime through standardized process communication.

The framework handles command routing, request validation, response serialization, events, errors, and process lifecycle.

Applications register business actions through defined framework extension points.

External dependencies are accessed through appropriate infrastructure connectors.

For example:

```text
Electron
    |
    v
AdharaSutra CLI Protocol
    |
    v
Framework Action Router
    |
    v
Application Business Action
    |
    v
Framework-Managed Infrastructure
    |
    +-- HTTP / WebSocket --> ComfyUI
    |
    +-- HTTP ------------> LM Studio
    |
    +-- External CLI ----> audio.cpp
    |
    +-- SQLite ----------> Local Database
```

The Electron-facing communication contract remains consistent regardless of the external integration used.

This separation is central to the framework's identity.

## 7. Application Development Vision

AdharaSutra should support both new and existing applications.

### 7.1 New application development

A developer should be able to generate a new Python application with predefined architecture, standard communication, configuration, testing facilities, and available infrastructure connectors.

The generated application should require primarily business-specific implementations.

### 7.2 Existing application adoption

An existing Python application should be analyzed to understand its current structure, execution model, dependencies, state, and integration boundaries.

The framework should identify architectural differences and generate an actionable migration plan.

Existing functionality should remain operational throughout incremental adoption wherever feasible.

### 7.3 Consistent application ecosystem

Applications should share the same framework conventions while retaining independent business capabilities, dependencies, and release lifecycles.

Updating shared infrastructure should not require rebuilding that infrastructure separately within each application.

## 8. Architecture Discovery and Verification Vision

Architecture should be observable and verifiable rather than merely documented.

AdharaSutra should provide the capability to:

- Discover an application's existing architecture.
- Identify module relationships and entry points.
- Inspect CLI and Electron communication patterns.
- Identify external integrations and infrastructure ownership.
- Verify compliance with architecture profiles.
- Produce clear findings with source evidence.
- Identify unsupported or uncertain checks.
- Recommend remediation approaches.
- Track conformance improvements over time.
- Prevent newly introduced architecture violations.

The same architecture rules should guide project creation, verification, and migration.

A passing verification result must represent the checks actually performed, not a general guarantee of software correctness.

## 9. Migration Vision

Migration is a core framework capability.

AdharaSutra should not assume every consuming application is new.

Its migration approach should enable existing applications to converge toward the same architectural standards as newly generated applications.

A migration workflow should:

1. Understand the current implementation.
2. Preserve a baseline of existing behavior.
3. Compare the implementation with the target architecture.
4. Identify gaps and compatibility risks.
5. Generate actionable migration tasks.
6. Introduce framework infrastructure incrementally.
7. Preserve business functionality and data.
8. Verify each migration stage.
9. Remove obsolete infrastructure after successful validation.

Migration must be transparent, reviewable, and reversible where technically feasible.

## 10. Developer and Coding-Agent Experience

AdharaSutra should provide a consistent experience for developers and AI coding agents.

A coding agent should be able to understand an application's architectural conventions through standardized documentation and framework-generated reports.

The reports should explain:

- Current implementation structure.
- Component responsibilities.
- Framework integration points.
- Architectural violations.
- Relevant source files and evidence.
- Required changes.
- Acceptance criteria.
- Verification procedures.

The framework should support coding-agent-assisted development without requiring an LLM to operate its core functionality.

Agent-assisted analysis is an enhancement to deterministic tooling, not a replacement.

## 11. Documentation-Driven Design

AdharaSutra should be designed and documented before large-scale implementation.

The initial engineering process should focus on:

1. Defining the framework vision.
2. Establishing functional and non-functional requirements.
3. Designing the application and module architecture.
4. Defining communication and infrastructure contracts.
5. Evaluating alternatives and architectural tradeoffs.
6. Validating representative usage and migration scenarios.
7. Refining unresolved decisions.
8. Approving a stable architecture baseline.

Formal specification systems, knowledge-management formats, and implementation workflows may be adopted after the architectural baseline is established.

Documentation must remain aligned with the actual implementation as