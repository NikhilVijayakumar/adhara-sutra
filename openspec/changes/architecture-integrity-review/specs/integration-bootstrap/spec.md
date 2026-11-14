## ADDED Requirements

### Requirement: Executable generated-project startup guidance

Generated projects SHALL document startup commands compatible with their actual
package imports. Standalone file loading SHALL provide remediation when supplied
a package module requiring relative-import context. (FR-SCAF-004, FR-SCAF-007,
FR-SCAF-008)

#### Scenario: Generated CLI project uses relative action imports

- **WHEN** the project is installed and started through its documented module target
- **THEN** its greeting action runs without relative-import failure

#### Scenario: Package module is supplied as a standalone file

- **WHEN** a file target attempts a package-relative import without package context
- **THEN** the loader advises installing the project and using a dotted module target
- **AND** the original import error remains available as the cause
