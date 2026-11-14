# Design: integration workflows follow-up

Status: proposed. Preserve existing runtime ownership and protocol behavior.
T16 introduces a genuinely asynchronous managed HTTP path without implying remote
cancellation. T18 resolves backend candidates in Node before Python starts, with
explicit packaged and development fallback policy. T08 isolates development imports
without removing existing public names. Detailed interfaces and failure policies
remain those in [the implementation handoff](../../../docs/architecture-fix-plan.md).
The selected consuming application and workflow remain open decisions.
