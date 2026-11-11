<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 20. Reference Benchmark Environment

Performance targets require a defined reference environment before approval.

The following is a proposed baseline, not a representation of benchmark results.

| Parameter | Proposed baseline |
|---|---|
| Operating system | Windows 11 and Ubuntu LTS |
| Python | Supported Python 3.12 environment |
| CPU | Modern 8-core desktop CPU |
| Memory | 16 GB RAM or more |
| Storage | SSD |
| Electron | Supported stable Electron version |
| Protocol | Local stdin/stdout NDJSON |
| Test payload | 1 KB, 16 KB, and 1 MB JSON |
| External network | Mock local HTTP service |
| External CLI | Controlled test executable |
| Database | Temporary local SQLite database |

Measurements should additionally be performed on representative lower-resource environments to identify inappropriate baseline assumptions.

MacOS validation should be added where macOS is a supported release target.

---

# 21. Proposed Performance Acceptance Matrix

| Metric | Initial proposed target | Measurement |
|---|---|---|
| Warm CLI dispatch p95 | ≤ 20 ms | No-op handler benchmark |
| Warm CLI dispatch p99 | ≤ 50 ms | No-op handler benchmark |
| Framework startup p95 | ≤ 500 ms | Minimal runtime initialization |
| 16 KB protocol processing p95 | ≤ 10 ms | Validation and serialization |
| Persistent CLI throughput | ≥ 1,000 requests/s | Local no-op workload |
| Progress event latency p95 | ≤ 50 ms | In-process emit to bridge receipt |
| HTTP connector overhead | ≤ 10% relative | Controlled HTTPX comparison |
| Minimal runtime overhead | ≤ 40 MiB | Incremental steady-state memory |
| Static analysis of 100k LOC | ≤ 60 seconds | Defined repository fixture |
| Long-running stability | 8-hour endurance test | Repeated actions and lifecycle |
| Core line coverage | ≥ 85% | Automated coverage reports |
| Protocol/error branch coverage | ≥ 90% | Automated coverage reports |

**Important:** All numerical thresholds remain provisional until representative benchmarks establish whether they are realistic, useful, and sufficiently portable.

Unrealistic thresholds should be revised explicitly rather than met by excluding important behavior from benchmarks.

---

# 22. Non-Functional Validation Scenarios

## Scenario NFS-01 — Minimal CLI Performance

**Given** a generated minimal AdharaSutra application,

**When** a no-op action is invoked repeatedly through a persistent process,

**Then** framework dispatch latency shall satisfy the approved benchmark target.

**And** the test shall exclude business-handler execution.

## Scenario NFS-02 — External Service Unavailable

**Given** an application uses a configured HTTP connector,

**When** the external service becomes unavailable,

**Then** the framework shall return a classified error.

**And** unrelated healthy application functionality shall remain available where supported.

## Scenario NFS-03 — External CLI Crash

**Given** a running external CLI process,

**When** the process terminates unexpectedly,

**Then** the framework shall detect the termination.

**And** release managed resources.

**And** report the correct failure state.

## Scenario NFS-04 — Concurrent State Updates

**Given** multiple active requests,

**When** those requests update shared framework-managed state,

**Then** the resulting state shall follow documented concurrency semantics without corruption.

## Scenario NFS-05 — Job Cancellation

**Given** a long-running job,

**When** Electron requests cancellation,

**Then** the framework shall report the actual cancellation outcome.

**And** avoid reporting completion before the operation has reached its terminal state.

## Scenario NFS-06 — Persistent CLI Endurance

**Given** a long-running application,

**When** repeated requests, connector operations, and job executions occur over an extended period,

**Then** the framework shall remain operational within approved resource-growth limits.

## Scenario NFS-07 — Architecture Reproducibility

**Given** identical application source, analyzer configuration, and tool versions,

**When** architecture verification is executed repeatedly,

**THEN** deterministic findings shall remain identical.

## Scenario NFS-08 — Migration Safety

**Given** an existing application with working business functionality,

**When** an infrastructure migration is performed,

**Then** required regression tests shall verify preserved behavior.

**And** the migration shall not be considered complete solely because architecture rules pass.

## Scenario NFS-09 — Protocol Version Mismatch

**Given** incompatible Electron bridge and Python protocol versions,

**When** communication is attempted,

**Then** the incompatibility shall be detected.

**And** the framework shall fail safely rather than silently misinterpreting messages.

## Scenario NFS-10 — Packaged Application Startup

**Given** a production-packaged Electron application,

**When** the application launches on a supported operating system,

**Then** its Python runtime shall be discoverable and executable without relying on an undeclared developer environment.

---

# 23. Quality Gates

## Gate Q1 — Core Runtime Quality

Required evidence:

- Lifecycle tests.
- CLI protocol contract tests.
- Error-handling tests.
- Minimal runtime benchmarks.
- Resource cleanup verification.

## Gate Q2 — Connector Quality

Required evidence:

- HTTP connector tests.
- External CLI process tests.
- SQLite transaction tests.
- Timeout and cancellation tests.
- Connector failure isolation.

## Gate Q3 — Electron Quality

Required evidence:

- Shared bridge contract tests.
- Process startup and shutdown tests.
- Protocol version mismatch tests.
- Event streaming tests.
- Packaged application smoke tests.

## Gate Q4 — State and Job Quality

Required evidence:

- State concurrency tests.
- Persistent-state restoration tests.
- Job lifecycle tests.
- Cancellation tests.
- Recovery-policy tests.

## Gate Q5 — Architecture Verification Quality

Required evidence:

- Reproducible static rule results.
- Stable rule identifiers.
- Evidence-backed findings.
- Baseline integrity tests.
- Verification coverage reporting.

## Gate Q6 — Migration Quality

Required evidence:

- Non-destructive discovery.
- Source revision validation.
- Reviewable migration diffs.
- Data integrity tests.
- Regression tests.
- Migration completion report.

## Gate Q7 — Production Quality

Required evidence:

- Supported-platform builds.
- Release artifact validation.
- Dependency security checks.
- Compatibility matrix.
- Documentation and upgrade instructions.

---

# 24. Requirement Dependencies and Tradeoffs

Certain quality requirements may conflict.

These conflicts must be resolved explicitly during architecture design.

| Tradeoff | Consideration |
|---|---|
| Startup speed vs extensibility | Eager initialization increases startup work |
| Memory vs throughput | Caching and persistent resources consume memory |
| Reliability vs latency | Retries and health checks may increase response time |
| Simplicity vs configurability | Excessive options complicate maintenance |
| Strong isolation vs performance | Process boundaries introduce overhead |
| Strict architecture vs migration flexibility | Legacy applications need controlled exceptions |
| Detailed logging vs security | Diagnostics must avoid exposing sensitive data |
| Persistent jobs vs complexity | Durable execution requires defined worker ownership |
| Cross-platform behavior vs native features | Some process capabilities differ by OS |
| Automated migration vs safety | Complex refactoring requires review and regression evidence |

Architecture decisions must explicitly account for these tradeoffs.

---

# 25. Non-Functional Requirements Summary

| Group | Category | Count |
|---|---|---:|
| NFR-PERF | Performance | 8 |
| NFR-RES | Resource Efficiency | 5 |
| NFR-REL | Reliability | 10 |
| NFR-AVAIL | Availability and Recovery | 6 |
| NFR-SCALE | Scalability and Concurrency | 7 |
| NFR-SEC | Security | 12 |
| NFR-PORT | Portability | 7 |
| NFR-MAINT | Maintainability | 10 |
| NFR-EXT | Extensibility | 7 |
| NFR-TEST | Testability | 9 |
| NFR-COMP | Compatibility and Versioning | 8 |
| NFR-ARCH | Architecture Verification | 10 |
| NFR-MIG | Migration Safety | 10 |
| NFR-DOC | Documentation Quality | 8 |
| NFR-DX | Developer Experience | 8 |
| NFR-OPS | Operations and Packaging | 8 |
| NFR-OBS | Observability | 6 |
| **Total** | **17 requirement groups** | **139** |

These requirements define the intended quality characteristics of the complete framework.

Not every P1 or P2 capability must be implemented in the first software release.

---

# 26. Review and Approval Checklist

Before approving this document:

- [ ] Confirm supported operating systems.
- [ ] Confirm supported Python versions.
- [ ] Establish representative benchmark environments.
- [ ] Validate proposed performance thresholds.
- [ ] Review memory and resource-overhead targets.
- [ ] Define accepted concurrency and cancellation semantics.
- [ ] Verify security requirements cover Electron and external processes.
- [ ] Confirm SQLite durability and recovery expectations.
- [ ] Review protocol and public API compatibility policies.
- [ ] Validate architecture verification reproducibility requirements.
- [ ] Validate migration safety and data preservation policies.
- [ ] Define the required test evidence for each quality gate.
- [ ] Confirm release and maintenance requirements.
- [ ] Record unresolved tradeoffs.
- [ ] Approve the non-functional requirements baseline.

---
