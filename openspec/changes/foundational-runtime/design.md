# Design: foundational runtime

## Context

The framework is in architecture planning. Requirements are proposed and must be
reviewed against the protocol and runtime source documents before implementation.

## Boundaries

Applications register business handlers through framework extension points;
the framework must not import application-specific business logic. Runtime
initialization validates configuration before starting dependent resources and
cleans up resources if initialization fails. CLI transport validates requests
before dispatch and separates protocol output from diagnostics.

## Open decisions

- Exact lifecycle transition table, cleanup order, and failure reporting.
- Message schemas, protocol version negotiation, correlation and ordering.
- Sync and async execution, concurrency, cancellation, and shutdown semantics.
- Package layout, libraries, public APIs, and compatibility policy.

Do not infer these details from illustrative APIs. Resolve them against the
source requirements and record durable decisions before implementing them.
