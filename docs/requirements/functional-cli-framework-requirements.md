<!-- Extracted from the original requirement drafts; proposed, not approved. -->

# 5. CLI Framework Requirements

**Requirement group:** `FR-CLI`

AdharaSutra shall own the CLI infrastructure used by consuming applications.

Applications shall not need to independently implement command routing, protocol serialization, or process communication infrastructure.

### FR-CLI-001 — Centralized CLI Routing

**Priority:** P0

The framework shall provide a centralized action and command router.

**Acceptance criteria:**

- Registered actions can be invoked by identifier.
- Unknown actions produce standardized errors.
- Duplicate action registrations are detected.
- Routing does not contain application-specific business logic.

### FR-CLI-002 — Action Registration

**Priority:** P0

Applications shall register action handlers through a documented API.

**Acceptance criteria:**

- Action identifiers are validated.
- Handlers can define input and output schemas.
- Synchronous and asynchronous handlers are supported through documented execution semantics.
- Registered actions can be discovered for diagnostics and documentation.

### FR-CLI-003 — Input Validation

**Priority:** P0

The framework shall validate request envelopes and application-defined payload schemas.

**Acceptance criteria:**

- Invalid protocol envelopes are rejected.
- Invalid business-action payloads produce structured validation errors.
- Validation occurs before the handler executes.
- Validation errors identify the affected fields without exposing sensitive values.

### FR-CLI-004 — Structured Output

**Priority:** P0

The framework shall serialize action results using standardized response envelopes.

**Acceptance criteria:**

- Successful requests produce valid protocol responses.
- Failed requests produce valid error responses whenever communication remains possible.
- Application results are represented as response data.
- Diagnostic logs do not corrupt protocol output.

### FR-CLI-005 — One-Shot CLI Execution

**Priority:** P0

The framework shall support executing a single request through a CLI process.

**Acceptance criteria:**

- The process accepts the request through a documented input mechanism.
- The requested action is dispatched.
- A structured result is returned.
- The process exits with a documented status.

### FR-CLI-006 — Persistent CLI Execution

**Priority:** P0

The framework shall support persistent bidirectional communication over a CLI process.

**Acceptance criteria:**

- Multiple requests can be processed within one process lifetime.
- Requests and responses are correlated.
- Events can be emitted during processing.
- Process shutdown and disconnection are handled.
- Shared process resources follow defined lifecycle rules.

### FR-CLI-007 — Standard Exit Codes

**Priority:** P1

The framework shall define consistent process exit-code semantics.

Exit categories shall distinguish:

- Success.
- Input errors.
- Configuration errors.
- Dependency failures.
- Execution failures.
- Timeouts.
- Cancellation.

Exact numeric values will be finalized in the CLI protocol design.

### FR-CLI-008 — CLI Help and Discovery

**Priority:** P1

The framework shall support discovering registered commands and their usage.

**Acceptance criteria:**

- Users can list available commands.
- Commands expose their documented arguments.
- Invalid invocations provide meaningful guidance.
- Machine-readable action metadata can be generated.

### FR-CLI-009 — CLI Version Information

**Priority:** P1

Applications shall expose application, framework, and supported protocol versions.

### FR-CLI-010 — Standard Input Support

**Priority:** P1

The framework shall support structured requests and large-input references without requiring all data to be embedded in command-line arguments.

---

