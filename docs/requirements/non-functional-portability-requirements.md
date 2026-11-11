<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 9. Portability Requirements

**Requirement group:** `NFR-PORT`

## NFR-PORT-001 — Supported Operating Systems

**Priority:** P1

The framework shall target:

- Windows.
- Linux.
- macOS.

Support levels and tested versions shall be documented.

## NFR-PORT-002 — Cross-Platform Process Management

**Priority:** P0

Process execution, termination, and cleanup shall account for platform-specific behavior.

The framework must not assume Unix process signals exist on Windows.

## NFR-PORT-003 — Cross-Platform Filesystem Behavior

**Priority:** P0

Path handling shall account for platform-specific separators, permissions, symbolic links, and application data directories.

## NFR-PORT-004 — Python Version Compatibility

**Priority:** P1

The framework shall define a supported Python version range.

**Initial proposed baseline:** Python 3.12 and later explicitly tested releases.

Compatibility shall be established by CI testing rather than inferred solely from version numbering.

## NFR-PORT-005 — Electron Compatibility

**Priority:** P1

The TypeScript Electron bridge shall maintain a documented compatibility matrix for supported Electron and Node.js versions.

## NFR-PORT-006 — External Dependency Portability

**Priority:** P1

The framework shall not assume every external CLI or service is available on every supported operating system.

Applications must be able to declare platform-specific requirements.

## NFR-PORT-007 — Packaged Runtime Portability

**Priority:** P1

The framework shall support deployment arrangements where Python is bundled or otherwise supplied as an application dependency.

A separately installed Python development environment shall not be an undocumented requirement.

---

