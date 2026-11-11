<!-- Extracted from ../../docs/raw/non-functional-requirements.md; proposed, not approved. -->

# 3. Performance Requirements

**Requirement group:** `NFR-PERF`

AdharaSutra must minimize infrastructure overhead while supporting applications with potentially expensive external workloads.

Performance measurements must isolate the framework from external AI inference, file processing, and third-party execution time.

## NFR-PERF-001 — CLI Dispatch Latency

**Priority:** P1

The framework shall minimize the overhead of validating and dispatching an action.

**Proposed target:**

For an already initialized persistent CLI process:

- p50 framework dispatch overhead: ≤ 5 ms.
- p95 framework dispatch overhead: ≤ 20 ms.
- p99 framework dispatch overhead: ≤ 50 ms.

These measurements exclude business-handler execution and external dependencies.

**Verification:**

Benchmark no-op actions in a warmed process using at least 10,000 requests.

The final target shall be confirmed on a documented reference machine.

## NFR-PERF-002 — CLI Process Startup

**Priority:** P1

The framework shall avoid unnecessary startup overhead.

**Proposed target:**

For a minimal application using no optional integrations:

- p95 time from Python process entry to framework readiness: ≤ 500 ms on the reference machine.

This excludes operating-system process creation and Python interpreter startup unless a separate end-to-end benchmark explicitly includes them.

**Verification:**

Measure startup over at least 100 clean process executions.

## NFR-PERF-003 — Protocol Serialization

**Priority:** P1

JSON request and response serialization shall not introduce disproportionate latency.

**Proposed target:**

- p95 combined validation, serialization, and deserialization overhead: ≤ 10 ms for a 16 KB request/response payload on the reference machine.

**Verification:**

Execute isolated serialization benchmarks with representative schemas.

## NFR-PERF-004 — Persistent CLI Throughput

**Priority:** P1

Persistent CLI execution shall efficiently process repeated requests.

**Proposed target:**

- At least 1,000 lightweight no-op requests per second under a controlled single-client benchmark, excluding business execution.

**Verification:**

Use a warmed persistent CLI process and record throughput, latency, CPU usage, and memory usage.

## NFR-PERF-005 — Progress Event Latency

**Priority:** P1

The framework shall deliver progress events with minimal additional delay.

**Proposed target:**

- p95 event delivery overhead ≤ 50 ms for an uncongested local CLI connection.

**Verification:**

Measure the interval between event publication and Electron bridge receipt.

This measurement excludes delays introduced by external dependencies.

## NFR-PERF-006 — Connector Overhead

**Priority:** P1

Generic connector infrastructure shall avoid significant overhead relative to its underlying transport.

**Proposed target:**

- HTTP connector overhead should remain within 10% of equivalent direct HTTPX execution under controlled local benchmarking.

**Verification:**

Compare identical request workloads using direct HTTPX and the framework connector.

## NFR-PERF-007 — Large Artifact Handling

**Priority:** P0

The framework shall avoid unnecessary duplication of large binary artifacts in memory.

**Acceptance criteria:**

- Large files can be represented through managed file references.
- Binary artifacts are not required to be base64-encoded in CLI protocol messages.
- Streaming operations do not require loading an entire artifact into memory unless explicitly requested.

## NFR-PERF-008 — Optional Component Initialization

**Priority:** P1

Unused optional connectors and integrations shall not be initialized during ordinary startup.

**Verification:**

A minimal application startup test shall confirm that unused connector implementations are not activated.

---

