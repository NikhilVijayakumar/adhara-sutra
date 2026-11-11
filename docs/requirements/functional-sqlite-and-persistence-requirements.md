<!-- Extracted from ../../docs/raw/functional-requirements.md; proposed, not approved. -->

# 10. SQLite and Persistence Requirements

**Requirement group:** `FR-DB`

### FR-DB-001 — SQLite Connection Management

**Priority:** P0

The framework shall provide managed SQLite connection facilities.

### FR-DB-002 — Transaction Management

**Priority:** P0

The framework shall support explicit transaction boundaries.

### FR-DB-003 — Database Configuration

**Priority:** P0

Applications shall configure database locations and connection policies through framework configuration.

### FR-DB-004 — Schema Migration Infrastructure

**Priority:** P1

The framework shall provide or integrate with a database schema migration mechanism.

Applications remain responsible for their domain schemas.

### FR-DB-005 — Persistence Abstraction

**Priority:** P1

Applications shall be able to implement domain repositories using framework-managed database facilities.

### FR-DB-006 — Database Concurrency Policy

**Priority:** P0

The framework shall define and enforce supported concurrency and connection-ownership semantics.

### FR-DB-007 — Backup and Recovery Support

**Priority:** P1

The framework shall provide facilities or approved procedures for SQLite backup, integrity checking, and recovery.

### FR-DB-008 — Persistent State Support

**Priority:** P1

The state-management subsystem shall be able to use SQLite-backed persistence through a documented adapter.

---

