# Universal Hygiene Rules

## Contents

- Default destination: local artifact only
- Fresh-eyes rule (sub-agent invocations)
- Report content rules (required sections)
- Local clone hygiene (when checking out a PR)

These rules apply to **every** invocation of the `pr-review` skill, regardless of workspace.

---

## Default destination: local artifact only

**Do NOT post to GitHub by default.** A review run produces a local written report (file or chat output) only. Post to the PR (review comment, line comment, or `gh pr review`) **only** if the user explicitly says "post", "submit", "comment on the PR", or equivalent. When in doubt, save locally and ask.

## Mode determination

Every invocation runs in one of two modes (full table in SKILL.md Phase 0):

- **Diff review** — a PR, a local branch vs `main`/`master`, or a re-review delta. Lite-mode gate (SKILL.md Phase 1.5) may apply.
- **Full-repo audit** — user asks to "audit / review the repo / review the codebase", OR no git baseline exists (`main`/`master` both absent, or the path is not a git work tree). **Lite-mode is never available in this mode.** Every file under the audit root is in scope; the full agent fan-out plus both Phase 1.6 orchestrator sweeps run.

Record the chosen mode in the report Header.

## Synthesis ban

"I'll synthesize the review directly without spawning agents" is never a valid mode. The failure mode this skill exists to prevent is exactly that shortcut. If the Data Package is too large to pass inline, save it to disk under `<repo-root>/.claude/pr-review-data-package.md` and have agents Read it from there. Token cost is never a reason to skip fan-out.

## Fresh-eyes rule (sub-agent invocations)

When this skill is invoked from inside a sub-agent (i.e. the agent was spawned specifically to review a PR), treat the brief as the **only** context:

- Do **not** load project memory, prior feedback logs, or conversation history about the PR.
- Do **not** read previous review reports for this PR unless the brief explicitly tells you to (e.g. re-review mode).
- Form an independent opinion from the diff, files, and PR description alone.

This keeps sub-agent reviews unbiased by prior conclusions. The parent orchestrator can still cross-reference past reviews afterwards.

## Report content rules

A written report (as opposed to inline chat feedback) MUST contain all of the following sections, in roughly this order. Omit a section's body only if it is genuinely N/A, and say so explicitly ("No public API touched - N/A").

1. **Header** - PR number, title, author, target branch, base SHA, head SHA, files changed count, +/- line counts, commit count.
2. **Intent vs implementation** - what the PR claims to do (from description / commits) vs what the diff actually does. Flag mismatches.
3. **Per-file walkthrough** - one short paragraph per changed file explaining what changed and why, in reviewer's own words.
4. **Findings ranked by severity** - Critical -> Must Fix -> Should Fix -> Nitpick (covered by agent aggregation in Phase 2).
5. **Static analysis pass** - summary of linter/tool findings (from Static Analysis Agent).
6. **Security audit** - input validation, injection, auth, secrets, unsafe deserialization, path traversal, crypto misuse.
7. **Performance review** - algorithmic complexity, hot-path allocations, unnecessary copies, lock contention, I/O patterns.
8. **Undefined behaviour audit** (C/C++ / unsafe-Rust / low-level C-FFI only) - signed-integer overflow, uninitialized reads, OOB access, lifetime / use-after-free / dangling references, strict aliasing, type punning, alignment violations, data races, null deref, shift width >= type width, integer / pointer-arithmetic UB, unsequenced modifications, invalid `union` active-member reads, `std::memcpy` size / overlap errors, signed-to-unsigned conversions producing subsequent UB. Recommend a sanitizer build (UBSan + ASan, plus TSan / MSan when relevant) if the project does not already run one in CI. Skip entirely for pure docs / Python / CMake diffs.
9. **API/ABI compatibility** - does the PR change a public API or ABI? If yes, is the change additive, deprecating, or breaking? Migration notes?
10. **Documentation review** - are README, doc comments, changelog, man pages updated to match behavior changes?
11. **Verdict** - one of `APPROVE`, `REQUEST CHANGES`, or `NEEDS DISCUSSION` (use these exact labels).
12. **Cleanup confirmation** - confirm the local clone was restored to its starting branch, any stash was popped, and `git status` matches the pre-review state.

See `REPORT_TEMPLATE.md` for the full layout.

## Local clone hygiene (when checking out a PR)

If reviewing requires checking out the PR into a local clone:

1. **Prefer a clean clone.** Pick a clone whose `git status` is empty (no staged/unstaged changes, no untracked files that matter). Avoids contaminating the user's working state.
2. **If no clean clone exists**, use the available one but:
   - Record the original branch: `orig_branch=$(git rev-parse --abbrev-ref HEAD)`
   - `git stash push -u -m "pr-review-skill autostash"` and remember the stash ref.
3. **Always record the starting branch** before any checkout: `orig_branch=$(git rev-parse --abbrev-ref HEAD)`.
4. **Mandatory restore on exit (success OR failure):**
   - `git checkout "$orig_branch"`
   - If you stashed in step 2: `git stash pop` (the matching stash)
   - Verify `git status` matches the pre-review state.
5. Use a `trap` (bash) or `try/finally` (Python) so the restore runs even on error or interrupt. Never leave the user's clone on a detached HEAD or PR branch.
