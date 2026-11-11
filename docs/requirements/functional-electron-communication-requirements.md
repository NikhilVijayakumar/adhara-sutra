<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 6. Electron Communication Requirements

**Requirement group:** `FR-ELC`

The framework shall establish a unified communication contract between Electron and Python.

### FR-ELC-001 — Unified Electron Protocol

**Priority:** P0

Electron applications shall communicate with AdharaSutra applications through one versioned CLI protocol.

**Acceptance criteria:**

- The same request envelope is supported across applications.
- The same response and error envelope structures are supported.
- External integration transport choices do not change the frontend protocol.

### FR-ELC-002 — CLI-Based Communication

**Priority:** P0

Electron-to-Python communication shall use process communication rather than requiring an HTTP server.

Supported communication channels shall include stdin, stdout, and stderr according to the protocol design.

### FR-ELC-003 — Standard Request Envelope

**Priority:** P0

Requests shall support:

- Protocol version.
- Request identifier.
- Action identifier.
- Action payload.

Additional metadata may be supported through versioned optional fields.

### FR-ELC-004 — Standard Response Envelope

**Priority:** P0

Responses shall support:

- Protocol version.
- Request identifier.
- Success or failure.
- Result data.
- Structured error information.

### FR-ELC-005 — Event Streaming

**Priority:** P0

The framework shall support structured events during request execution.

**Acceptance criteria:**

- Events can be correlated with requests or jobs.
- Events follow a documented schema.
- Malformed events are detectable.
- Electron can distinguish events from terminal results.

### FR-ELC-006 — Cancellation

**Priority:** P0

Electron shall be able to request cancellation of supported active operations.

**Acceptance criteria:**

- Cancellation requests identify their target.
- Cancellation produces an explicit outcome.
- Unsupported cancellation is reported.
- Cancellation does not automatically imply that an external dependency successfully stopped.

### FR-ELC-007 — Connection and Process Failure Handling

**Priority:** P0

The framework and Electron bridge shall detect and report unexpected process termination and communication failures.

### FR-ELC-008 — Correlation and Ordering

**Priority:** P0

The protocol shall define request correlation and message-ordering guarantees.

### FR-ELC-009 — Protocol Compatibility

**Priority:** P0

The framework shall identify unsupported protocol versions and prevent unsafe interpretation of incompatible messages.

### FR-ELC-010 — Shared Electron Bridge

**Priority:** P1

AdharaSutra shall provide or specify a reusable TypeScript bridge for Electron applications.

The bridge shall manage:

- Python process startup.
- Request submission.
- Response parsing.
- Event subscriptions.
- Cancellation.
- Timeouts.
- Process lifecycle.
- Error propagation.

### FR-ELC-011 — Electron Security Boundary

**Priority:** P0

The bridge shall ensure that renderer-provided input cannot directly invoke arbitrary system commands through the framework.

---

