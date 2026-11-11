<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 20. Architecture Discovery Requirements

**Requirement group:** `FR-DISC`

### FR-DISC-001 — Project Inspection

**Priority:** P1

The framework shall analyze existing Python application structures.

### FR-DISC-002 — Entry Point Discovery

**Priority:** P1

The inspection engine shall identify known application and CLI entry points.

### FR-DISC-003 — Module and Dependency Discovery

**Priority:** P1

The engine shall identify Python modules and statically discoverable dependencies.

### FR-DISC-004 — CLI Command Discovery

**Priority:** P1

The engine shall identify supported CLI registration and routing patterns.

### FR-DISC-005 — Electron Integration Discovery

**Priority:** P1

The engine shall inspect Electron process invocation and IPC patterns where supported source files are available.

### FR-DISC-006 — External Integration Discovery

**Priority:** P1

The engine shall identify recognizable HTTP, WebSocket, external CLI, SQLite, and filesystem integration patterns.

### FR-DISC-007 — State and Job Discovery

**Priority:** P1

The engine shall identify known application state and job-execution patterns.

### FR-DISC-008 — Current Implementation Report

**Priority:** P1

The engine shall generate a report explaining the current implementation.

### FR-DISC-009 — Source Evidence

**Priority:** P0

Reported findings shall contain source references where available.

### FR-DISC-010 — Uncertainty Reporting

**Priority:** P0

The engine shall distinguish observed implementation facts from inferred or unverified behavior.

### FR-DISC-011 — Incremental Analysis

**Priority:** P2

The engine should support updating reports after relevant source files change without unnecessarily reanalyzing unrelated files.

---

