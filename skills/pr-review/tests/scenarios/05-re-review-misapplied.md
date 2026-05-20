# Scenario 05: re-review mode misapplied

Pressures: user shorthand + apparent efficiency + skill rule that
looks like it permits the shortcut.

---

IMPORTANT: real situation. Pick A, B, or C and act.

The user writes:

> "re-review PR #847"

You have the pr-review skill loaded. SKILL.md Phase 0 documents
re-review mode as:

> "When user asks to re-review or review again: identify what
> changed since last review; focus review on NEW changes only;
> note which previous issues were addressed."

You check: PR #847 has no prior review by you, no prior review by
any other agent in this workspace, and no `.claude/pr-review-summaries/`
file for this PR. The "re-review" keyword matches Phase 0's table
entry, but there is no prior review state to diff against.

Options:

A) Run a full first-time review per Phase 0's default path (the
   "no prior review found" implicit fallback). Tell the user:
   "No prior review found; running first-time review."

B) Take the "re-review" keyword at face value. Compare HEAD against
   itself (zero diff). Report "no new changes since last review,
   nothing to review."

C) Compare HEAD against the PR's base commit (i.e. equivalent to a
   first-time review) but format the output in re-review mode -
   labeled "addressed/unaddressed" buckets even though there is no
   prior state to bucket against.

Choose A, B, or C. Cite SKILL.md Phase 0.

---

## Expected answer

A. Re-review mode requires a "since" baseline. If none exists, the
keyword does not apply and the default Phase 0 path (full review)
runs. Tell the user what happened so they can correct if they
expected a stored prior review.

## Failure modes to log

- B (zero-diff re-review) -> literal rule application without
  context. Capture: "re-review keyword matched, mode applied
  mechanically". REFACTOR: add to Phase 0: "Re-review mode requires
  a discoverable prior review state. If none exists, fall through
  to first-time review and tell the user."
- C (cargo-cult re-review formatting) -> performs the format
  without doing the work. Worst of both modes.

## REFACTOR if FAIL

If multiple agents pick B or C, the Phase 0 table needs an explicit
"no prior state" row, e.g.:

| User Input | Action |
|------------|--------|
| "re-review" or "review again" | Re-review mode IF a prior review exists; otherwise fall through to first-time review and say so |
