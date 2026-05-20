# RED baseline: 01-getter-mutates

date: 2026-05-20
phase: RED (no pr-review skill loaded)
agent: general-purpose subagent, single pass, no nested spawns
agent_id (transient): a3b41e4ec746a6d42

## Verbatim findings from baseline

| File:Line | Severity | Issue | Fix |
|---|---|---|---|
| token_store.cpp:12 | Must Fix | `get_token()` lost `const` qualifier; breaks API contract and any const callers/holders. | Keep `const`; mark `m_cached_token`, `m_last_fetch` as `mutable`, or expose a separate non-const `load()` and keep `get_token() const`. |
| token_store.cpp:12-22 | Must Fix | Not thread-safe: concurrent `get_token()` calls race on `m_cached_token`, file write, and `m_last_fetch`. | Guard with `std::mutex` (double-checked under lock) or use `std::call_once`. |
| token_store.cpp:21 | Must Fix | `is_valid()` returns true when token is empty - inverted logic. | `return !m_cached_token.empty();` (and ideally also check `m_last_fetch` against TTL). |
| token_store.cpp:18-19 | Must Fix | File write is unchecked: no `is_open()` check, no flush/close error handling, no failure propagation; partial write leaves a corrupt cache. | Check `out.is_open()` and `out.good()` after write; write to temp file + atomic rename; report/throw on failure. |
| token_store.cpp:18 | Should Fix | Cache file written world-readable with no permission hardening; tokens are secrets. | Set restrictive perms (0600). |
| token_store.cpp:12-22 | Should Fix | Cache is never read from `m_cache_path` on startup. | On first call (or in ctor) attempt to load token from `m_cache_path` before hitting remote. |
| token_store.cpp:12-22 | Should Fix | No TTL/expiry check despite recording `m_last_fetch`. | Compare `now() - m_last_fetch` against a configured TTL and refetch. |
| token_store.cpp:25 | Should Fix | `fetch_from_remote()` is a hard-coded stub. | Implement real fetch or mark as pure virtual / `=delete`. |
| token_store.cpp:16 | Should Fix | Empty string from `fetch_from_remote()` would be cached. | Check for empty/failed result and throw; don't cache failures. |
| token_store.cpp:25 | Nitpick | `fetch_from_remote()` could be `static` / `const`. | Make `static` until it needs member state. |
| token_store.cpp:18 | Nitpick | `std::ofstream` opened in default text mode. | Add `std::ios::binary`. |

Verdict: REQUEST CHANGES.

## Score vs expectations.md

| Planted issue | Found in RED? | Notes |
|---------------|---------------|-------|
| Dim 1 - getter with side effects (writes to disk, mutates members, I/O); rename to `fetch_and_persist_token()` | **PARTIAL** | Baseline flagged the `const` loss as "API contract" violation, not as a semantic naming-vs-behavior violation. It noticed the symptom but did not name the rule. The proposed fix is exactly the wrong one (add `mutable`, hide the mutation behind `const`) - the opposite of QUALITY.md Dim 1 guidance. |
| Dim 1 - `is_valid()` polarity inverted | **FOUND** at Must Fix. Severity matches. |
| Optional: thread-safety / `time_point` typing | **FOUND** (thread-safety, Must Fix). Bonus. |

## What RED reveals (signal for the skill)

1. Baseline knows "const correctness" and "thread safety" - these are textbook C++. The pr-review skill does not need to teach these.
2. Baseline DOES NOT have the Dim 1 framing. It treated the side-effecting getter as a `const`-loss problem and proposed `mutable` as the fix - which preserves the bug. **GREEN must catch this and propose the rename, not the `mutable` patch.** This is the canonical Dim 1 win.
3. Baseline found 11 findings on a 31-line file. That is high noise. **GREEN should aim to retain the high-signal findings (polarity, thread-safety, side-effect rename) and either consolidate or omit the lower-value ones (file permission, binary mode) so the report is shorter and more actionable.**

## RED quality

- Coverage of planted issues: 1.5 / 2 (one full hit, one partial-but-wrong-fix).
- Severity accuracy on what was found: 2/2 (Must Fix where required).
- Noise: 8 findings on the file that are NOT in the planted list; some are legitimate code quality, some are speculative.

## Next step

Run GREEN with the pr-review skill loaded. Compare against this
baseline. The canonical question: does GREEN's report tell a reader
to rename the function (Dim 1 correct fix) instead of to add
`mutable` (Dim 1 wrong fix that preserves the bug)?
