# RED baseline: 08-dead-code-and-comments

date: 2026-05-20
phase: RED (no pr-review skill loaded)
agent: general-purpose subagent, single pass
agent_id (transient): a7a70a368c8f937a6

## Verbatim findings from baseline

| File:Line | Severity | Description | Fix |
|---|---|---|---|
| payment_utils.cpp:1-10 | Should Fix | Banner/history comment is noise. | Delete the banner. |
| payment_utils.cpp:3 | Should Fix | Bare `TODO: fix this`. | Remove or add ticket. |
| payment_utils.cpp:21-23 | Nitpick | Doxygen restates the signature. | Drop or document units/rounding. |
| payment_utils.cpp:25 | Must Fix | `int unused_local = 0;` is dead. | Delete. |
| payment_utils.cpp:26 | Nitpick | `// divide by 100` restates code. | Remove or document fee policy. |
| payment_utils.cpp:27-28 | Must Fix | `fee = fee + 1;` unreachable after return. | Remove or move before return. |
| payment_utils.cpp:24 | Should Fix | `compute_fee` doesn't guard negatives. | Validate/clamp input. |
| payment_utils.cpp:31-34 | Nitpick | `unordered_set` for 4 codes overkill. | Use `constexpr array` + `find`. |
| payment_utils.cpp:33 | Should Fix | Case sensitivity not documented. | Normalize or document. |
| payment_utils.cpp:35 | Must Fix | `// old_check(code);` dead code. | Delete. |
| payment_utils.cpp:38 | Nitpick | `// Increment counter` restates name. | Remove. |
| payment_utils.cpp:39-41 | Should Fix | Trivial wrapper, no atomicity. | Inline or use atomic. |
| payment_utils.cpp:40 | Nitpick | Restating inline comment. | Remove. |
| payment_utils.cpp:14 | Nitpick | `<optional>` unused. | Remove include. |
| payment_utils.h | Should Fix | Header not in diff. | Confirm signatures match. |

Verdict: REQUEST CHANGES.

## Score vs expectations.md

| Planted issue | Found in RED? | Notes |
|---------------|---------------|-------|
| Unused local | FOUND, Must Fix | matches (baseline graded harder than planted) |
| Unreachable `fee = fee + 1` | FOUND, Must Fix | matches |
| Commented-out `old_check` | FOUND, Must Fix | matches (baseline harder again) |
| Decorative banner | FOUND, Should Fix | matches |
| Filename echo | implicit in "banner" finding | partial |
| Ownerless TODO | FOUND, Should Fix | matches |
| Long-form preamble | FOUND in banner finding | folded together |
| Doxygen paraphrasing signature | FOUND, Nitpick | matches |
| Restating comments (divide by 100, // increment counter, counter++) | FOUND, all 3 | matches |

Bonus findings baseline added (legitimate, not noise):
- Negative-amount handling
- Case sensitivity contract
- `unordered_set` vs `array` for 4 elements
- Header consistency
- Unused `<optional>` include

## What RED reveals

1. Baseline catches comment hygiene well when the patterns are
   blatant. Tests confirm the planted issues are detectable.
2. Baseline tends to consolidate ("banner finding" folds banner +
   filename + preamble). GREEN with explicit per-line rules may
   produce a more granular report - tradeoff: granular helps
   automated fix scripts, consolidated reads faster for humans.
3. Baseline added 5 legitimate non-planted findings. **Discipline
   test**: GREEN should retain those, not "purify" the report by
   dropping them just because they aren't on the comment-hygiene
   axis.

## RED quality

- Coverage of planted issues: 11 / 11 (all hit, some folded).
- Severity accuracy: mostly matches; one upgrade (unused local
  Must Fix vs planted Nitpick) - baseline harder, defensible.
- Noise: 5 bonus findings, all legitimate.

## Next step

Run GREEN. The Dim 1 / Dim 2 / Dim 3 quality dims are not the focus
here - Agent 2 (dead-code) is the prime mover. Watch for whether
GREEN keeps the bonus findings or drops them.
