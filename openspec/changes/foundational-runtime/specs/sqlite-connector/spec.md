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

### Requirement: Schema migrations

The connector SHALL provide a versioned mechanism for application-defined schema
migrations, recording applied versions and applying pending changes atomically.
(FR-DB-004)

#### Scenario: A migration fails

- **WHEN** a pending migration fails
- **THEN** pending schema changes and version records are rolled back

### Requirement: Domain repositories

Applications SHALL be able to implement domain repositories using the managed
SQLite connection and transaction facilities. (FR-DB-005)

#### Scenario: Repository lifecycle

- **WHEN** a repository depends on a managed SQLite service
- **THEN** it can perform domain operations while the application is running and the connection is closed on shutdown

### Requirement: Backup, integrity checking, and recovery

The connector SHALL provide facilities for consistent backups, integrity
checking, and restoring a verified backup. (FR-DB-007, NFR-AVAIL-004)

#### Scenario: Backing up an idle database

- **WHEN** an application backs up a database outside a transaction
- **THEN** it creates a consistent backup at a new path, and an existing destination or an active transaction is rejected

#### Scenario: The database is damaged

- **WHEN** an integrity check reports damage
- **THEN** the application can stop using the database, restore a verified backup, and confirm integrity before resuming

### Requirement: Persistent state adapter

The framework SHALL provide a documented SQLite-backed adapter for persistent
state with separate namespaces and restart-safe values. (FR-DB-008, FR-STATE-006, FR-STATE-008)

#### Scenario: Values survive a restart

- **WHEN** an application stores JSON values through the adapter and restarts against the same database
- **THEN** the values are available again in their namespace

### Requirement: Connection ownership and concurrency policy

The connector SHALL define and enforce connection ownership for the supported
runtime concurrency model. (FR-DB-006)

#### Scenario: Use from another thread

- **WHEN** code uses the connector from a thread other than the one that started it
- **THEN** the connector rejects the statement rather than sharing the connection unsafely
