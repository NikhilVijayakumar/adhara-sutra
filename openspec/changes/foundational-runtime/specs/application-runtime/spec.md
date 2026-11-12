## ADDED Requirements

### Requirement: Application definition

The public API SHALL define an application with a non-empty name and version.
Names SHALL be unique among live application objects in one process; invalid or
duplicate definitions SHALL produce structured errors. (FR-RUN-001)

#### Scenario: Duplicate application name

- **WHEN** an application is defined with the name of another live application in the process
- **THEN** the API rejects the definition with a structured duplicate-name error

#### Scenario: Missing application version

- **WHEN** an application is defined without a non-empty version
- **THEN** the API rejects the definition with a structured error identifying the version field

### Requirement: Application bootstrap

The framework SHALL provide a standard mechanism to define an application and
initialize its services after validating configuration. (FR-RUN-001, FR-RUN-002)

#### Scenario: Invalid configuration

- **WHEN** application configuration is invalid
- **THEN** dependent services do not start and initialization fails with a structured error

#### Scenario: Partial initialization failure

- **WHEN** initialization fails after resources have started
- **THEN** the application does not enter the ready state and initialized resources are cleaned up

### Requirement: Managed lifecycle

The runtime SHALL manage documented lifecycle states and release managed resources
on shutdown. (FR-RUN-003)

#### Scenario: Shutdown

- **WHEN** a running application shuts down
- **THEN** the runtime releases framework-managed resources according to the lifecycle policy

### Requirement: Failure isolation and traceability

Expected handler and connector failures SHALL be contained in structured errors,
SHALL NOT terminate a healthy application, and SHALL remain traceable through
request correlation. Managed resources SHALL be released when the application
stops. (NFR-REL-001, NFR-REL-002, NFR-REL-008, NFR-RES-003)

#### Scenario: A handler fails

- **WHEN** one handler raises an expected exception
- **THEN** the request returns a structured error, the application keeps serving, and other requests succeed

#### Scenario: A request fails

- **WHEN** a handler failure is logged
- **THEN** the diagnostic record carries the request identifier and action, with sensitive values redacted

#### Scenario: The application stops

- **WHEN** an application with started services stops
- **THEN** each managed service is released exactly once

### Requirement: Application extension points

Applications SHALL be able to register business actions and services without
modifying framework source code. (FR-RUN-004, FR-RUN-005)

#### Scenario: Register a business action

- **WHEN** an application registers an action through the public extension point
- **THEN** it can use framework facilities without the framework importing the application's modules directly
