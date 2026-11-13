## ADDED Requirements

### Requirement: Action allowlisting

The router SHALL execute only actions registered with the application and SHALL
report unknown actions without invoking a handler. (FR-SEC-002, NFR-SEC-002)

#### Scenario: An unregistered action is requested

- **WHEN** a request names an action that was not registered
- **THEN** the response is an `ACTION_NOT_FOUND` error listing the available actions and no handler runs

### Requirement: Safe process execution

External command execution SHALL keep the executable and its arguments separate,
SHALL NOT invoke a shell, and SHALL reject a command string or non-string
arguments. (FR-SEC-003, NFR-SEC-001)

#### Scenario: An argument contains shell syntax

- **WHEN** an argument contains shell metacharacters
- **THEN** it is passed to the program verbatim and no shell interprets it

### Requirement: Protect sensitive diagnostics

The framework SHALL protect sensitive values in logs, errors and diagnostics.
`redact` masks sensitive mapping keys, quoted or bare assignments, and
authorization headers; logging and protocol errors apply it before
serialization, and generated reports apply it to findings and evidence.
(FR-SEC-004, FR-SEC-008, NFR-SEC-005, NFR-SEC-011)

#### Scenario: A request fails with credentials in its context

- **WHEN** the failure is reported through diagnostics
- **THEN** credentials are not exposed in the diagnostic output

#### Scenario: A log record or error contains a sensitive assignment

- **WHEN** a log message, exception text, error message, or error detail contains a password, token, secret, or API key
- **THEN** the value is replaced with `[REDACTED]` before serialization

#### Scenario: A framework log record uses the default handler

- **WHEN** the framework logs a message or exception without a structured handler installed
- **THEN** sensitive assignments are redacted before the handler formats the record

#### Scenario: A report contains sensitive evidence

- **WHEN** a generated implementation, verification, or migration report includes evidence with a credential
- **THEN** the credential is redacted in both JSON and Markdown output

### Requirement: Secure configuration and credentials

Applications SHALL be configurable from environment variables and JSON config
files without embedding secrets in source, and connectors SHALL accept
credentials through those mechanisms. (FR-SEC-006, NFR-SEC-006)

#### Scenario: A connector credential comes from the environment

- **WHEN** an application reads a credential from `context.config` supplied by `ADHARA_CONFIG_*` and passes it to a connector
- **THEN** the credential is used without appearing in application source or diagnostics

#### Scenario: Configuration is invalid

- **WHEN** configuration cannot be read or validated
- **THEN** startup fails with a configuration error that does not disclose secret values

### Requirement: Restrict Electron IPC

Electron integration SHALL expose controlled operations through the preload
boundary. The bridge SHALL fix the backend executable and arguments at
construction, spawn without a shell, and accept only action names and payloads
from requests. (FR-SEC-007, NFR-SEC-007, NFR-SEC-008)

#### Scenario: Renderer requests an unexposed operation

- **WHEN** renderer code requests an operation outside the exposed interface
- **THEN** it cannot invoke that operation through the bridge

#### Scenario: A request payload contains a command

- **WHEN** a request payload contains a command string or executable path
- **THEN** it reaches the backend as action data and cannot change the spawned executable or arguments

### Requirement: Standard error model

Framework and application errors SHALL be classified into a standard error
model and serialized through the protocol error envelope. (FR-ERR-001, FR-ERR-002, FR-ERR-004)

#### Scenario: Application handler raises a domain error

- **WHEN** an application handler raises an error during a request
- **THEN** the failure reaches the caller as a structured protocol error with a stable category and no internal traceback by default

#### Scenario: Shutdown fails while another error is propagating

- **WHEN** a request fails and resource cleanup also fails
- **THEN** the original failure propagates and the cleanup failure is reported in diagnostics

#### Scenario: Errors are classified by kind

- **WHEN** an error is returned for a protocol, validation, action, lifecycle, or internal failure
- **THEN** its `category` identifies the failure kind and stays stable for that error code across requests

### Requirement: Application-specific error mapping

Applications SHALL be able to map domain exceptions raised by action handlers
into supported framework error codes with a safe public message. (FR-ERR-006)

#### Scenario: A mapped domain error is raised

- **WHEN** a handler raises an exception with a registered mapping
- **THEN** the response reports the configured code, category, message, and retryability without internal details

#### Scenario: Several mappings could apply

- **WHEN** an exception matches mappings for both its class and a base class
- **THEN** the most specific registered class wins

#### Scenario: Mapping is invalid

- **WHEN** an unsupported code, empty message, duplicate type, or non-exception type is registered
- **THEN** registration fails, and mappings cannot be added after startup

### Requirement: Connector failure diagnostics

Connector failures SHALL expose the connector identity and the stable connector
failure category alongside the message, retryability, and any connector-supplied
details. (NFR-OBS-003)

#### Scenario: A managed connector fails

- **WHEN** an HTTP, external-command, or SQLite connector raises a failure
- **THEN** the protocol error has category `connector` and error details naming the connector (`http`, `external`, or `sqlite`)

#### Scenario: An application connector fails

- **WHEN** an application raises `ConnectorError(..., connector="billing")`
- **THEN** the error details name that connector and keep the application-supplied detail fields

### Requirement: Structured diagnostics with correlation

Logging SHALL be structured, correlated across requests and jobs, and kept
separate from protocol output. (FR-LOG-001, FR-LOG-002, FR-LOG-003, FR-LOG-004, FR-LOG-005)

#### Scenario: Concurrent requests log diagnostics

- **WHEN** two requests are processed concurrently and one logs a diagnostic
- **THEN** each log line identifies the request it belongs to and protocol messages on stdout remain unpolluted

#### Scenario: A handler logs during a request

- **WHEN** an application handler writes a diagnostic through standard logging
- **THEN** the record identifies the request's `request_id` and `action`, and stdout carries only protocol messages

#### Scenario: A diagnostic is logged outside a request

- **WHEN** the runtime logs while no request is active
- **THEN** the record's request correlation fields are empty

#### Scenario: Log verbosity is configured

- **WHEN** the environment sets `ADHARA_LOG_LEVEL` or the application configures a level
- **THEN** records below that level are suppressed and protocol output is unchanged

### Requirement: Runtime diagnostics

The developer command SHALL report framework, interpreter, dependency,
configuration, and readiness diagnostics without exposing configuration values,
and SHALL expose registered capabilities for an optional application target.
(FR-DEV-002, FR-DEV-006, FR-LOG-006, NFR-DX-005, NFR-OPS-003)

#### Scenario: The environment is diagnosed

- **WHEN** `adhara doctor` runs without an application target
- **THEN** it reports the framework and protocol versions, the Python platform, optional connector availability, and configuration-file validity with remediation for failures

#### Scenario: Configuration cannot be read

- **WHEN** `ADHARA_CONFIG_FILE` names a missing or non-object file
- **THEN** the command reports a failed configuration check with remediation and exits nonzero

#### Scenario: Application capabilities are discovered

- **WHEN** `adhara doctor <target>` loads an application
- **THEN** it lists the registered actions, jobs, and services and reports readiness without printing configuration values
