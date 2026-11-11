---
type: Concept
title: Architecture verification
description: Proposed evidence-based, deterministic evaluation of applications against versioned architecture profiles.
status: draft
tags: [verification, architecture, rules, profiles]
---

# Verification boundary

The proposed verifier evaluates an application's existing implementation against a selected, versioned architecture profile and its applicable rules, consuming the evidence-backed model discovery produces: discovery describes implementation facts, verification judges them against rules, without duplicating source parsing. The central principle — verdicts come from actual evidence, never from the absence of detected violations; every verdict ties to an explicit rule, a versioned profile and sufficient evidence, or is clearly marked unresolved. Verification is read-only — no source modification, no dependency installation, no application-code execution by default — and needs no LLM inference.

# Architecture profiles

A profile declares identifier, version, architecture style, required modules or layers, applicable rules, prohibited dependencies, required tests and permitted severity overrides, and is proposed as composable across structure, interface capabilities and runtime capabilities (e.g. `ddd` structure plus `electron-cli` interface and `process`/`sqlite` capabilities). Initial profiles: `minimal`, `cli`, `ddd`, `electron-cli`, `ai-worker`. Applicability is profile-scoped — a minimal application must not fail for lacking unused DDD layers; an app without jobs gets no job-specific failures. Scaffolding and verification share versioned profile contracts; templates declare compatible profile versions so generated projects never silently claim compliance they were not designed to satisfy.

# Rule model

Each rule carries a stable identifier, definition version, title, description, category, severity, applicability, evidence requirements, a deterministic evaluation method, remediation, exception policy and enforcement setting; a stable ID is never repurposed, and material interpretation changes require a version bump. Proposed categories: structure, dependency, runtime, CLI, Electron, connector, state, job, configuration, security, testing, packaging, documentation. Cross-cutting rules — framework runtime adoption, public contract compatibility, unsafe arbitrary command execution, bootstrap correctness — apply to every profile; others apply only when their capability is enabled. Common checks use declarative operators; complex patterns may need trusted custom evaluators. Severity (critical, high, medium, low, informational) is separate from verdict — a critical rule may be NOT_CHECKED. Rules live in a versioned catalog with a draft/active/deprecated/retired lifecycle; drafts never silently become blocking.

# Evaluation pipeline and verdicts

Verification loads the architecture model, resolves the profile and applicable rules, validates rule dependencies, evaluates evidence coverage, executes deterministic evaluators, resolves exceptions, compares the migration baseline and aggregates results; independent rules may run concurrently while dependent ones wait for prerequisite findings. Each applicable rule yields exactly one canonical verdict:

- `PASS` — available evidence satisfies the rule's proof requirements within the analyzed scope
- `FAIL` — evidence establishes a violation, with finding and supporting evidence identified
- `NEEDS_REVIEW` — evidence relevant but ambiguous or conflicting (dynamic IPC channels, reflection imports, unclear ownership)
- `NOT_CHECKED` — not evaluated (missing parser, unexecuted test runner, failed detector, out-of-scope source)

Nonapplicable rules are recorded as `not_applicable` metadata — never a fifth verdict — and must not inflate PASS counts; invalid inputs never silently produce success. Before a rule passes, coverage must meet its declared proof requirements: unanalyzed required source yields NEEDS_REVIEW or NOT_CHECKED, never PASS, while a clear observed violation may still FAIL with incomplete coverage reported, scoped narrowly so an unparseable documentation utility does not invalidate a fully analyzed domain package. Trusted test evidence (unit, integration, protocol-contract, Electron, lifecycle, persistence, security) must record identifier, runner, timestamp, source revision, environment and result; stale results prove nothing, and behavioral rules without executed compatible tests report NOT_CHECKED.

# Exceptions and baselines

Exceptions are explicit and reviewable — rule ID and version range, affected scope, justification, owner, approval reference, creation date, expiry policy — with the engine rejecting unknown rules, invalid scopes, expired records, missing approvals and attempts to waive nonwaivable constraints. An approved exception never rewrites FAIL into PASS: the raw verdict is preserved and the enforcement effect recorded separately. Migration baselines permit controlled progress toward compliance without establishing it, recording profile and rule versions, source snapshot, violation fingerprints, severity and source references; new violations are identified independently, resolved ones reported, persistent ones stay visible, and baseline updates are explicit. Fingerprints should survive harmless formatting changes but never silently merge unrelated violations or treat a new violation as baseline debt because the rule ID matches; nonwaivable security constraints cannot be suppressed by ordinary exceptions or baselines.

# Determinism, enforcement and reporting

Equivalent discovery facts, profile versions, rule versions and configuration produce equivalent canonical verdicts — only timestamps and report metadata differ. VerificationResult — source snapshot, profile and rule versions, summary counts, per-rule verdicts with evidence, exceptions, baseline comparison, coverage, diagnostics — serializes to versioned JSON, Markdown and CLI summaries. Enforcement is separate from verdicts, with proposed modes advisory, standard, strict and migration; aggregate statuses passed/failed/incomplete/error; exit codes 0 passed, 1 failed, 2 invalid invocation, 3 incomplete, 4 discovery failure, 5 internal failure. Findings carry rule identifier, severity, file path, source range, observed and expected relationships, remediation and evidence identifier in repository-relative paths — consumable by any coding agent, with NOT_CHECKED never treated as PASS; explicit CLI profile overrides are reported so results are not mistaken for the declared baseline.

# What static verification does not establish

It does not prove business-logic correctness, runtime behavior from static inspection alone or application startup, and does not replace unit or integration tests, a dedicated security scanner, or formatting and linting tools; it cannot guarantee detecting every vulnerability. It must not execute project code by default, automatically rewrite violating source (repair is a separate, explicitly authorized operation), automatically approve exceptions or waive security requirements, infer every dynamic dependency, or assume compliance because a scan completed. It requires no running Electron application, no external AI service, and never silently assumes unresolved dynamic imports or computed IPC channels are harmless.

# Alternatives considered

Proposed: shared discovery model as foundation, declarative rules with trusted evaluators for complex checks, stable versioned IDs, composable profiles, four verdicts with separate applicability metadata, mandatory evidence, never-automatic PASS on missing evidence, read-only static default, explicit runtime-test evidence, reviewable exceptions, visible baselines with independent new-violation detection, nonwaivable security constraints, four enforcement modes, Markdown and JSON reports with deterministic exit codes, agent-readable findings, no LLM dependency, evidence-aware caching reusing discovery facts. Deferred: automated repair as a separate subsystem, incremental rule-result caching until correctness is established, SARIF output, cross-repository dependency verification, violation trend analytics.

# Open questions

- AV-OQ-001 — Should the rule engine support a declarative YAML format, Python rule classes, or both?
- AV-OQ-002 — Should profiles be stored in the same package as scaffolding templates?
- AV-OQ-003 — Should `adhara verify` execute tests by default?
- AV-OQ-004 — Should migration baselines be committed to the application repository?
- AV-OQ-005 — How should exception approval authority be verified?
- AV-OQ-006 — Which rules should be nonwaivable?
- AV-OQ-007 — Should standard verification fail on high and critical violations?
- AV-OQ-008 — Should unresolved high-severity rules block CI?
- AV-OQ-009 — How stable should baseline fingerprints be across source refactoring?
- AV-OQ-010 — Should rule upgrades automatically invalidate existing baselines?
- AV-OQ-011 — Should incremental rule evaluation ship in the first implementation?
- AV-OQ-012 — Should verification reports support SARIF for code-hosting annotations?
- AV-OQ-013 — Should missing project documentation block architecture verification?
- AV-OQ-014 — Should shared packages be verified across multiple repositories?
- AV-OQ-015 — Should custom evaluators run in isolated subprocesses?
- AV-OQ-016 — Should verification track violation trends across commits?

See [architecture verification requirements](../../docs/requirements/functional-architecture-verification-requirements.md), [verification quality requirements](../../docs/requirements/non-functional-architecture-verification-quality-requirements.md), and the [discovery concept](architecture-discovery.md).
