<!-- Extracted from ../../docs/raw/non-functional-requirements.md; proposed, not approved. -->

# 12. Testability Requirements

**Requirement group:** `NFR-TEST`

## NFR-TEST-001 — Deterministic Core Testing

**Priority:** P0

Core framework behavior shall be testable without reliance on external network services.

## NFR-TEST-002 — Mockable Infrastructure

**Priority:** P1

Connectors and application services shall support substitution with test implementations.

## NFR-TEST-003 — Protocol Contract Coverage

**Priority:** P0

All defined protocol message categories shall have executable positive and negative tests.

## NFR-TEST-004 — Lifecycle Test Coverage

**Priority:** P0

Application, connector, process, and job lifecycle transitions shall be covered by automated tests.

## NFR-TEST-005 — Failure Injection

**Priority:** P1

Tests shall be able to simulate:

- External service unavailability.
- Child-process crashes.
- Timeouts.
- Malformed protocol messages.
- Database failures.
- Interrupted jobs.
- Configuration errors.

## NFR-TEST-006 — Code Coverage Targets

**Priority:** P1

**Proposed target:**

- At least 85% line coverage for core framework modules.
- At least 90% branch coverage for protocol validation and error classification modules.

Coverage is supporting evidence and does not replace behavioral testing.

## NFR-TEST-007 — Reproducible Test Environment

**Priority:** P1

Tests shall specify required dependencies, configuration, and external fixtures.

## NFR-TEST-008 — Packaging Tests

**Priority:** P1

Production packaging shall be validated through executable smoke tests on supported platforms.

## NFR-TEST-009 — Migration Regression Evidence

**Priority:** P0

Migration completion shall not be inferred from architecture conformance alone.

Relevant existing application behavior must be independently verified.

---

