---
type: Concept
title: Architecture discovery, verification, and migration
description: Evidence-backed governance and controlled adoption of framework conventions.
status: draft
tags: [architecture, discovery, verification, migration]
---

Discovery observes an application's current structure and records source-backed
facts with uncertainty. Verification applies versioned rules and profiles to
available evidence. The proposed verdicts are PASS, FAIL, NEEDS_REVIEW and
NOT_CHECKED; missing evidence must not become PASS. Exceptions and migration
baselines affect enforcement without erasing the underlying finding. Static
verification is read-only and does not establish runtime or business correctness.

Migration compares discovered implementation against a target profile. Planning
is read-only; proposed changes require explicit application, freshness checks,
reviewable diffs, and regression evidence. Applied and verified are distinct
states. Data changes and business-logic modifications need their own explicit
scope and safeguards. Partial migration is supported without assuming that a
partially migrated application already conforms.

Scaffolding generates a new application's foundation using the same profile
concepts. Application-owned files must not be silently overwritten. Generated
code belongs to the consuming application, which retains its business logic.

See the requirements for [discovery](../../docs/requirements/functional-architecture-discovery-requirements.md),
[verification](../../docs/requirements/functional-architecture-verification-requirements.md),
[migration](../../docs/requirements/functional-existing-application-migration-requirements.md),
and [scaffolding](../../docs/requirements/functional-project-scaffolding-requirements.md).
