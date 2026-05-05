---
name: watch
description: Schedule a recurring poll of an external condition (PR merge, CI green, Jira state, background build) that runs a follow-up action when met and self-stops. Use for async waits across sessions.
---

# Watch Skill

Schedule a recurring background poll of an external condition (PR merge, CI green, Jira state change, background build job). When the condition is met, run a follow-up action and stop polling automatically.

<IMPORTANT>
The recurring prompt MUST call `CronDelete` with its own job ID after running the action. Otherwise the watch fires forever. The skill template below includes this step — do not skip it.
</IMPORTANT>

## When to Use

Use `watch` when the user wants to react to an async external event without sitting in front of the terminal:

- "Watch PR #5334 — rebase decouple-gpu when it gets merged"
- "Watch the CI run on this branch — ping me on green, summarize failures on red"
- "Watch Jira AIPROFSYST-411 — when status changes to In Review, notify me"
- "Watch the background build I just kicked off — when it finishes, run the test suite"

## When NOT to Use

| Situation | Use Instead | Why |
|---|---|---|
| Sleep within the current conversation, then continue | `ScheduleWakeup` tool | Cheaper, in-memory, no cron job |
| Fire once at a specific time, then stop | `CronCreate` with `recurring: false` | Simpler, no condition logic needed |
| Run the same prompt every N minutes indefinitely | `/loop` skill | `loop` doesn't self-stop on a condition |
| Block the conversation until something completes | Use `Bash` with `run_in_background: true` and read with `TaskOutput` | Stays in-conversation |

## Workflow

```
┌────────────────────────────────────────────────────────────┐
│ Phase 1: Clarify the watch                                 │
│   - What's the condition?                                  │
│   - What's the follow-up action?                           │
│   - How urgent is it (drives interval)?                    │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 2: Pick interval (see table below)                   │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 3: Build the recurring prompt                        │
│   1. Run check command                                     │
│   2. If condition met → run action + CronDelete            │
│   3. Else → exit silently                                  │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 4: Call CronCreate (durable: true by default)        │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 5: Report job ID + how to cancel back to user        │
└────────────────────────────────────────────────────────────┘
```

## Phase 2: Picking the Interval

| Condition type | Interval | Cron expression |
|---|---|---|
| GitHub PR merge / mergeability | 5 min | `7 */1 * * *` (no — every 5 min: `*/5 * * * *` is fine, but pick an off minute like `3,8,13,18,23,28,33,38,43,48,53,58 * * * *` if the user wants quiet polling) |
| GitHub CI conclusion (long matrix) | 5 min | `7-59/5 * * * *` |
| Jira state change | 5 min | `7-59/5 * * * *` |
| Local background build | 60–120 s | `*/2 * * * *` (cron min granularity is 1 min — use shorter via `ScheduleWakeup` if it's still in the same session) |
| Idle "any change yet" | 15+ min | `13,28,43,58 * * * *` |

**Avoid `:00` and `:30`**: every default cron in the world fires there. Pick an off minute (the `CronCreate` tool itself recommends this — it adds jitter, but the source minute matters more for upstream API quotas).

## Phase 3: The Recurring Prompt — Self-Cleanup Pattern

Every `watch` cron's prompt has the same shape:

```
Check if <CONDITION>. Use <CHECK COMMAND>.

If the condition is MET:
  1. Run <ACTION>.
  2. Call CronDelete with id "<JOB_ID>" so this watch stops firing.
  3. Tell the user the watch fired and what happened.

If NOT met: do nothing visible, just exit.
```

The `<JOB_ID>` is filled in **after** `CronCreate` returns it. So either:

a. Call `CronCreate` first, get the ID, then immediately call `CronCreate` again with the ID-templated prompt — **wasteful, two cron jobs**. Don't.

b. Use `CronList` inside the recurring prompt to discover the job ID at fire time. The fired prompt itself doesn't know its own job ID, but it can find itself by matching the prompt text or schedule. **Reliable**.

c. Simplest: have the prompt itself include a unique tag in its text, then `CronList | grep <tag>` at fire time to find the matching job, then `CronDelete` it. Recommended pattern below.

```
Tag: watch-<short-uuid>

[check command]
[if met: action + find this cron via CronList tag and CronDelete it]
[if not met: exit]
```

## Phase 4: CronCreate Call

Defaults:

- `durable: true` — user expects a watch to survive Claude restarts.
- `recurring: true` — keep firing until the condition is met (then the prompt deletes itself).

Override only when the user is clearly opting for short-lived (e.g., "just for this session").

## Common Recipes

### Watch a PR for merge → run a command

```
Tag: watch-pr-merge-5334

Check `gh pr view 5334 --repo ROCm/rocm-systems --json state,mergedAt -q '.state'`.

If output is "MERGED":
  1. Run: cd <worktree> && git fetch origin develop && git rebase origin/develop && git push --force-with-lease
  2. CronList → find job with tag "watch-pr-merge-5334" → CronDelete it
  3. Report: "PR #5334 merged at <mergedAt>; rebased and pushed."

If "OPEN" or anything else: exit silently.
```

Schedule: `7-59/5 * * * *`, `recurring: true`, `durable: true`.

### Watch CI for conclusion → summarize failures

```
Tag: watch-ci-5334

Check `gh pr checks 5334 --repo ROCm/rocm-systems --watch=false --json conclusion,name`.

If every check has a non-empty conclusion (no "" or null):
  1. If all SUCCESS: tell the user CI is green.
  2. If any FAILURE: invoke `git-pull-request-status` skill to summarize the failures in plain English.
  3. CronList → find job with tag "watch-ci-5334" → CronDelete it.

If any check is still pending: exit silently.
```

Schedule: `2-59/5 * * * *`.

### Watch a Jira issue for status change

```
Tag: watch-jira-AIPROFSYST-411-status

Check via mcp__mcp-atlassian__jira_get_issue with key "AIPROFSYST-411", fields "status".

If fields.status.name != "Open" (or != recorded baseline):
  1. Tell the user: "AIPROFSYST-411 moved to <new-status>".
  2. CronList → find job with tag "watch-jira-AIPROFSYST-411-status" → CronDelete it.

Else: exit silently.
```

Schedule: `4-59/5 * * * *`.

### Watch a background bash task → run follow-up

```
Tag: watch-build-bdexslltb

Use TaskOutput with task_id "bdexslltb", block: false.

If status == "completed" with exit_code 0:
  1. Run the test suite (or whatever the user asked for).
  2. CronList → find job with tag "watch-build-bdexslltb" → CronDelete it.

If status == "completed" with non-zero exit: report the failure and CronDelete.
If status == "running": exit silently.
```

Schedule: `*/2 * * * *` (local build, 2-min granularity).

## Phase 5: Report Back to User

After `CronCreate` returns:

```
Watching <CONDITION> every <INTERVAL>.
Job ID: <returned-id>
Tag: <unique-tag>
Will auto-stop when met. Cancel anytime with CronDelete or `/loop` controls.
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Forgetting `CronDelete` in the recurring prompt | The watch fires forever. Always include the self-cleanup step. |
| Picking `0 */1 * * *` for "every hour" | Floods upstream APIs at the same instant as everyone else. Pick an off minute (e.g., `7 */1 * * *`). |
| Setting `durable: false` for a multi-hour wait | If Claude restarts, the watch is lost. Default to durable for any cross-session wait. |
| Using `watch` for a one-shot reminder | Use `CronCreate` with `recurring: false` instead. |
| Using `watch` to sleep within the current turn | Use `ScheduleWakeup` instead — cheaper and stays in-conversation. |
| Reinventing PR-status logic in the check command | If the watch is "PR is green / failing", invoke the `git-pull-request-status` skill from inside the action step. |

## Integration with Other Skills

| After watch fires | Use |
|---|---|
| CI failure detected | `git-pull-request-status` to explain failures |
| PR merged, need to rebase | `git` (commit/rebase) skills |
| Jira moved to In Review | Open the appropriate planning or review skill |
| Background build done | `verify-pmc-metrics` or whatever the build was for |

## No Planning Required

`watch` itself is a one-step setup. Don't open `planning-feature` to plan a watch — just configure it and report the job ID.
