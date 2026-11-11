<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 6. Availability and Recoverability Requirements

**Requirement group:** `NFR-AVAIL`

## NFR-AVAIL-001 — Startup Readiness

**Priority:** P0

The framework shall expose a readiness state only after required initialization succeeds.

## NFR-AVAIL-002 — Optional Dependency Degradation

**Priority:** P1

Where permitted by application configuration, failure of an optional dependency shall not prevent unrelated application functions from operating.

## NFR-AVAIL-003 — Job Recovery Semantics

**Priority:** P1

Persistent jobs shall have explicit recovery behavior after interruption.

Possible outcomes include:

- Resume.
- Retry.
- Mark as interrupted.
- Require manual intervention.

The framework must not claim durable execution without a persistent execution owner.

## NFR-AVAIL-004 — Persistent Data Recovery

**Priority:** P0

Persistent-state facilities shall preserve database integrity across supported failures.

**Acceptance criteria:**

- Transaction boundaries are respected.
- Incomplete transactions do not appear as committed results.
- Database recovery procedures are documented and tested.

## NFR-AVAIL-005 — Crash Recovery

**Priority:** P1

The framework shall support recovering from unexpected application termination without assuming that in-memory state survived.

## NFR-AVAIL-006 — Recovery Diagnostics

**Priority:** P1

When recovery fails, diagnostic reports shall identify affected resources and available recovery actions.

---

