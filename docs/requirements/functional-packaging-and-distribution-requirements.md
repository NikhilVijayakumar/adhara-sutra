<!-- Extracted from ../../docs/raw/functional-requirements.md; proposed, not approved. -->

# 26. Packaging and Distribution Requirements

**Requirement group:** `FR-PKG`

### FR-PKG-001 — Python Package Distribution

**Priority:** P1

The framework shall support installation as a versioned Python distribution.

### FR-PKG-002 — Command-Line Entry Point

**Priority:** P1

The framework shall provide an executable developer command.

Proposed executable: `adhara`.

### FR-PKG-003 — Optional Dependencies

**Priority:** P1

Applications shall be able to install only required connector and integration dependencies.

### FR-PKG-004 — Electron Bridge Distribution

**Priority:** P1

The shared Electron bridge shall be distributable as a versioned TypeScript/JavaScript package.

### FR-PKG-005 — Supported Platform Packaging

**Priority:** P1

The framework shall define packaging and runtime-discovery mechanisms for supported desktop operating systems.

### FR-PKG-006 — Production Runtime Support

**Priority:** P1

Packaged Electron applications shall be able to locate and execute their Python backend without relying on an undeclared development environment.

### FR-PKG-007 — External Executable Packaging

**Priority:** P1

The framework shall support configuration and diagnostics for bundled or separately installed external executables.

### FR-PKG-008 — Version Compatibility

**Priority:** P0

Framework and bridge releases shall identify compatible CLI protocol versions.

### FR-PKG-009 — Upgrade and Migration Guidance

**Priority:** P1

Breaking framework changes shall have documented compatibility and upgrade guidance.

---

