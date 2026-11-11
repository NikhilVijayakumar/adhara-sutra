<!-- Extracted from ../../docs/raw/non-functional-requirements.md; proposed, not approved. -->

# 11. Extensibility Requirements

**Requirement group:** `NFR-EXT`

## NFR-EXT-001 — Connector Extensibility

**Priority:** P1

New connector implementations shall be introducible without modifying core runtime behavior.

## NFR-EXT-002 — Application Extension Points

**Priority:** P0

Applications shall register their business capabilities through stable, documented extension mechanisms.

## NFR-EXT-003 — Optional Plugin Isolation

**Priority:** P1

An unavailable optional plugin shall not prevent unrelated functionality from operating unless declared mandatory by the application.

## NFR-EXT-004 — Architecture Profile Extensibility

**Priority:** P1

Additional architecture profiles shall be definable without rewriting the architecture verifier.

## NFR-EXT-005 — Verification Rule Extensibility

**Priority:** P1

New architecture rules shall be registerable through documented extension interfaces.

## NFR-EXT-006 — Migration Analyzer Extensibility

**Priority:** P1

Migration tooling shall support additional analyzers for new project layouts, CLI libraries, and infrastructure patterns.

## NFR-EXT-007 — Backward-Compatible Extension

**Priority:** P1

Adding new optional extension capabilities should not require changes to existing application business handlers.

---

