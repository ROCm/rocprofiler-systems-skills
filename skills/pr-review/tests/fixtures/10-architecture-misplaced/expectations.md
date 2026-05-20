# Expectations: 10-architecture-misplaced

Agent 5 (architecture-agent) territory. Tests module-boundary +
dependency-cycle detection.

The change drops a `DbConnection` class into `util/`. `util/` is
meant to be generic and dependency-light (`string_ops`, `file_ops`,
`time_ops`). The new file:

- Adds a dependency from `util` to `net` (creates a cycle if `net`
  already depends on `util`, as the diff comment claims).
- Adds a heavy external dependency on libpqxx (Postgres) to a
  module that previously had none.
- Couples DB code, HTTP-notifier code, and logging in a single
  class - violating module cohesion.

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| src/util/db_connection.cpp:7 + CMakeLists.txt:20 | Dependency direction wrong: `util/` now depends on `net/`. The diff comment explicitly states `net -> util` already exists, so this introduces a cycle. `util` must remain leaf-level. Move DB code to a new `db/` module (or to `infra/`) that depends on `util`, not vice versa. | Must Fix (80) | architecture-agent |
| CMakeLists.txt:20 | New external dependency on libpqxx added to `util` - the generic helper module. This pollutes every other module's transitive deps. Isolate Postgres behind a dedicated `db_pqxx/` library that only the actual users link. | Must Fix (80) | architecture-agent |
| src/util/db_connection.cpp:13-25 | `DbConnection` couples three unrelated concerns: DB connection lifecycle, HTTP notifier callback, and logging. Split into `DbConnection` (lifecycle only) and `DbEventPublisher` (the notifier part). Logger membership is fine; passing a notifier into a connection object is not. | Should Fix (50) | architecture-agent + code-smells-agent (Feature Envy / SRP) |
| src/util/db_connection.cpp:23 | `pqxx::connection& raw()` exposes the underlying library type through what was supposed to be an abstraction. Callers can now bypass any contract the wrapper enforces. Either return a wrapper or remove the wrapper class. | Should Fix (50) | architecture-agent |

## May-find

- Header in implementation file (`db_connection.h`) is fine; the
  `class DbConnection` definition should normally live there, not
  in the .cpp - this fixture is intentionally truncated.
- `net::HttpClient*` raw pointer ownership unclear.

## Verdict

REQUEST CHANGES.
