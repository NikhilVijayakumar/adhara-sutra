# Integration workflows follow-up tasks

These tasks were transferred from the closed scope of the architecture-integrity
review; none is complete or waived. Use the exact implementation and acceptance
packets in [the handoff](../../../docs/architecture-fix-plan.md).

- [ ] T16 Implement managed async HTTP request/lifecycle and streaming/cancellation for an HTTP integration; run the async and existing sync checks in the T16 packet.
- [ ] T18 Implement Node-owned backend discovery with explicit packaged/development fallback for an Electron integration; run the resolver and bridge checks in the T18 packet.
- [ ] T08 After first integration, consider lazy tooling imports without changing public names or installed commands; run the fresh-process boundary checks in the T08 packet if selected.

Do not infer the first integration or mark any task complete without its acceptance
evidence. Record an explicit deferral if a selected workflow does not use one of them.
