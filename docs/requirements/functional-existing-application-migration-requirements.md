<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 22. Existing Application Migration Requirements

**Requirement group:** `FR-MIG`

### FR-MIG-001 — Existing Project Migration

**Priority:** P1

AdharaSutra shall support adopting the framework in existing applications.

### FR-MIG-002 — Migration Analysis

**Priority:** P1

Migration analysis shall use discovered implementation information and architecture verification results.

### FR-MIG-003 — Gap Analysis

**Priority:** P1

The migration engine shall identify differences between the existing implementation and target architecture.

### FR-MIG-004 — Migration Strategies

**Priority:** P1

The framework shall support planning migration using:

- Adapter-first adoption.
- Incremental refactoring.
- Controlled rebuild.

### FR-MIG-005 — Migration Plan Generation

**Priority:** P1

The framework shall generate a structured migration plan.

### FR-MIG-006 — Business Behavior Preservation

**Priority:** P0

Migration operations shall not intentionally alter application business behavior unless explicitly authorized.

### FR-MIG-007 — CLI Compatibility Preservation

**Priority:** P0

Migration planning shall account for existing CLI commands and Electron-facing contracts.

### FR-MIG-008 — Persistence Preservation

**Priority:** P0

Migration shall account for existing data, schema compatibility, backups, and recovery.

### FR-MIG-009 — Incremental Migration

**Priority:** P1

Migration shall support independently verifiable migration units.

### FR-MIG-010 — Migration Status Tracking

**Priority:** P1

The framework shall track migration progress against planned tasks and findings.

### FR-MIG-011 — Safe Automated Transformations

**Priority:** P2

The framework may provide deterministic automated transformations for explicitly supported source patterns.

### FR-MIG-012 — Reviewable Changes

**Priority:** P0

Automated transformations shall produce inspectable changes and shall not silently modify unrelated application logic.

### FR-MIG-013 — Migration Verification

**Priority:** P1

Migration completion shall be evaluated through architecture verification and required regression tests.

### FR-MIG-014 — Rollback Planning

**Priority:** P1

Migration plans shall document rollback or recovery strategies appropriate to affected code and data.

### FR-MIG-015 — Migration Completion Report

**Priority:** P1

The framework shall generate a report of completed, deferred, and unresolved migration requirements.

---

