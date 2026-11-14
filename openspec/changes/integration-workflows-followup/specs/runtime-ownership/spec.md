## ADDED Requirements

### Requirement: Nonblocking managed HTTP integration

An optional AsyncHttpClient SHALL provide async lifecycle, requests, and byte
streaming without blocking the runtime control loop. Existing synchronous HTTP
APIs SHALL remain available. Local cancellation SHALL not imply remote job
cancellation. (FR-HTTP-001, FR-HTTP-002, FR-HTTP-003, FR-HTTP-006, FR-HTTP-007, FR-JOB-005)

#### Scenario: HTTP stream is waiting

- **WHEN** an async HTTP stream waits for its next bytes
- **THEN** unrelated short control requests can progress
- **AND** cancellation closes the local stream without promising remote termination
