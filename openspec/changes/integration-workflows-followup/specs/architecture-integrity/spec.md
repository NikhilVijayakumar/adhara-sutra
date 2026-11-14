## ADDED Requirements

### Requirement: Runtime and development-tool import separation

Importing the core Application API or running an application SHALL NOT eagerly
load development-only discovery, migration, verification, scaffolding, or test
helpers. Existing explicit public imports SHALL remain available on demand.
(FR-RUN-004, NFR-EXT-007)

#### Scenario: Packaged application imports only Application

- **WHEN** a fresh process imports Application and starts its runtime entry point
- **THEN** unrelated development tooling modules are not imported
- **AND** explicitly importing an existing tooling export still resolves that public name
