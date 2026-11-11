# AdharaSutra — Security and Reliability Architecture

**Project:** AdharaSutra (आधारसूत्र)  
**Document:** `docs/design/security-and-reliability.md`  
**Document Version:** 0.1.0  
**Status:** Draft — Architecture Planning  
**Classification:** Cross-Cutting Security, Reliability, and Runtime Infrastructure Architecture  
**Architecture Style:** Defense in Depth, Explicit Trust Boundaries, Failure Isolation, Controlled Recovery  
**Primary Language:** Python 3.12+  
**Additional Runtime:** Electron / TypeScript  
**Target Platforms:** Windows, Linux, macOS

**Related Documents:**

- `docs/design/vision.md`
- `docs/design/functional-requirements.md`
- `docs/design/non-functional-requirements.md`
- `docs/design/system-architecture.md`
- `docs/design/module-architecture.md`
- `docs/design/application-architecture.md`
- `docs/design/cli-protocol.md`
- `docs/design/electron-integration.md`
- `docs/design/connector-framework.md`
- `docs/design/state-management.md`
- `docs/design/job-and-process-management.md`
- `docs/design/configuration-and-lifecycle.md`
- `docs/design/error-handling-and-observability.md`
- `docs/design/project-scaffolding.md`
- `docs/design/architecture-discovery.md`
- `docs/design/architecture-verification.md`
- `docs/design/migration-framework.md`
- `docs/design/testing-strategy.md`

---

# 1. Purpose

This document defines the security and reliability architecture of AdharaSutra.

AdharaSutra provides infrastructure used by multiple independent applications.

Its components may manage:

- Python runtime execution.
- Electron-to-Python communication.
- HTTP and WebSocket connections.
- External executables.
- Local databases.
- Application files and artifacts.
- In-memory and persistent state.
- Background jobs.
- Configuration and credentials.
- Application startup and shutdown.
- Development-time repository analysis.
- Automated source migration.

These capabilities introduce different trust boundaries, failure modes, and resource ownership requirements.

A defect in shared framework infrastructure may affect several consuming applications.

The framework must therefore establish consistent security controls and reliability guarantees while allowing applications to define stricter requirements for their business domains.

## 1.1 Central Principle

**Every privileged operation must have an explicit trust boundary, an authorized execution path, and a defined failure policy.**

**Every managed resource must have an owner, a bounded operating policy, and a verifiable cleanup or recovery strategy.**

Security and reliability are related but distinct:

- **Security** protects against unauthorized access, unsafe execution, data exposure, and malicious inputs.
- **Reliability** ensures predictable behavior during normal execution, faults, shutdown, and recovery.

An application can be reliable while insecure, or secure in its access controls while operationally unreliable.

Both must be addressed independently.

## 1.2 Objectives

The architecture shall:

1. Define framework-wide security principles.
2. Establish trust boundaries.
3. Protect the Electron-to-Python communication path.
4. Prevent unrestricted renderer access to privileged operations.
5. Control external executable invocation.
6. Protect filesystem and artifact access.
7. Provide credential and configuration security.
8. Protect persistent and volatile state.
9. Establish safe connector behavior.
10. Define application isolation assumptions.
11. Support resource exhaustion protection.
12. Establish failure classification and isolation.
13. Support explicit recovery policies.
14. Preserve transaction and durability semantics.
15. Manage process and job termination safely.
16. Define reliable application startup and shutdown.
17. Support secure framework packaging and distribution.
18. Protect development tooling from untrusted repositories.
19. Define auditability and diagnostic safeguards.
20. Establish security and reliability testing requirements.
21. Support architecture verification.
22. Allow consuming applications to adopt stronger policies.

## 1.3 Non-Goals

The initial architecture does not promise:

- Complete isolation of malicious Python code running with the application's own privileges.
- A hardened operating-system sandbox for every subprocess.
- Protection against an already compromised operating system.
- Automatic encryption of all application files.
- A universal authentication system.
- A universal user-account or identity service.
- Distributed high availability.
- Exactly-once execution of arbitrary jobs.
- Automatic recovery from every process crash.
- Guaranteed protection against all supply-chain attacks.
- Automatic prevention of every software vulnerability.
- Formal verification of application security.
- Mandatory cloud monitoring.
- A security compliance certification.

These capabilities may require application-specific infrastructure or future optional framework extensions.

---

# 2. Security and Reliability Principles

## SR-001 — Secure Defaults

Framework configurations shall prefer safe behavior unless an application explicitly selects a different supported policy.

## SR-002 — Least Privilege

Components should receive only the capabilities and access needed to perform their responsibilities.

## SR-003 — Explicit Trust Boundaries

Operations crossing process, IPC, filesystem, network, or persistence boundaries shall have defined validation and authorization policies.

## SR-004 — Defense in Depth

A single validation or security mechanism shall not be treated as sufficient for every risk.

## SR-005 — No Arbitrary Execution

Untrusted inputs shall not directly control executable paths, shell commands, module imports, or privileged runtime operations.

## SR-006 — Data Minimization

The framework shall avoid collecting, persisting, or exposing unnecessary sensitive information.

## SR-007 — Secret Protection

Credentials shall be handled through explicitly supported protected sources and access paths.

## SR-008 — Input Validation

External inputs shall be validated at the relevant boundary before privileged operations.

## SR-009 — Explicit Resource Ownership

Managed processes, connectors, jobs, subscriptions, and storage resources shall have identifiable owners.

## SR-010 — Bounded Resource Usage

Queues, streams, payloads, processes, connections, and retained artifacts shall follow configurable limits.

## SR-011 — Failure Isolation

A recoverable failure in one operation or optional component shall not unnecessarily terminate unrelated healthy operations.

## SR-012 — Truthful Failure Reporting

The framework shall distinguish confirmed success, confirmed failure, interruption, cancellation, timeout, and unknown outcomes.

## SR-013 — Controlled Recovery

Recovery mechanisms shall operate only under documented preconditions and guarantees.

## SR-014 — No Implicit Durability

Persisted metadata shall not be confused with continued execution or successful recovery.

## SR-015 — Safe Cleanup

Managed resources shall follow explicit cleanup and termination policies.

## SR-016 — Version and Compatibility Awareness

Security-sensitive interfaces shall use supported, validated versions and fail safely when incompatible.

## SR-017 — Auditable Operations

Important privileged actions and failure decisions should produce controlled diagnostic evidence.

## SR-018 — No Secret Leakage Through Diagnostics

Sensitive values shall not automatically appear in logs, events, errors, reports, or support exports.

## SR-019 — Development Tooling Isolation

Scaffolding, discovery, verification, and migration tooling shall not become unnecessary production runtime dependencies.

## SR-020 — Evidence-Based Security Claims

Security and reliability claims require appropriate static, contract, integration, or runtime evidence.

---

# 3. Security Scope and Ownership

## 3.1 Framework Responsibilities

AdharaSutra owns common technical controls for:

- CLI protocol validation.
- Framework action routing.
- Runtime capability registration.
- Connector security contracts.
- Process execution safeguards.
- State access mechanisms.
- Job resource limits.
- Framework configuration.
- Lifecycle coordination.
- Safe error serialization.
- Diagnostic redaction.
- Development-tooling execution policies.

## 3.2 Application Responsibilities

Consuming applications own:

- Business authorization rules.
- Domain-specific access policies.
- Business data classification.
- User identity, if required.
- Sensitive domain records.
- Domain-specific retention policies.
- External service credentials.
- Application-specific allowed executables.
- Application-specific network destinations.
- Business operation idempotency.
- Domain recovery policies.

## 3.3 Deployment Responsibilities

The deploying application or operator owns:

- Operating-system permissions.
- Executable signing and distribution.
- Runtime user privileges.
- External network access.
- Application installation paths.
- Credential provisioning.
- Production backups.
- Operating-system patching.
- User-device security.

## 3.4 Shared Responsibility Rule

The framework must make ownership boundaries explicit.

It must not claim application-level protection merely because a lower-level connector validates its input.

---

# 4. High-Level Security Architecture

```text
┌─────────────────────────────────────────────────────┐
│                 ELECTRON RENDERER                   │
│                                                     │
│ Untrusted or Lower-Trust UI Input                   │
│ No Direct Python / OS Process Access                │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   PRELOAD LAYER                     │
│                                                     │
│ Restricted API                                      │
│ Input Validation                                    │
│ Approved IPC Surface                                │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                 ELECTRON MAIN                       │
│                                                     │
│ IPC Authorization                                   │
│ Action Allowlisting                                 │
│ Python Runtime Ownership                            │
│ Process and Session Lifecycle                       │
└─────────────────────────┬───────────────────────────┘
                          │
                   CLI Protocol
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                 ADHARASUTRA RUNTIME                 │
│                                                     │
│  Protocol Validation                                │
│          │                                          │
│          ▼                                          │
│  Action Authorization                               │
│          │                                          │
│          ▼                                          │
│  Application Use Cases                              │
│          │                                          │
│          ▼                                          │
│  Managed Capabilities                               │
│                                                     │
│  ┌──────────┬──────────┬──────────┬──────────────┐  │
│  │ HTTP/WS  │ Process  │ SQLite   │ Filesystem   │  │
│  └──────────┴──────────┴──────────┴──────────────┘  │
│                                                     │
│  State | Jobs | Configuration | Lifecycle           │
│                                                     │
│  Errors | Logging | Diagnostics                     │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  EXTERNAL RESOURCES                 │
│                                                     │
│ Executables / Local Services / Database / Files     │
└─────────────────────────────────────────────────────┘
```

Each boundary must establish appropriate input, access, and failure controls.

---

# 5. Threat Modeling Architecture

## 5.1 Purpose

The framework shall support repeatable identification of security threats across its major components.

## 5.2 Threat Categories

The architecture shall consider:

- Spoofing.
- Tampering.
- Repudiation.
- Information disclosure.
- Denial of service.
- Elevation of privilege.

The STRIDE model may be used as a threat-analysis aid.

## 5.3 Assets to Protect

Important assets include:

- Framework runtime integrity.
- Application business data.
- Local SQLite databases.
- User-generated files.
- Credentials and tokens.
- External process execution privileges.
- Electron IPC authorization.
- Job ownership.
- Application configuration.
- Migration source repositories.
- Diagnostic reports.

## 5.4 Threat Actors and Sources

Potential threats may originate from:

- Malicious or malformed renderer input.
- Compromised renderer content.
- Untrusted external service responses.
- Malicious subprocess output.
- Untrusted files.
- Untrusted repository source.
- Compromised third-party dependencies.
- Other local processes with sufficient privileges.
- Accidental developer misconfiguration.

## 5.5 Threat Model Record

Each material threat should identify:

- Threat ID.
- Affected asset.
- Entry point.
- Trust boundary.
- Preconditions.
- Potential impact.
- Existing controls.
- Residual risk.
- Required tests.
- Responsible owner.

## 5.6 Example

| Threat | Boundary | Primary control |
|---|---|---|
| Renderer requests arbitrary OS command | Renderer → Electron main | Restricted IPC and action allowlisting |
| Malformed protocol message | stdin → Python runtime | Envelope validation and size limits |
| Path traversal | Application input → Filesystem | Validated path resolution and access policy |
| Command argument injection | Action → Process Connector | Structured arguments and controlled executable selection |
| Secret exposure | Config → Logs | Restricted access and redaction |
| Unbounded job submission | Action → Job Manager | Admission control and queue limits |
| Stale migration patch | Repository → Apply Engine | Source fingerprint and precondition validation |

## 5.7 Threat Model Maintenance

Threat models should be reviewed when adding:

- New protocol transports.
- New executable capabilities.
- New filesystem permissions.
- New credential providers.
- New Electron APIs.
- New untrusted input sources.
- New deployment models.

---

# 6. Trust Boundary Model

## 6.1 Primary Boundaries

The framework recognizes these boundaries:

1. Renderer to preload.
2. Preload to Electron main.
3. Electron main to Python runtime.
4. CLI protocol to registered actions.
5. Application use cases to connectors.
6. Python runtime to external executables.
7. Runtime to local filesystem.
8. Runtime to SQLite.
9. Runtime to remote or local HTTP services.
10. Development tooling to inspected repositories.

## 6.2 Boundary Controls

Each boundary should define:

- Trusted initiator.
- Allowed operations.
- Input validation.
- Authorization.
- Resource limits.
- Error handling.
- Audit or diagnostic requirements.

## 6.3 Trust Does Not Automatically Propagate

Authorization at one boundary does not imply authorization at every downstream boundary.

For example, a valid Electron IPC message must still satisfy the relevant application action authorization policy.

## 6.4 Same-User Process Boundary

The standard Electron-to-Python subprocess protocol primarily provides communication structure, not strong security isolation from other malicious code running with the same operating-system user privileges.

The framework must not represent an ordinary child process as a fully isolated sandbox.

---

# 7. Electron Security Architecture

## 7.1 Purpose

Electron may expose privileged operating-system capabilities through its main process.

The renderer must not receive unrestricted access to those privileges.

## 7.2 Security Defaults

Generated Electron integrations should configure:

- Context isolation enabled.
- Renderer Node integration disabled.
- Sandbox enabled where compatible with the application's Electron architecture.
- Restricted preload exports.
- Explicit IPC allowlists.
- Controlled navigation.
- Approved window creation.
- Appropriate content security policy.

Exact settings must be validated against supported Electron versions.

## 7.3 Main Process Ownership

Electron main shall own:

- Python backend process creation.
- Backend lifecycle.
- Runtime path resolution.
- Bridge configuration.
- Privileged IPC handlers.

## 7.4 Renderer Restrictions

The renderer shall not directly:

- Spawn Python.
- Execute arbitrary shell commands.
- Read unrestricted local files.
- Modify backend executable paths.
- Access backend credentials.
- Call unrestricted internal framework actions.

## 7.5 Preload API

Preload shall expose the smallest application-facing API needed by the renderer.

## 7.6 IPC Authorization

Electron main must validate:

- The sending webContents.
- The origin or frame identity where relevant.
- The requested operation.
- The input schema.
- Applicable application permissions.

## 7.7 IPC Allowlists

The bridge may support many Python actions, but individual renderers must only receive access to the actions they are authorized to invoke.

## 7.8 Dynamic Channels

Unrestricted dynamic IPC channel invocation should be prohibited by default.

## 7.9 Event Subscriptions

Event subscriptions must be scoped to authorized renderer contexts.

When a renderer is destroyed, its subscriptions must be cleaned up.

## 7.10 Navigation Security

Unexpected navigation to untrusted origins must not preserve access to privileged preload functionality.

## 7.11 Development Tools

Developer tools and debugging capabilities should follow explicit environment policies.

## 7.12 Application Packaging

Packaged Electron security settings must be tested separately from development mode.

---

# 8. Electron-to-Python Protocol Security

## 8.1 Primary Transport

The default transport is a managed subprocess using stdin/stdout/stderr.

## 8.2 Protocol Validation

Incoming messages shall be validated before action execution.

Validation includes:

- UTF-8 handling.
- JSON parsing.
- Message size.
- Protocol version.
- Message kind.
- Required fields.
- Request identifier.
- Action identifier.
- Payload schema.

## 8.3 Message Limits

The protocol shall enforce a configurable maximum message size.

The CLI protocol currently proposes a default limit of 1 MiB.

The exact value remains subject to performance and compatibility review.

## 8.4 Input Buffering

Partial messages must be buffered with limits.

Unterminated or oversized messages must not cause unbounded memory growth.

## 8.5 Reserved Actions

Reserved framework actions shall not be overridden by arbitrary application registration.

## 8.6 Action Authorization

A syntactically valid action request must still pass applicable action-level authorization.

## 8.7 Request Identity

Request IDs provide correlation.

They are not proof of caller identity or authority.

## 8.8 Handshake

Persistent sessions shall negotiate compatible protocol capabilities before ordinary action execution.

## 8.9 Protocol Errors

Malformed requests shall produce safe classified errors where recovery and transport integrity permit.

## 8.10 stdout Protection

stdout is reserved for valid protocol messages.

Ordinary logging and raw subprocess output must not corrupt protocol framing.

## 8.11 Broken Transport

When the transport fails, pending requests shall receive an appropriate transport outcome.

The framework must preserve uncertainty about operations that may have produced external side effects.

---

# 9. Python Action Security

## 9.1 Action Registry

Applications expose supported functionality through registered actions.

## 9.2 Default-Deny Authorization

Privileged or externally reachable actions should require explicit authorization policies.

A framework may apply trusted local defaults, but it must not assume every valid request is authorized.

## 9.3 Schema Validation

Action inputs must be validated before business execution.

## 9.4 Business Authorization

The consuming application is responsible for determining whether an operation is permitted for the current caller and domain context.

## 9.5 Internal Versus Public Actions

The runtime should distinguish:

- Internal framework operations.
- Approved application-facing actions.
- Administrative or diagnostic actions.

## 9.6 Dangerous Operations

Operations such as deleting files, terminating jobs, changing runtime configuration, or launching external executables require appropriately restricted interfaces.

## 9.7 No Arbitrary Python Evaluation

The framework shall not expose unrestricted `eval`, `exec`, dynamic import, or arbitrary Python-code execution through ordinary application actions.

## 9.8 Authorization Context

Where authorization is needed, it must be supplied through a trusted execution context rather than inferred from user-controlled payload fields.

---

# 10. Subprocess Security Architecture

## 10.1 Purpose

The Process Connector executes approved external programs.

This capability requires careful controls because subprocesses inherit operating-system privileges and may affect files, resources, and other processes.

## 10.2 Executable Identity

The framework should support explicitly registered executable identities.

## 10.3 Executable Resolution

Executable paths should come from trusted application configuration or approved manifests.

Renderer input must not directly become an unrestricted executable path.

## 10.4 Shell Execution

Shell execution shall be disabled by default.

The Process Connector shall prefer structured argument arrays.

## 10.5 Argument Validation

Application adapters shall validate executable-specific argument values before invocation.

Structured arguments reduce shell-injection risk but do not eliminate application-specific dangerous argument combinations.

## 10.6 Working Directory

Working directories must be validated against applicable access policies.

## 10.7 Environment

The framework should construct subprocess environments from controlled configuration.

Sensitive environment values must not be logged indiscriminately.

## 10.8 Process Privileges

Subprocesses ordinarily inherit the privileges of their launching process.

Stronger isolation requires operating-system-specific sandboxing, restricted accounts, containers, or equivalent mechanisms.

These are optional deployment capabilities, not automatic guarantees of the initial Process Connector.

## 10.9 Process Ownership

Every managed process shall have an identifiable owner.

## 10.10 Process Groups and Descendants

The connector shall use supported platform mechanisms for process-tree management.

## 10.11 Process Timeouts

Execution and termination deadlines shall be configurable.

## 10.12 Resource Limits

Where supported, applications may configure process concurrency, output limits, and relevant operating-system resource restrictions.

## 10.13 Process Output

stdout and stderr from external programs shall be treated as untrusted data.

Output must not be executed or interpreted as privileged commands by the framework.

## 10.14 Executable Integrity

Applications may validate bundled executable hashes or signatures where justified.

The framework should provide extension points for such verification without assuming every third-party executable is signed.

---

# 11. Process Termination Safety

## 11.1 Purpose

The framework must safely manage process termination during cancellation, timeout, failure, and shutdown.

## 11.2 Termination Stages

A typical termination policy:

```text
Termination Requested
        │
        ▼
Record Request
        │
        ▼
Attempt Graceful Termination
        │
        ▼
Wait Within Grace Period
        │
        ├── Confirmed Exit
        │
        └── Still Running
                 │
                 ▼
          Allowed Escalation
                 │
                 ▼
          Confirm Final State
```

## 11.3 Platform Differences

Termination semantics differ across Windows, Linux, and macOS.

The framework must expose consistent high-level outcomes without pretending the low-level mechanisms are identical.

## 11.4 Descendant Processes

Termination of a parent PID does not necessarily terminate all descendants.

Process-tree cleanup must use tested, platform-appropriate mechanisms.

## 11.5 Unknown Outcome

If termination cannot be confirmed, the process status must remain appropriately uncertain.

## 11.6 Forced Termination

Forced termination may leave partially written files or incomplete external work.

Applications must validate output artifacts before treating the related job as successful.

---

# 12. Filesystem Security Architecture

## 12.1 Purpose

The framework shall provide safe filesystem access contracts for application files, temporary resources, logs, and generated artifacts.

## 12.2 Path Ownership

Applications shall declare or resolve appropriate filesystem roots.

Examples:

- Application configuration.
- Application data.
- Logs.
- Cache.
- Temporary files.
- Managed artifacts.

## 12.3 Path Validation

Input paths must be validated against the intended filesystem operation.

## 12.4 Path Traversal

Untrusted paths shall not be permitted to escape approved roots through relative traversal.

## 12.5 Symbolic Links

Symlink resolution must be considered in access decisions.

Lexical path normalization alone is insufficient when symlinks are present.

## 12.6 Time-of-Check/Time-of-Use

Filesystem state may change between path validation and file access.

Security-sensitive implementations should prefer appropriate handle-relative or no-follow operations where available and practical, rather than treating an earlier path check as permanently authoritative.

## 12.7 File Permissions

The framework shall respect operating-system permissions.

## 12.8 Atomic Writes

Critical file updates should use safe temporary-file and replacement patterns where supported.

## 12.9 Temporary Files

Temporary files must use controlled locations and ownership.

## 12.10 Artifact Access

Managed artifact references must not become unrestricted filesystem access tokens.

## 12.11 Deletion

Deletion operations shall have explicit scope and validation.

## 12.12 Sensitive Files

Applications may require stronger filesystem restrictions for confidential content.

Those requirements shall be defined by application policy.

---

# 13. Artifact Security

## 13.1 Purpose

Applications may create audio, images, documents, model outputs, and other large artifacts.

## 13.2 Artifact Identity

Managed artifacts should use opaque framework-managed identifiers or validated references rather than unrestricted client-selected paths.

## 13.3 Artifact Metadata

Relevant metadata may include:

- Artifact ID.
- Owning application.
- Owning job or operation.
- Content type.
- Size.
- Storage location.
- Creation time.
- Retention policy.
- Access policy.

## 13.4 Content-Type Validation

Declared content type is not sufficient evidence that a file is safe or matches its actual format.

Applications may require file signature or format validation.

## 13.5 Large Data

Large artifacts shall not be embedded in ordinary CLI JSON messages by default.

## 13.6 Access Control

Artifact retrieval shall respect application authorization.

## 13.7 Retention

Temporary and persistent artifacts shall have explicit retention and cleanup policies.

## 13.8 Partial Artifacts

Artifacts produced by failed or interrupted work must not automatically be treated as complete business results.

---

# 14. Configuration Security

## 14.1 Configuration Sources

Framework configuration may originate from defaults, files, environment variables, and trusted runtime overrides.

## 14.2 Source Trust

The framework must distinguish trusted startup configuration from untrusted runtime request input.

## 14.3 Security-Sensitive Settings

Examples:

- Executable paths.
- Allowed filesystem roots.
- Allowed network destinations.
- IPC permissions.
- Secret-provider configuration.
- Diagnostic exposure.
- Runtime administrative actions.

## 14.4 Override Restrictions

Security-sensitive settings must not be freely overridden by renderer-controlled payloads.

## 14.5 Configuration Validation

Invalid security configuration shall fail before affected privileged components initialize.

## 14.6 Environment Separation

Development configuration must not silently override production security policy.

## 14.7 Immutable Snapshots

Validated immutable configuration snapshots are preferred for the initial runtime.

## 14.8 Reconfiguration

Live reconfiguration, if supported later, must use explicit authorization, validation, and safe component transition semantics.

---

# 15. Credential and Secret Management

## 15.1 Purpose

The framework must support safe access to secrets without making any single secret-management provider mandatory.

## 15.2 Secret Sources

Proposed sources include:

- Environment-variable references.
- Operating-system credential stores.
- Approved protected configuration providers.
- Application-defined secret adapters.

## 15.3 Secrets in Configuration

Ordinary committed configuration files should contain secret references rather than credential values.

## 15.4 Least Privilege

Only components requiring a secret should receive access to it.

## 15.5 Logging

Secret values must not be included in routine logs.

## 15.6 Error Serialization

Underlying exceptions may contain secret-bearing messages.

External error serialization must use controlled safe fields.

## 15.7 Secret Lifetimes

Secrets should not be retained beyond their required operational lifetime where practical.

## 15.8 Rotation

Applications may define secret-rotation procedures.

Connector restart or reconfiguration requirements must be explicit.

## 15.9 Local-Process Limitations

A Python process holding a credential cannot provide strong confidentiality against malicious code running within the same process with equivalent access.

The framework shall document this limitation.

## 15.10 Secret-Provider Failures

Missing or unavailable secrets must produce classified failures without leaking the secret's content.

---

# 16. HTTP Connector Security

## 16.1 Purpose

The HTTP Connector communicates with external and local services.

## 16.2 Transport Security

HTTPS should be preferred for remote communications.

TLS certificate verification shall remain enabled by default for HTTPS.

## 16.3 Explicit Insecure Modes

Disabling certificate verification must require an explicit, restricted configuration option with diagnostic visibility.

## 16.4 Destination Policy

Applications may configure allowed service destinations.

## 16.5 Server-Side Request Forgery

When request destinations are influenced by untrusted inputs, applications must prevent access to unintended internal or privileged network resources.

A simple URL allowlist alone may be insufficient if redirects, DNS resolution, and address changes are not considered.

## 16.6 Redirects

Redirect behavior shall be configurable and follow destination-security policy.

## 16.7 Credentials

Authentication headers and tokens shall be protected from diagnostic exposure.

## 16.8 Request Limits

HTTP operations should support:

- Connection timeout.
- Read timeout.
- Overall deadline.
- Response-size policy.
- Connection limits.
- Retry limits.

## 16.9 Response Validation

External response bodies are untrusted data and require application-appropriate validation.

## 16.10 Retry Safety

Automatic retry must consider the possibility of external side effects.

## 16.11 Local AI Services

ComfyUI, LM Studio, and similar local services shall not automatically be treated as trustworthy merely because they use a localhost endpoint.

Their interfaces, payloads, and output artifacts require appropriate validation.

---

# 17. WebSocket Security

## 17.1 Connection Security

Secure WebSocket transport should be preferred for remote connections.

## 17.2 Endpoint Validation

Connections shall follow the configured destination policy.

## 17.3 Authentication

Authentication shall use approved application-specific mechanisms.

## 17.4 Message Validation

Incoming messages shall be treated as untrusted data.

## 17.5 Message Limits

Message sizes and buffering must be bounded.

## 17.6 Reconnection

Reconnection must follow bounded backoff and retry policies.

## 17.7 Replay Safety

The framework must not automatically replay non-idempotent messages after reconnection.

## 17.8 Subscription Cleanup

Subscriptions and connections must be released when their owning lifecycle ends.

---

# 18. SQLite and Persistence Security

## 18.1 Purpose

SQLite may store application configuration, state, job metadata, and domain data through separate application repositories.

## 18.2 Database Location

Database files shall use application-approved storage locations.

## 18.3 File Permissions

Database access follows operating-system and application permission policies.

## 18.4 Parameterized Queries

Application database operations should use parameterized SQL for untrusted values.

## 18.5 SQL Identifiers

Parameterized queries do not cover arbitrary SQL identifiers.

Dynamic table or column names require separate validation or allowlisting.

## 18.6 Transaction Safety

Transaction ownership, commit, and rollback must follow explicit contracts.

## 18.7 Database Integrity

The persistence subsystem should classify corruption and integrity failures where detectable.

## 18.8 Backups

Important application data requires appropriate backup procedures.

## 18.9 Consistent SQLite Backup

Database backups must use an appropriate SQLite-consistent method.

Copying a live database file without considering journal mode and concurrent writes may produce an incomplete backup.

## 18.10 Encryption

SQLite does not automatically provide application-level encryption at rest.

Encryption requirements are application- and deployment-specific.

## 18.11 Schema Migration

Schema and data migrations require approved compatibility and recovery procedures.

## 18.12 Multiple Processes

Concurrency and locking guarantees must follow SQLite's actual transaction and filesystem behavior.

---

# 19. State Management Security

## 19.1 State Ownership

Every managed state definition shall identify its scope and owner.

## 19.2 Scope Isolation

Request, session, job, process, and persistent state shall follow the isolation guarantees defined in `state-management.md`.

## 19.3 Framework State

Framework-owned state shall not be freely mutable by arbitrary application actions.

## 19.4 Sensitive State

State definitions may classify values as sensitive.

## 19.5 Notifications

Sensitive values shall not be automatically published to all subscribers.

## 19.6 Persistence

Persistent state uses explicit configured storage.

## 19.7 Revision Control

Concurrent updates should use appropriate atomicity and conflict-detection mechanisms.

## 19.8 Stale State

State consumers must not assume local cached state is authoritative after missed events or reconnects.

## 19.9 Electron Exposure

Only explicitly approved state information shall be exposed to Electron renderers.

---

# 20. Job Security Architecture

## 20.1 Purpose

Long-running jobs can consume significant resources and perform privileged operations.

## 20.2 Job Authorization

Applications shall authorize job submission, cancellation, status retrieval, and result access where required.

## 20.3 Job Identity

A job ID is an identifier, not an access credential.

## 20.4 Admission Control

Job submission shall follow configured queue and concurrency limits.

## 20.5 Resource Classification

Job definitions may declare:

- CPU-intensive.
- Memory-intensive.
- External-process.
- I/O-intensive.
- GPU-intensive.

These classifications may guide concurrency policy.

They do not automatically provide operating-system resource isolation.

## 20.6 Cancellation

Cancellation is capability-specific.

## 20.7 Timeouts

Execution timeouts must be distinguished from request timeouts.

## 20.8 Job Results

Results and artifacts require application-appropriate access control.

## 20.9 Job Persistence

Persistent job metadata must not indiscriminately contain secrets or large sensitive payloads.

## 20.10 Durable Execution

Durable execution requires an actual durable worker architecture.

## 20.11 Retry Safety

Jobs with external side effects must not be automatically retried without appropriate idempotency or recovery policies.

---

# 21. Resource Exhaustion Protection

## 21.1 Purpose

The framework must prevent ordinary or malicious workloads from causing uncontrolled resource growth.

## 21.2 Resource Categories

The framework should control:

- Protocol message size.
- Request concurrency.
- Job queue size.
- Active job count.
- Subprocess count.
- Connector connection count.
- Output buffer size.
- Event subscription count.
- Log queue size.
- Artifact size and retention.
- Memory caches.
- Analysis duration.
- Source transformation size.

## 21.3 Bounded Queues

Queues shall have documented capacity limits.

## 21.4 Backpressure

When capacity is exhausted, the framework shall apply a supported backpressure, queueing, or rejection policy.

## 21.5 Process Output

Subprocess output shall not accumulate indefinitely in memory.

## 21.6 Event Delivery

Slow subscribers must not indefinitely block critical runtime operations.

## 21.7 External Services

HTTP and WebSocket clients shall use appropriate connection and request limits.

## 21.8 Logging

Logging shall use bounded buffers and retention.

## 21.9 Denial-of-Service Limitations

Application-level resource limits reduce risk but do not guarantee protection from all operating-system resource exhaustion conditions.

---

# 22. Reliability Architecture

## 22.1 Purpose

Reliability architecture defines how AdharaSutra behaves when components fail or become unavailable.

## 22.2 Reliability Properties

The framework shall emphasize:

- Predictable lifecycle transitions.
- Classified failures.
- Failure isolation.
- Bounded retries.
- Safe timeouts.
- Accurate state reporting.
- Resource cleanup.
- Recovery evidence.
- Data integrity.

## 22.3 Failure Domains

Potential failure domains include:

- One request.
- One action.
- One connector.
- One job.
- One subprocess.
- One persistent CLI session.
- The Python runtime.
- Electron main.
- An external service.
- Local storage.

## 22.4 Failure Scope

A failure should affect the smallest safe scope.

For example, failure of an optional HTTP service should not automatically terminate unrelated SQLite operations.

## 22.5 Critical Failures

If runtime integrity cannot be preserved, the lifecycle manager may initiate controlled shutdown.

## 22.6 Reliability Guarantees

Guarantees must be expressed in terms of actual observed and supported behavior rather than broad claims such as "fault tolerant."

---

# 23. Failure Classification and Isolation

## 23.1 Recoverable Failures

Examples:

- Temporary HTTP unavailability.
- Invalid user input.
- Optional connector failure.
- One job failure.

## 23.2 Potentially Fatal Failures

Examples:

- Corrupted protocol engine state.
- Critical service initialization failure.
- Mandatory persistence unavailability where no safe fallback exists.
- Unrecoverable lifecycle invariant failure.

## 23.3 Error Boundaries

Framework execution boundaries shall convert expected failures into classified outcomes.

## 23.4 Unexpected Exceptions

Unexpected exceptions must be logged safely and handled according to their impact on runtime integrity.

## 23.5 Exception Isolation

An exception from one job handler should not automatically terminate unrelated jobs.

## 23.6 Unknown Outcomes

If the framework cannot establish whether an external side effect completed, it must report uncertainty.

## 23.7 Recovery

Recovery shall restore only capabilities whose valid operating state can be established.

---

# 24. Retry and Backoff Policies

## 24.1 Purpose

Retries may improve availability for transient failures but may also cause duplicate side effects.

## 24.2 Retry Categories

Potentially retryable operations include:

- Selected connection establishment.
- Some read-only HTTP operations.
- Certain transient storage conflicts.
- Explicitly idempotent application actions.

## 24.3 Non-Idempotent Operations

Operations with potentially irreversible side effects require explicit retry eligibility.

## 24.4 Backoff

Retry policies should support bounded exponential backoff with jitter where appropriate.

## 24.5 Retry Limits

Retries must have:

- Maximum attempts.
- Applicable deadline.
- Failure classification.
- Cancellation handling.
- Diagnostics.

## 24.6 Circuit Breaking

Circuit breakers may be supported as optional connector policies when repeated failure protection is useful.

They are not required for every connector in the initial implementation.

## 24.7 Recovery Claims

A successful connection retry does not prove that every previous failed operation was recovered.

---

# 25. Timeout Architecture

## 25.1 Timeout Ownership

Timeouts may exist at different layers.

| Layer | Timeout responsibility |
|---|---|
| Electron bridge | Client request and backend startup |
| CLI runtime | Request execution |
| HTTP connector | Connection and request operations |
| WebSocket connector | Connection and message operations |
| Job Manager | Queue wait and job execution |
| Process Connector | Process execution and termination |
| Lifecycle Manager | Startup and shutdown |
| Development tooling | Analysis, verification, transformations |

## 25.2 Deadline Propagation

Where supported, downstream operations should respect the remaining parent deadline.

## 25.3 Timeout Versus Cancellation

A timeout is not proof that an underlying operation stopped.

## 25.4 External Side Effects

A timed-out HTTP request may still have completed on the remote service.

## 25.5 Timeout Testing

Tests shall cover:

- Timeout firing.
- Cancellation requests.
- Non-cooperative operations.
- Race conditions.
- Unknown outcomes.
- Resource cleanup.

---

# 26. Startup Reliability

## 26.1 Bootstrap

Application startup shall follow validated configuration and dependency composition.

## 26.2 Dependency Graph

Required components initialize according to declared dependencies.

## 26.3 Partial Initialization

If startup fails after some components initialize, the lifecycle manager shall clean up managed resources where possible.

## 26.4 Readiness

Readiness must not be reported until mandatory startup conditions are satisfied.

## 26.5 Optional Components

Failure of an optional capability may result in degradation rather than full startup failure.

## 26.6 Startup Deadline

Startup may have configurable deadlines.

## 26.7 Electron Handshake

Electron must not treat the Python backend as ready before successful required initialization and compatible protocol negotiation.

## 26.8 Startup Diagnostics

Failures should identify the component and phase while protecting sensitive configuration values.

---

# 27. Shutdown Reliability

## 27.1 Purpose

Shutdown shall stop new work, coordinate active operations, and release managed resources.

## 27.2 Shutdown Sequence

```text
Shutdown Initiated
        │
        ▼
Stop New Admission
        │
        ▼
Apply Request Policy
        │
        ▼
Apply Job Policy
        │
        ▼
Request Process Termination
        │
        ▼
Close Dependent Services
        │
        ▼
Close Connectors and State Stores
        │
        ▼
Flush Diagnostics
        │
        ▼
Terminate Runtime
```

The actual sequence follows dependency ownership and selected shutdown policies.

## 27.3 Idempotency

Repeated shutdown requests must not cause unsafe duplicate cleanup.

## 27.4 Shutdown Deadline

Shutdown must be bounded according to configuration.

## 27.5 Cleanup Failure

Cleanup failures shall be recorded without erasing the primary failure cause.

## 27.6 Forced Termination

Forced termination may prevent final cleanup or persistence operations.

The framework shall not promise that all resources are released after abrupt process death.

## 27.7 Job Interruption

Unfinished work must be reconciled according to job ownership and recovery policies.

---

# 28. Crash Recovery

## 28.1 Purpose

Crash recovery reestablishes a known valid state after unexpected termination.

## 28.2 Recovery Inputs

Relevant inputs may include:

- Persistent configuration.
- Database state.
- Job metadata.
- Artifact metadata.
- Process ownership evidence.
- Recovery journals.
- Application-specific checkpoints.

## 28.3 Recovery Sequence

```text
Runtime Restart
      │
      ▼
Validate Configuration
      │
      ▼
Initialize Persistence
      │
      ▼
Inspect Recoverable State
      │
      ▼
Reconcile Interrupted Jobs
      │
      ▼
Validate Required Artifacts
      │
      ▼
Initialize Services
      │
      ▼
Evaluate Readiness
```

## 28.4 In-Memory State

In-memory state is lost after process termination unless reconstructed through an explicit mechanism.

## 28.5 Persistent State

Committed persistent state may be restored according to its backend guarantees.

## 28.6 Job Metadata

A persisted `running` status from a previous runtime must not automatically mean the job is still running.

## 28.7 Orphan Processes

Process reattachment requires reliable evidence of process identity and ownership.

## 28.8 Unknown External Outcomes

Unconfirmed external operations shall be represented as interrupted or unknown until adequate evidence is available.

## 28.9 Recovery Policy

Each recoverable capability must declare its recovery behavior.

---

# 29. Data Integrity and Durability

## 29.1 Purpose

Reliability requires accurate treatment of data persistence, transactional behavior, and incomplete writes.

## 29.2 Commit Guarantees

A persistent operation shall not report committed success before satisfying its storage contract.

## 29.3 Atomicity

Atomicity is guaranteed only within the documented supported boundary.

## 29.4 External Operations

The framework shall not promise atomic transactions across unrelated filesystems, processes, databases, and network services.

## 29.5 Write Recovery

Critical file writes should use supported safe-replacement patterns where appropriate.

## 29.6 Database Recovery

Database restoration and recovery shall follow backend-specific mechanisms.

## 29.7 Backups

Applications with valuable persistent data should define backup and restoration policies.

## 29.8 Backup Testing

A backup procedure is not fully validated until restoration has been tested.

## 29.9 Data Corruption

Corrupted or incompatible data shall produce classified failures.

The framework must not silently discard important persistent business data.

---

# 30. Observability and Auditability

## 30.1 Purpose

Security and reliability decisions require sufficient diagnostic evidence.

## 30.2 Important Events

Relevant events may include:

- Application startup.
- Readiness changes.
- Unauthorized action rejection.
- Connector failure.
- Process launch.
- Process termination.
- Job cancellation.
- Persistence failure.
- Recovery attempt.
- Migration apply.
- Application shutdown.

## 30.3 Correlation

Diagnostics should associate related operations using:

- Request ID.
- Session ID.
- Job ID.
- Attempt ID.
- Process execution ID.
- Connector ID.

## 30.4 Audit Versus Diagnostic Logs

Ordinary diagnostics and security audit requirements are distinct.

The initial framework provides structured diagnostic records.

Applications requiring tamper-resistant or legally compliant audit trails need a separately defined audit capability.

## 30.5 Sensitive Information

Logs and reports shall avoid unnecessary sensitive values.

## 30.6 Log Integrity

Local rotating logs are useful diagnostics but are not automatically tamper-proof.

## 30.7 Redaction

Redaction should occur before records are delivered to external sinks.

---

# 31. Dependency and Supply-Chain Security

## 31.1 Purpose

AdharaSutra may be distributed through Python packages and a separately versioned npm Electron bridge.

## 31.2 Dependency Minimization

Minimal runtime installations should not require unused connector or development-tooling dependencies.

## 31.3 Dependency Pinning

Release and test environments should use reproducible dependency constraints or lockfiles where appropriate.

## 31.4 Dependency Review

Known dependency vulnerabilities should be evaluated using suitable scanning tools.

## 31.5 Package Provenance

Published artifacts should be traceable to their approved source revision and build workflow.

## 31.6 Trusted Publishing

Package publishing should use supported secure credentials or trusted-publishing mechanisms where available.

## 31.7 Build Artifacts

Release validation must inspect actual built artifacts.

## 31.8 External Executables

Bundled external tools may require:

- Version identification.
- Source provenance.
- Integrity checks.
- License review.
- Platform compatibility validation.

## 31.9 Software Bill of Materials

SBOM generation may be supported as an optional release capability.

## 31.10 Supply-Chain Limitations

Dependency scanners and checksums reduce risk but do not guarantee that every dependency is safe.

---

# 32. Packaging Security

## 32.1 Python Package

The Python distribution shall expose only intended runtime and developer interfaces.

## 32.2 Optional Dependencies

Optional modules must not be silently imported or initialized by the minimal runtime.

## 32.3 Electron Bridge

The bridge package shall publish intended TypeScript/JavaScript exports without exposing development-only capabilities unintentionally.

## 32.4 Bundled Python Runtime

Packaged Electron applications must resolve the intended Python executable from approved deployment locations.

## 32.5 Executable Paths

Applications must not depend on uncontrolled current-working-directory executable resolution.

## 32.6 Code Signing

Signing and notarization requirements are deployment-specific.

## 32.7 Application Updates

Updates must preserve version compatibility and avoid unsafe replacement of executing resources.

## 32.8 Runtime Version Negotiation

The Electron bridge and Python backend shall validate supported protocol compatibility.

## 32.9 Upgrade Rollback

Application upgrades should provide a recovery strategy when persistent schemas or runtime contracts change incompatibly.

---

# 33. Development Tooling Security

## 33.1 Purpose

Scaffolding, discovery, verification, and migration operate on application repositories.

Repositories may contain untrusted or malformed source.

## 33.2 Static Discovery

Ordinary discovery shall be read-only and shall not import arbitrary application modules.

## 33.3 Architecture Verification

Default static verification shall not execute inspected application code.

## 33.4 Custom Detectors

Detector plugins are executable tooling and must be explicitly trusted.

## 33.5 Custom Rules

Custom rule evaluators require equivalent trust controls.

## 33.6 Project Scaffolding

Templates shall be validated before writing generated files.

## 33.7 Migration Planning

Migration planning shall be read-only by default.

## 33.8 Source Transformation

Transformations shall require explicit apply authorization.

## 33.9 Source Drift

Migration changes shall not be applied blindly when source fingerprints no longer match expected preconditions.

## 33.10 Rollback

Rollback must protect unrelated developer changes.

## 33.11 Test Execution

Running project tests may execute arbitrary project code and must use appropriate trust and isolation policies.

## 33.12 LLM Assistance

Any optional AI-assisted analysis shall follow explicit source-data disclosure and trust policies.

---

# 34. Application Isolation

## 34.1 Process Isolation

Independent AdharaSutra applications normally run in separate Python processes.

## 34.2 State Isolation

Process-scoped state does not automatically cross process boundaries.

## 34.3 Filesystem Isolation

Applications should use distinct data, log, cache, and artifact locations.

## 34.4 Database Isolation

Separate applications shall not accidentally share private database files.

## 34.5 Connector Isolation

Application connector instances and credentials should be scoped appropriately.

## 34.6 Shared Resources

Explicitly shared resources require an application-defined coordination and authorization policy.

## 34.7 Isolation Limitations

Separate processes running under the same operating-system user are not equivalent to strongly sandboxed security principals.

---

# 35. Security and Reliability Configuration

## 35.1 Purpose

The framework should expose typed security and resource policies through centralized configuration.

## 35.2 Illustrative Configuration

```yaml
security:
  protocol:
    max_message_bytes: 1048576
    validate_payloads: true

  process:
    shell_enabled: false
    require_registered_executable: true

  filesystem:
    restrict_managed_artifacts: true

  diagnostics:
    redact_sensitive_values: true

reliability:
  requests:
    max_concurrent: 32

  jobs:
    max_concurrent: 4
    max_pending: 100

  shutdown:
    timeout_seconds: 30

  connectors:
    retry_max_attempts: 3
```

This is a conceptual configuration example.

Values are proposed examples, not approved defaults.

The final schema must define which policies are mandatory, optional, or capability-specific.

## 35.3 Configuration Validation

Invalid security policy must not silently fall back to unsafe defaults.

## 35.4 Configuration Provenance

Diagnostics should identify the source of effective security settings without exposing secrets.

## 35.5 Production Overrides

Untrusted runtime requests must not freely override security policy.

---

# 36. Reliability and Security Testing Strategy

## 36.1 Testing Foundation

Security and reliability tests shall follow `testing-strategy.md`.

## 36.2 Unit Tests

Verify:

- Authorization decisions.
- Input validation.
- Error classification.
- Resource limits.
- Redaction.
- Retry eligibility.

## 36.3 Contract Tests

Verify:

- Protocol validation.
- Connector error semantics.
- Process execution contracts.
- State access policy.
- Job cancellation semantics.

## 36.4 Integration Tests

Verify actual interactions involving:

- Electron IPC.
- Python subprocess transport.
- SQLite.
- HTTP/WebSocket fixtures.
- External process fixtures.
- Filesystem access.

## 36.5 Security Abuse Cases

Test malformed and unauthorized inputs.

## 36.6 Failure Injection

Test:

- Connection failures.
- Timeouts.
- Process crashes.
- Database errors.
- Resource exhaustion.
- Shutdown failures.
- Partial writes.

## 36.7 Cross-Platform Testing

Operating-system-dependent security and process behavior must be validated on supported platforms.

## 36.8 Packaged Testing

Security controls must be evaluated against representative packaged desktop applications.

## 36.9 Test Evidence

Evidence must identify the source revision, environment, and executed tests.

---

# 37. Threat-Specific Test Matrix

| Threat or failure | Required test category |
|---|---|
| Malformed CLI messages | Protocol contract tests |
| Oversized protocol payload | Resource-limit tests |
| Unauthorized IPC request | Electron integration tests |
| Renderer direct process execution | Electron security tests |
| Command injection | Process argument tests |
| Unapproved executable path | Executable allowlist tests |
| Path traversal | Filesystem security tests |
| Symlink escape | Filesystem integration tests |
| SSRF-prone destination | HTTP security tests |
| Untrusted WebSocket payload | WebSocket validation tests |
| SQL injection | Persistence adapter tests |
| Lost state update | State concurrency tests |
| Unbounded job submission | Admission-control tests |
| Cancellation race | Job lifecycle tests |
| Orphan subprocess | Platform process tests |
| Database write interruption | Persistence recovery tests |
| Credential exposure | Logging and serialization tests |
| Startup failure | Lifecycle fault-injection tests |
| Unsafe migration apply | Migration safety tests |
| Vulnerable dependency | Dependency scanning |
| Package incompatibility | Release compatibility tests |

---

# 38. Architecture Verification Rules

The following security and reliability rules are proposed.

| Rule ID | Description |
|---|---|
| SR-VER-001 | Privileged actions use approved authorization boundaries |
| SR-VER-002 | Renderer cannot access unrestricted backend process controls |
| SR-VER-003 | Electron preload exports follow approved API constraints |
| SR-VER-004 | IPC handlers enforce applicable caller and action validation |
| SR-VER-005 | CLI messages are validated before application execution |
| SR-VER-006 | Protocol message and buffer limits are defined |
| SR-VER-007 | Framework-reserved actions are protected |
| SR-VER-008 | Subprocess execution uses approved interfaces |
| SR-VER-009 | Shell execution is disabled by default |
| SR-VER-010 | Executable selection follows approved policy |
| SR-VER-011 | Managed processes have lifecycle owners |
| SR-VER-012 | Process output does not corrupt protocol stdout |
| SR-VER-013 | Filesystem access follows defined boundaries |
| SR-VER-014 | Persistent data has appropriate storage ownership |
| SR-VER-015 | Sensitive configuration is protected from ordinary diagnostics |
| SR-VER-016 | Job queues and concurrency are bounded |
| SR-VER-017 | Retry policies account for idempotency |
| SR-VER-018 | Required startup and shutdown policies are defined |
| SR-VER-019 | Persistent job records are not treated as durable execution |
| SR-VER-020 | Security-sensitive configuration is validated |
| SR-VER-021 | Runtime dependencies exclude unnecessary development tooling |
| SR-VER-022 | Packaged runtime paths follow approved deployment rules |
| SR-VER-023 | Security-critical test requirements are identified |
| SR-VER-024 | Unsupported security claims are marked unresolved |
| SR-VER-025 | Exceptions to security rules follow approved governance |

## 38.1 Verification Limitations

Static verification can identify relevant configuration and source patterns.

It cannot prove:

- Complete security.
- Correct behavior under all attacks.
- Successful cleanup under every failure.
- Absence of all race conditions.
- Production operating-system hardening.

These require executable evidence and deployment review.

## 38.2 Mandatory Rule Policy

A narrowly defined subset of critical safety rules may be nonwaivable under ordinary application exception policies.

The specific rules must be approved during architecture finalization.

---

# 39. Reliability Validation Scenarios

## SR-S01 — Malformed CLI Input

**Given** a persistent CLI runtime,

**When** a malformed request arrives,

**Then** the runtime shall reject it according to protocol policy.

**And** avoid executing an application action.

## SR-S02 — Unauthorized Electron Action

**Given** a renderer lacks permission for a privileged operation,

**When** it invokes the corresponding IPC action,

**Then** Electron main shall reject the request.

**And** the privileged operation shall not execute.

## SR-S03 — Unregistered Executable

**Given** process execution requires registered executables,

**When** an application request selects an unapproved executable,

**Then** the Process Connector shall reject the operation.

## SR-S04 — Argument Safety

**Given** an external process accepts user-derived arguments,

**When** the framework launches it,

**Then** arguments shall be passed according to the structured invocation contract.

**And** shell interpretation shall not be enabled implicitly.

## SR-S05 — Symlink Escape

**Given** an artifact path resolves outside an approved root,

**When** a restricted operation attempts to access it,

**Then** the framework shall reject the operation according to the filesystem access policy.

## SR-S06 — Credential Redaction

**Given** a synthetic credential is present in connector configuration,

**When** errors and diagnostics are produced,

**Then** ordinary external diagnostic output shall not expose the credential.

## SR-S07 — Optional Connector Failure

**Given** an optional HTTP service becomes unavailable,

**When** a request uses that service,

**Then** the affected operation shall receive a classified failure.

**And** unrelated capabilities may remain available.

## SR-S08 — Job Queue Exhaustion

**Given** the pending-job queue reaches capacity,

**When** another job is submitted,

**Then** the Job Manager shall enforce the configured admission policy.

## SR-S09 — External Process Timeout

**Given** an external executable exceeds its allowed runtime,

**When** its deadline is reached,

**Then** the Process Connector shall apply the configured termination policy.

**And** report the observed outcome.

## SR-S10 — Cancellation Race

**Given** a job completes while cancellation is requested,

**When** lifecycle reconciliation occurs,

**Then** the framework shall preserve the correct confirmed terminal outcome.

## SR-S11 — Python Runtime Crash

**Given** Electron has pending requests,

**When** Python terminates unexpectedly,

**Then** the bridge shall report transport failure.

**And** preserve uncertainty about side-effecting operations.

## SR-S12 — Job Recovery

**Given** persisted job metadata indicates a previously running job,

**When** a new runtime starts,

**Then** the Job Manager shall reconcile execution ownership.

**And** shall not assume the job is still running.

## SR-S13 — Database Commit Failure

**Given** a persistent state update fails before its required commit,

**When** the operation returns,

**Then** the framework shall not report durable success.

## SR-S14 — Partial Startup Failure

**Given** several components initialize before a required component fails,

**When** startup aborts,

**Then** the lifecycle manager shall attempt safe cleanup.

**And** preserve the primary error.

## SR-S15 — Forced Shutdown

**Given** a non-cooperative workload prevents graceful shutdown,

**When** the shutdown deadline expires,

**Then** the framework shall apply the supported escalation policy.

**And** report any unconfirmed termination or incomplete cleanup.

## SR-S16 — Untrusted Repository

**Given** an inspected repository contains import-time side effects,

**When** default architecture discovery runs,

**Then** the application code shall not execute.

## SR-S17 — Unsafe Migration

**Given** a migration plan would modify files outside its approved scope,

**When** the Apply Engine validates the operation,

**Then** it shall reject the unsafe modification.

## SR-S18 — Package Compatibility

**Given** an Electron bridge and Python runtime use incompatible protocol versions,

**When** their handshake occurs,

**Then** the integration shall report a compatibility failure rather than silently continue.

## SR-S19 — Logging Failure

**Given** an optional logging sink becomes unavailable,

**When** logging continues,

**Then** the framework shall apply its documented sink failure policy.

**And** preserve essential runtime operation where safe.

## SR-S20 — Packaged Runtime

**Given** a packaged Electron application,

**When** its Python backend starts,

**Then** executable and resource paths shall resolve through approved package configuration.

**And** shall not rely on developer-specific local paths.

---

# 40. Security and Reliability Decisions

| ID | Decision | Proposed direction |
|---|---|---|
| SR-D01 | Security baseline | Secure defaults and defense in depth |
| SR-D02 | Trust boundaries | Explicitly documented |
| SR-D03 | Renderer privileges | Restricted |
| SR-D04 | Electron process ownership | Main process |
| SR-D05 | IPC authorization | Explicit allowlists and validation |
| SR-D06 | Protocol validation | Mandatory |
| SR-D07 | Request identifiers | Correlation, not authentication |
| SR-D08 | Arbitrary execution | Prohibited by default |
| SR-D09 | Subprocess shell mode | Disabled by default |
| SR-D10 | Executable identity | Registered or trusted configuration |
| SR-D11 | Filesystem security | Validated, scoped access |
| SR-D12 | Artifact access | Managed references |
| SR-D13 | Secret handling | Provider-based references |
| SR-D14 | Network transport | Secure defaults |
| SR-D15 | Connector retries | Bounded and idempotency-aware |
| SR-D16 | State access | Explicit scope ownership |
| SR-D17 | Job admission | Bounded queues and concurrency |
| SR-D18 | Process cleanup | Platform-aware |
| SR-D19 | Failure isolation | Smallest safe failure domain |
| SR-D20 | Unknown outcomes | Explicitly preserved |
| SR-D21 | Crash recovery | Evidence-based |
| SR-D22 | Durable execution | Requires independent owner |
| SR-D23 | Database durability | Backend-specific guarantees |
| SR-D24 | Logs and diagnostics | Structured and redacted |
| SR-D25 | Supply chain | Reproducible, reviewed releases |
| SR-D26 | Development tooling | Read-only by default |
| SR-D27 | Migration apply | Explicit authorization |
| SR-D28 | Security verification | Static plus executable evidence |
| SR-D29 | LLM dependency | None |
| SR-D30 | Deployment hardening | Application-specific extension |

All decisions remain proposed until architecture review.

---

# 41. Outstanding Questions

## SR-OQ-001 — Default Security Policy

Should every AdharaSutra application use the same default security profile?

**Recommendation:** Define a common mandatory safety baseline and allow application-specific stricter policies.

## SR-OQ-002 — Electron Sandboxing

Should renderer sandboxing be mandatory?

**Recommendation:** Enable it where supported and compatible with the selected Electron integration. Require explicit review for exceptions.

## SR-OQ-003 — IPC Authorization

Should the bridge implement authorization or delegate it entirely to the application?

**Recommendation:** The bridge should enforce technical allowlists and trusted caller validation, while the application owns domain authorization.

## SR-OQ-004 — Python Action Authorization

Should AdharaSutra provide a standard action-authorization interface?

**Recommendation:** Yes. Provide an extensible policy hook without requiring a universal user-identity framework.

## SR-OQ-005 — Executable Allowlists

Should every external executable require registration?

**Recommendation:** Prefer registered executable identities for packaged and privileged workflows. Allow controlled developer configuration where appropriate.

## SR-OQ-006 — Subprocess Sandboxing

Should AdharaSutra provide an operating-system sandbox abstraction?

**Recommendation:** Defer as an optional advanced capability. Do not claim that ordinary subprocesses are isolated security sandboxes.

## SR-OQ-007 — Filesystem API

Should all application filesystem access use AdharaSutra wrappers?

**Recommendation:** Require managed facilities for security-sensitive or framework-owned paths, while avoiding unnecessary restrictions on ordinary trusted application domain code.

## SR-OQ-008 — Artifact Authorization

Should artifact access use opaque IDs, signed references, or both?

**Recommendation:** Begin with opaque IDs and explicit authorization. Signed references may be useful for future cross-process or remote distribution scenarios.

## SR-OQ-009 — Encryption at Rest

Should persistent state and SQLite databases be encrypted automatically?

**Recommendation:** Do not enable universal encryption without a key-management design. Provide optional capabilities for applications with explicit confidentiality requirements.

## SR-OQ-010 — Credential Providers

Which secret providers should be implemented initially?

**Recommendation:** Start with environment-variable references and an extensible provider interface, then add platform credential-store adapters when required.

## SR-OQ-011 — HTTP Destination Restrictions

Should the HTTP Connector enforce destination allowlists?

**Recommendation:** Support configurable policies, especially for requests influenced by untrusted input. Include redirect and address-resolution considerations.

## SR-OQ-012 — Retry Defaults

Should retries be enabled automatically for all connectors?

**Recommendation:** No. Default retry policies must be conservative and operation-aware.

## SR-OQ-013 — Circuit Breakers

Should circuit breakers be part of the initial connector framework?

**Recommendation:** Keep them optional and introduce them after the simpler timeout, retry, and health contracts stabilize.

## SR-OQ-014 — Resource Limit Defaults

What initial queue, process, and memory limits should apply?

**Recommendation:** Establish conservative configurable defaults and benchmark representative applications before approving hard thresholds.

## SR-OQ-015 — Audit Logging

Should AdharaSutra provide tamper-evident audit logs?

**Recommendation:** Treat audit logging as a separate optional capability. Ordinary structured logs are not sufficient for strong audit-integrity guarantees.

## SR-OQ-016 — Automatic Crash Recovery

Should the runtime automatically restart failed jobs?

**Recommendation:** Only for job types with explicit safe recovery or retry contracts.

## SR-OQ-017 — Orphan Process Recovery

Should the framework reattach to processes surviving a Python crash?

**Recommendation:** Defer until process identity, ownership, and recovery guarantees can be established and tested.

## SR-OQ-018 — Durable Workers

Should durable workers be mandatory for Electron applications?

**Recommendation:** No. They should remain optional for applications requiring execution continuity beyond the normal Python runtime.

## SR-OQ-019 — Security Rule Waivers

Which architecture security rules should be nonwaivable?

**Recommendation:** Define a narrow mandatory core covering genuinely dangerous violations, with formal review for any exception outside ordinary application configuration.

## SR-OQ-020 — Dependency Scanning

Should dependency vulnerability scanning be a release requirement?

**Recommendation:** Yes, within a defined risk and exception policy. Scanner findings must be evaluated rather than interpreted as automatic proof of exploitation.

## SR-OQ-021 — Artifact Integrity

Should downloaded or generated artifacts receive automatic checksums?

**Recommendation:** Support integrity metadata for artifacts whose downstream use or recovery requires it, without hashing every temporary file unnecessarily.

## SR-OQ-022 — Threat Modeling Frequency

When should threat models be reviewed?

**Recommendation:** Review material new trust boundaries, privileged operations, and release-significant architectural changes.

## SR-OQ-023 — Localhost Trust

Should localhost HTTP services be treated as trusted?

**Recommendation:** No. Locality alone does not prove service identity or content safety.

## SR-OQ-024 — Security Test Coverage

Should every security rule require executable tests?

**Recommendation:** Each critical rule requires suitable verification evidence. Some properties are static, while others require integration or runtime tests.

## SR-OQ-025 — Framework Threat Model

Should the final architecture baseline include a formal threat register?

**Recommendation:** Yes. Include major assets, boundaries, threats, controls, residual risks, and ownership.

---

# 42. Functional Requirement Traceability

| Requirement group | Security/reliability responsibility |
|---|---|
| FR-SEC | Security controls and access boundaries |
| FR-RUN | Runtime isolation and execution safety |
| FR-CLI | Protocol validation and limits |
| FR-ELC | Electron IPC and backend ownership |
| FR-CON | Connector security contracts |
| FR-HTTP | HTTP transport and destination security |
| FR-WS | WebSocket message and connection security |
| FR-EXT | Subprocess execution and termination |
| FR-DB | Database access and integrity |
| FR-FS | Filesystem and artifact restrictions |
| FR-STATE | State scope security |
| FR-JOB | Job authorization and admission |
| FR-CFG | Secure configuration and secrets |
| FR-ERR | Safe error reporting |
| FR-LOG | Redaction and diagnostic control |
| FR-DI | Component ownership |
| FR-SCAF | Secure generated templates |
| FR-DISC | Safe repository inspection |
| FR-ARCH | Security rule evaluation |
| FR-MIG | Safe migration changes |
| FR-TEST | Security and failure tests |
| FR-PKG | Packaging and supply-chain security |
| FR-REP | Evidence and security reporting |

---

# 43. Non-Functional Requirement Traceability

| Requirement group | Architectural mechanism |
|---|---|
| NFR-SEC | Trust boundaries and least privilege |
| NFR-REL | Failure isolation and recovery |
| NFR-AVAIL | Readiness, degradation, bounded retries |
| NFR-PERF | Resource limits and overload policies |
| NFR-RES | Cleanup and bounded resource usage |
| NFR-PORT | Platform-specific process and filesystem safety |
| NFR-MAINT | Centralized security contracts |
| NFR-EXT | Configurable security capabilities |
| NFR-TEST | Security and reliability testing |
| NFR-COMP | Version and protocol compatibility |
| NFR-ARCH | Enforceable security rules |
| NFR-MIG | Non-destructive source modification |
| NFR-OBS | Correlation, diagnostics, redaction |
| NFR-OPS | Packaging and recovery |
| NFR-DOC | Threat models and deployment guidance |

Exact requirement identifiers must be reconciled with the final approved requirements catalog.

---

# 44. Security and Reliability Acceptance Criteria

The architecture may be approved when:

### Security Foundation

- [ ] Security ownership is divided between framework, application, and deployment.
- [ ] Trust boundaries are defined.
- [ ] Threat modeling is included.
- [ ] Mandatory security defaults are identified.
- [ ] Privileged operations follow authorization policies.
- [ ] Security limitations are explicit.

### Electron and CLI

- [ ] Electron renderer privileges are restricted.
- [ ] Preload APIs are allowlisted.
- [ ] IPC authorization is defined.
- [ ] Python process ownership remains in Electron main.
- [ ] Protocol message validation is required.
- [ ] Protocol payload limits are defined.
- [ ] Reserved actions are protected.
- [ ] Request IDs are not treated as authorization tokens.
- [ ] stdout isolation is addressed.

### Connectors and Processes

- [ ] Process execution uses trusted executable configuration.
- [ ] Shell execution is disabled by default.
- [ ] Argument validation is defined.
- [ ] Process ownership and termination are defined.
- [ ] Descendant-process cleanup is considered.
- [ ] HTTP destination security is addressed.
- [ ] TLS defaults are defined.
- [ ] Retry and timeout policies are explicit.
- [ ] WebSocket buffering and validation are defined.

### Storage and Secrets

- [ ] Filesystem boundaries are defined.
- [ ] Path traversal and symlink behavior are addressed.
- [ ] Artifact access is controlled.
- [ ] Sensitive configuration uses protected references.
- [ ] Credential logging is restricted.
- [ ] SQLite integrity and transaction semantics are documented.
- [ ] Backup and restoration responsibilities are explicit.
- [ ] Encryption limitations are documented.

### Reliability

- [ ] Failure domains are defined.
- [ ] Recoverable and fatal failures are distinguished.
- [ ] Resource limits are defined.
- [ ] Job queue backpressure is addressed.
- [ ] Cancellation and timeout outcomes remain accurate.
- [ ] Startup readiness is evidence-based.
- [ ] Partial initialization cleanup is specified.
- [ ] Shutdown is bounded and coordinated.
- [ ] Crash recovery follows explicit policies.
- [ ] Persistent metadata is not confused with durable execution.
- [ ] Unknown outcomes are preserved.

### Tooling and Distribution

- [ ] Development tooling is read-only by default where applicable.
- [ ] Untrusted source is not executed during ordinary discovery.
- [ ] Migration applies require explicit authorization.
- [ ] Dependency and package security are addressed.
- [ ] Packaged runtime security is considered.
- [ ] Cross-platform testing is defined.
- [ ] Security verification rules are identifiable.
- [ ] Important security guarantees have test evidence requirements.
- [ ] Remaining threats and risks are documented.
- [ ] Open decisions are approved or explicitly deferred.

---

# 45. Final Architecture Summary

AdharaSutra's Security and Reliability Architecture establishes shared controls across the framework's runtime, communication, integration, persistence, execution, and development-tooling capabilities.

The security architecture provides:

- Explicit trust boundaries.
- Secure defaults.
- Restricted Electron IPC.
- Validated CLI protocol communication.
- Controlled action execution.
- Safe subprocess invocation.
- Filesystem and artifact access policies.
- Secret-management interfaces.
- Connector security requirements.
- Data integrity protections.
- Sensitive diagnostic redaction.
- Supply-chain and packaging considerations.

The reliability architecture provides:

- Explicit resource ownership.
- Failure isolation.
- Bounded concurrency.
- Backpressure.
- Timeouts.
- Cancellation policies.
- Retry safety.
- Startup readiness.
- Graceful shutdown.
- Crash recovery.
- Persistent data integrity.
- Truthful execution outcomes.

The framework shall remain local-first and usable without mandatory cloud security or monitoring infrastructure.

Security and reliability controls should be shared across applications, while business authorization, domain data protection, and deployment hardening remain application-specific.

The architecture must not claim that subprocesses are sandboxed, job records guarantee durable execution, or static verification proves complete security.

**The central guarantee is: Every privileged capability is governed by an explicit trust policy, and every managed operation follows a defined resource, failure, and recovery contract.**

---

# 46. Document Status

**Status:** Draft — Architecture Planning  
**Version:** 0.1.0  
**Approval:** Pending security and reliability architecture review

**Next Document:** `docs/design/packaging-and-distribution.md`

The next document should define the Python package structure, optional dependency groups, development-tooling distribution, TypeScript Electron bridge package, semantic versioning, build artifacts, cross-platform packaging, trusted publishing, release validation, and compatibility between AdharaSutra runtime and application distributions.

---

**AdharaSutra — Build once. Standardize everywhere.**
