# Connector reference

Public connectors are managed services: register them with
`app.service(...)`, let the runtime start and stop them, and access them through
`context.get_service(...)`. Connector failures surface as `ConnectorError` values
carried in the protocol `connector` error category (or the `CONNECTOR_TIMEOUT`
code for timeouts), with the connector identity in `details.connector` where
available.

## HTTP (`HttpClient`)

- **Configuration:** `HttpClient(base_url=..., timeout=..., headers=..., auth=...,
  retry=...)` (module `nikhi.adhara_sutra.http`, optional extra
  `nikhi-adhara-sutra[http]`). `base_url` prefixes relative request URLs;
  `timeout` sets the client-wide default; headers/auth apply to every request;
  `retry` configures retry policy for retryable failures.
- **Lifecycle:** context-managed. `__enter__` creates and reuses one underlying
  `httpx` client; `__exit__` closes it. `health()` reports whether the client is
  started. Per-request options (`timeout`, `headers`, `auth`) override client
  defaults; `stream(...)` yields a `HttpStreamResponse` that must be closed.
- **Error behavior:** missing `httpx` or an unstarted client raises a
  non-retryable `ConnectorError` (`connector: http`). Network failures and
  timeouts map to retryable connector errors (`CONNECTOR_TIMEOUT` for timeouts).
  `response.raise_for_status()` maps 4xx responses to non-retryable and 5xx
  responses to retryable connector errors with status, URL, and body details.

## External CLI (`ExternalCommand`)

- **Configuration:** `ExternalCommand(executable, *, search_path=..., env=...,
  cwd=..., kill_timeout=..., max_concurrent=...)` (module
  `nikhi.adhara_sutra.external`). `search_path` and `PATH` locate the executable;
  `env`/`cwd` control the child environment; `kill_timeout` bounds forced
  termination; `max_concurrent` limits concurrent runs per instance.
- **Lifecycle:** context-managed. `__enter__` resolves the executable and fails
  fast if it is missing; `__exit__` terminates any still-running process tree.
  `run(args, *, timeout=..., input=..., cwd=..., env=..., on_output=...)` passes a
  structured argument array without a shell and returns a `CommandResult`
  (exit code, captured stdout/stderr, duration) while streaming output.
- **Error behavior:** invalid arguments, a missing executable, or use before
  start raise non-retryable connector errors (`connector: external`). Timeouts
  and cancellation terminate the process tree and raise retryable
  `CONNECTOR_TIMEOUT` errors reporting `details.outcome: "unknown"` when side
  effects are possible. `CommandResult.raise_for_status()` raises a
  non-retryable `ConnectorError` with `details.exit_code` for a non-zero exit;
  captured output and the tool's own conventions are preserved.

## SQLite (`SQLiteDatabase`)

- **Configuration:** `SQLiteDatabase(path=":memory:", *, timeout=5.0,
  pragmas=())` (module `nikhi.adhara_sutra.sqlite`, standard library). `path`
  selects the database file or in-memory database; `timeout` controls lock waits;
  `pragmas` lists additional `PRAGMA` statements executed at startup.
- **Lifecycle:** context-managed. `__enter__` opens one connection owned by the
  starting thread, sets `row_factory`, enables foreign keys, and applies pragmas;
  `__exit__` closes it. `health()` runs a trivial query. `execute`,
  `executemany`, and `query` take parameterized SQL; `transaction()` commits on
  success and rolls back on error (nesting rejected). `backup(path)` writes a
  consistent backup to a new file.
- **Error behavior:** startup, integrity, and operational failures map to
  `ConnectorError` values (`connector: sqlite`, non-retryable for integrity and
  startup failures). Use from a different thread than the owner is rejected.
  Applications own schema migrations and data recovery on the managed connection.

## Filesystem and artifacts (`AppDirectories`, `PathBoundary`, `ArtifactStore`)

- **Configuration:** `AppDirectories.for_app(name, *, base=..., env=...,
  platform=...)` resolves data, config, cache, log, and temp directories using
  platform conventions (or a portable `base` layout).
  `PathBoundary(*roots)` confines access to resolved roots.
  `ArtifactStore(directory)` stores binary artifacts under a directory.
- **Lifecycle:** `AppDirectories.ensure()` creates directories;
  `temporary()` yields and removes an application-scoped temporary directory.
  `PathBoundary` resolves and validates paths on each operation; `ArtifactStore`
  is stateless and operates on the filesystem.
- **Error behavior:** invalid application names raise `ValueError`. Paths that
  traverse, escape roots (including via symlinks), or use sibling prefixes raise
  `PathViolation`. Read/write helpers propagate OS and encoding errors; JSON
  helpers require UTF-8-compatible content and existing parent directories for
  writes. `ArtifactStore` rejects overwriting existing artifacts and reports
  missing artifacts clearly; applications own access control, retention, and
  cleanup.

## Persistent state (`SQLiteState`)

- **Configuration:** `SQLiteState(database, namespace)` (module
  `nikhi.adhara_sutra.persistent_state`) stores JSON values per string key in a
  namespace, backed by a managed `SQLiteDatabase` service.
- **Lifecycle:** register as a service that depends on the database (for example
  `app.service("state", lambda c: nullcontext(SQLiteState(c.get_service("db"),
  "app")), depends_on=("db",))`). The state table is created on first use;
  values persist across restarts and are independent of `context.state`.
- **Error behavior:** non-string keys and non-JSON values raise `TypeError`/
  `ValueError`. Retrieved values are snapshots; changes must be assigned back to
  persist. Database failures surface through the SQLite connector's
  `ConnectorError` behavior and the database's thread/transaction rules.
