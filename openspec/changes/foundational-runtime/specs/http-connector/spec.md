## ADDED Requirements

### Requirement: Outbound HTTP requests

The framework SHALL provide a reusable connector for common outbound HTTP
methods. (FR-HTTP-001)

#### Scenario: Calling an upstream API

- **WHEN** a handler uses the HTTP connector to send a request
- **THEN** it receives the response status, headers, body, and final URL

### Requirement: Connection lifecycle

The HTTP connector SHALL initialize its client once, reuse it across requests,
and close it during application shutdown. (FR-HTTP-002)

#### Scenario: Application shutdown

- **WHEN** the application stops
- **THEN** the connector closes its client and releases the connection pool

### Requirement: Timeout policies

The connector SHALL support a client-wide timeout and a per-request override.
(FR-HTTP-003)

#### Scenario: A slow upstream

- **WHEN** a request exceeds its timeout
- **THEN** it fails with a retryable connector error instead of hanging

### Requirement: Response and failure information

The connector SHALL expose status, headers, body, and failure information through
documented interfaces. (FR-HTTP-006)

#### Scenario: An unsuccessful status

- **WHEN** the upstream returns a non-success status
- **THEN** the caller can inspect the response, or raise a connector error whose retryability follows the status

### Requirement: Authentication configuration

The connector SHALL support HTTP Basic credentials and authorization headers
provided by application configuration, without requiring credentials in source
code. (FR-HTTP-005)

#### Scenario: Configured credentials

- **WHEN** an application supplies a username and password or a bearer authorization header
- **THEN** the connector sends the corresponding authorization on requests

### Requirement: Operation outcome uncertainty

Transport failures SHALL distinguish requests that were never sent from those
whose outcome is unknown, so callers do not assume a non-idempotent operation
failed. (NFR-REL-010)

#### Scenario: A request outcome is unknown

- **WHEN** a transport failure occurs after the request may have been sent
- **THEN** the connector error carries `details.outcome: "unknown"`

#### Scenario: A request was never sent

- **WHEN** a connection cannot be established
- **THEN** the connector error carries `details.outcome: "not_sent"`
