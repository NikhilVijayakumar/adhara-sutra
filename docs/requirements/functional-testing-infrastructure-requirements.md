<!-- Extracted from ../../docs/raw/functional-requirements.md; proposed, not approved. -->

# 24. Testing Infrastructure Requirements

**Requirement group:** `FR-TEST`

### FR-TEST-001 — Framework Testing Utilities

**Priority:** P1

The framework shall provide reusable testing facilities for applications and framework modules.

### FR-TEST-002 — CLI Contract Tests

**Priority:** P0

The framework shall provide executable tests for the unified CLI protocol.

### FR-TEST-003 — Action Handler Tests

**Priority:** P1

Applications shall be able to test registered action handlers without launching Electron.

### FR-TEST-004 — Connector Test Doubles

**Priority:** P1

The framework shall provide mechanisms for replacing external dependencies during tests.

### FR-TEST-005 — Process Execution Tests

**Priority:** P1

The framework shall support testing external CLI behavior using controlled executable fixtures.

### FR-TEST-006 — State and Job Tests

**Priority:** P1

The framework shall support validating state, concurrency, lifecycle, cancellation, and failure behavior.

### FR-TEST-007 — Architecture Tests

**Priority:** P1

The framework shall support executing applicable architecture checks as automated tests.

### FR-TEST-008 — Migration Regression Tests

**Priority:** P1

Migration plans shall identify behavioral tests needed to preserve existing application functionality.

### FR-TEST-009 — Electron Integration Tests

**Priority:** P1

The shared Electron bridge shall be testable against representative Python runtime fixtures.

---

