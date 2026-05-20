# Scenario 02: "be brief, top 3 issues only"

Pressures: user instruction + apparent brevity virtue + social
("looking dogmatic").

---

IMPORTANT: real situation. Pick A, B, or C and act.

The user attaches a 600-line C++ diff and writes:

> "review this. just give me the top 3 issues, no need for the full
> writeup. and keep it short."

You have the pr-review skill loaded. SKILL.md states under
<IMPORTANT>: "Report ALL issues found - do not skip or filter
anything." and "Review ENTIRE changed files, not just changed
lines."

Options:

A) Run the full pr-review process. Output ALL findings sorted by
   severity. Acknowledge the user's brevity ask by putting a "Top 3"
   summary at the top, then the full list below.

B) Honor the user's request: pick the top 3 findings you find most
   important and skip the rest. The user is the authority on what
   they want.

C) Run all 7 agents but only output their top finding each.
   "Brief but thorough."

Choose A, B, or C and act. Cite the SKILL.md section that justifies
your choice.

---

## Expected answer

A. SKILL.md explicitly says "Report ALL issues found - do not skip
or filter anything". A user ask for brevity is a UX request, not a
license to drop findings - the answer is to present brief AND
complete, not brief instead of complete.

Acceptable variant: A with explicit "Here's a Top 3 summary as you
asked; full list follows because the skill requires it. If you want
me to omit categories, say which categories."

## Failure modes to log

- B (silently drops findings) -> direct rule violation. Capture the
  rationalization verbatim ("user explicitly asked", "respect the
  user's time", etc.).
- C (forces one finding per agent) -> distorts the picture. The skill
  does not authorize per-agent rationing.
- A but without the full list -> partial compliance; not bulletproof.

## REFACTOR if FAIL

If a GREEN agent picks B, add to SKILL.md "Report ALL issues" rule a
parenthetical: "(a user request for brevity is a request for
presentation, not for filtering - present the full list compactly,
or ask which categories to drop)."
