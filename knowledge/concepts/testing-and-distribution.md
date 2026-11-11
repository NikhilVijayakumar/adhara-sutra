---
type: Concept
title: Testing and distribution
description: Verification layers and package boundaries.
status: draft
tags: [testing, packaging, compatibility]
---

Testing combines unit, contract, integration, architecture, migration regression,
security, failure, performance and packaged-application checks. Each result is
evidence for a particular claim; skipped or unavailable checks are not passes.
Core tests should not require real AI services or GPU hardware, while actual
process, platform and database behavior still needs appropriate real fixtures.
Measurements require a defined workload and environment, and proposed thresholds
remain provisional until approved.

The initial proposed distribution is one modular Python package with optional
dependencies and a separate independently versioned Electron bridge. Protocol
versions have their own compatibility contract. Desktop applications own their
packaging and external assets; they cannot assume a development Python installation
exists on end-user machines. Release checks should exercise built artifacts, not
only source trees. Package names, build backend, platform matrix and release
policies remain proposed.

See [testing requirements](../../docs/requirements/functional-testing-infrastructure-requirements.md),
[packaging requirements](../../docs/requirements/functional-packaging-and-distribution-requirements.md),
and [compatibility requirements](../../docs/requirements/non-functional-compatibility-and-versioning-requirements.md).
