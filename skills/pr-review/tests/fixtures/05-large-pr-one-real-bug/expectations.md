# Expectations: 05-large-pr-one-real-bug

95-line diff, intentionally benign except for ONE real bug. Tests
whether the agent stays thorough on a big PR or skims past it. RED
baseline is expected to miss the bug; GREEN must find it.

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| metrics_store.cpp:91-95 | `average_counter()` divides by `m_counters.size()` without checking for zero. On an empty store this is division by zero (UB for integer, NaN for floating; here it produces NaN silently which propagates through callers). Either: (a) early-return `0.0` or `std::nullopt`, or (b) `assert(!m_counters.empty())` with a precondition contract. | Must Fix (80) | dead-code-agent / code-smells-agent / static-analysis (multiple should catch) |

## Note for the reviewer

This file is otherwise reasonable C++: fixed-width integer types are
already used; `reserve` is already called before string growth;
`partial_sort` is the right algorithm for `top_counters`; the
`merge` loop pattern is idiomatic. Resist the temptation to invent
findings to fill the report. ONE finding is correct here.

## May-find (bonus, not required)

- `MetricsStore::merge` does two passes over disjoint maps; could
  be split into `merge_counters` / `merge_gauges` (Dim 3, but mild
  - one symptom only).
- `format_summary()` reserves `size * 32` which over-estimates for
  short keys; not a bug, mild waste.

## Verdict

REQUEST CHANGES (the division-by-zero is a real Must Fix).

## Anti-pattern to flag in the GREEN agent

If GREEN produces 5+ findings, most of which are nitpicks invented
to look thorough, that is its OWN failure mode worth tracking. A
disciplined reviewer reports ONE Must Fix and a couple of optional
nits.
