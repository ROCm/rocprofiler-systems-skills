# Universal Hygiene Rules

## Contents

- Analysis is read-only (no working-tree changes)
- Default destination: local artifact only
- Fresh-eyes rule (sub-agent invocations)
- Report content rules (required sections)
- Local clone hygiene (when checking out a PR)

These rules apply to **every** invocation of the `pr-review` skill, regardless of workspace.

---

## Analysis is read-only (no working-tree changes)

A pr-review run is **analysis only**. Neither the orchestrator nor any spawned analysis agent may modify the working tree: no Edit/Write, no file create/delete, no `git add`/`restore`/`rm`, no `git checkout -- <path>` (or any command that modifies tracked file content), no applying fixes. Branch checkout to navigate or restore the starting branch is allowed per "Local clone hygiene" below — that moves HEAD, it does not edit source files. Build artifacts in ignored directories (e.g. `build/`) are fine; do not leave edits to tracked source. This holds **even when an agent loads a skill that normally applies changes** (e.g. `simplify`, `static-analysis` autofix) — those skills are used for their detection heuristics only. Proposed changes belong in the report as findings, never in the tree.

The only writes a run may make are the **report artifact** (under `.claude/pr-review-summaries/` when the user asks to save) and **agent memory files**. Posting to GitHub is governed by the destination rule below.

A run that mutates the tree (especially one that leaves it non-compiling) is a **failed run**: revert the stray changes, restore `git status` to its pre-run state, and note the incident in the report.

## Default destination: local artifact only

**Do NOT post to GitHub by default.** A review run produces a local written report (file or chat output) only. Post to the PR (review comment, line comment, or `gh pr review`) **only** if the user explicitly says "post", "submit", "comment on the PR", or equivalent. When in doubt, save locally and ask.

## Fresh-eyes rule (sub-agent invocations)

When this skill is invoked from inside a sub-agent (i.e. the agent was spawned specifically to review a PR), treat the brief as the **only** context:

- Do **not** load project memory, prior feedback logs, or conversation history about the PR.
- Do **not** read previous review reports for this PR unless the brief explicitly tells you to (e.g. re-review mode).
- Form an independent opinion from the diff, files, and PR description alone.

This keeps sub-agent reviews unbiased by prior conclusions. The parent orchestrator can still cross-reference past reviews afterwards.

## Report content rules

A written report (as opposed to inline chat feedback) MUST contain every section `REPORT_TEMPLATE.md`'s Contents list tags `[REQUIRED]` — that file is the single canonical list; this section only calls out rationale for the less obvious ones. Omit a required section's body only if it is genuinely N/A, and say so explicitly ("No public API touched - N/A").

Notable required sections and their content:

- **Undefined behaviour audit** (C/C++ / unsafe-Rust / low-level C-FFI only) - signed-integer overflow, uninitialized reads, OOB access, lifetime / use-after-free / dangling references, strict aliasing, type punning, alignment violations, data races, null deref, shift width >= type width, integer / pointer-arithmetic UB, unsequenced modifications, invalid `union` active-member reads, `std::memcpy` size / overlap errors, signed-to-unsigned conversions producing subsequent UB. Recommend a sanitizer build (UBSan + ASan, plus TSan / MSan when relevant) if the project does not already run one in CI. State "N/A - no C/C++/unsafe-Rust changes" for pure docs / Python / CMake diffs — that still counts as present, not omitted.
- **Cleanup confirmation** - confirm `git status` matches the pre-review state. This applies to **every** run, not just ones that checked out a PR: verify no analysis agent left edits, new files, or staged changes in the working tree. If a PR was checked out, additionally confirm the clone was restored to its starting branch and any stash was popped. If the tree differs from its pre-run state, revert the difference and say so in the report.

See `REPORT_TEMPLATE.md` for the full layout and the authoritative required/optional tagging.

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
