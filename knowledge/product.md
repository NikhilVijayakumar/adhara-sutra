---
type: Product
title: AdharaSutra product and scope
description: Purpose, users, and boundaries of the proposed framework.
status: draft
tags: [product, scope]
---

# Purpose

AdharaSutra is a proposed CLI-first Python application framework for developers
building new applications or incrementally migrating existing ones. It aims to
provide shared runtime, integration, state, lifecycle, and verification facilities.
Electron applications communicate with Python through a common CLI protocol.

# Boundaries

Consuming applications own their business rules and workflows. The framework
must not require Electron, a local HTTP server, or an LLM for its core runtime.
Migration should preserve behavior and data; verification reports should state
what was actually checked rather than imply complete correctness.

Sources: [vision and scope](../docs/raw/vision-and-scope.md),
[README](../README.md), and [requirements](../docs/requirements/README.md).
