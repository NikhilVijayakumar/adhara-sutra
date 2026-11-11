## ADDED Requirements

### Requirement: Reusable testing facilities

The framework SHALL support CLI contract tests and connector test doubles.
(FR-TEST-002, FR-TEST-004)

#### Scenario: Test a connector without the live service

- **WHEN** a test substitutes a connector test double
- **THEN** it can test application interaction without requiring that live service

### Requirement: Packaged runtime support

The desktop integration SHALL support a production runtime without assuming
that an end user's machine has a Python development environment. (FR-PKG-006)

#### Scenario: Launch a packaged application

- **WHEN** a supported packaged application starts on an end-user machine
- **THEN** it can locate its configured production Python backend without a development environment
