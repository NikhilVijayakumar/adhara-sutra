# Requirement and implementation status

Snapshot: 2026-11-12. Requirements and linked OpenSpec specifications remain proposed; implementation status records the evidence available so far, not architectural approval.

**In progress**: the single active requirement. **New**: no implementation of the requirement has been identified. **Partially implemented**: related code exists, but the requirement or its verification is incomplete; this does not mean it is being actively worked on. **Completed**: the requirement has been implemented and checked against its stated acceptance criteria. Status is per requirement, not per OpenSpec artifact.

The specification column identifies draft specifications that explicitly cite the requirement, including cited ranges. A link does not imply the entire requirement is specified. “Not mapped” means no explicit citation was found; it does not mean the requirement is rejected. Open questions are decisions, not implementation tasks.

Current code: [application runtime and protocol](../../src/nikhi/adhara_sutra/application.py); [jobs](../../src/nikhi/adhara_sutra/jobs.py); [Electron bridge](../../bridge/index.js); [example](../../examples/basic_app.py); [package metadata](../../pyproject.toml). The current persistent protocol is sequential; connector implementations, migration, and verification tooling are not present.

OpenSpec tracks the [foundational-runtime change](../../openspec/changes/foundational-runtime/proposal.md) and its [implementation tasks](../../openspec/changes/foundational-runtime/tasks.md). Four completed OpenSpec planning artifacts describe document readiness, not finished functionality.

## [Application Runtime Requirements](functional-application-runtime-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-RUN-001 | Framework-Based Application Creation | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| FR-RUN-002 | Application Bootstrap | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md), [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-RUN-003 | Application Lifecycle | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md), [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-RUN-004 | Application Extension Points | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| FR-RUN-005 | Application Context | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| FR-RUN-006 | Runtime Execution Modes | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-RUN-007 | Graceful Shutdown | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |

## [Architecture and Migration Reporting Requirements](functional-architecture-and-migration-reporting-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-REP-001 | Implementation Report | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-002 | Verification Report | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-003 | Migration Report | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-004 | Markdown Output | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-005 | JSON Output | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-006 | Report Versioning | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-007 | Source Revision Tracking | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-008 | Finding Traceability | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-009 | Actionable Recommendations | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-REP-010 | Report Refresh | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |

## [Architecture Discovery Requirements](functional-architecture-discovery-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-DISC-001 | Project Inspection | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-002 | Entry Point Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-003 | Module and Dependency Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-004 | CLI Command Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-005 | Electron Integration Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-006 | External Integration Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-007 | State and Job Discovery | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-008 | Current Implementation Report | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-009 | Source Evidence | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-010 | Uncertainty Reporting | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DISC-011 | Incremental Analysis | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |

## [Architecture Verification Requirements](functional-architecture-verification-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-ARCH-001 | Architecture Profiles | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-002 | Rule Catalog | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-003 | Project Structure Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-004 | Dependency Boundary Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-005 | Framework Adoption Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-006 | CLI Protocol Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-007 | Connector Policy Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-008 | State and Job Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-009 | Deterministic Results | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-010 | Verification Status | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-011 | Machine-Readable Reports | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-012 | Evidence and Remediation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-013 | Baseline Support | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-014 | Approved Exceptions | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-015 | CI Enforcement | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-ARCH-016 | Optional LLM Review | Out of Scope | Not mapped — advisory LLM review is the consuming application's responsibility; the library keeps deterministic results only. |

## [CLI Framework Requirements](functional-cli-framework-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-CLI-001 | Centralized CLI Routing | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-002 | Action Registration | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-003 | Input Validation | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-004 | Structured Output | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-005 | One-Shot CLI Execution | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-006 | Persistent CLI Execution | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-007 | Standard Exit Codes | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-008 | CLI Help and Discovery | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-009 | CLI Version Information | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-CLI-010 | Standard Input Support | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |

## [Configuration Requirements](functional-configuration-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-CFG-001 | Central Configuration | Completed | Not mapped |
| FR-CFG-002 | Multiple Configuration Sources | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-CFG-003 | Configuration Validation | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-CFG-004 | Configuration Precedence | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-CFG-005 | Application-Specific Settings | Completed | Not mapped |
| FR-CFG-006 | Secret Handling | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-CFG-007 | Runtime Overrides | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| FR-CFG-008 | Configuration Diagnostics | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |

## [Connector Framework Requirements](functional-connector-framework-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-CON-001 | Connector Registry | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-002 | Connector Lifecycle | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-003 | Connector Configuration | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-004 | Standard Error Mapping | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-005 | Connector Isolation | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-006 | Connector Health Reporting | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-007 | Connector Test Doubles | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| FR-CON-008 | Custom Connector Registration | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |

## [Dependency and Service Management Requirements](functional-dependency-and-service-management-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-DI-001 | Service Registration | Completed | Not mapped |
| FR-DI-002 | Dependency Resolution | Completed | Not mapped |
| FR-DI-003 | Service Lifecycle | Completed | Not mapped |
| FR-DI-004 | Dependency Validation | Completed | Not mapped |
| FR-DI-005 | Test Replacement | Completed | Not mapped |
| FR-DI-006 | Optional Dependencies | Completed | Not mapped |

## [Developer Experience Requirements](functional-developer-experience-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-DEV-001 | Standard Developer Commands | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| FR-DEV-002 | Local Diagnostics | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-DEV-003 | Examples | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| FR-DEV-004 | Documentation Discovery | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| FR-DEV-005 | Agent-Friendly Reports | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| FR-DEV-006 | Framework Capability Discovery | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |

## [Documentation Requirements](functional-documentation-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-DOC-001 | Framework Documentation | New | Not mapped |
| FR-DOC-002 | Application Documentation Templates | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-DOC-003 | Protocol Reference | Completed | [protocol-reference](../protocol-reference.md) |
| FR-DOC-004 | Connector Reference | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| FR-DOC-005 | Architecture Rule Reference | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-DOC-006 | Migration Documentation | New | Not mapped |
| FR-DOC-007 | Documentation Validation | New | Not mapped |

## [Electron Communication Requirements](functional-electron-communication-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-ELC-001 | Unified Electron Protocol | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md), [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-002 | CLI-Based Communication | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md), [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-003 | Standard Request Envelope | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-ELC-004 | Standard Response Envelope | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-ELC-005 | Event Streaming | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md), [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-006 | Cancellation | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-007 | Connection and Process Failure Handling | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-008 | Correlation and Ordering | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-009 | Protocol Compatibility | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md), [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-010 | Shared Electron Bridge | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-ELC-011 | Electron Security Boundary | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |

## [Error Handling Requirements](functional-error-handling-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-ERR-001 | Standard Error Model | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-ERR-002 | Error Classification | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-ERR-003 | Error Propagation | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-ERR-004 | Error Serialization | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-ERR-005 | Sensitive Information Protection | Completed | Not mapped |
| FR-ERR-006 | Application-Specific Error Mapping | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |

## [Existing Application Migration Requirements](functional-existing-application-migration-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-MIG-001 | Existing Project Migration | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-002 | Migration Analysis | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-003 | Gap Analysis | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-004 | Migration Strategies | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-005 | Migration Plan Generation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-006 | Business Behavior Preservation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-007 | CLI Compatibility Preservation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-008 | Persistence Preservation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-009 | Incremental Migration | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-010 | Migration Status Tracking | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-011 | Safe Automated Transformations | Out of Scope | Not mapped — the library analyzes and reviews migrations; applying transformations is left to library users. |
| FR-MIG-012 | Reviewable Changes | Out of Scope | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) — library evaluates/reviews migration; users apply changes themselves (no automated transformation/apply). |
| FR-MIG-013 | Migration Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-014 | Rollback Planning | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| FR-MIG-015 | Migration Completion Report | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |

## [External CLI Connector Requirements](functional-external-cli-connector-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-EXT-001 | External Executable Invocation | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-002 | Executable Discovery | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-003 | Argument Management | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-004 | Process Output Capture | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-005 | Streaming Output | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-006 | Timeout and Cancellation | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-007 | Process Cleanup | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-008 | Output Parsing Extensions | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-009 | External CLI Compatibility | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |
| FR-EXT-010 | Interactive External Processes | Completed | [external-cli-connector](../../openspec/changes/foundational-runtime/specs/external-cli-connector/spec.md) |

## [Filesystem Requirements](functional-filesystem-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-FS-001 | Application Data Directories | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| FR-FS-002 | Path Validation | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| FR-FS-003 | Temporary File Management | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| FR-FS-004 | File Operation Utilities | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| FR-FS-005 | Large Artifact Handling | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |

## [HTTP Connector Requirements](functional-http-connector-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-HTTP-001 | Outbound HTTP Requests | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |
| FR-HTTP-002 | Connection Management | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |
| FR-HTTP-003 | Timeout Policies | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |
| FR-HTTP-004 | Retry Policies | Completed | Not mapped |
| FR-HTTP-005 | Authentication Support | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |
| FR-HTTP-006 | Response Processing | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |
| FR-HTTP-007 | Streaming Support | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |

## [Job Management Requirements](functional-job-management-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-JOB-001 | Job Registration and Execution | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-002 | Job Identifiers | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-003 | Job Lifecycle | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-004 | Progress Reporting | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-005 | Cancellation | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-006 | Timeout Management | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-007 | Concurrency Management | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-008 | Job Results | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-009 | Job Persistence | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-010 | Worker Ownership | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-JOB-011 | Recovery Policy | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |

## [Logging and Diagnostics Requirements](functional-logging-and-diagnostics-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-LOG-001 | Central Logging | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-002 | Structured Logs | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-003 | Request Correlation | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-004 | Log Destination Separation | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-005 | Configurable Log Levels | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-006 | Runtime Diagnostics | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-LOG-007 | Diagnostic Export | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |

## [Packaging and Distribution Requirements](functional-packaging-and-distribution-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-PKG-001 | Python Package Distribution | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-PKG-002 | Command-Line Entry Point | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-PKG-003 | Optional Dependencies | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-PKG-004 | Electron Bridge Distribution | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| FR-PKG-005 | Supported Platform Packaging | New | Not mapped |
| FR-PKG-006 | Production Runtime Support | New | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-PKG-007 | External Executable Packaging | New | Not mapped |
| FR-PKG-008 | Version Compatibility | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-PKG-009 | Upgrade and Migration Guidance | New | Not mapped |

## [Project Scaffolding Requirements](functional-project-scaffolding-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-SCAF-001 | New Project Generation | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-002 | Architecture Profiles | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-003 | Standard Folder Structure | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-004 | Framework Bootstrap Generation | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-005 | Connector Selection | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-006 | Testing Boilerplate | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-007 | Documentation Generation | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-008 | Architecture Verification Readiness | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |
| FR-SCAF-009 | Safe Generation | Completed | [project-scaffolding](../../openspec/changes/foundational-runtime/specs/project-scaffolding/spec.md) |

## [Security-Related Functional Requirements](functional-security-related-functional-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-SEC-001 | Request Validation | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| FR-SEC-002 | Action Allowlisting | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-SEC-003 | Safe Process Execution | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-SEC-004 | Sensitive Data Redaction | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-SEC-005 | Controlled Filesystem Access | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| FR-SEC-006 | Connector Credential Handling | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-SEC-007 | Electron IPC Boundary | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| FR-SEC-008 | Diagnostic Data Protection | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |

## [SQLite and Persistence Requirements](functional-sqlite-and-persistence-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-DB-001 | SQLite Connection Management | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-002 | Transaction Management | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-003 | Database Configuration | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-004 | Schema Migration Infrastructure | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-005 | Persistence Abstraction | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-006 | Database Concurrency Policy | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-007 | Backup and Recovery Support | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |
| FR-DB-008 | Persistent State Support | Completed | [sqlite-connector](../../openspec/changes/foundational-runtime/specs/sqlite-connector/spec.md) |

## [State Management Requirements](functional-state-management-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-STATE-001 | Central State Facilities | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-002 | Application-Defined State | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-003 | State Access | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-004 | State Change Notifications | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-005 | State Scope | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-006 | State Persistence | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-007 | State Concurrency | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-008 | State Restoration | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| FR-STATE-009 | State Cleanup | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |

## [Testing Infrastructure Requirements](functional-testing-infrastructure-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-TEST-001 | Framework Testing Utilities | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-002 | CLI Contract Tests | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-003 | Action Handler Tests | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-004 | Connector Test Doubles | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-005 | Process Execution Tests | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-006 | State and Job Tests | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-007 | Architecture Tests | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| FR-TEST-008 | Migration Regression Tests | New | Not mapped |
| FR-TEST-009 | Electron Integration Tests | New | Not mapped |

## [WebSocket Connector Requirements](functional-websocket-connector-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| FR-WS-001 | WebSocket Client Connections | Completed | [websocket-connector](../../openspec/changes/foundational-runtime/specs/websocket-connector/spec.md) |
| FR-WS-002 | Event Reception | Completed | [websocket-connector](../../openspec/changes/foundational-runtime/specs/websocket-connector/spec.md) |
| FR-WS-003 | Connection Lifecycle | Completed | [websocket-connector](../../openspec/changes/foundational-runtime/specs/websocket-connector/spec.md) |
| FR-WS-004 | Reconnection Policies | Completed | [websocket-connector](../../openspec/changes/foundational-runtime/specs/websocket-connector/spec.md) |
| FR-WS-005 | Message Validation | Completed | [websocket-connector](../../openspec/changes/foundational-runtime/specs/websocket-connector/spec.md) |

## [Architecture Verification Quality Requirements](non-functional-architecture-verification-quality-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-ARCH-001 | Deterministic Verification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-002 | Evidence-Based Findings | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-003 | Explicit Verification Coverage | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-004 | False Positive Management | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-005 | Stable Rule Identification | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-006 | Incremental Verification | New | Not mapped |
| NFR-ARCH-007 | CI Reliability | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-008 | LLM Independence | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-009 | Result Transparency | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-ARCH-010 | Baseline Integrity | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |

## [Availability and Recoverability Requirements](non-functional-availability-and-recoverability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-AVAIL-001 | Startup Readiness | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-AVAIL-002 | Optional Dependency Degradation | New | Not mapped |
| NFR-AVAIL-003 | Job Recovery Semantics | New | Not mapped |
| NFR-AVAIL-004 | Persistent Data Recovery | New | Not mapped |
| NFR-AVAIL-005 | Crash Recovery | New | Not mapped |
| NFR-AVAIL-006 | Recovery Diagnostics | New | Not mapped |

## [Compatibility and Versioning Requirements](non-functional-compatibility-and-versioning-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-COMP-001 | Semantic Versioning Policy | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| NFR-COMP-002 | Protocol Versioning | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| NFR-COMP-003 | Schema Versioning | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| NFR-COMP-004 | Public API Compatibility | New | Not mapped |
| NFR-COMP-005 | Electron Bridge Compatibility | Completed | [testing-and-packaging](../../openspec/changes/foundational-runtime/specs/testing-and-packaging/spec.md) |
| NFR-COMP-006 | Deprecation Policy | New | Not mapped |
| NFR-COMP-007 | Migration Compatibility | New | Not mapped |
| NFR-COMP-008 | Historical Report Compatibility | New | Not mapped |

## [Developer Experience Requirements](non-functional-developer-experience-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-DX-001 | Predictable Project Structure | New | Not mapped |
| NFR-DX-002 | Actionable Error Messages | New | Not mapped |
| NFR-DX-003 | Consistent Command Interface | New | Not mapped |
| NFR-DX-004 | Minimal New-Project Setup | New | Not mapped |
| NFR-DX-005 | Discoverable Capabilities | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-DX-006 | Cross-Agent Accessibility | New | Not mapped |
| NFR-DX-007 | Offline Core Development | New | Not mapped |
| NFR-DX-008 | Clear Framework Boundaries | New | Not mapped |

## [Documentation Quality Requirements](non-functional-documentation-quality-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-DOC-001 | Documentation Completeness | New | Not mapped |
| NFR-DOC-002 | Documentation Consistency | New | Not mapped |
| NFR-DOC-003 | Documentation Traceability | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| NFR-DOC-004 | Machine-Readable Reports | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| NFR-DOC-005 | Source References | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| NFR-DOC-006 | Documentation Freshness | Completed | [developer-experience](../../openspec/changes/foundational-runtime/specs/developer-experience/spec.md) |
| NFR-DOC-007 | Documentation Validation | New | Not mapped |
| NFR-DOC-008 | Documentation Ownership | New | Not mapped |

## [Extensibility Requirements](non-functional-extensibility-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-EXT-001 | Connector Extensibility | New | Not mapped |
| NFR-EXT-002 | Application Extension Points | New | Not mapped |
| NFR-EXT-003 | Optional Plugin Isolation | New | Not mapped |
| NFR-EXT-004 | Architecture Profile Extensibility | New | Not mapped |
| NFR-EXT-005 | Verification Rule Extensibility | New | Not mapped |
| NFR-EXT-006 | Migration Analyzer Extensibility | New | Not mapped |
| NFR-EXT-007 | Backward-Compatible Extension | New | Not mapped |

## [Maintainability Requirements](non-functional-maintainability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-MAINT-001 | Separation of Responsibilities | New | Not mapped |
| NFR-MAINT-002 | Modular Architecture | New | Not mapped |
| NFR-MAINT-003 | Dependency Direction | New | Not mapped |
| NFR-MAINT-004 | Independent Component Testing | New | Not mapped |
| NFR-MAINT-005 | Explicit Public Interfaces | New | Not mapped |
| NFR-MAINT-006 | Controlled Complexity | New | Not mapped |
| NFR-MAINT-007 | Consistent Code Standards | New | Not mapped |
| NFR-MAINT-008 | Dependency Minimization | New | Not mapped |
| NFR-MAINT-009 | Architecture Conformance | New | Not mapped |
| NFR-MAINT-010 | Sustainable Release Maintenance | New | Not mapped |

## [Migration Safety Requirements](non-functional-migration-safety-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-MIG-001 | Business Behavior Preservation | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-002 | Non-Destructive Analysis | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-003 | Reviewable Transformations | Out of Scope | Not mapped — no automated transformations are performed by the library. |
| NFR-MIG-004 | Data Integrity | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-005 | Incremental Migration | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-006 | Rollback Readiness | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-007 | Source Revision Awareness | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-008 | Agent Report Accuracy | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-009 | Migration Completion Evidence | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |
| NFR-MIG-010 | Business Logic Modification Control | Completed | [architecture-governance](../../openspec/changes/foundational-runtime/specs/architecture-governance/spec.md) |

## [Observability Requirements](non-functional-observability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-OBS-001 | Structured Diagnostics | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-OBS-002 | Request and Job Correlation | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-OBS-003 | Connector Diagnostics | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-OBS-004 | Runtime Health | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| NFR-OBS-005 | Diagnostic Isolation | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-OBS-006 | Optional Advanced Telemetry | New | Not mapped |

## [Open Questions](non-functional-open-questions.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-OQ-001 | Python Runtime Packaging | Open question | Not mapped |
| NFR-OQ-002 | Persistent Process Model | Open question | Not mapped |
| NFR-OQ-003 | Job Execution Isolation | Open question | Not mapped |
| NFR-OQ-004 | State Persistence | Open question | Not mapped |
| NFR-OQ-005 | Connector Reliability | Open question | Not mapped |
| NFR-OQ-006 | Architecture Verification Scope | Open question | Not mapped |
| NFR-OQ-007 | Migration Automation | Out of Scope | Not mapped — automated source transformation is not part of this library. |
| NFR-OQ-008 | Performance Baseline | Open question | Not mapped |
| NFR-OQ-009 | Release Compatibility | Open question | Not mapped |
| NFR-OQ-010 | Framework Packaging | Open question | Not mapped |

## [Operational and Packaging Requirements](non-functional-operational-and-packaging-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-OPS-001 | Reproducible Builds | New | Not mapped |
| NFR-OPS-002 | Production Packaging Validation | New | Not mapped |
| NFR-OPS-003 | Diagnostic Availability | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-OPS-004 | Safe Upgrade Behavior | New | Not mapped |
| NFR-OPS-005 | Platform-Specific Dependency Handling | New | Not mapped |
| NFR-OPS-006 | Controlled Resource Termination | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-OPS-007 | Release Artifact Integrity | New | Not mapped |
| NFR-OPS-008 | Production Configuration Separation | New | Not mapped |

## [Performance Requirements](non-functional-performance-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-PERF-001 | CLI Dispatch Latency | New | Not mapped |
| NFR-PERF-002 | CLI Process Startup | New | Not mapped |
| NFR-PERF-003 | Protocol Serialization | New | Not mapped |
| NFR-PERF-004 | Persistent CLI Throughput | New | Not mapped |
| NFR-PERF-005 | Progress Event Latency | New | Not mapped |
| NFR-PERF-006 | Connector Overhead | New | Not mapped |
| NFR-PERF-007 | Large Artifact Handling | New | Not mapped |
| NFR-PERF-008 | Optional Component Initialization | New | Not mapped |

## [Portability Requirements](non-functional-portability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-PORT-001 | Supported Operating Systems | New | Not mapped |
| NFR-PORT-002 | Cross-Platform Process Management | New | Not mapped |
| NFR-PORT-003 | Cross-Platform Filesystem Behavior | New | Not mapped |
| NFR-PORT-004 | Python Version Compatibility | New | Not mapped |
| NFR-PORT-005 | Electron Compatibility | New | Not mapped |
| NFR-PORT-006 | External Dependency Portability | New | Not mapped |
| NFR-PORT-007 | Packaged Runtime Portability | New | Not mapped |

## [Reliability Requirements](non-functional-reliability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-REL-001 | Predictable Execution | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-REL-002 | Failure Isolation | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-REL-003 | Partial Initialization Recovery | Partially implemented | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| NFR-REL-004 | External Dependency Failure Handling | Completed | [connector-framework](../../openspec/changes/foundational-runtime/specs/connector-framework/spec.md) |
| NFR-REL-005 | Process Failure Detection | Completed | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md) |
| NFR-REL-006 | Cancellation Consistency | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-REL-007 | Idempotent Cleanup | Completed | [configuration-lifecycle](../../openspec/changes/foundational-runtime/specs/configuration-lifecycle/spec.md) |
| NFR-REL-008 | Error Traceability | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-REL-009 | Communication Failure Recovery | New | Not mapped |
| NFR-REL-010 | External Operation Uncertainty | Completed | [http-connector](../../openspec/changes/foundational-runtime/specs/http-connector/spec.md) |

## [Resource Efficiency Requirements](non-functional-resource-efficiency-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-RES-001 | Runtime Memory Overhead | New | Not mapped |
| NFR-RES-002 | Bounded Queues | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-RES-003 | Resource Cleanup | Completed | [application-runtime](../../openspec/changes/foundational-runtime/specs/application-runtime/spec.md) |
| NFR-RES-004 | Long-Running Stability | New | Not mapped |
| NFR-RES-005 | Configurable Concurrency Limits | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |

## [Scalability and Concurrency Requirements](non-functional-scalability-and-concurrency-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-SCALE-001 | Concurrent Request Handling | New | Not mapped |
| NFR-SCALE-002 | Concurrency Safety | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-SCALE-003 | Backpressure | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-SCALE-004 | Job Scheduling Limits | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-SCALE-005 | Connector Independence | New | Not mapped |
| NFR-SCALE-006 | Application Isolation | Completed | [state-and-jobs](../../openspec/changes/foundational-runtime/specs/state-and-jobs/spec.md) |
| NFR-SCALE-007 | Large Project Analysis | New | Not mapped |

## [Security Requirements](non-functional-security-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-SEC-001 | Secure Process Execution | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-002 | Action Authorization Boundary | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-003 | Input Validation | Completed | [cli-protocol](../../openspec/changes/foundational-runtime/specs/cli-protocol/spec.md) |
| NFR-SEC-004 | Filesystem Safety | Completed | [filesystem](../../openspec/changes/foundational-runtime/specs/filesystem/spec.md) |
| NFR-SEC-005 | Secret Protection | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-006 | Secure Configuration | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-007 | Electron Process Isolation | Partially implemented | [electron-bridge](../../openspec/changes/foundational-runtime/specs/electron-bridge/spec.md), [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-008 | Controlled IPC Exposure | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-009 | External Network Safety | New | Not mapped |
| NFR-SEC-010 | Dependency Security | New | Not mapped |
| NFR-SEC-011 | Safe Diagnostics | Completed | [security-and-diagnostics](../../openspec/changes/foundational-runtime/specs/security-and-diagnostics/spec.md) |
| NFR-SEC-012 | Unsafe Automated Modification Prevention | Out of Scope | Not mapped — the library never modifies application source; scaffold/analysis operations are non-destructive. |

## [Testability Requirements](non-functional-testability-requirements.md)

| ID | Functionality | Implementation | Draft OpenSpec |
| --- | --- | --- | --- |
| NFR-TEST-001 | Deterministic Core Testing | New | Not mapped |
| NFR-TEST-002 | Mockable Infrastructure | New | Not mapped |
| NFR-TEST-003 | Protocol Contract Coverage | New | Not mapped |
| NFR-TEST-004 | Lifecycle Test Coverage | New | Not mapped |
| NFR-TEST-005 | Failure Injection | New | Not mapped |
| NFR-TEST-006 | Code Coverage Targets | New | Not mapped |
| NFR-TEST-007 | Reproducible Test Environment | New | Not mapped |
| NFR-TEST-008 | Packaging Tests | New | Not mapped |
| NFR-TEST-009 | Migration Regression Evidence | New | Not mapped |
