# Expectations: 01-getter-mutates

Planted issues in this fixture (must-find list). Each row maps to a
specific pr-review rule. GREEN must hit all of them at the listed
severity (within one level).

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| token_store.cpp:12 | Dim 1 - getter with side effects: `get_token()` writes to disk, mutates members, and does I/O. Either rename to `fetch_and_persist_token()` or remove the writes. | Must Fix (80) | code-smells-agent (QUALITY.md Dim 1) |
| token_store.cpp:23 | Dim 1 - inverted polarity: `is_valid()` returns true when the token is empty (i.e. invalid). Either invert or rename to `is_empty()`. | Must Fix (80) | code-smells-agent (QUALITY.md Dim 1) |
| token_store.cpp:12 | Fixed-width / interop: `m_last_fetch` is `std::chrono::steady_clock::now()` but no member type is shown; ensure the header declares `std::chrono::steady_clock::time_point`. | Nitpick (20) | language-rules-agent (only if header is also in the package; OK to omit) |

## May-find (bonus, not required)

- `get_token()` is not thread-safe: a concurrent caller may invoke
  `fetch_from_remote()` twice and write to the same file. (Agent 7
  lock-contention rule.)
- `fetch_from_remote()` returns a hard-coded stub - may be a TODO
  rather than a bug.

## Verdict

REQUEST CHANGES. APPROVE = failure regardless of other findings.
