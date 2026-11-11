---
type: Concept
title: Configuration and lifecycle
description: Configuration precedence, runtime composition, readiness and cleanup.
status: draft
tags: [configuration, lifecycle, runtime]
---

The framework owns configuration composition; applications define their own
settings and business services. Proposed sources, in increasing precedence, are
framework defaults, application defaults, base file, environment-specific file,
environment variables and explicit runtime or CLI overrides. The default file
format and exact precedence are proposed, not approved. The proposed merge policy
recursively merges mappings where permitted and replaces scalars and lists. An
invalid override must not silently fall back; missing, null and default values
need distinct handling. Diagnostics should identify the source of effective
settings without exposing secrets.

Bootstrap validates configuration, composes dependencies, initializes required
components and evaluates readiness. Initialization follows dependencies; optional
capabilities should not start without need. When startup partially fails, already
started resources are cleaned up in reverse dependency order where applicable.
Cleanup errors must not hide the original failure.

Proposed states are created, configuring, initializing, ready, running, stopping,
stopped and failed. Invalid transitions are rejected. Once shutdown starts, new
work is restricted, active operations follow explicit policies, and managed
resources are released within configured deadlines. Repeated shutdown must not
cause unsafe duplicate cleanup. The precise failure-state representation and
active-work policy remain open.

See [configuration requirements](../../docs/requirements/functional-configuration-requirements.md)
and [runtime requirements](../../docs/requirements/functional-application-runtime-requirements.md).
