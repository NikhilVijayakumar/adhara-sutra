## ADDED Requirements

### Requirement: Managed SQLite connections

The framework SHALL provide a connector that owns a SQLite connection, opens it
during application startup, and closes it during shutdown. (FR-DB-001)

#### Scenario: Application shutdown

- **WHEN** the application stops
- **THEN** the connector closes its connection and rejects further statements

### Requirement: Explicit transactions

The connector SHALL support explicit transaction boundaries with commit on
success and rollback on failure. (FR-DB-002)

#### Scenario: A failing statement

- **WHEN** a statement inside a transaction raises
- **THEN** the connector rolls back every statement in that transaction

#### Scenario: Nested transactions

- **WHEN** a transaction starts inside another transaction
- **THEN** the connector rejects the nested transaction instead of committing partial work

### Requirement: Database configuration

Applications SHALL configure the database location and connection policy through
framework configuration. (FR-DB-003)

#### Scenario: A configured database file

- **WHEN** an application reads its database path from configuration
- **THEN** the connector opens that file and enables foreign-key enforcement

### Requirement: Connection ownership and concurrency policy

The connector SHALL define and enforce connection ownership for the supported
runtime concurrency model. (FR-DB-006)

#### Scenario: Use from another thread

- **WHEN** code uses the connector from a thread other than the one that started it
- **THEN** the connector rejects the statement rather than sharing the connection unsafely
