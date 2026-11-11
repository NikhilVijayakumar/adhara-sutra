<!-- Extracted from ../../docs/raw/non-functional-requirements.md; proposed, not approved. -->

# 14. Architecture Verification Quality Requirements

**Requirement group:** `NFR-ARCH`

## NFR-ARCH-001 — Deterministic Verification

**Priority:** P0

Given identical source content, configuration, analyzer versions, and declared environment, deterministic rules shall produce identical results.

## NFR-ARCH-002 — Evidence-Based Findings

**Priority:** P0

Each confirmed violation shall include sufficient evidence to identify the violated rule and relevant implementation location.

## NFR-ARCH-003 — Explicit Verification Coverage

**Priority:** P0

Verification reports shall distinguish executed checks from unsupported or unexecuted checks.

## NFR-ARCH-004 — False Positive Management

**Priority:** P1

The verifier shall support documented exceptions and mechanisms to investigate suspected false positives.

## NFR-ARCH-005 — Stable Rule Identification

**Priority:** P1

Architecture rule identifiers shall remain stable across compatible rule catalog versions.

## NFR-ARCH-006 — Incremental Verification

**Priority:** P2

Where feasible, architecture checks should avoid reprocessing unchanged sources unnecessarily.

## NFR-ARCH-007 — CI Reliability

**Priority:** P1

Noninteractive architecture verification shall produce stable exit statuses and machine-readable reports.

## NFR-ARCH-008 — LLM Independence

**Priority:** P0

Mandatory deterministic architecture checks shall remain executable without an LLM provider or network access.

## NFR-ARCH-009 — Result Transparency

**Priority:** P0

Reports shall not label partially analyzed applications as fully compliant.

## NFR-ARCH-010 — Baseline Integrity

**Priority:** P1

Baseline handling shall not allow new violations to be silently accepted as previously known findings.

---

