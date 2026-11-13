## ADDED Requirements

### Requirement: Reusable testing facilities

The framework SHALL support CLI contract tests, connector test doubles,
controlled executable fixtures, state and job behavior checks, and executable
architecture checks. (FR-TEST-002, FR-TEST-004, FR-TEST-005, FR-TEST-006,
FR-TEST-007)

#### Scenario: Run the shipped protocol contract tests

- **WHEN** an application's test suite subclasses the shipped CLI contract test case and returns its application from `create_application()`
- **THEN** the inherited executable tests check the handshake, help metadata, structured error envelopes, health, and unsupported cancellation against that application

#### Scenario: Test a connector without the live service

- **WHEN** a test substitutes a connector test double
- **THEN** it can test application interaction without requiring that live service

#### Scenario: Test external process behavior

- **WHEN** a test runs `ExternalCommand` against a controlled executable fixture with its own environment and working directory
- **THEN** it can assert the captured exit code and output without depending on the real external program

#### Scenario: Validate state and job behavior

- **WHEN** a test drives the managed job queue through a failing or cancelled operation
- **THEN** the terminal state, error detail, and lifecycle transitions are observable and assertable

#### Scenario: Run architecture checks in a test

- **WHEN** a test evaluates an architecture profile against an inspected fixture project
- **THEN** each catalogued rule reports a deterministic status with evidence, so conformance is checked without the CLI

### Requirement: Packaged runtime support

The desktop integration SHALL support a production runtime without assuming
that an end user's machine has a Python development environment. It SHALL define
backend discovery for supported desktop platforms, configuration and diagnostics
for bundled or separately installed external executables, and documented
compatibility and upgrade guidance. (FR-PKG-005, FR-PKG-006, FR-PKG-007, FR-PKG-009)

#### Scenario: Launch a packaged application

- **WHEN** a supported packaged application starts on an end-user machine
- **THEN** it can locate its configured production Python backend without a development environment

#### Scenario: Diagnose a missing executable

- **WHEN** a configured external executable cannot be resolved
- **THEN** its diagnostic report identifies the executable as not found without starting it

### Requirement: Python distribution and developer command

The framework SHALL install as a versioned Python distribution that provides an
`adhara` developer command. (FR-PKG-001, FR-PKG-002)

#### Scenario: Running an application

- **WHEN** a developer runs `adhara run app.py` or `adhara run package.module`
- **THEN** the command loads the application's `app`, `application`, or `create_app()` and serves the CLI protocol

#### Scenario: An unknown target

- **WHEN** the target cannot be loaded or does not define an application
- **THEN** the command reports the problem and exits with the invalid-invocation code

### Requirement: Optional dependencies

The core distribution SHALL install without connector dependencies, and
connectors SHALL be available through optional extras. (FR-PKG-003)

#### Scenario: Installing the HTTP connector

- **WHEN** an application installs `nikhi-adhara-sutra[http]`
- **THEN** it can use the HTTP connector, and a core-only install reports a clear non-retryable error if the connector is used

### Requirement: Application test client

The framework SHALL provide reusable testing utilities that start an application
and dispatch registered actions without Electron or the CLI transport.
(FR-TEST-001, FR-TEST-003)

#### Scenario: Testing a handler

- **WHEN** a test uses `ApplicationTestClient` to call an action
- **THEN** the handler runs with the real runtime lifecycle and returns its data, and a failure raises an assertion with the protocol error

### Requirement: Version compatibility

Public releases SHALL follow Semantic Versioning, the CLI protocol SHALL carry a
version independent of the application version, and machine-readable reports
SHALL carry their own schema versions. The framework and bridge SHALL advertise
the protocol versions they support and reject incompatible peers. Public API
changes and deprecations SHALL be documented, and supported report schemas SHALL
be readable. (FR-PKG-008, NFR-COMP-001, NFR-COMP-002, NFR-COMP-003,
NFR-COMP-004, NFR-COMP-005, NFR-COMP-006, NFR-COMP-008)

#### Scenario: Discovering compatible versions

- **WHEN** a client calls `system.hello`
- **THEN** the response reports the framework version, the current protocol version, and every supported protocol version, independent of the application version

#### Scenario: Reading a historical report

- **WHEN** a consumer loads a machine-readable report
- **THEN** a supported schema version is accepted and an unsupported version is rejected with an explicit error

#### Scenario: An incompatible bridge backend

- **WHEN** the bridge completes the handshake with a backend that does not list its protocol version
- **THEN** startup fails with `BRIDGE_PROTOCOL_UNSUPPORTED` and no requests are sent
