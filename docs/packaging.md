# Packaging and Runtime Discovery

How a packaged desktop application locates its Python backend and its external
executables, and what to check when upgrading.

## Supported platforms

`nikhi.adhara_sutra.runtime.supported_platforms()` defines the desktop platforms
with a backend-discovery mechanism: Windows (`win32`), macOS (`darwin`), and
Linux (`linux`).

## Locating the Python backend

When Python is already running, `nikhi.adhara_sutra.runtime.locate_backend(...)`
can resolve an interpreter using the following order:

1. `ADHARA_PYTHON` environment variable (must point to an existing file).
2. Bundled interpreter paths passed as `bundled=(...)`, relative to `app_root`
   when supplied.
3. Platform interpreter names on `PATH` (`python.exe` on Windows; `python3`,
   `python` elsewhere).
4. The interpreter running the application.

A missing override or missing interpreter raises `RuntimeDiscoveryError` with a
remediation message. This Python helper cannot bootstrap the first Python process.
The Electron main process must currently receive or determine a fixed backend
command by application-specific means. Node-owned packaged/development resolution
is unimplemented and tracked as T18 in the [architecture integrity plan](../openspec/changes/integration-workflows-followup/tasks.md).

## External executables

`ExternalCommand(executable, search_path=...)` resolves bundled executables by
configured path and separately installed tools through `PATH`.
`ExternalCommand.diagnose()` reports `executable`, `resolved`, `found`, and the
resolution `source` without starting the process, so startup checks can report
missing tools with actionable errors.

## Public API

`nikhi.adhara_sutra.__all__` is the public surface. Anything not listed there is
internal and may change without notice. Breaking changes to a listed name are
called out in the release notes with the replacement and removal conditions.

## Deprecation policy

Deprecated public functionality keeps working for the current major release.
A declared incompatible release must announce any removal and upgrade guidance;
removal happens no earlier than the next major release. The synchronous job-handler
warning has no declared removal date. Deprecation warnings are emitted where a runtime warning is practical,
and the documentation is updated before removal.

## Compatibility and upgrades

- Releases follow Semantic Versioning; the CLI protocol version is independent
  of the application version, and reports carry their own `schema_version`.
- The bridge advertises supported protocol versions and rejects incompatible
  backends during `system.hello` (`BRIDGE_PROTOCOL_UNSUPPORTED`).
- Consumers should accept additive report fields and check `schema_version`
  before relying on structure.
- Upgrade procedure: install the new distribution, run `adhara doctor`, rerun
  `adhara verify`, and regenerate migration plans. Breaking changes require
  documented upgrade notes in the release.
- See the [migration guide](migration.md) for analysis, review, and recovery
  procedures.
