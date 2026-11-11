---
type: Concept
title: State, jobs and execution ownership
description: Scope, persistence, job lifecycle, and recovery boundaries.
status: draft
tags: [state, jobs, lifecycle]
---

Applications define their own state schemas and values; the framework provides
access, validation, concurrency and optional persistence facilities. Request,
session, process and persistent state have distinct lifetimes. Persistent state
can be restored under its configured policy; expired session state is cleaned up.

Applications define job behavior. The framework provides identifiable job
records, execution, progress, results, supported cancellation, and timeouts.
Proposed states include pending, running, completed, failed, cancelled and
interrupted. An accepted job is not a completed job. Each active execution has
an owner: persisted metadata alone does not mean a job survives its owning
process. Recovery must distinguish interruption from actual durable execution.

State concurrency semantics, the exact job transition table, process termination
rules and durable-worker behavior require design review. See [state requirements](../../docs/requirements/functional-state-management-requirements.md)
and [job requirements](../../docs/requirements/functional-job-management-requirements.md).
