<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 15. Migration Safety Requirements

**Requirement group:** `NFR-MIG`

## NFR-MIG-001 — Business Behavior Preservation

**Priority:** P0

Migration shall prioritize preservation of existing business behavior.

## NFR-MIG-002 — Non-Destructive Analysis

**Priority:** P0

Architecture inspection and migration planning shall not modify application source files or persistent data.

## NFR-MIG-003 — Reviewable Transformations

**Priority:** P0

Automated migration changes shall produce inspectable diffs.

## NFR-MIG-004 — Data Integrity

**Priority:** P0

Migration operations affecting persistent data shall use appropriate integrity, backup, and recovery controls.

## NFR-MIG-005 — Incremental Migration

**Priority:** P1

Migration shall support independently verifiable implementation units.

## NFR-MIG-006 — Rollback Readiness

**Priority:** P1

Migration steps shall document whether they are reversible and identify relevant recovery procedures.

## NFR-MIG-007 — Source Revision Awareness

**Priority:** P0

Migration tools shall detect when the source analyzed for a proposed change no longer matches the current working tree.

## NFR-MIG-008 — Agent Report Accuracy

**Priority:** P0

Generated reports shall distinguish:

- Observed facts.
- Confirmed violations.
- Inferences.
- Recommendations.
- Unverified assumptions.

## NFR-MIG-009 — Migration Completion Evidence

**Priority:** P0

Migration shall not be marked complete solely on the basis of generated code or an LLM assessment.

Required deterministic checks and behavioral tests must pass.

## NFR-MIG-010 — Business Logic Modification Control

**Priority:** P0

Automated migration shall not silently rewrite domain algorithms or business rules.

---

