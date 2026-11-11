<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 8. Security Requirements

**Requirement group:** `NFR-SEC`

## NFR-SEC-001 — Secure Process Execution

**Priority:** P0

External CLI execution shall avoid unsafe command construction.

**Acceptance criteria:**

- Executables and arguments are represented separately.
- Shell execution is disabled by default.
- Any shell-enabled execution path requires explicit opt-in and documented risk controls.

## NFR-SEC-002 — Action Authorization Boundary

**Priority:** P0

The runtime shall execute only registered actions that are permitted in the current application context.

## NFR-SEC-003 — Input Validation

**Priority:** P0

Untrusted requests shall be validated before invoking application handlers or infrastructure facilities.

## NFR-SEC-004 — Filesystem Safety

**Priority:** P0

Framework-managed filesystem operations shall support protections against unsafe paths and traversal outside configured boundaries.

Where symbolic links are supported, relevant operations shall account for resolved targets.

## NFR-SEC-005 — Secret Protection

**Priority:** P0

Secrets shall not be included in ordinary logs, error envelopes, or generated diagnostic reports.

## NFR-SEC-006 — Secure Configuration

**Priority:** P0

The framework shall support configuration from protected sources and shall not require embedding secrets in application source code.

## NFR-SEC-007 — Electron Process Isolation

**Priority:** P0

The Electron bridge shall keep operating-system process management outside the renderer process.

## NFR-SEC-008 — Controlled IPC Exposure

**Priority:** P0

Electron preload interfaces shall expose only approved operations.

Renderer input shall not directly control unrestricted executable paths or shell commands.

## NFR-SEC-009 — External Network Safety

**Priority:** P1

HTTP and WebSocket connectors shall support secure transport configuration and appropriate certificate verification.

Insecure transport options must be explicit.

## NFR-SEC-010 — Dependency Security

**Priority:** P1

The framework's release process shall support dependency vulnerability analysis and reproducible dependency resolution.

## NFR-SEC-011 — Safe Diagnostics

**Priority:** P0

Architecture and migration reports shall avoid exposing sensitive runtime information, credentials, or private data not required for analysis.

## NFR-SEC-012 — Unsafe Automated Modification Prevention

**Priority:** P0

Migration and scaffold operations shall not silently overwrite or delete unrelated source files.

---

