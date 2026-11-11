---
type: Concept
title: Packaging and distribution
description: Proposed packaging, versioning, and release model for the framework, the Electron bridge, and consuming applications.
status: draft
tags: [packaging, distribution, releases, compatibility]
---

# Python distribution and optional capabilities

One modular Python distribution is proposed — name and import namespace `adharasutra` — on PyPI, holding core, CLI, connectors, state, jobs, events, observability and tooling modules. The monolith avoids many small releases, cross-package dependency cycles and premature public package boundaries while allowing clean internal modules and optional dependency groups; splits wait for dependency-weight, cadence, ownership, adoption or security justification. Metadata follows `pyproject.toml` from one authoritative version source. Applications use documented exports (proposed: `from adharasutra import Application`), not internals, which change without public guarantees. Proposed extras: `http`, `websocket`, `devtools`, `testing`, `all-runtime`, `all`. Minimal imports must not pull connector or tooling dependencies, and a missing extra yields a classified error with install guidance; SQLite and subprocess capabilities need no extra. Extras are installation metadata only — they never authorize a connector or register an executable. Dev tooling stays in-distribution with lazy imports behind the proposed `adhara` CLI (`new`, `inspect`, `verify`, `migrate`, `test`, `doctor`), separate from application entry points.

# Versioning and compatibility

Seven independent version dimensions are tracked: Python distribution, Electron bridge, CLI protocol, configuration schema, architecture profile, architecture model schema, migration plan schema. Public distributions follow semantic versioning; during `0.x` APIs may evolve faster but breaking changes stay documented. Bridge-to-runtime compatibility is negotiated through protocol versions and capabilities, never assumed from package numbers — Python `1.2.0` with bridge `1.3.0` may interoperate, and incompatible versions fail at handshake. Release docs publish an approved compatibility matrix (Python, OS, package, protocol, bridge, Electron/Node, connector dependencies, config schema, executable strategy) based on actual testing, not packaging metadata; unsupported combinations produce understandable errors. Deprecated APIs carry a replacement, version, planned removal and migration guidance. Upgrades evaluate API, protocol, configuration and dependency compatibility; rollback is data-aware — downgrading never undoes database schema changes or external side effects.

# Electron bridge package

The TypeScript bridge is a separate npm distribution, `@adharasutra/electron-bridge` (proposed, subject to namespace ownership), shipping compiled JavaScript and TypeScript declarations. It owns backend lifecycle, protocol serialization/parsing, request correlation, timeouts, event subscription, error translation, handshake and crash handling — never business actions, domain models, renderer UI, application authentication rules or application-specific executable installation. Electron stays a peer dependency of the consuming application. Public exports are explicit, declarations match the compiled API, and release validation inspects the archive to exclude development files and credentials. Python and TypeScript share a monorepo for coordinated contract changes, shared fixtures and centralized CI, without sharing a version number or release triggers.

# Desktop backend strategies and runtime discovery

Electron apps launch their Python backend through one of three proposed strategies:

- Bundled Python environment — predictable interpreter and dependencies; larger package and platform-specific assembly. Preferred for end-user desktop applications.
- Frozen executable — simple launch interface; freezer compatibility and native dependency handling must be validated (PyInstaller, Nuitka or another; none approved).
- External Python installation — smaller package; environment variability and setup burden. Primarily development or managed deployment.

None requires a localhost HTTP server; the bridge uses subprocess communication. A bundled backend carries a platform-specific interpreter, application package, framework, dependencies, native extensions and approved resources, built reproducibly and treated as installation content — mutable databases, logs and generated artifacts belong in writable directories. A frozen backend must include the optional modules the application requires and support bootstrap, imports, configuration, stdout/stderr protocol, connectors, state, jobs, external processes and shutdown, without source-tree path assumptions. A packaged app locates its backend via a versioned `runtime-manifest.json` (backend strategy, OS, architecture, executable path, arguments, protocol compatibility, integrity metadata); executables must not be assumed executable inside ASAR. The bridge verifies existence and permissions before launch, reports actionable startup errors instead of launching an unrelated executable, and the renderer must not replace trusted manifest paths or inject unrestricted environment configuration.

# External assets and platform support

External programs and large models (audio tools, AI inference engines, media encoders) are application-owned, not framework dependencies: each packaged tool carries name and version, origin, path, platform compatibility, integrity metadata, license review and an invocation contract. Large AI models never enter the core wheel; applications distribute them separately or via explicit installs, startup never downloads them silently, and the framework neither bundles GPU drivers nor redistributes third-party tools without license review. Windows, Linux and macOS are the proposed targets with per-platform validation (Windows: path spaces, DLL loading, termination; Linux: shared libraries, executable permissions, signals; macOS: bundle structure, signing, notarization); artifacts declare architectures (x86-64, ARM64) validated on native platforms.

# Release checks and artifact validation

The proposed pipeline runs metadata validation, unit and contract tests, architecture verification, integration tests, both builds, package-content inspection, installation of the built artifacts, smoke tests, compatibility evaluation, security and provenance checks, approval, publication, and post-publication verification. Built, tested, approved, published and installed are distinct states — a successful build never authorizes publication, and a required unexecuted test leaves its gate incomplete or blocked, never passed. Publishing uses trusted publishing (short-lived, narrowly scoped OIDC credentials) from protected environments on PyPI and npm; published versions are immutable. Post-publish verification compares registry version, filenames, hashes, metadata and clean-install behavior against approved build evidence. Builds record source revision, tool versions, dependency constraints, platform and architecture; artifacts get recorded SHA-256 hashes, optional provenance, signing, SBOM and vulnerability scanning — a matching checksum proves bytes match a digest, not that the source was trustworthy.

# Alternatives considered

Adopted: one modular Python distribution, capability extras, a monorepo with independent releases, a separate versioned npm bridge, protocol-negotiated rather than lockstep compatibility, bundled-backend preference, a versioned runtime manifest, trusted publishing. Rejected or deferred: per-connector PyPI distributions, a package per internal module, mandatory embedded Python, framework-distributed interpreters, an application marketplace, a framework-managed auto-updater, automatic model or tool redistribution, a private registry, multiple maintenance branches, bit-for-bit installer reproducibility without extra controls.

# Open questions

- PKG-OQ-001 — Should the public package name be `adharasutra`, `adhara-sutra`, or another form?
- PKG-OQ-002 — Which Python build backend: Hatchling, setuptools, or another?
- PKG-OQ-003 — Should development tooling stay in the main package or become a separate distribution?
- PKG-OQ-004 — Should extras map to each connector, broad categories, or both?
- PKG-OQ-005 — Which Python versions beyond 3.12 should be supported?
- PKG-OQ-006 — Should the Electron bridge use an organization-owned npm scope?
- PKG-OQ-007 — Should the bridge publish ESM, CommonJS, or dual-format outputs?
- PKG-OQ-008 — Should Electron be a peer dependency of the bridge?
- PKG-OQ-009 — Should protocol types be generated automatically from JSON Schema?
- PKG-OQ-010 — Should the Python framework and Electron bridge share one version number?
- PKG-OQ-011 — Should generated desktop applications default to bundled Python or a frozen executable?
- PKG-OQ-012 — Should AdharaSutra itself distribute Python interpreters?
- PKG-OQ-013 — Should generated Electron applications use electron-builder or Electron Forge?
- PKG-OQ-014 — How should architecture-specific native modules and Python wheels be packaged?
- PKG-OQ-015 — Should AdharaSutra define standard distribution conventions for audio.cpp and similar tools?
- PKG-OQ-016 — Should model downloads be managed by the framework?
- PKG-OQ-017 — Should versions be derived automatically from Git tags?
- PKG-OQ-018 — Should every version have a maintenance branch?
- PKG-OQ-019 — Should package signing be mandatory?
- PKG-OQ-020 — Should every release include an SBOM?
- PKG-OQ-021 — Should CI reinstall published packages after release?
- PKG-OQ-022 — When should AdharaSutra commit to a 1.0 public API?
- PKG-OQ-023 — Should alpha, beta, and stable release channels exist?
- PKG-OQ-024 — Which license should the project publish under?
- PKG-OQ-025 — Should AdharaSutra manage Electron auto-updates?

See [packaging and distribution requirements](../../docs/requirements/functional-packaging-and-distribution-requirements.md),
[operational and packaging requirements](../../docs/requirements/non-functional-operational-and-packaging-requirements.md),
and [portability requirements](../../docs/requirements/non-functional-portability-requirements.md).
