<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 18. Operational and Packaging Requirements

**Requirement group:** `NFR-OPS`

## NFR-OPS-001 — Reproducible Builds

**Priority:** P1

Framework releases shall use documented, reproducible dependency and build configurations.

## NFR-OPS-002 — Production Packaging Validation

**Priority:** P1

The framework shall support validation of packaged applications, not only development environments.

## NFR-OPS-003 — Diagnostic Availability

**Priority:** P1

Production application failures shall produce sufficient diagnostic evidence for troubleshooting without exposing secrets.

## NFR-OPS-004 — Safe Upgrade Behavior

**Priority:** P1

Application upgrades shall account for protocol, schema, configuration, and persistent-state compatibility.

## NFR-OPS-005 — Platform-Specific Dependency Handling

**Priority:** P1

External executable paths and platform-specific dependencies shall be configurable and diagnosable.

## NFR-OPS-006 — Controlled Resource Termination

**Priority:** P0

Application shutdown shall attempt controlled termination and resource cleanup within configurable limits.

## NFR-OPS-007 — Release Artifact Integrity

**Priority:** P1

Release processes shall support verifying artifact integrity and identifying source revisions.

## NFR-OPS-008 — Production Configuration Separation

**Priority:** P1

Development, test, and production configuration shall be distinguishable through documented mechanisms.

---

