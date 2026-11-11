---
type: Concept
title: Testing strategy
description: Proposed layered, evidence-driven verification spanning the framework, consuming applications, and shared contracts.
status: draft
tags: [testing, quality, verification]
---

# Central principle

Every important framework contract must have executable evidence appropriate to the behavior it promises. Because AdharaSutra owns critical infrastructure shared by many consuming applications, testing must distinguish implementation correctness from architecture conformance, and no single level — unit, contract, integration, end-to-end, or performance — establishes overall quality alone.

# Testing principles

Routine tests use controlled inputs, fixtures, and environment configuration (deterministic core), and tests that were not executed are never reported as passing (honest results). Results identify the tested source snapshot, environment, and relevant requirements (evidence traceability), and evidence must correspond to the source snapshot being evaluated. Other proposed principles:

- Contract-first: public interfaces carry explicit behavioral contracts with matching tests, each behavior tested at the narrowest useful layer.
- Test independence: no dependence on other tests' execution order or side effects.
- Critical boundaries — subprocess termination, SQLite transactions, NDJSON pipe framing — also receive tests against real implementations.
- Error, cancellation, timeout, and recovery paths are tested explicitly; uncertainty stays explicit when final side effects cannot be confirmed.
- Bounded resource usage: no uncontrolled process creation, unbounded queues, persistent temporary files, or excessive memory.
- Development-mode success does not establish packaged runtime correctness; persisted job/state metadata is not conflated with genuine continued execution.
- Testing operates without coding-agent or LLM inference; an agent's claim that tests passed is not equivalent to recorded evidence.

# Testing scope

Four owners split responsibility. Framework tests validate AdharaSutra's own implementation (runtime, CLI protocol, connector contracts, job lifecycle, architecture verifier) and belong to the framework project. Consuming-application tests validate use cases, domain rules, repositories, application-specific adapters, and Electron workflows, owned by applications. Shared contract tests validate the framework/application boundary — action registration, request/response schemas, connector capabilities, state adapters, job handlers, Electron bridge compatibility — with the framework providing reusable test utilities where practical. Development-tooling tests (scaffolding, discovery, verification, migration, reporting) belong to the tooling distribution and must not become mandatory application runtime dependencies.

# Test layers and selection

Proposed levels: unit (isolated logic, every relevant change), contract (public interface compatibility, every relevant change), integration (component interaction, pull request/CI), end-to-end (representative workflows, CI/release), architecture (structural conformance, pull request/CI), plus security, reliability, performance, packaging, and compatibility levels run in CI, scheduled, benchmark, or release pipelines. The test pyramid favors many fast unit and contract tests, fewer integration tests, and focused end-to-end coverage — a cost guideline, not fixed percentages. Selection depends on changed module, public contract impact, architecture profile, supported capability, platform requirements, risk classification, and release stage. Canonical results are `PASS`, `FAIL`, `SKIPPED`, `ERROR`, `NOT_RUN`; a skipped test never becomes an architecture PASS, and architecture rules retain their own verdicts (PASS, FAIL, NEEDS_REVIEW, NOT_CHECKED).

# Test doubles and connector contracts

Stubs, fakes, mocks, spies, and controlled service implementations are used when the behavior under test does not require the real dependency; a mock that returns expected values proves only how consuming code responds to simulated behavior. Real implementations remain mandatory for OS process termination, SQLite transaction guarantees, NDJSON pipe behavior, Electron IPC, and filesystem permissions. Process tests run against controlled executable fixtures with predictable behaviors (`exit_success`, `sleep_process`, `ignore_termination`, `spawn_child` — fixture names, not required filenames), with explicit cleanup of all test-created processes even when assertions fail. SQLite tests use real temporary databases — in-memory for speed, file-backed for durability, locking, backup, and crash recovery.

Every managed connector passes a common contract suite — registration, configuration validation, initialization, readiness semantics, health, technical error mapping, resource ownership, cleanup, repeated close, partial-initialization failure — while capability-specific tests apply only to declared capabilities (SQLite transaction behavior does not apply to an HTTP connector). The framework provides a reusable connector contract-test harness; applications test adapters against fake connector capabilities. HTTP and WebSocket integration uses controlled local server fixtures; live ComfyUI or LM Studio tests remain optional suites never required by routine framework tests.

# Migration regression protection

Migration must preserve required application behavior through executed regression evidence. Characterization and regression tests run before migration where feasible, and the same behavioral contracts are evaluated after changes; differential verification compares old and new implementations where deterministic comparison is possible. Apply tests cover dry run, explicit apply, source drift detection, dirty-worktree protection, partial-failure journaling, and rollback of migration-owned file changes. A migration is verified only when applied changes, required architecture checks, and behavioral checks all pass, and migration tests must not claim source rollback reverses external service calls or committed database operations.

# Failure-path coverage

Proposed failure categories: invalid requests, connector unavailable, network timeout, database locked or corrupt, external-process crash, Python backend crash, Electron disconnect, job-cancellation races, logging sink unavailable, disk full, permission failure, and shutdown timeout. Failure in an optional subsystem must not unnecessarily terminate unrelated capabilities. Recovery is confirmed through observable checks, never assumed from a successful restart, and cleanup is checked for orphaned processes, unclosed connections, temporary-file leaks, and retained subscriptions. Concurrency tests use deterministic scheduling (barriers, controlled events, test hooks) rather than arbitrary sleeps, with controlled repeated stress runs for race-sensitive paths; reproducible failures are not dismissed as test noise.

# Performance and endurance

Performance tests establish whether approved non-functional requirements are satisfied. Draft targets (not verified claims): warm CLI dispatch p95 ≤20 ms / p99 ≤50 ms; framework initialization p95 ≤500 ms excluding interpreter startup; 16 KB protocol message processing p95 ≤10 ms; ≥1,000 lightweight requests/second; event dispatch p95 ≤50 ms; ≤40 MiB incremental memory; 100k-LOC architecture verification ≤60 s. Each benchmark documents hardware, OS, versions, dependencies, workload, sample size, warm-up, measurement method, and resource utilization, and runs in a controlled environment since shared CI runners produce misleading latencies; regressions are compared against approved baselines with variability-appropriate tolerances. A proposed eight-hour endurance test monitors resident memory, threads, file handles, processes, subscriptions, job queue size, connections, and temporary storage under a repeatable representative workload, with leak thresholds established before use as a release gate.

# Cross-platform validation

Windows, Linux, and macOS are the initial targets (Python 3.12 minimum proposed). Not every unit test needs per-OS assertions; platform-dependent contracts and release artifacts receive platform-specific validation. At least one representative packaged desktop application is tested per supported platform, since packaged applications must not depend on developer virtual environments, machine-specific paths, or globally installed tools. Compatibility tests protect public Python APIs, protocol versions, bridge versions, connector interfaces, configuration schemas, rule catalogs, and migration schemas, validated against actual built distributions rather than only source-tree imports, using shared versioned JSON fixtures between Python and TypeScript. If a platform's required tests have not run, the release report must state the limitation.

# Reproducible environments and evidence

Test dependencies, execution settings, and relevant environment characteristics are recorded so equivalent source, dependencies, and configuration yield equivalent deterministic results across coding agents. Evidence records capture run ID, suite, test identifiers, source revision, worktree state, framework version, environment, timestamp, outcome, duration, logs, and coverage references; adapters normalize pytest and TypeScript runner output into a versioned evidence model without claiming more detail than the underlying runner provided. Coverage is evidence of executed paths, not a correctness guarantee; provisional targets are 85% core line and 90% branch coverage for critical protocol and error logic, and quality gates combine coverage with contract and behavior evidence. Proposed tooling: pytest as the Python runner, a TypeScript runner (Vitest candidate), and an Electron-capable test host exercising real main/preload/renderer boundaries — a browser-only renderer test does not prove main-process behavior. The developer CLI (`adhara test`, `adhara verify`) coordinates approved runners rather than reimplementing assertion engines; test execution is side-effecting and requires a trusted environment, and a missing runner reports `NOT_RUN`.

# Alternatives considered

Proposed: pytest as the primary runner; unit/contract/integration/E2E layering; controlled fixtures for routine external dependencies; real controlled executables and temporary databases at real boundaries; an actual Electron test host; shared versioned JSON protocol fixtures; a versioned machine-readable evidence model; measured coverage never the sole acceptance criterion; a dedicated benchmark environment; a Windows/Linux/macOS matrix; `PASS`/`FAIL`/`SKIPPED`/`ERROR`/`NOT_RUN` results with missing evidence never treated as passing; test tooling distributed separately from the minimal production runtime; machine-readable results independent of any coding agent; reuse of established test runners. Explicitly rejected: a proprietary testing platform, cloud testing services, real ComfyUI or LM Studio servers for every test, large AI-model downloads during CI, mandatory GPU hardware, LLM-generated tests, running every expensive integration test on every commit, coverage as proof of correctness, and treating architecture PASS as behavioral correctness.

# Open questions

- TS-OQ-001 — Should pytest be the mandatory framework testing tool? (Recommended: primary internally, public contracts independent of pytest types.)
- TS-OQ-002 — Should pytest-asyncio be a required development dependency, kept out of application runtime?
- TS-OQ-003 — Should the Electron bridge use Vitest or another TypeScript test runner?
- TS-OQ-004 — Should Playwright be the primary Electron E2E framework?
- TS-OQ-005 — Should tests against ComfyUI, LM Studio, or audio.cpp be mandatory? (Recommended: no.)
- TS-OQ-006 — Should CI require NVIDIA or AMD GPUs? (Recommended: no.)
- TS-OQ-007 — Should shared test fixtures ship in the production AdharaSutra package?
- TS-OQ-008 — Custom JSON test-evidence format or an established one? (Recommended: versioned internal schema importing JUnit XML.)
- TS-OQ-009 — Should 85% core and 90% critical-branch coverage become mandatory? (Recommended: provisional.)
- TS-OQ-010 — Should Python and TypeScript share the same protocol fixtures? (Recommended: yes.)
- TS-OQ-011 — Should every pull request run on Windows, Linux, and macOS?
- TS-OQ-012 — Should packaged Electron smoke tests be mandatory for releases? (Recommended: yes, per supported platform.)
- TS-OQ-013 — Should an eight-hour persistent-runtime endurance test become mandatory?
- TS-OQ-014 — How should intermittent concurrency failures be evaluated? (Deterministic fixtures plus repeated stress.)
- TS-OQ-015 — Should the test orchestrator automatically retry failed tests, keeping the original failure visible?
- TS-OQ-016 — Should `adhara verify` run behavioral tests automatically? (Recommended: no, add an explicit test-enabled mode.)
- TS-OQ-017 — Should the Migration Framework auto-generate before/after regression tests, with executed characterization tests still required?
- TS-OQ-018 — What performance regression tolerance should block releases? (Benchmark-specific thresholds, not one global percentage.)
- TS-OQ-019 — How long should CI logs, coverage reports, and test evidence be retained? (Configurable retention.)
- TS-OQ-020 — Should `adhara test` execute tests from any repository automatically? (Trusted environment, explicit invocation only.)
- TS-OQ-021 — Should standardized application testing profiles be defined (minimal, cli, ddd, electron-cli, ai-worker)?
- TS-OQ-022 — Should all quality gates be mandatory for every application? (Recommended: profile- and capability-dependent.)
- TS-OQ-023 — Should test results be reused when source files appear unchanged? (Only with validated caching.)
- TS-OQ-024 — Should AdharaSutra introduce its own failure-injection engine? (Start with fixture utilities.)
- TS-OQ-025 — Should agent-written tests receive special treatment? (Recommended: no, same requirements.)

See [testing infrastructure requirements](../../docs/requirements/functional-testing-infrastructure-requirements.md) and [testability requirements](../../docs/requirements/non-functional-testability-requirements.md).
