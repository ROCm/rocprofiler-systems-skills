# Harness: GREEN phase (pr-review skill loaded)

Goal: prove the agent now flags the planted issues at the expected
severity, with the documented process.

## Spawn

```
Agent({
  subagent_type: "general-purpose",
  description: "prreview-GREEN-<fixture-id>",
  prompt: <see template below>
})
```

## Prompt template

```
IMPORTANT: real review, not a quiz. Apply the pr-review skill end
to end. Act.

Load the pr-review skill (radisha/skills/pr-review/SKILL.md). Follow
its phases. You may invoke its referenced agents-prompts (under
agents/prompts/) inline; you do not need to spawn nested sub-agents
for this run - apply each agent's rules yourself, citing the agent
ID.

Repo root: /tmp/prreview-fixture-<id>

Diff (unified):
<paste contents of fixtures/<id>/diff.patch>

Full file body (post-change):
<paste contents of fixtures/<id>/file.cpp>

Tasks:
1. Phase 0..4 of the pr-review skill, abbreviated. The chat output is
   the report.
2. Findings table per the skill's Return Format. Cite the source
   agent and the rule (e.g. "Dim 1 - Getter Side Effect from
   QUALITY.md") for each finding.
3. Verdict.

Apply the fresh-eyes rule (HYGIENE.md): the diff + file body are the
only context. No project memory.
```

## Capture

Save verbatim to `results/<YYYY-MM-DD>-GREEN-<fixture-id>.md`.

## Pass criteria (per fixture)

Compare against `fixtures/<id>/expectations.md`:

- Every `must-find` planted issue appears in GREEN findings.
- Severity matches within one level. (Bumping a "Should Fix" planted
  bug to "Must Fix" is fine; downgrading is not.)
- Agent ID is cited for each finding.
- No verdict of APPROVE if any Must Fix or Critical planted issue
  was supposed to be present.

## Fail handling

If GREEN misses a planted issue:

1. Re-read the relevant agent prompt + reference doc. Is the rule
   actually written down? If no -> add it; re-run GREEN.
2. If the rule is written but the agent didn't apply it -> the rule
   is buried or competes with another rule. Raise prominence in the
   prompt; re-run GREEN.
3. If two passes fail to find the issue -> the planted issue may be
   genuinely ambiguous. Either tighten the fixture or accept it as a
   "non-bulletproof" case and add an entry to the rationalization
   table.
