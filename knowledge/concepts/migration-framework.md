---
type: Concept
title: Migration framework
description: Proposed evidence-based, incremental, non-destructive approach for moving existing applications onto AdharaSutra.
status: draft
tags: [migration, adoption, safety]
---

# Purpose and central principle

The proposed Migration Framework (developer interface `adhara migrate`) analyzes an existing application, selects a versioned AdharaSutra target profile, plans authorized changes, applies them, and verifies required behavior stays intact. Its central principle: migration changes infrastructure ownership and architectural organization without unnecessarily changing business behavior. Success means the approved target is met AND required existing behavior is demonstrably intact — not merely that architecture verification passes. It serves applications already using parts of AdharaSutra and fully custom legacy ones, and stays development tooling outside packaged runtimes.

# Migration principles

Core: non-destructive by default (planning never modifies source), explicit authorization (source changes require an explicit apply and approvals), behavior preservation (unless separately authorized), and evidence-based planning (recommendations cite discovery evidence and verification rules).

- Incremental adoption per subsystem; adapter-first when it reduces risk.
- Versioned target profile, never invented during transformation.
- Source freshness: plans are not applied blindly after source changes.
- Reviewable changes, bounded scope, no hidden domain rewrites.
- No false success: architecture conformance is not behavioral proof.
- Controlled rollback, evidence preservation, application ownership; no mandatory LLM.

# Entry points, strategies, and scope

A new assessment starts from the repository, a selected target profile, a discovery snapshot, a verification result, and an optional migration baseline; a continuation resumes or revalidates a previous plan without assuming the repository is unchanged. Proposed strategies: adapter-first (wrap existing infrastructure behind compatible boundaries, lowest risk), incremental refactor (replace infrastructure subsystem by subsystem), and rebuild (replace selected layers while retaining approved business contracts, for severely coupled legacy systems). The developer selects the strategy — the framework never auto-chooses a destructive rebuild merely because violations are numerous. Scope spans the whole application down to a module, connector, CLI communication, Electron integration, jobs or state; partial scope must be explicit.

# Pipeline stages

- Source assessment — consume the shared ApplicationArchitecture model; missing coverage and unsupported constructs reduce automation eligibility, never silently ignored.
- Behavioral baseline — regression evidence before modification; missing coverage becomes recorded risk requiring explicit review before high-risk changes.
- Gap analysis — categories: missing capability, competing infrastructure, boundary violation, compatibility, lifecycle, configuration, verification, unresolved; gaps carry evidence, confidence, risk and a suggested strategy; mandatory changes are distinguished from optional modernization.
- Plan generation — records source revision and fingerprints, target profile, strategy, dependency-ordered tasks (class, affected files, preconditions, validation, rollback), approvals and a risk register; approved plans change only via new revisions or recorded amendments.
- Incremental application — previewable, explicitly authorized, journaled.
- Verification — per-task validation against declared postconditions.
- Completion — target conformance plus required behavior within declared scope; applied, verified and complete remain distinct.

# Risk classification and automation boundaries

Transformations are classified T0–T4: advisory (no source changes), deterministic mechanical (configuration keys, approved directories, dependency declarations, verified import mappings — preconditions still checked), contextual (composition-root moves, adapter interfaces — review before apply), behavior-sensitive (asynchronous behavior, cancellation, transaction ownership — never safe merely because an AST rewrite parses), and destructive or externally consequential (deleting tables or persisted data, changing exposed contracts — separate authorization and a recovery plan). Automation eligibility also weighs evidence completeness, preconditions, rule compatibility, behavioral risk, existing tests and approval policy; class alone never establishes safety. The deterministic core needs no LLM: transformations are syntax-aware, preserve unrelated formatting, and reject or replan on failed preconditions — unrestricted search-and-replace is prohibited where structure is required. Coding agents may propose changes for transformations that are not safely automatable, still subject to task scope, review, behavioral tests and architecture verification; agent claims never substitute for executable validation results.

# Apply, rollback, and safeguards

Before writing, the apply engine validates approved plan, authorized scope, source freshness, expected file contents, compatibility, prerequisites, destination safety and an available recovery mechanism; source drift stops the apply or forces replanning — user edits and dirty worktrees are never silently overwritten. Changes are staged and journaled (paths, fingerprints, transformation, backup, status); partial application is recorded exactly; rollback restores only migration-owned changes and cannot reverse external side effects (sent requests, completed processes, committed transactions), which need separate compensation. Failed rollbacks are reported, never claimed recovered. Destructive data operations require specific approval naming affected resources; schema migration stays application-owned and separate from connection migration; SQLite backups use a consistent mechanism, never raw copies of an active database; domain entities are never silently rewritten or moved into generic framework state merely for consistency.

# Verification and status tracking

Validation levels — syntax, structural, architecture, contract, unit, integration, end-to-end, packaging — run as declared in the plan; failed required tests prevent verified status, unexecuted tests stay NOT_CHECKED, and evidence must match the post-transformation snapshot. Characterization tests are recommended before modifying uncovered behavior; old and new implementations may be differentially compared on controlled inputs. Task statuses run planned, ready, blocked, approved, applying, applied, validating, verified, failed, rolled_back, needs_review — a task is never verified merely because its patch applied. Applications track migration states from not assessed to target-compliant with verified behavior, distinct from runtime availability; baselines keep existing violations visible, block new ones per enforcement policy, and record resolved ones; completion cannot be declared while mandatory tasks or validation remain. Markdown and JSON reports preserve the applied-versus-verified distinction.

# Alternatives considered

Proposed: read-only planning default, shared discovery and verification reuse (no competing analyzer), versioned target profiles, T0–T4 classification, explicit apply with freshness validation, acyclic task dependency graphs, reviewable diffs, syntax-aware editing, operation-scoped rollback, adapter-first preference, optional agent assistance, no LLM dependency, tooling excluded from production runtime. Rejected or out of scope: fully automatic migration of arbitrary applications, automatic plan approval, mandatory Git or LLM, unrestricted repository rewriting, guaranteed preservation of untested behavior, distributed multi-repository orchestration.

# Open questions

- MIG-OQ-001 — Which transformations should be implemented first?
- MIG-OQ-002 — Should Python modifications use LibCST or another source-preserving library?
- MIG-OQ-003 — Should Electron migration use the TypeScript compiler API or another structural transformation library?
- MIG-OQ-004 — Should migration plans be stored inside the application repository?
- MIG-OQ-005 — Should developers apply whole plans or individual tasks?
- MIG-OQ-006 — Should Git be mandatory for migration?
- MIG-OQ-007 — Should failed validation automatically revert changes?
- MIG-OQ-008 — Should migration tooling automatically generate characterization tests?
- MIG-OQ-009 — Should the same migration engine manage AdharaSutra version upgrades?
- MIG-OQ-010 — Should schema migration execution be part of this tool?
- MIG-OQ-011 — Should agent-assisted migrations be invoked directly through the developer CLI?
- MIG-OQ-012 — Should a migration plan impose maximum files or lines modified per task?
- MIG-OQ-013 — Should the framework allow completion with outstanding low-severity findings?
- MIG-OQ-014 — Should migration automatically install Python packages, npm dependencies, or external executables?
- MIG-OQ-015 — Should the framework assign numeric confidence scores to migration transformations?
- MIG-OQ-016 — Should the framework coordinate migration across multiple repositories?

See [migration requirements](../../docs/requirements/functional-existing-application-migration-requirements.md) and [migration safety requirements](../../docs/requirements/non-functional-migration-safety-requirements.md).
