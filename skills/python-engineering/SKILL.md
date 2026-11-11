---
name: python-engineering
description: Python engineering guidance for AdharaSutra, including types, async lifecycle, protocol boundaries, testing, and packaging. Use when implementing or reviewing Python code.
license: MIT
compatibility: Python 3.12+
metadata:
  author: chitraguptasutra (adapted for AdharaSutra)
---

# Python Engineering

Apply existing project conventions and the applicable architecture contracts. The
architecture in the repository README is proposed; do not treat illustrative
APIs or commands as already implemented. Keep framework mechanisms independent
of consuming applications' business logic.

## Contracts and types

- Type public APIs and use precise types for protocol messages and extension points.
- Validate external input at the boundary; keep error cases explicit and avoid
  returning success-shaped defaults when operations fail.
- Preserve documented compatibility and versioning contracts. Review changes to
  public interfaces for their impact on applications and the Electron bridge.
- Keep domain behavior independent of transport and infrastructure adapters.

## Async and lifecycle

- Use async for operations that await I/O; avoid blocking the event loop.
- Let the entry point own the event loop. Manage tasks and resources explicitly,
  including cancellation, timeouts, shutdown and cleanup.
- Test observable failure and cancellation behavior at the relevant boundary.

## CLI and security

- Keep structured protocol output on stdout and diagnostics on stderr when
  the protocol is active. Follow the applicable versioned message contract.
- Validate untrusted inputs and paths, avoid shell interpolation, protect secrets,
  and apply appropriate process and network timeouts.

## Dependencies, packaging and verification

- Prefer the standard library or established project dependencies when suitable;
  introduce dependencies only when justified and declare direct dependencies.
- Follow the repository's actual package layout and build configuration; do not
  assume proposed packages, tools or commands already exist.
- Run relevant tests and available type, lint and build checks for the change.
  Cover protocol and connector contracts and regression behavior when affected.
- Use the architecture-review, test-driven-development and code-reviewer skills
  when their scope applies.
