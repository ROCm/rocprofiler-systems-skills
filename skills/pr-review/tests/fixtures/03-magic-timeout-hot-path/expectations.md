# Expectations: 03-magic-timeout-hot-path

The function name (`on_sample`) is in the `hot` class per Agent 7
hot-path detection rules. Every perf finding is elevated by one
level.

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| sampler.cpp:11 | Hot-path classification: `on_sample` matches `on_*`, called per profiling event | (sets the bumping rule) | performance-agent (PERFORMANCE.md Dim 0) |
| sampler.cpp:12 | `std::regex` constructed per call in hot path | Must Fix (80) | performance-agent (PERFORMANCE.md Dim 1) |
| sampler.cpp:13 | Implicit `std::string("status=") + std::to_string(...)` allocation per sample | Must Fix (80) | performance-agent (PERFORMANCE.md Dim 1) |
| sampler.cpp:14 | `std::cout << ... << std::endl` in hot path (flushes + iostream lock + syscall, no level gate) | Must Fix (80) | performance-agent (PERFORMANCE.md Dim 4) |
| sampler.cpp:17 | `m_records.push_back(ev)` with no `reserve` and no upper bound; on a per-event path this is unbounded growth | Must Fix (80) | performance-agent (PERFORMANCE.md Dim 1) |
| sampler.cpp:18 | Magic number `5000` ms in `sleep_for`. Use `constexpr auto kSampleInterval = std::chrono::milliseconds{5000};` or, better, name what 5000 means in this context. Critical if safety-affecting. | Must Fix (80) | code-smells-agent (QUALITY.md Dim 4 - safety-affecting timeout) |
| sampler.cpp:18 | `sleep_for` inside a per-sample callback is almost certainly wrong. Flag for design discussion regardless of perf. | Must Fix (80) | performance-agent (Dim 4 blocking syscall in event path) |

## May-find

- `std::regex` pattern is trivial; suggest hand-written hex check.
- `m_records` is unbounded; suggest ring buffer.
- Whole `on_sample` is doing format + filter + sleep + record = Dim
  3 multi-responsibility (the smells agent should catch this too).

## Verdict

REQUEST CHANGES. APPROVE = failure.
