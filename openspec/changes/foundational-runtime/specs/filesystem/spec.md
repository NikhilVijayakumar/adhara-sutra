## ADDED Requirements

### Requirement: Standard application directories

The framework SHALL resolve application data, configuration, cache, log, and
temporary directories using platform conventions, and create them on demand.
(FR-FS-001)

#### Scenario: Resolving directories for an application

- **WHEN** directories are resolved for a named application
- **THEN** data, configuration, cache, log, and temporary locations are returned for the current platform, and `ensure()` creates them

#### Scenario: An invalid application name is used

- **WHEN** a name contains path separators or is empty
- **THEN** resolution fails instead of escaping the intended directory

### Requirement: Controlled path access

Framework-managed path resolution SHALL confine access to configured roots and
reject traversal, escaping symbolic links, and sibling-prefix paths.
(FR-FS-002, FR-SEC-005, NFR-SEC-004)

#### Scenario: A path escapes the configured root

- **WHEN** a path resolves outside every configured root
- **THEN** resolution fails with a path violation and no file is created

#### Scenario: A symbolic link points outside the root

- **WHEN** a path traverses a symbolic link whose target is outside the boundary
- **THEN** resolution rejects it using the resolved target

### Requirement: Managed temporary directories

Temporary directories created through the framework SHALL be application-scoped
and removed when their context exits, including on error. (FR-FS-003)

#### Scenario: A temporary directory is released

- **WHEN** a temporary directory context exits successfully or raises
- **THEN** the directory and its contents are removed

### Requirement: Reusable file operations

The framework SHALL provide text and JSON file operations within a configured
path boundary. (FR-FS-004)

#### Scenario: Reading and writing files

- **WHEN** an application writes and reads text or JSON within a boundary
- **THEN** the content is encoded and decoded as UTF-8 by default, and filesystem and JSON errors are reported to the caller

#### Scenario: Writing outside the boundary

- **WHEN** a write resolves outside all configured roots
- **THEN** it fails with a path violation before creating the file
