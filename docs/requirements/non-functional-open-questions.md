<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 27. Open Questions

The following questions require architectural resolution.

### NFR-OQ-001 — Python Runtime Packaging

Should packaged Electron applications primarily bundle a Python runtime, a frozen executable, or support both?

### NFR-OQ-002 — Persistent Process Model

Should the default Electron integration use one persistent Python process per application or favor one-shot execution?

### NFR-OQ-003 — Job Execution Isolation

Should jobs execute in the CLI runtime process, managed child workers, or a configurable combination?

### NFR-OQ-004 — State Persistence

Should SQLite be the default persistent state backend, or remain an explicitly configured optional facility?

### NFR-OQ-005 — Connector Reliability

What retry and health-check policies should be enabled by default for external dependencies?

### NFR-OQ-006 — Architecture Verification Scope

Which checks must be enforced for every application profile, and which checks should be optional?

### NFR-OQ-007 — Migration Automation

Which source transformations are sufficiently safe to perform automatically without agent intervention?

### NFR-OQ-008 — Performance Baseline

What minimum hardware configuration should define the official benchmark reference machine?

### NFR-OQ-009 — Release Compatibility

How long should previously released CLI protocol and public API versions remain supported?

### NFR-OQ-010 — Framework Packaging

Should AdharaSutra begin as one Python distribution with optional extras or as several independently versioned packages?

---

