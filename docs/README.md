# Documentation Index

Authoritative documentation locations and their maintainers. Framework
maintainers own this index and update each entry when behavior or location
changes.

| Topic | Location | Maintainer |
| --- | --- | --- |
| Overview, capabilities, development workflows | [README](../README.md) | Framework maintainers |
| Architecture rules | [architecture-rules.md](architecture-rules.md) | Architecture maintainers |
| Connectors (HTTP, external CLI, SQLite, filesystem, WebSocket, persistent state) | [connectors.md](connectors.md) | Connector maintainers |
| Migration guidance | [migration.md](migration.md) | Migration maintainers |
| Packaging and runtime discovery | [packaging.md](packaging.md) | Packaging maintainers |
| Architecture decisions | [decisions.md](decisions.md) | Architecture maintainers |
| CLI protocol reference | [protocol-reference.md](protocol-reference.md) | Runtime maintainers |
| Migration status tracking | [migration-status.md](migration-status.md) | Migration maintainers |
| Requirements | [requirements/README.md](requirements/README.md) | Requirements maintainers |
| OpenSpec changes | [../openspec/README.md](../openspec/README.md) | Change authors |

Documentation is validated for required sections and resolvable local links by
`nikhi.adhara_sutra.validate_documentation` (see `tests/test_documentation.py`).
