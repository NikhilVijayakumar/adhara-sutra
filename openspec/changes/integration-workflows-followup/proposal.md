# Integration workflows and tooling boundary follow-up

## Why

The architecture-integrity review completed its implemented scope and the user
requested closure. Three previously conditional or optional tasks remain open;
transferring them here preserves their scope without claiming they are implemented.
No first consuming integration has yet selected HTTP or Electron.

## Scope and requirement trace

- T16: managed async HTTP for a first integration that uses HTTP. FR-HTTP-001/002/003/006/007 and FR-JOB-005.
- T18: Node-owned backend discovery for a first Electron integration. FR-PKG-004/005/006.
- T08: optional lazy tooling imports after first integration. FR-RUN-004 and NFR-EXT-007.

## Dependencies and open questions

Depends on completed [architecture-integrity work](../architecture-integrity-review/tasks.md).
Select the first integration and determine whether its HTTP or Electron workflow
requires the corresponding task. Existing synchronous HTTP and Python runtime
resolver remain supported. The [implementation handoff](../../../docs/architecture-fix-plan.md)
retains the detailed task interfaces and acceptance checks. No broad release,
security, reliability, or platform qualification is implied by this follow-up.
