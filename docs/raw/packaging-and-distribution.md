# AdharaSutra — Packaging and Distribution Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/packaging-and-distribution.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Build, Packaging, Release, and Distribution Architecture  
**Architecture Style:** Modular Monolith, Optional Capabilities, Reproducible Builds, Independently Versioned Distribution Artifacts  
**Primary Language:** Python 3.12+  
**Additional Language:** TypeScript  
**Target Platforms:** Windows, Linux, macOS  
**Preferred Package Registries:** PyPI and npm — Proposed  
**License:** To be established through an explicit repository and distribution decision

**Related Documents:**

- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`
- `docs/design/electron-integration.md`
- `docs/design/connector-framework.md`
- `docs/design/state-management.md`
- `docs/design/job-and-process-management.md`
- `docs/design/configuration-and-lifecycle.md`
- `docs/design/error-handling-and-observability.md`
- `docs/design/project-scaffolding.md`
- `docs/design/architecture-discovery.md`
- `docs/design/architecture-verification.md`
- `docs/design/migration-framework.md`
- `docs/design/testing-strategy.md`
- `docs/design/security-and-reliability.md`

---

# 1. Purpose

This document defines how AdharaSutra and its integration components are packaged and distributed.

AdharaSutra is designed to support several independent applications, including standalone Python CLIs, Electron desktop software, local processing applications, and applications that integrate third-party tools.

These applications should reuse common infrastructure without being forced to install or deploy unrelated components.

The distribution architecture must therefore address five distinct concerns:

1. Packaging the Python framework.
2. Providing optional runtime capabilities.
3. Distributing development and architecture tooling.
4. Packaging the separate TypeScript Electron bridge.
5. Packaging consuming applications and their Python runtimes.

## 1.1 Central Principle

**One framework, multiple independently selectable capabilities, predictable package contracts, and verified distribution artifacts.**

Packaging must reflect architectural boundaries without creating unnecessary package complexity.

## 1.2 Objectives

The architecture shall:

1. Define the initial Python distribution model.
2. Separate mandatory and optional dependencies.
3. Support Python 3.12 and approved later versions.
4. Provide stable Python import and public API contracts.
5. Provide a framework developer CLI.
6. Prevent unnecessary developer dependencies in production applications.
7. Define a separate Electron bridge package.
8. Establish cross-package compatibility rules.
9. Support standalone Python installations.
10. Support Electron applications with bundled Python.
11. Support supported frozen-backend executables.
12. Establish Windows, Linux, and macOS packaging requirements.
13. Define package metadata and versioning.
14. Support local development and editable installations.
15. Establish artifact build and validation pipelines.
16. Support secure automated publishing.
17. Provide release provenance and integrity information.
18. Define installation and upgrade behavior.
19. Support rollback planning.
20. Keep application-specific dependencies and large assets outside unnecessary framework distributions.
21. Produce machine-readable release evidence.
22. Define compatibility and deprecation policies.
23. Support deterministic CI and coding-agent workflows.
24. Establish acceptance criteria for package readiness.

## 1.3 Non-Goals

The initial packaging system does not require:

- A separate PyPI distribution for every connector.
- A Python package for every internal module.
- A centralized application marketplace.
- An AdharaSutra-managed desktop auto-updater.
- A mandatory embedded Python runtime for every application.
- Bundling GPU drivers.
- Automatically redistributing third-party AI models.
- Automatically redistributing external tools without license review.
- Supporting every package manager equally.
- Maintaining a private package registry.
- Maintaining multiple independent release branches from the first version.
- Guaranteeing bit-for-bit reproducibility of every platform installer without additional platform-specific controls.

---

# 2. Architectural Principles

## PKG-001 — One Initial Python Distribution

The initial implementation should use one modular Python distribution rather than many independently published core packages.

## PKG-002 — Optional Dependency Isolation

Applications shall not be required to install unused optional infrastructure dependencies.

## PKG-003 — Stable Public Imports

Consuming applications shall depend on documented public APIs rather than internal module paths.

## PKG-004 — Development Tooling Isolation

Scaffolding, discovery, verification, migration, and test utilities shall not be mandatory imports during ordinary application execution.

## PKG-005 — Independent Electron Bridge

The TypeScript Electron bridge shall be distributed as a separate npm package.

## PKG-006 — Protocol-Based Compatibility

Electron bridge compatibility with Python runtimes shall be established using supported protocol versions and capabilities, not by assuming package versions are identical.

## PKG-007 — Application-Owned Packaging

Consuming applications own their own distribution, external tools, data, and deployment requirements.

## PKG-008 — Verified Artifacts

Release claims shall be based on built and tested artifacts, not merely source-tree test results.

## PKG-009 — Reproducible Build Inputs

Builds should record their source revision, dependency constraints, toolchain, target platform, and outputs.

## PKG-010 — Secure Publishing

Package publication should use short-lived, scoped authentication mechanisms where supported.

## PKG-011 — Explicit Versioning

Public API and protocol compatibility must follow documented versioning policies.

## PKG-012 — No Hidden Runtime Downloads

Installed applications shall not download Python runtimes, AI models, or executables unexpectedly as part of ordinary startup.

## PKG-013 — Cross-Platform Validation

Platform-specific artifacts shall be tested on the platforms they claim to support.

## PKG-014 — Controlled Upgrades

Upgrades shall identify compatibility constraints and applicable migration requirements.

## PKG-015 — Distribution Transparency

Installation, build, publication, and verification processes shall produce useful diagnostic and provenance information.

---

# 3. Distribution Architecture Overview

```text
                       AdharaSutra Source
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
    Python Framework Package             Electron Bridge
              │                                 │
              ▼                                 ▼
        PyPI Distribution                  npm Package
        adharasutra                     @adharasutra/
              │                         electron-bridge
       ┌──────┴───────┐                        │
       ▼              ▼                        │
   Core Runtime   Optional Extras              │
       │          and Tooling                   │
       │              │                         │
       └──────┬───────┘                         │
              │                                 │
              ▼                                 ▼
        Python Applications               Electron Main
              │                                 │
              │                    ┌────────────┘
              │                    ▼
              │              Python Backend
              │                    │
              └─────────┬──────────┘
                        ▼
              Application Packaging
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
         Windows       Linux        macOS
```

## 3.1 Distribution Boundaries

AdharaSutra's Python framework is a reusable library.

The `adhara` developer CLI is development tooling.

The Electron bridge is a reusable TypeScript/JavaScript package.

A consuming application is a separate product and has its own package dependencies and delivery artifacts.

The framework itself does not automatically own the complete installation experience of every consuming application.

---

# 4. Proposed Distribution Inventory

| Distribution | Format | Responsibility |
|---|---|---|
| `adharasutra` | Python wheel / source distribution | Framework runtime and modular capabilities |
| `adharasutra` optional extras | Python dependency groups | Install additional supported dependencies |
| `adhara` | Python console entry point | Developer commands, with tooling dependencies |
| `@adharasutra/electron-bridge` | npm package | Electron-to-Python integration |
| Application Python package | Python wheel, environment, or frozen executable | Application business backend |
| Application Electron package | Platform installer or application bundle | Desktop delivery |
| External executable bundle | Application-owned resources | audio.cpp or other approved tools |
| Model and data resources | Application-owned distributions or downloads | Models, templates, media, data |

All package names above are **proposed names**. Registry ownership and package availability are not established by this document.

---

# 5. Python Distribution Strategy

## 5.1 Initial Decision

Adopt one Python distribution containing the framework's modules.

**Proposed distribution name:** `adharasutra`.

**Proposed import namespace:** `adharasutra`.

## 5.2 Rationale

A modular monolith avoids:

- Many small releases.
- Cross-package dependency cycles.
- Repeated compatibility management.
- Unnecessary installation complexity.
- Premature public package boundaries.

It still allows clean internal modules and optional dependency groups.

## 5.3 Internal Modules

The distribution may contain:

```text
adharasutra/
├── core/
├── cli/
├── connectors/
│   ├── http/
│   ├── websocket/
│   ├── process/
│   ├── sqlite/
│   └── filesystem/
├── state/
├── jobs/
├── events/
├── observability/
└── tooling/
    ├── scaffold/
    ├── discovery/
    ├── verification/
    ├── migration/
    └── reporting/
```

The physical structure may change during implementation.

## 5.4 Runtime Import Boundary

Importing the minimal framework shall not automatically import heavy optional connector or developer-tooling dependencies.

## 5.5 Public API Boundary

Applications should use documented exports such as:

```python
from adharasutra import Application
```

This is a proposed API shape.

Applications should not depend on undocumented internal functions such as private parser implementations, registry internals, or migration utilities.

## 5.6 Internal Stability

Private internal modules may change without the same compatibility guarantees as public APIs.

The public/private distinction must be documented.

## 5.7 Future Package Splitting

Independent distributions should only be considered when justified by:

- Dependency weight.
- Different release cadence.
- Distinct ownership.
- Independent adoption.
- Security isolation.
- Meaningful operational advantages.

A package split itself is a compatibility-sensitive architectural change.

---

# 6. Python Packaging Metadata

## 6.1 Packaging Standard

The Python project shall use `pyproject.toml`.

Python's packaging standard supports build-system declarations, project metadata, optional dependencies, and console entry points. <escape></escape><Cite ref="turn162575search0"/>

## 6.2 Illustrative Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "adharasutra"
version = "0.1.0"
description = "Reusable Python application infrastructure"
requires-python = ">=3.12"
readme = "README.md"
license = "MIT"
dependencies = []

[project.optional-dependencies]
http = ["httpx"]
websocket = ["websockets"]
sqlite = []
process = []
devtools = ["libcst"]
all-runtime = [
    "httpx",
    "websockets"
]

[project.scripts]
adhara = "adharasutra.tooling.cli:main"
```

This is a **conceptual example**, not a finalized package manifest. The license, build backend, dependencies, extras, API, and versions all require approval.

## 6.3 Dependency-Free Capabilities

A connector does not need a packaging extra merely because it exists.

For example, SQLite functionality using Python's standard library may require no additional installation dependency.

Similarly, basic subprocess management may use the standard library.

## 6.4 Package Metadata Validation

Release validation shall check:

- Distribution name.
- Version.
- Python requirement.
- Dependency declarations.
- Entry points.
- Included package files.
- License metadata.
- README.
- Build artifacts.

## 6.5 Source of Version

The project shall have one authoritative package-version source.

Duplicated manually maintained version values should be avoided.

---

# 7. Optional Dependency Architecture

## 7.1 Purpose

Applications should install only the capabilities they need.

## 7.2 Proposed Extras

| Extra | Candidate purpose |
|---|---|
| `http` | HTTP connector dependencies |
| `websocket` | WebSocket client dependencies |
| `devtools` | Architecture tooling, scaffolding, migration |
| `testing` | Reusable framework contract-test utilities |
| `all-runtime` | All approved optional runtime integrations |
| `all` | All optional capabilities, potentially including tooling |

The final extra names must be selected before publication.

## 7.3 Installation Examples

Minimal framework:

```bash
python -m pip install adharasutra
```

HTTP integration:

```bash
python -m pip install "adharasutra[http]"
```

Electron-backed Python application requiring HTTP and WebSocket:

```bash
python -m pip install "adharasutra[http,websocket]"
```

Developer tooling:

```bash
python -m pip install "adharasutra[devtools]"
```

These commands describe the **proposed distribution**, not an assertion that it has already been published.

## 7.4 Missing Optional Dependencies

When an optional feature is requested without its dependency, the framework shall report a classified error with installation guidance.

It must not fail unexpectedly during unrelated minimal runtime imports.

## 7.5 Dependency Direction

The minimal runtime must not depend on development tooling.

Developer tooling may depend on the runtime's public architecture contracts.

## 7.6 Dependency Compatibility

Optional dependencies shall use tested compatible version ranges.

The framework should avoid unconstrained dependency upgrades where they could silently introduce breaking behavior.

## 7.7 Extras Are Installation Metadata

Installing an extra makes dependencies available.

It does not automatically authorize a connector, register an external executable, or enable a runtime capability.

Capability activation remains explicit application configuration.

---

# 8. Developer Tooling Distribution

## 8.1 Responsibilities

Developer tooling includes:

- Project scaffolding.
- Architecture discovery.
- Architecture verification.
- Migration planning and apply operations.
- Architecture reporting.
- Test orchestration.
- Diagnostic commands.

## 8.2 Initial Recommendation

Keep developer tooling in the same source repository and initial Python distribution, but load its heavy dependencies only when tooling features are used.

## 8.3 Import Isolation

Applications importing core runtime interfaces shall not import parser or transformation dependencies as an incidental side effect.

## 8.4 CLI Entry Point

**Proposed command:** `adhara`.

The console entry point should provide clear diagnostics when a selected tooling command requires an uninstalled optional extra.

## 8.5 Future Standalone CLI Package

A future `adharasutra-tools` distribution may be considered if tooling dependencies, release cadence, or adoption needs justify separation.

This is not an initial requirement.

## 8.6 Production Installations

Production applications should install the necessary runtime capabilities without unnecessary development tooling.

---

# 9. Python CLI Distribution

## 9.1 Framework Developer CLI

The developer CLI may expose commands such as:

```text
adhara new
adhara inspect
adhara verify
adhara migrate
adhara test
adhara doctor
```

These are proposed commands.

## 9.2 Application CLI

Consuming applications shall define their own entry points.

They need not expose the developer CLI to their end users.

## 9.3 Console Entry Points

Python packaging supports console-script entry points that map installed command names to Python callables. <Cite ref="turn162575search6"/>

## 9.4 One-Shot Execution

Applications may expose one-shot commands using their installed Python entry point.

## 9.5 Persistent Execution

Applications may expose a persistent backend entry point intended to be launched by Electron.

## 9.6 stdout Contract

Application protocol entry points must preserve structured stdout.

Developer tooling may use ordinary human-readable output unless a machine-readable output mode is selected.

## 9.7 CLI Name Collisions

The framework's `adhara` executable and consuming application commands must be treated as separate identities.

---

# 10. Source Repository Organization

## 10.1 Proposed Layout

```text
adharasutra/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
│
├── src/
│   └── adharasutra/
│       ├── core/
│       ├── cli/
│       ├── connectors/
│       ├── state/
│       ├── jobs/
│       ├── observability/
│       └── tooling/
│
├── electron/
│   └── bridge/
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       └── tests/
│
├── contracts/
│   ├── cli-protocol/
│   ├── action-schemas/
│   └── compatibility/
│
├── tests/
│   ├── unit/
│   ├── contracts/
│   ├── integration/
│   └── packaging/
│
├── examples/
│   ├── minimal-cli/
│   ├── ddd-cli/
│   └── electron-python/
│
├── docs/
│   └── design/
│
└── .github/
    └── workflows/
```

## 10.2 Monorepo Preference

The Python framework and Electron bridge should initially share a source repository.

Benefits include:

- Coordinated contract changes.
- Shared protocol fixtures.
- Centralized CI.
- Unified architecture documentation.
- Easier compatibility testing.

## 10.3 Independent Publication

A shared repository does not require a single version number or simultaneous publication of all packages.

## 10.4 Release Boundaries

Each distributed package shall identify its own version, artifact set, and compatibility declarations.

---

# 11. Electron Bridge Package

## 11.1 Proposed Package Name

`@adharasutra/electron-bridge`

This is a proposed name subject to npm namespace availability and ownership.

## 11.2 Distribution Format

The bridge shall be published as an npm package with compiled JavaScript and TypeScript declarations.

## 11.3 Responsibilities

The bridge owns:

- Python backend process lifecycle.
- CLI protocol serialization and parsing.
- Request correlation.
- Timeout management.
- Event subscription handling.
- Error translation.
- Compatible handshake.
- Backend crash handling.

## 11.4 Excluded Responsibilities

The bridge must not own:

- Application-specific business actions.
- Domain models.
- Renderer UI design.
- Arbitrary application authentication rules.
- External application-specific executable installation.

## 11.5 Package Layout

```text
@adharasutra/electron-bridge/
├── package.json
├── dist/
│   ├── index.js
│   ├── index.d.ts
│   └── ...
├── README.md
└── LICENSE
```

## 11.6 Proposed package.json

```json
{
  "name": "@adharasutra/electron-bridge",
  "version": "0.1.0",
  "description": "Electron integration for AdharaSutra Python runtimes",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "engines": {
    "node": ">=22"
  },
  "peerDependencies": {
    "electron": ">=35"
  }
}
```

All version ranges and package fields are illustrative and require compatibility validation.

## 11.7 Electron Dependency Policy

Electron should normally remain a consuming-application dependency rather than being bundled as an unnecessary duplicate dependency of the bridge.

## 11.8 Public Exports

The package shall explicitly define approved public exports.

Internal process parsers and helpers should not automatically become supported public APIs.

## 11.9 Type Declarations

Published TypeScript declarations shall correspond to the actual compiled JavaScript API.

## 11.10 Package Contents

Release validation shall inspect the published archive to ensure source-only development files, credentials, or unrelated assets are not included accidentally.

---

# 12. Shared Protocol Contract Distribution

## 12.1 Purpose

Python and TypeScript must implement compatible versions of the CLI protocol.

## 12.2 Canonical Contract Source

The monorepo should maintain authoritative, versioned protocol schemas.

Possible formats include:

- JSON Schema.
- Explicit protocol contract definitions.
- Versioned example fixtures.

## 12.3 Generated Types

The build process may generate Python validation artifacts or TypeScript types from shared schemas.

The exact source of truth must be selected before code generation is adopted.

## 12.4 Cross-Language Testing

Both implementations shall use common protocol fixtures.

## 12.5 Contract Version

The protocol version is separate from the Python distribution version and npm bridge version.

## 12.6 Backward Compatibility

New optional fields must follow the declared protocol compatibility rules.

## 12.7 Unsupported Protocols

Incompatible versions must fail during handshake or the earliest appropriate compatibility boundary.

## 12.8 No Assumed Matching Versions

A Python runtime version `1.2.0` and bridge version `1.3.0` may be compatible if their supported protocol and capability contracts overlap.

Version-number equality is not a general requirement.

---

# 13. Versioning Architecture

## 13.1 Independent Version Dimensions

AdharaSutra shall track at least:

1. Python distribution version.
2. Electron bridge version.
3. CLI protocol version.
4. Configuration schema version.
5. Architecture profile version.
6. Architecture model schema version.
7. Migration plan schema version.

## 13.2 Proposed Versioning Policy

Use semantic versioning principles for public software distributions.

Python versions must also follow Python-compatible version syntax.

## 13.3 Major Version

A major release may introduce incompatible public API or package contracts.

## 13.4 Minor Version

A minor release may introduce backward-compatible capabilities and public APIs.

## 13.5 Patch Version

A patch release should contain compatible fixes and maintenance changes.

## 13.6 Pre-1.0 Releases

During `0.x` development, public APIs may evolve more frequently.

However, breaking changes must still be documented clearly.

## 13.7 Protocol Versioning

The CLI protocol shall have an explicit compatibility and version-negotiation policy.

## 13.8 Schema Versioning

Serialized architecture and tooling artifacts must declare versions independent of the package itself.

## 13.9 Version Source

Each published distribution shall derive its version from one authoritative source.

---

# 14. Compatibility Matrix

## 14.1 Purpose

Package users must be able to determine which component versions are supported together.

## 14.2 Compatibility Dimensions

The framework shall publish information for:

- Python version.
- Operating system.
- AdharaSutra Python package.
- CLI protocol.
- Electron bridge.
- Electron/Node versions.
- Optional connector dependencies.
- Configuration schema.
- Packaged Python executable strategy.

## 14.3 Illustrative Matrix

| Component | Example version | Compatibility basis |
|---|---|---|
| Python runtime | 0.1.0 | Python ≥3.12 |
| Electron bridge | 0.1.0 | Negotiated protocol 1.0 |
| CLI protocol | 1.0 | Validated envelopes and capabilities |
| Configuration schema | 1.0 | Supported configuration parser |
| Architecture model | 1.0 | Versioned discovery consumer |
| Electron | Selected supported range | Actual bridge tests |

This is a proposed example, not a verified compatibility statement.

## 14.4 Matrix Publication

The release documentation shall publish approved compatibility combinations.

## 14.5 Unsupported Combinations

Unsupported combinations shall produce understandable errors wherever runtime detection is possible.

## 14.6 Minimum Supported Versions

Support windows and minimum versions must be established from actual compatibility testing, not inferred from packaging metadata alone.

---

# 15. Standalone Python Application Distribution

## 15.1 Purpose

Applications not using Electron may be distributed as normal Python packages.

## 15.2 Application Ownership

The application owns:

- Its package name.
- Version.
- CLI command.
- Business dependencies.
- Connector configuration.
- Data files.
- Test suite.
- Release process.

## 15.3 Framework Dependency

The application declares its supported AdharaSutra version range.

## 15.4 Optional Dependencies

The application selects only the framework extras it needs.

## 15.5 Application Packaging

An application may publish a wheel or source distribution.

It may also be distributed through a controlled private installation method.

## 15.6 Installation Validation

Tests shall install the built application package into a clean environment and execute its documented entry points.

## 15.7 Environment Isolation

Production applications should use an appropriate isolated Python environment rather than relying on uncontrolled global package installations.

## 15.8 Application Data

Mutable application data shall not be stored inside an installed package directory.

---

# 16. Electron Application Packaging Strategies

## 16.1 Purpose

Electron applications require a reliable method to launch their Python backend on the end user's machine.

## 16.2 Supported Strategies

Three packaging strategies are proposed.

### Strategy A — Bundled Python Environment

Package the application together with a compatible Python interpreter and installed dependencies.

### Strategy B — Frozen Python Executable

Package the backend as a standalone executable created with a selected freezing tool.

### Strategy C — External Python Installation

Require the user or deployment environment to provide a compatible Python runtime.

## 16.3 Comparison

| Strategy | Advantages | Limitations |
|---|---|---|
| Bundled Python | Predictable interpreter and dependencies | Larger package, platform-specific assembly |
| Frozen executable | Simple backend launch interface | Freezer compatibility, native dependency handling |
| External Python | Smaller desktop package | Environment variability and setup burden |

## 16.4 Initial Recommendation

For end-user desktop applications, prefer a bundled, application-controlled backend runtime.

Support frozen executables as a validated alternative.

Treat system Python as primarily a development or explicitly managed deployment strategy.

## 16.5 No Mandatory HTTP Server

None of these strategies requires a localhost HTTP server between Electron and Python.

The standard bridge uses subprocess communication.

---

# 17. Bundled Python Runtime

## 17.1 Contents

A bundled backend may contain:

- Platform-specific Python interpreter.
- Application Python package.
- AdharaSutra.
- Required Python dependencies.
- Native extensions.
- Approved runtime resources.

## 17.2 Platform-Specific Builds

A Windows Python environment cannot automatically be redistributed as a Linux or macOS backend.

Each target platform requires compatible interpreter and dependency artifacts.

## 17.3 Environment Creation

The packaging pipeline shall construct a clean, reproducible backend environment.

## 17.4 Interpreter Integrity

The packaged runtime shall resolve the intended interpreter rather than an arbitrary system executable.

## 17.5 Runtime Isolation

The application should avoid accidental dependency resolution from unrelated system Python environments.

## 17.6 Native Libraries

Native extensions must be compatible with the target operating system, architecture, and Python version.

## 17.7 Writable Directories

The bundled runtime should be treated as application installation content.

Mutable databases, logs, and generated artifacts belong in configured writable application directories.

## 17.8 Runtime Manifest

The package should include a manifest describing the backend entry point and relevant compatibility information.

---

# 18. Frozen Backend Executable

## 18.1 Purpose

Some applications may choose to freeze the Python backend.

## 18.2 Candidate Tools

Potential tools include PyInstaller, Nuitka, or another compatible solution.

No freezing tool is approved by this document.

## 18.3 Validation Requirements

A frozen backend shall support:

- Application bootstrap.
- Required module imports.
- Configuration loading.
- stdout/stderr protocol communication.
- Connector access.
- State persistence.
- Job execution.
- External process management.
- Shutdown.

## 18.4 Optional Modules

Freezing must include the optional modules actually required by the application.

## 18.5 Resource Discovery

Runtime resource paths must not rely on assumptions valid only in source-tree execution.

## 18.6 Build Modes

One-file and directory-based frozen executables may have different startup and extraction behavior.

These differences require measurement and testing.

## 18.7 Security and Signing

Executable integrity and code signing are deployment responsibilities, with framework guidance where relevant.

---

# 19. Electron Resource Layout

## 19.1 Purpose

The Electron application must reliably locate and execute Python backend resources.

## 19.2 Proposed Layout

```text
DesktopApplication/
│
├── Electron Application
│   ├── main
│   ├── preload
│   └── renderer
│
└── resources/
    ├── backend/
    │   ├── runtime/
    │   ├── application/
    │   └── dependencies/
    │
    └── runtime-manifest.json
```

The exact layout is packaging-tool-dependent.

## 19.3 ASAR Restrictions

Executables must not be assumed directly executable from inside an ASAR archive. Electron packaging tools provide mechanisms for placing executable resources outside ASAR or in appropriately unpacked locations. <Cite ref="turn162575search8"/>

## 19.4 Runtime Location

Electron main shall use an approved runtime manifest and platform-aware path resolver.

## 19.5 Development Location

Development runtime paths may differ from packaged runtime paths.

## 19.6 Path Validation

The bridge shall verify executable existence and applicable permissions before launch.

## 19.7 Integrity Checks

Applications may verify hashes or signatures of bundled backend resources when required by their threat model.

## 19.8 Startup Diagnostics

Missing or invalid packaged runtime resources must produce actionable startup errors.

---

# 20. Backend Runtime Manifest

## 20.1 Purpose

The runtime manifest describes how the packaged application locates and launches its Python backend.

## 20.2 Proposed Fields

- Manifest schema version.
- Application identity.
- Backend packaging strategy.
- Target operating system.
- CPU architecture.
- Executable relative path.
- Required arguments.
- Working-directory policy.
- Protocol compatibility.
- Backend version.
- Optional integrity metadata.

## 20.3 Example

```json
{
  "schema_version": "1.0",
  "application": "example-desktop",
  "backend": {
    "strategy": "bundled-python",
    "version": "0.1.0",
    "platform": "win32",
    "architecture": "x64",
    "executable": "backend/runtime/python.exe",
    "module": "example_app.backend",
    "protocol": {
      "supported": ["1.0"]
    }
  }
}
```

This is an illustrative Windows manifest.

## 20.4 Trust Boundary

The renderer shall not be allowed to replace backend executable paths in the trusted runtime manifest.

## 20.5 Environment Variables

The bridge may pass approved runtime environment settings.

Untrusted renderer input shall not become unrestricted process environment configuration.

## 20.6 Manifest Versioning

Manifest schema changes must follow an explicit compatibility policy.

---

# 21. Cross-Platform Packaging

## 21.1 Windows

Validate:

- Executable resolution.
- Path spaces and Unicode.
- DLL and native extension loading.
- Process termination.
- File access permissions.
- Application data directories.
- Installer and portable package formats where supported.

## 21.2 Linux

Validate:

- Interpreter and shared-library compatibility.
- Executable permissions.
- Application data locations.
- Process groups and signals.
- Supported desktop packaging formats.
- Distribution compatibility policy.

## 21.3 macOS

Validate:

- Application bundle structure.
- Backend executable permissions.
- Code signing.
- Notarization where applicable.
- Runtime library loading.
- Architecture-specific binaries.
- Application data locations.

## 21.4 CPU Architecture

Artifacts must declare supported architectures.

Examples:

- x86-64.
- ARM64.

A package claiming ARM64 support requires appropriate backend and native dependency builds.

## 21.5 Build Hosts

Cross-compilation may be used only when the selected toolchain supports the required output.

Native platform validation remains necessary for platform-specific behavior.

## 21.6 Platform Matrix

The release pipeline should maintain an explicit supported operating-system and architecture matrix.

---

# 22. External Executables and AI Assets

## 22.1 Purpose

Some consuming applications use external programs or large models.

Examples include audio-processing tools, AI inference engines, image-processing utilities, and media encoders.

## 22.2 Ownership

These resources are generally application-owned, not mandatory AdharaSutra dependencies.

## 22.3 External Executable Policy

Each packaged tool should have:

- Name and version.
- Source or origin.
- Executable path.
- Platform compatibility.
- Integrity metadata where appropriate.
- License and redistribution review.
- Expected invocation contract.

## 22.4 Model Assets

Large AI model files should not be bundled into the core AdharaSutra wheel.

## 22.5 Download Strategy

Applications may distribute model assets separately or provide explicit installation workflows.

## 22.6 No Silent Downloads

Normal application startup should not unexpectedly download substantial assets.

## 22.7 License Compliance

Redistribution of third-party models and executables requires review of their applicable licenses and terms.

## 22.8 Framework Boundary

AdharaSutra may help locate and invoke approved resources.

It does not assume ownership of the resources' business semantics or redistribution rights.

---

# 23. Dependency Management

## 23.1 Framework Dependencies

The Python framework declares compatible dependency ranges.

## 23.2 Application Dependencies

Consuming applications declare their own dependencies and compatible AdharaSutra versions.

## 23.3 Development Dependencies

Linters, formatters, test runners, architecture parsers, and build tools shall not be mandatory runtime dependencies unless an actual runtime capability requires them.

## 23.4 Lockfiles

Applications should maintain reproducible dependency resolution through an appropriate lockfile or equivalent pinned build input.

## 23.5 Framework Library Versus Application

A reusable library typically publishes compatible dependency constraints.

An application deployment typically resolves those constraints into a reproducible environment.

## 23.6 Native Dependency Review

Dependencies requiring native binaries must be validated on supported Python and operating-system combinations.

## 23.7 Dependency Conflicts

Optional extras and application dependencies must be tested for common compatibility conflicts.

## 23.8 Dependency Updates

Updating a dependency should trigger affected tests and compatibility checks.

---

# 24. Build Architecture

## 24.1 Purpose

The build pipeline produces distribution artifacts from an identified source revision.

## 24.2 Build Inputs

The pipeline shall record:

- Source revision.
- Worktree state.
- Package version.
- Build tool versions.
- Dependency constraints.
- Target platform.
- CPU architecture.
- Relevant environment settings.

## 24.3 Python Build

Produce:

- Wheel.
- Source distribution.

## 24.4 TypeScript Build

Produce:

- Compiled JavaScript.
- TypeScript declarations.
- npm package archive.

## 24.5 Desktop Application Build

Produce platform-specific packages or installers according to consuming application requirements.

## 24.6 Build Separation

Build and publish are separate operations.

Successful build does not authorize publication.

## 24.7 Artifact Verification

Artifacts shall be inspected and tested before release approval.

---

# 25. Build Reproducibility

## 25.1 Definition

A reproducible build should produce equivalent expected artifacts from equivalent approved inputs under the documented build environment.

## 25.2 Factors Affecting Output

Potential sources of variation include:

- File timestamps.
- Dependency versions.
- Native compilers.
- Build-host differences.
- Nondeterministic file ordering.
- Electron packaging metadata.
- Signing and notarization.
- Generated resource identifiers.

## 25.3 Deterministic Inputs

Build pipelines should use pinned or controlled toolchains and dependency resolutions.

## 25.4 Artifact Hashes

Produced artifacts shall have recorded cryptographic hashes.

## 25.5 Byte-for-Byte Versus Functional Reproducibility

The framework must distinguish identical artifact bytes from functionally equivalent builds.

## 25.6 Reproducibility Tests

Where feasible, repeat builds in controlled environments and compare relevant outputs.

## 25.7 Rebuild Evidence

Release records should preserve enough information to reconstruct the build process.

---

# 26. Release Pipeline Architecture

## 26.1 Proposed Pipeline

```text
Approved Source Revision
           │
           ▼
Validate Release Metadata
           │
           ▼
Run Unit and Contract Tests
           │
           ▼
Run Architecture Verification
           │
           ▼
Run Relevant Integration Tests
           │
           ▼
Build Python Distribution
           │
           ▼
Build Electron Bridge
           │
           ▼
Inspect Package Contents
           │
           ▼
Install Built Artifacts
           │
           ▼
Run Package Smoke Tests
           │
           ▼
Compatibility Evaluation
           │
           ▼
Security and Provenance Checks
           │
           ▼
Release Approval
           │
           ▼
Publish Approved Artifacts
           │
           ▼
Verify Published Packages
```

## 26.2 Independent Releases

The Python and npm packages may have separate release triggers while sharing appropriate CI checks.

## 26.3 Release Environment

Publishing should use a protected release environment with restricted permissions.

## 26.4 Artifacts Before Publish

The pipeline should inspect the actual built artifacts rather than rebuilding them implicitly with different dependencies during publication.

## 26.5 Failed Gates

A required failing or incomplete gate must prevent ordinary release approval unless an explicit authorized release exception policy permits otherwise.

---

# 27. PyPI Publishing

## 27.1 Proposed Registry

PyPI is the preferred public registry for the Python framework.

## 27.2 Publishing Authentication

Use trusted publishing through supported OpenID Connect workflows where available.

PyPI recommends trusted publishing, which replaces long-lived publishing credentials with short-lived tokens issued through an approved identity workflow. <Cite ref="turn162575search1"/>

## 27.3 GitHub Actions

A GitHub Actions release job may publish using a configured PyPI trusted publisher and the required OIDC permissions.

## 27.4 Publication Authorization

Release workflows should be restricted to approved tags, branches, or environments.

## 27.5 TestPyPI

TestPyPI may be used to validate the publication workflow without treating it as a substitute for installed-artifact validation.

## 27.6 Published Artifact Verification

After publishing, verify:

- Registry version.
- Artifact filenames.
- Package hashes.
- Metadata.
- Dependency declarations.
- Installation into a clean environment.
- Runtime imports.

## 27.7 Version Immutability

Published releases shall not rely on overwriting an existing version.

Corrections require an appropriate new release.

---

# 28. npm Publishing

## 28.1 Proposed Registry

npm is the preferred public registry for the TypeScript Electron bridge.

## 28.2 Package Identity

The selected npm scope must be owned and configured before publishing.

## 28.3 Trusted Publishing

Use npm trusted publishing with an approved CI provider where supported.

Current npm trusted publishing supports OIDC-based authentication and has minimum toolchain requirements that must be satisfied by the publishing environment. <Cite ref="turn162575search5"/>

## 28.4 Package Inspection

Before publication, validate the npm archive contents.

## 28.5 TypeScript Declarations

The published package shall contain the intended declaration files.

## 28.6 Module Compatibility

Package exports must match supported module formats and Node/Electron compatibility requirements.

## 28.7 Published Verification

After publishing, verify:

- Package version.
- Registry metadata.
- Published archive integrity.
- Clean installation.
- JavaScript imports.
- Type declarations.
- Compatibility tests.

## 28.8 Dist Tags

Release channels may use approved npm distribution tags.

These must not silently point stable consumers to incompatible prereleases.

---

# 29. Trusted Publishing and Credentials

## 29.1 Principle

Publishing credentials shall be as narrowly scoped and short-lived as practical.

## 29.2 OIDC

Trusted publishing should be preferred over persistent registry tokens where supported.

## 29.3 Workflow Permissions

Publication jobs shall use only the permissions required by their publishing actions.

## 29.4 Protected Environments

Production publishing should use appropriate repository/environment protections.

## 29.5 Approval

The release process shall identify the person or workflow authorized to publish.

## 29.6 Secret Leakage

CI logs must not expose tokens, credentials, or private signing keys.

## 29.7 Supply-Chain Threats

A trusted publishing configuration does not eliminate the risk of compromised source code, malicious dependencies, or unauthorized workflow modifications.

## 29.8 Release Verification

The published artifact must be traced back to the approved source revision and build result.

---

# 30. Package Integrity and Provenance

## 30.1 Integrity Metadata

Release artifacts should include hashes such as SHA-256.

## 30.2 Provenance

Where supported, release systems should generate provenance information identifying the build environment and source revision.

## 30.3 Signing

Artifact signing may be required for certain desktop platforms or organizational deployments.

## 30.4 SBOM

An SBOM may be generated for dependency transparency.

## 30.5 Dependency Scanning

Release pipelines should execute appropriate vulnerability checks.

## 30.6 Source-to-Artifact Traceability

The framework should retain:

- Source commit.
- Release tag.
- Workflow run.
- Build environment.
- Package version.
- Artifact hash.
- Registry location.

## 30.7 Integrity Limitations

A matching checksum proves that bytes match the expected digest.

It does not by itself prove the artifact is safe or the build source was trustworthy.

---

# 31. Installation Architecture

## 31.1 Python Library Install

Applications install the framework through their Python dependency manager.

## 31.2 Editable Development Install

Developers may use editable installations during framework development.

## 31.3 Tooling Install

Developers may install the tooling extra or a future standalone tools package.

## 31.4 npm Bridge Install

Electron applications install the bridge as a package dependency.

## 31.5 Application Build Integration

The Electron application's packaging pipeline assembles its approved Python backend strategy.

## 31.6 Installation Verification

An installation check should validate required runtime imports and entry points.

## 31.7 No Silent Configuration Changes

Installing AdharaSutra shall not automatically rewrite application source or production configuration.

---

# 32. Upgrade and Rollback Architecture

## 32.1 Purpose

Applications must upgrade framework versions safely.

## 32.2 Upgrade Categories

- Compatible patch upgrade.
- Compatible feature upgrade.
- Breaking major upgrade.
- Protocol upgrade.
- Configuration schema upgrade.
- Architecture profile upgrade.
- Connector dependency upgrade.

## 32.3 Upgrade Verification

An upgrade shall evaluate:

- Public API compatibility.
- Protocol compatibility.
- Configuration compatibility.
- Dependency resolution.
- Required runtime tests.
- Application-specific behavior.

## 32.4 Migration Integration

The Migration Framework may create controlled plans for breaking framework upgrades.

## 32.5 Rollback

Rollback may restore an earlier application build when its data and schema remain compatible.

## 32.6 Persistent Data Limitations

Downgrading software does not automatically undo database schema changes or external side effects.

## 32.7 Electron Backend Mismatch

A desktop application must not silently use an arbitrary Python backend version that fails its approved compatibility contract.

## 32.8 Update Ownership

Desktop auto-update delivery remains application-owned or delegated to an approved update system.

---

# 33. Deprecation and Compatibility Policy

## 33.1 Public API Deprecation

Deprecated APIs should have:

- Clear replacement.
- Version of deprecation.
- Planned removal version where known.
- Migration guidance.
- Appropriate compatibility tests.

## 33.2 Protocol Deprecation

Protocol versions shall have an explicit support window.

## 33.3 Configuration Deprecation

Deprecated configuration fields should produce actionable warnings or validation errors according to the approved migration policy.

## 33.4 Rule and Profile Changes

Architecture rules and profiles must be versioned so existing baseline results remain interpretable.

## 33.5 Removal

Removal of a public capability requires a documented compatibility assessment.

## 33.6 Pre-1.0

The framework may evolve more rapidly before 1.0, but compatibility changes must still be transparent.

---

# 34. Release Artifacts and Reporting

## 34.1 Release Artifact Manifest

The build pipeline should produce a manifest containing the generated artifacts.

## 34.2 Example

```json
{
  "schema_version": "1.0",
  "release": "0.1.0",
  "source_revision": "example-commit",
  "artifacts": [
    {
      "name": "adharasutra-0.1.0-py3-none-any.whl",
      "type": "python-wheel",
      "sha256": "<calculated-hash>"
    },
    {
      "name": "electron-bridge-0.1.0.tgz",
      "type": "npm-package",
      "sha256": "<calculated-hash>"
    }
  ]
}
```

This is illustrative.

Actual artifact filenames and hashes must be taken from the build output.

## 34.3 Report Contents

Reports shall identify:

- Package identities.
- Versions.
- Source revision.
- Toolchain.
- Target platforms.
- Build status.
- Artifact integrity.
- Tests executed.
- Tests not executed.
- Compatibility results.
- Publishing status.
- Published registry references.

## 34.4 Reporting Accuracy

Built, tested, approved, published, and installed are separate states.

A package must not be reported as published merely because its build succeeded.

---

# 35. Developer CLI and Release Commands

## 35.1 Proposed Commands

Inspect package configuration:

```bash
adhara package inspect .
```

Validate package metadata:

```bash
adhara package verify .
```

Build Python artifacts:

```bash
adhara package build .
```

Check release compatibility:

```bash
adhara package compatibility .
```

Create a release report:

```bash
adhara package report . --format json
```

These are **proposed developer-tooling interfaces**.

## 35.2 Tool Delegation

The developer CLI should orchestrate established Python and JavaScript packaging tools rather than reimplementing full package builders.

## 35.3 Publishing Separation

A generic `adhara package build` operation shall not automatically publish packages.

## 35.4 Publishing Authorization

Registry publication requires a distinct, explicitly authorized workflow.

## 35.5 No Unapproved Installation

Package inspection and validation must not silently install or execute unrelated dependencies.

---

# 36. CI and Release Quality Gates

| Gate | Focus |
|---|---|
| PKG-QG-01 | Package metadata validation |
| PKG-QG-02 | Dependency compatibility |
| PKG-QG-03 | Python unit and contract tests |
| PKG-QG-04 | TypeScript bridge tests |
| PKG-QG-05 | Cross-language protocol compatibility |
| PKG-QG-06 | Architecture verification |
| PKG-QG-07 | Security and vulnerability checks |
| PKG-QG-08 | Python wheel and sdist build |
| PKG-QG-09 | npm package build |
| PKG-QG-10 | Installed-artifact smoke tests |
| PKG-QG-11 | Cross-platform validation |
| PKG-QG-12 | Electron packaged runtime validation |
| PKG-QG-13 | Artifact integrity and provenance |
| PKG-QG-14 | Authorized registry publishing |
| PKG-QG-15 | Published artifact verification |

## 36.1 Gate Outcomes

- PASSED.
- FAILED.
- INCOMPLETE.
- BLOCKED.

## 36.2 Missing Evidence

A required unexecuted test cannot be treated as a passed release gate.

## 36.3 Approval

The mandatory release gate set must be approved before production publication.

---

# 37. Packaging Testing Strategy

## 37.1 Python Wheel Tests

Verify:

- Wheel builds.
- Wheel installs.
- Runtime imports succeed.
- Entry points resolve.
- Package data exists.
- Optional imports remain isolated.

## 37.2 Source Distribution Tests

Build a wheel from the source distribution and verify that required files and metadata are included.

## 37.3 Optional Extras Tests

Install representative extras combinations in clean environments.

## 37.4 Development Tooling Tests

Verify developer commands work with their declared optional dependencies.

## 37.5 npm Package Tests

Install the package archive into a clean test consumer and verify exported APIs and declarations.

## 37.6 Protocol Compatibility

Run shared fixtures against the packaged Python runtime and bridge.

## 37.7 Electron Packaged Tests

Launch a representative packaged Electron application and exercise its backend.

## 37.8 Cross-Platform Tests

Validate supported operating systems and architectures.

## 37.9 Upgrade Tests

Test supported upgrade paths and incompatible-version detection.

## 37.10 Rollback Tests

Validate package rollback behavior where a supported rollback contract exists.

---

# 38. Packaging Architecture Verification Rules

| Rule ID | Description |
|---|---|
| PKG-VER-001 | Python distribution metadata is valid |
| PKG-VER-002 | Python version constraints are declared |
| PKG-VER-003 | Public API exports are documented |
| PKG-VER-004 | Optional dependencies remain isolated |
| PKG-VER-005 | Minimal imports do not require development tooling |
| PKG-VER-006 | Developer CLI entry points are valid |
| PKG-VER-007 | Electron bridge is independently packaged |
| PKG-VER-008 | Bridge public exports match declarations |
| PKG-VER-009 | Shared protocol contracts are versioned |
| PKG-VER-010 | Package compatibility is validated |
| PKG-VER-011 | Source revision is recorded in release evidence |
| PKG-VER-012 | Built artifacts are tested |
| PKG-VER-013 | Package archives exclude prohibited sensitive files |
| PKG-VER-014 | Cross-platform support claims have evidence |
| PKG-VER-015 | Packaged backend paths use approved resolution |
| PKG-VER-016 | Runtime executables are not incorrectly stored inside ASAR |
| PKG-VER-017 | External resources have appropriate ownership and licensing review |
| PKG-VER-018 | Publishing uses an approved authorization workflow |
| PKG-VER-019 | Published artifacts are verified against expected build artifacts |
| PKG-VER-020 | Release reports distinguish incomplete evidence |
| PKG-VER-021 | Framework and bridge version compatibility is explicit |
| PKG-VER-022 | Production distributions avoid unnecessary development dependencies |
| PKG-VER-023 | Upgrade and rollback limitations are documented |
| PKG-VER-024 | Package integrity information is retained |
| PKG-VER-025 | Packaging rules have suitable executable tests |

---

# 39. Representative End-to-End Scenarios

## PKG-S01 — Minimal Python Installation

**Given** a new Python environment,

**When** the minimal framework package is installed,

**Then** core runtime imports shall work without requiring unused optional connector or development-tooling dependencies.

## PKG-S02 — Optional HTTP Installation

**Given** an application selects the HTTP connector,

**When** the relevant optional dependencies are installed,

**Then** HTTP connector imports and registration shall work.

**And** unrelated connectors shall not initialize automatically.

## PKG-S03 — Developer CLI Installation

**Given** an installation includes development tooling,

**When** the developer invokes an approved `adhara` command,

**Then** its required tooling dependencies shall be available or the command shall report a clear missing-dependency error.

## PKG-S04 — Python Wheel Validation

**Given** an approved source revision,

**When** a wheel is built and installed into a clean environment,

**Then** documented public imports and entry points shall work.

## PKG-S05 — npm Bridge Validation

**Given** a built Electron bridge archive,

**When** a clean Electron test consumer installs it,

**Then** the intended JavaScript exports and TypeScript declarations shall be usable.

## PKG-S06 — Protocol Compatibility

**Given** compatible bridge and Python runtime versions,

**When** the handshake occurs,

**Then** the components shall negotiate the supported protocol contract.

## PKG-S07 — Incompatible Protocol

**Given** no compatible protocol version exists,

**When** Electron attempts backend initialization,

**Then** the bridge shall report a compatibility failure.

## PKG-S08 — Bundled Python

**Given** a packaged Electron application with a bundled Python backend,

**When** the application launches,

**Then** it shall resolve its intended packaged interpreter and execute the backend without requiring a separate system Python installation.

## PKG-S09 — Frozen Executable

**Given** a backend has been frozen using an approved strategy,

**When** its packaged executable starts,

**Then** the CLI protocol and required runtime capabilities shall function according to their contracts.

## PKG-S10 — Missing Backend

**Given** a packaged backend executable is missing,

**When** Electron attempts startup,

**Then** the bridge shall report a classified startup failure.

**And** shall not silently launch an unrelated executable.

## PKG-S11 — Windows Package

**Given** a supported Windows target,

**When** packaged runtime tests run,

**Then** executable paths, native libraries, subprocess behavior, and application data paths shall satisfy the applicable contracts.

## PKG-S12 — Linux Package

**Given** a supported Linux target,

**When** packaged runtime tests run,

**Then** executable permissions, library compatibility, and process behavior shall satisfy the applicable contracts.

## PKG-S13 — macOS Package

**Given** a supported macOS target,

**When** packaged runtime tests run,

**Then** application bundle and backend-launch requirements shall be validated.

## PKG-S14 — Unused AI Models

**Given** an application does not select any AI-model integration,

**When** the framework is installed,

**Then** it shall not download or install unrelated AI models.

## PKG-S15 — Package Upgrade

**Given** an application upgrades its AdharaSutra version,

**When** compatibility checks execute,

**Then** relevant public APIs, protocol versions, and configuration changes shall be evaluated.

## PKG-S16 — Dependency Conflict

**Given** an application dependency conflicts with an optional framework extra,

**When** dependency resolution or installation occurs,

**Then** the conflict shall be reported rather than masked by arbitrary runtime imports.

## PKG-S17 — Secure Publication

**Given** an approved release and configured trusted publisher,

**When** the publishing workflow executes,

**Then** the registry shall receive only the approved distribution artifacts.

## PKG-S18 — Published Artifact Verification

**Given** a package was published,

**When** release verification runs,

**Then** the registry artifacts and expected local build evidence shall be compared.

## PKG-S19 — No Unauthorized Publication

**Given** a developer runs a local package build,

**When** build completion occurs,

**Then** no registry publication shall happen implicitly.

## PKG-S20 — Incomplete Release Testing

**Given** a required supported-platform test has not executed,

**When** release readiness is evaluated,

**Then** the corresponding gate shall remain incomplete or blocked according to policy.

---

# 40. Architectural Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| PKG-D01 | Python distribution model | One modular distribution initially |
| PKG-D02 | Python distribution name | `adharasutra` proposed |
| PKG-D03 | Python version | 3.12 minimum |
| PKG-D04 | Python metadata | `pyproject.toml` |
| PKG-D05 | Build backend | Select after implementation evaluation |
| PKG-D06 | Optional dependencies | Python extras |
| PKG-D07 | Development tooling | Optional dependencies and lazy imports |
| PKG-D08 | Developer CLI | `adhara` |
| PKG-D09 | Electron bridge | Separate npm distribution |
| PKG-D10 | Bridge name | `@adharasutra/electron-bridge` proposed |
| PKG-D11 | Source repository | Monorepo initially |
| PKG-D12 | Release cadence | Independent per distribution |
| PKG-D13 | Public versioning | Semantic-versioning principles |
| PKG-D14 | Protocol version | Independent compatibility contract |
| PKG-D15 | Cross-language schemas | Shared versioned source |
| PKG-D16 | Standalone Python | Standard Python packaging |
| PKG-D17 | Desktop backend | Bundled runtime preferred |
| PKG-D18 | Frozen executable | Supported optional strategy |
| PKG-D19 | System Python | Development/managed deployment |
| PKG-D20 | Runtime manifest | Versioned backend launch configuration |
| PKG-D21 | ASAR | Executables external/unpacked as required |
| PKG-D22 | Large AI models | Application-owned assets |
| PKG-D23 | External tools | Explicitly owned and licensed |
| PKG-D24 | Build reproducibility | Controlled inputs and provenance |
| PKG-D25 | PyPI publishing | Trusted publishing preferred |
| PKG-D26 | npm publishing | Trusted publishing preferred |
| PKG-D27 | Registry authentication | Short-lived scoped credentials |
| PKG-D28 | Release validation | Test actual build artifacts |
| PKG-D29 | Release reporting | Machine-readable manifest |
| PKG-D30 | Upgrade compatibility | Explicit assessment |
| PKG-D31 | Deprecation | Documented support policy |
| PKG-D32 | Rollback | Application-specific and data-aware |
| PKG-D33 | Cross-platform packages | Validated target matrix |
| PKG-D34 | LLM requirement | None |
| PKG-D35 | Automatic publishing | Explicit authorized action only |

All decisions remain proposed until final architecture approval.

---

# 41. Outstanding Questions

## PKG-OQ-001 — Python Distribution Name

Should the public package name be `adharasutra`, `adhara-sutra`, or another registry-safe form?

**Recommendation:** Prefer `adharasutra` for consistency between installation and imports, subject to registry verification.

## PKG-OQ-002 — Python Build Backend

Should AdharaSutra use Hatchling, setuptools, or another build backend?

**Recommendation:** Select a modern backend supporting the project layout, package resources, and reproducible builds without unnecessary complexity.

## PKG-OQ-003 — Development Tooling Distribution

Should development tooling remain in the main package or become a separate distribution?

**Recommendation:** Keep one distribution initially with optional dependencies and lazy imports. Split only if measurable advantages justify it.

## PKG-OQ-004 — Optional Extra Names

Should extras correspond to each connector, use broad categories, or both?

**Recommendation:** Provide stable capability-oriented extras, and avoid meaningless extras for standard-library-only modules.

## PKG-OQ-005 — Python Support Window

Which versions beyond Python 3.12 should be supported?

**Recommendation:** Define a tested compatibility matrix and support additional versions when release CI can validate them.

## PKG-OQ-006 — npm Scope Ownership

Should the Electron bridge use an organization-owned npm scope?

**Recommendation:** Prefer an organization or project scope if it will be maintained long-term; verify availability and publish rights before committing to the name.

## PKG-OQ-007 — TypeScript Module Format

Should the Electron bridge publish ESM, CommonJS, or dual-format outputs?

**Recommendation:** Choose according to supported Electron and consuming-app requirements. A dual package should only be used if it can be tested without ambiguous export behavior.

## PKG-OQ-008 — Bridge Peer Dependencies

Should Electron be a peer dependency?

**Recommendation:** Yes, conceptually. Final supported versions must be based on actual Electron bridge tests.

## PKG-OQ-009 — Shared Schema Generation

Should protocol types be generated automatically from JSON Schema?

**Recommendation:** Prefer one canonical contract source with generated or validated language bindings where practical.

## PKG-OQ-010 — Independent Versioning

Should the Python framework and Electron bridge share one version number?

**Recommendation:** No mandatory lockstep versioning. Maintain independent package versions and explicit protocol compatibility.

## PKG-OQ-011 — Default Electron Backend Strategy

Should generated desktop applications use bundled Python or a frozen executable?

**Recommendation:** Prefer a bundled backend as the initial reference implementation and validate freezing as an alternative.

## PKG-OQ-012 — Python Runtime Distribution

Should AdharaSutra itself distribute Python interpreters?

**Recommendation:** No. Interpreter bundling belongs to consuming application packaging, with shared guidance and tooling.

## PKG-OQ-013 — Desktop Packaging Tool

Should generated Electron applications use electron-builder or Electron Forge?

**Recommendation:** Select one reference implementation based on tested platform packaging requirements, while keeping the bridge independent of the packager.

## PKG-OQ-014 — Native Dependencies

How should architecture-specific native modules and Python wheels be packaged?

**Recommendation:** Build separate target-platform artifacts and test their real installation and startup behavior.

## PKG-OQ-015 — External Tool Distribution

Should AdharaSutra provide standard distribution conventions for audio.cpp and similar executables?

**Recommendation:** Provide manifests and validation contracts, not mandatory redistributed binaries.

## PKG-OQ-016 — Model Distribution

Should model downloads be managed by the framework?

**Recommendation:** Keep model acquisition application-owned initially; add reusable asset-management capabilities only after distinct requirements emerge.

## PKG-OQ-017 — Release Version Automation

Should versions be derived automatically from Git tags?

**Recommendation:** Use one authoritative versioning workflow with validation between source metadata, tags, and artifact versions.

## PKG-OQ-018 — Release Branch Strategy

Should every version have a maintenance branch?

**Recommendation:** Begin with simple protected release tags and introduce maintenance branches only when supporting multiple concurrent release lines becomes necessary.

## PKG-OQ-019 — Signed Releases

Should package signing be mandatory?

**Recommendation:** Require platform-appropriate desktop signing where applicable, and evaluate registry provenance or signing for library releases based on supported tooling.

## PKG-OQ-020 — SBOM

Should every release include an SBOM?

**Recommendation:** Add SBOM generation as a release-quality capability, with mandatory status determined by security and deployment requirements.

## PKG-OQ-021 — Published Package Verification

Should CI reinstall published packages after release?

**Recommendation:** Yes. Verify the actual published artifacts and their compatibility with the approved build evidence.

## PKG-OQ-022 — Stable API Policy

When should AdharaSutra commit to a 1.0 public API?

**Recommendation:** After the core runtime, protocol, connector, application integration, and compatibility test contracts are validated by representative applications.

## PKG-OQ-023 — Release Channels

Should alpha, beta, and stable channels exist?

**Recommendation:** Support prerelease versions, but avoid complex channel management until there are concrete consumers.

## PKG-OQ-024 — Package License

Which license should the project publish under?

**Recommendation:** Decide explicitly before public release. If MIT is selected, include the appropriate license text and copyright notice; writing original code generally establishes copyright without requiring a purchased copyright license.

## PKG-OQ-025 — End-User Update System

Should AdharaSutra manage Electron auto-updates?

**Recommendation:** No initially. Application update delivery is separate from the reusable Python/Electron integration framework.

---

# 42. Functional Requirement Traceability

| Requirement group | Packaging responsibility |
|---|---|
| FR-PKG | Build, versioning, distribution, publishing |
| FR-RUN | Framework runtime installation |
| FR-CLI | Application and developer entry points |
| FR-ELC | Electron bridge distribution |
| FR-CON | Optional connector dependencies |
| FR-HTTP | HTTP connector dependency packaging |
| FR-WS | WebSocket connector packaging |
| FR-EXT | Process connector and external executable packaging |
| FR-DB | SQLite capability and native compatibility |
| FR-FS | Resource and artifact path conventions |
| FR-STATE | Persistence dependencies and schema compatibility |
| FR-JOB | Job runtime and worker packaging |
| FR-CFG | Packaged configuration and runtime manifests |
| FR-ERR | Installation and compatibility errors |
| FR-LOG | Logging resource paths |
| FR-SCAF | Generated package metadata |
| FR-DISC | Development-tooling distribution |
| FR-ARCH | Release architecture verification |
| FR-MIG | Framework upgrade planning |
| FR-TEST | Built-artifact tests |
| FR-DOC | Installation and release documentation |
| FR-SEC | Trusted publishing and supply-chain controls |
| FR-REP | Release evidence and artifact reports |
| FR-DEV | Developer build and package commands |

---

# 43. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-COMP | Explicit version and protocol compatibility |
| NFR-PORT | Cross-platform distributions |
| NFR-SEC | Trusted publishing and integrity |
| NFR-REL | Installed-artifact testing and rollback planning |
| NFR-PERF | Startup and package-size benchmarking |
| NFR-RES | Optional dependencies and bounded distributions |
| NFR-MAINT | Modular source and public API boundaries |
| NFR-EXT | Capability-oriented extras |
| NFR-TEST | Packaging and compatibility test matrix |
| NFR-ARCH | Architecture verification of distributions |
| NFR-MIG | Upgrade migration and deprecation policy |
| NFR-OBS | Release reporting and provenance |
| NFR-OPS | Build, install, update, and release workflows |
| NFR-DX | Predictable installation and developer tooling |
| NFR-DOC | Versioned installation documentation |

---

# 44. Packaging and Distribution Acceptance Criteria

The architecture may be approved when:

### Python Distribution

- [ ] Initial Python distribution model is selected.
- [ ] Distribution and import names are decided.
- [ ] Python minimum version is declared.
- [ ] Package metadata follows approved standards.
- [ ] Build backend is selected.
- [ ] Public APIs are identified.
- [ ] Optional dependencies are isolated.
- [ ] Minimal imports do not require heavy optional modules.
- [ ] Developer tooling is isolated from runtime execution.
- [ ] CLI entry points are valid.

### Electron Bridge

- [ ] npm package ownership and name are established.
- [ ] Public TypeScript API is defined.
- [ ] Package export format is selected.
- [ ] Type declarations are validated.
- [ ] Electron compatibility is declared.
- [ ] Shared protocol contracts are versioned.
- [ ] Bridge and Python runtime compatibility is tested.
- [ ] Package contents are inspected before publication.

### Application Distribution

- [ ] Standalone Python installation is supported.
- [ ] Electron backend packaging strategies are defined.
- [ ] Bundled Python has a reference layout.
- [ ] Frozen backend limitations are documented.
- [ ] Runtime manifests are versioned.
- [ ] Packaged executable resolution is tested.
- [ ] Writable application data remains outside immutable installation resources.
- [ ] External executable and model ownership is explicit.

### Build and Publishing

- [ ] Build input provenance is recorded.
- [ ] Python wheel and sdist are validated.
- [ ] npm archives are validated.
- [ ] Built artifacts receive smoke tests.
- [ ] Cross-platform release targets are declared.
- [ ] Package integrity hashes are produced.
- [ ] Trusted publishing is configured where supported.
- [ ] Registry publication requires authorization.
- [ ] Published artifacts are verified.
- [ ] Release evidence is machine-readable.

### Compatibility and Upgrades

- [ ] Python package versioning policy is defined.
- [ ] Electron bridge versioning policy is defined.
- [ ] CLI protocol compatibility is independent of package versions.
- [ ] Configuration and tooling schema versions are documented.
- [ ] Deprecation policy is defined.
- [ ] Upgrade migration paths are addressed.
- [ ] Rollback and persistent-data limitations are explicit.
- [ ] Unsupported combinations produce understandable errors.
- [ ] Missing release evidence cannot produce a false PASS.

---

# 45. Final Architecture Summary

AdharaSutra's Packaging and Distribution Architecture provides a consistent method for distributing reusable Python infrastructure and Electron integration without unnecessarily coupling independent applications.

The initial distribution model favors:

- One modular Python distribution.
- Optional capability dependencies.
- Development tooling isolated through optional dependencies and import boundaries.
- One independently versioned TypeScript Electron bridge.
- Shared versioned protocol contracts.
- Standard Python package installation.
- Application-owned desktop packaging.
- Bundled or frozen Python backends for desktop deployment.
- Cross-platform compatibility validation.
- Secure automated registry publishing.
- Built-artifact release testing.
- Explicit upgrade and deprecation policies.

AdharaSutra does not automatically bundle external executables, GPU drivers, or AI models into its core distribution.

Consuming applications own their business dependencies, application resources, packaging configuration, and end-user delivery.

A shared source repository simplifies coordinated development but does not require the Python runtime and Electron bridge to share package versions.

The release process shall distinguish source correctness, successful artifact construction, installed-artifact validation, and successful registry publication.

**The central guarantee is: Every published AdharaSutra component has a defined dependency boundary, a versioned compatibility contract, and verifiable evidence connecting the published artifact to its approved source and build.**

---

# 46. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending packaging and distribution architecture review

**Next Document:** `docs/design/developer-experience.md`

The next document should define the developer-facing workflow for installing, creating, configuring, running, testing, inspecting, verifying, and migrating AdharaSutra applications, including CLI ergonomics, documentation, troubleshooting, examples, and coding-agent interoperability.

---

**AdharaSutra — Build once. Standardize everywhere.**
