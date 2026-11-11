<!-- Extracted from ../../docs/raw/non-functional-requirements.md; proposed, not approved. -->

# 13. Compatibility and Versioning Requirements

**Requirement group:** `NFR-COMP`

## NFR-COMP-001 — Semantic Versioning Policy

**Priority:** P1

Public framework releases shall follow a documented versioning policy.

Semantic Versioning is the proposed approach.

## NFR-COMP-002 — Protocol Versioning

**Priority:** P0

The CLI communication protocol shall have an explicit version independent of the application version.

## NFR-COMP-003 — Schema Versioning

**Priority:** P0

Machine-readable architecture, migration, and implementation report formats shall include schema versions.

## NFR-COMP-004 — Public API Compatibility

**Priority:** P1

Breaking changes to public framework interfaces shall be identified and documented.

## NFR-COMP-005 — Electron Bridge Compatibility

**Priority:** P0

The Electron bridge and Python runtime shall reject unsupported protocol combinations rather than silently misinterpreting messages.

## NFR-COMP-006 — Deprecation Policy

**Priority:** P1

Deprecated public functionality shall have documented replacements and removal conditions.

## NFR-COMP-007 — Migration Compatibility

**Priority:** P1

Migration tooling shall identify compatibility risks associated with framework upgrades and architecture profile changes.

## NFR-COMP-008 — Historical Report Compatibility

**Priority:** P2

The framework should support reading or converting supported older report schemas where practical.

---

