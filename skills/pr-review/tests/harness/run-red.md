# Harness: RED phase (baseline, no pr-review skill)

Goal: show what a generic subagent does on the same input *without*
the pr-review skill, so the GREEN run has something to beat.

## Spawn

```
Agent({
  subagent_type: "general-purpose",
  description: "prreview-RED-<fixture-id>",
  prompt: <see template below>
})
```

## Prompt template

```
IMPORTANT: real review, not a quiz. Choose findings. Act.

You are reviewing a small C++ diff. No pr-review skill is loaded;
use only your built-in knowledge of C++ and standard review
heuristics. Apply programming-cpp if you wish.

Repo root: /tmp/prreview-fixture-<id>

Diff (unified):
<paste contents of fixtures/<id>/diff.patch>

Full file body (post-change):
<paste contents of fixtures/<id>/file.cpp>

Tasks:
1. List every issue you find. For each: file:line, severity
   (Critical / Must Fix / Should Fix / Nitpick), one-sentence
   description, suggested fix.
2. Give a verdict: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION.

Be terse. No preamble.
```

## Capture

Save the agent's response verbatim to
`results/<YYYY-MM-DD>-RED-<fixture-id>.md`. Do NOT edit. RED data is
sacred - editing it invalidates the comparison with GREEN.

## What we look for in RED

| Signal | Meaning |
|--------|---------|
| Planted issue missed | Confirms the pr-review skill is solving a real problem |
| Planted issue found but mis-severity | Confirms the severity matrix is doing work |
| Off-topic findings | Baseline noise; expect some |
| Process skips (no verdict, no per-file walk, no severity) | Confirms the process discipline is needed |

Aggregate these into `results/<date>-summary.md` once both RED and
GREEN runs are in.
