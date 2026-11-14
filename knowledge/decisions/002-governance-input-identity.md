# Bind governance claims to complete evidence and exact inputs

Status: proposed. Date: 2026-11-13. Decision ID: ADR-002.

## Context

The product makes deterministic verification and safe incremental migration core
capabilities. Current baselines match sampled evidence, while source identity is
only root/revision/dirty. These permit new violations to be acknowledged and changed
sources to be treated as the same analyzed state.

## Decision

Keep complete machine evidence and occurrence counts for exceptions. Capture
analyzed source/configuration bytes in a deterministic manifest. Carry source
fingerprint, analyzer version, and normalized profile identity through results,
plans, and supplied test evidence. Compare a saved plan to current inputs.
Creation, verification, and migration select one supported versioned profile.
Require evaluated mandatory rules and explicit required-test outcomes for completion.

## Alternatives

- Git commit alone: cannot identify dirty or non-Git input changes.
- Whole-directory hashing: report outputs can invalidate their own source identity;
  use the declared analyzed/configuration set instead.
- Display-sample baselines: silently widen exception scope.
- One passed-tests flag: cannot show required behavioral coverage or bind its source.

## Consequences

Legacy reports remain readable but old evidence may be insufficient for strict
completion. Custom analyzer sets need stable identity. These are source-bound
assertions, not signed attestations, whole-program correctness, or proof that all
business behavior is preserved. Profile/analyzer changes deliberately invalidate
old completion evidence.

## References

[Review A10/A11/A13/A14](../../docs/architecture-review-2026-11-13.md),
[OpenSpec requirements](../../openspec/changes/architecture-integrity-review/specs/architecture-integrity/spec.md).
