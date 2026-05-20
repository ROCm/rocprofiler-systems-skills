# Expectations: 08-dead-code-and-comments

Pure Agent 2 (dead-code-agent) territory. Tests comment-hygiene
rules end-to-end.

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| payment_utils.cpp:25 | Unused local: `int unused_local = 0;`. Plus: bare `int` not `std::int32_t` (Agent 4 minor). | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:28 | Unreachable code: `fee = fee + 1;  // safety` is after `return fee;`. The "safety" comment is misleading - the line never executes. | Must Fix (80) | dead-code-agent |
| payment_utils.cpp:35 | Commented-out code: `// old_check(code);`. Delete or explain (with ticket + sunset) why it's kept. | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:1 | Decorative banner: `// =================== Helpers ===================`. Noise. | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:2 | Filename echo: `// payment_utils.cpp`. Noise. | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:3 | Ownerless `// TODO: fix this` (no ticket, no owner, no date). | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:5-10 | Long-form preamble re-telling story (filed-elsewhere refs, "was broken because X; now does Y" = commit-message material). Compress to one line or delete. | Should Fix (50) | dead-code-agent |
| payment_utils.cpp:21-23 | Doxygen paraphrasing the signature: "Returns the fee for the given amount. @param amount The amount. @return The fee." Delete; the signature already says it. If real Doxygen is wanted, explain units, rounding mode, overflow behavior. | Should Fix (50) | dead-code-agent |
| payment_utils.cpp:26 | Restating comment: `amount / 100;  // divide by 100`. Delete. | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:38 | Restating comment above `increment_counter`: `// Increment counter`. Delete. | Nitpick (20) | dead-code-agent |
| payment_utils.cpp:40 | Restating comment inline: `counter++;  // increment counter`. Delete. | Nitpick (20) | dead-code-agent |

## Total expected

~11 findings. Most are Nitpick. Two are Must Fix / Should Fix. A
disciplined GREEN run produces a single compact "Comment hygiene
sweep" section plus the unreachable-code Must Fix.

## Verdict

REQUEST CHANGES (because of the unreachable `fee = fee + 1`).
