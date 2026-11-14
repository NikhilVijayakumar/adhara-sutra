## ADDED Requirements

### Requirement: Backend discovery before Python startup

The Node main-process integration SHALL resolve explicit override/bundled backend
paths without requiring Python to already run. Packaged mode SHALL fail explicitly
when configured candidates are unavailable; system-Python fallback SHALL require
explicit development opt-in. Resolution SHALL not invoke a shell. (FR-PKG-004,
FR-PKG-005, FR-PKG-006)

#### Scenario: Bundled backend exists at a path containing spaces

- **WHEN** Node resolves the configured bundled candidate
- **THEN** it returns one executable path for fixed-command bridge construction
- **AND** bridge startup subsequently verifies protocol readiness

#### Scenario: Packaged candidates are missing

- **WHEN** no override/bundled candidate exists and development fallback is disabled
- **THEN** discovery rejects with BRIDGE_BACKEND_NOT_FOUND rather than selecting an unrelated PATH interpreter
