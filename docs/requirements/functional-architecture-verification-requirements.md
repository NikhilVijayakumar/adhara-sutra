<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 21. Architecture Verification Requirements

**Requirement group:** `FR-ARCH`

### FR-ARCH-001 — Architecture Profiles

**Priority:** P1

The framework shall define versioned architecture profiles.

### FR-ARCH-002 — Rule Catalog

**Priority:** P1

The framework shall provide a catalog of architecture conformance rules.

### FR-ARCH-003 — Project Structure Verification

**Priority:** P1

The verifier shall validate required folders, files, and project metadata.

### FR-ARCH-004 — Dependency Boundary Verification

**Priority:** P1

The verifier shall detect forbidden dependencies and module-layer violations within supported analysis boundaries.

### FR-ARCH-005 — Framework Adoption Verification

**Priority:** P1

The verifier shall detect whether required framework entry points and registered infrastructure conventions are present.

### FR-ARCH-006 — CLI Protocol Verification

**Priority:** P1

The verifier shall evaluate the application's compatibility with required CLI protocol contracts.

### FR-ARCH-007 — Connector Policy Verification

**Priority:** P1

The verifier shall detect supported patterns that bypass required framework connector facilities.

### FR-ARCH-008 — State and Job Verification

**Priority:** P1

The verifier shall evaluate applicable state and job-management requirements using static analysis and executable tests.

### FR-ARCH-009 — Deterministic Results

**Priority:** P0

Deterministically verifiable rules shall produce reproducible results for the same inputs, configuration, and analyzer versions.

### FR-ARCH-010 — Verification Status

**Priority:** P0

The verifier shall distinguish:

- Pass.
- Fail.
- Needs review.
- Not checked.

### FR-ARCH-011 — Machine-Readable Reports

**Priority:** P1

Verification results shall be exportable in a versioned structured format.

### FR-ARCH-012 — Evidence and Remediation

**Priority:** P1

Violations shall provide rule identifiers, evidence, severity, and recommended remediation where possible.

### FR-ARCH-013 — Baseline Support

**Priority:** P1

Existing projects shall be able to track acknowledged violations while blocking newly introduced violations according to policy.

### FR-ARCH-014 — Approved Exceptions

**Priority:** P1

The verifier shall support explicitly documented, scoped, reviewable exceptions.

### FR-ARCH-015 — CI Enforcement

**Priority:** P1

Architecture verification shall support noninteractive execution and meaningful exit statuses.

### FR-ARCH-016 — Optional LLM Review

**Priority:** P2

The framework may support optional advisory architecture analysis using external coding agents or LLM services.

LLM review shall not override deterministic results.

---

