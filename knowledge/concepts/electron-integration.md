---
type: Concept
title: Electron integration
description: Renderer, preload, main-process and Python bridge responsibilities.
status: draft
tags: [electron, protocol, security]
---

The renderer owns presentation and user workflows; it does not discover Python,
spawn processes or parse the backend protocol. A restricted preload exposes
approved operations and subscriptions through IPC. The main process validates
callers, owns the backend process and coordinates startup and shutdown. The
shared bridge handles application-independent communication, not business actions.

The proposed startup sequence resolves and validates the runtime, starts Python,
attaches stream handlers, establishes protocol compatibility and only then marks
the bridge ready. Startup failures, unsupported versions and timeouts are reported;
owned processes need cleanup. A successful handshake is the current proposed
readiness signal, subject to the protocol readiness decision.

Renderer-originated paths and actions are untrusted. Context isolation, disabled
renderer Node integration, approved IPC handlers and scoped event forwarding are
the proposed security baseline. Do not turn renderer strings into shell commands
or expose backend diagnostics without authorization and redaction.

Open decisions include bundled versus frozen Python, multiple runtimes and windows,
bounded restart, artifact access, generated clients and durable-job reconnection.
Restart must not automatically replay operations with unknown outcomes. A job can
survive a UI restart only when an actual durable execution owner exists.

See [Electron requirements](../../docs/requirements/functional-electron-communication-requirements.md),
[security requirements](../../docs/requirements/non-functional-security-requirements.md),
and [CLI protocol](cli-protocol.md).
