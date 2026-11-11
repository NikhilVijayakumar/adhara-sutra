<!-- Extracted from ../../docs/raw/functional-requirements.md; proposed, not approved. -->

# 9. External CLI Connector Requirements

**Requirement group:** `FR-EXT`

### FR-EXT-001 — External Executable Invocation

**Priority:** P0

The framework shall support safely executing external CLI programs.

### FR-EXT-002 — Executable Discovery

**Priority:** P0

The framework shall support locating executables through configured paths and approved discovery mechanisms.

### FR-EXT-003 — Argument Management

**Priority:** P0

The framework shall pass structured argument arrays to external processes.

Unsafe shell interpretation must not be required for ordinary execution.

### FR-EXT-004 — Process Output Capture

**Priority:** P0

The framework shall capture stdout, stderr, and exit status.

### FR-EXT-005 — Streaming Output

**Priority:** P0

The framework shall support processing output incrementally while an external process executes.

### FR-EXT-006 — Timeout and Cancellation

**Priority:** P0

The framework shall support timeouts and cancellation policies for external processes.

### FR-EXT-007 — Process Cleanup

**Priority:** P0

The framework shall manage child-process cleanup according to defined platform and ownership policies.

### FR-EXT-008 — Output Parsing Extensions

**Priority:** P1

Applications or integration plugins shall be able to register parsers for external command outputs.

### FR-EXT-009 — External CLI Compatibility

**Priority:** P1

The framework shall support external executables with different argument conventions, exit codes, and output formats without changing the Electron protocol.

### FR-EXT-010 — Interactive External Processes

**Priority:** P2

The framework should support managed interactive or persistent external CLI sessions where necessary.

---

