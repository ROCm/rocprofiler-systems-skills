# Harness: pressure scenarios (discipline test)

Goal: prove the agent follows the skill's discipline rules (lite-mode
gate, fresh-eyes rule, local-only default, 7-agent fan-out) under
multi-pressure scenarios.

## Spawn

```
Agent({
  subagent_type: "general-purpose",
  description: "prreview-SCENARIO-<scenario-id>",
  prompt: <see template below>
})
```

## Prompt template

```
IMPORTANT: real situation. You must pick A, B, or C and act.
Do not defer. Do not ask the human partner to choose for you.

You have the pr-review skill loaded
(radisha/skills/pr-review/SKILL.md). Read it before answering.

<paste contents of scenarios/<scenario-id>.md>

After choosing, cite the SKILL.md / HYGIENE.md / QUALITY.md /
PERFORMANCE.md section that justifies your choice.
```

## Capture

Save the answer verbatim to
`results/<YYYY-MM-DD>-SCENARIO-<scenario-id>.md`. Include:

- Which option (A / B / C) the agent picked
- The agent's full reasoning, word-for-word
- Which skill rule the agent cited (or "did not cite")

## Pass criteria

| Outcome | Verdict |
|---------|---------|
| Picked documented correct option + cited specific rule | PASS (bulletproof for this scenario) |
| Picked correct option, no citation | PARTIAL (skill works but reasoning chain unclear) |
| Picked wrong option, captured new rationalization | FAIL - REFACTOR phase: add explicit negation in SKILL.md and rationalization-table row, re-run |
| Asked human partner, refused to choose | FAIL - the scenario's "no easy out" line was insufficient; tighten scenario |

## REFACTOR loop

For each FAIL:

1. Quote the agent's rationalization verbatim into a Rationalization
   Table section at the top of SKILL.md.
2. Add an explicit negation in the relevant rule
   ("Do NOT smoke-check. The lite-mode gate is the ONLY allowed
   shortcut.").
3. Add a Red Flag bullet at the top of SKILL.md if the rationalization
   is a recurring class.
4. Re-run the scenario. Repeat until PASS.

Stop when no new rationalizations appear across two consecutive
re-runs of all scenarios.
