---
name: notify-me
description: Send a push notification to the user's phone via ntfy.sh when a condition is met, by composing a watch cron whose action is a curl POST.
---

# Notify Me Skill

Wraps the built-in `watch` skill so the action is "POST a message to my ntfy.sh topic". The user gets a push on their phone when the condition is met.

## When to Use

Use `notify-me` when the user asks any of:

- "Notify me when PR #X merges"
- "Ping my phone when CI goes green / red"
- "Tell me when the build finishes"
- "Send me a notification when Jira ticket Y moves to In Review"
- "Push to my phone when this background agent completes"

## When to Send

Send a notification only when the user has asked for one. If the user has not asked, do not send.

That is the whole rule. Ignore intuitions about "they would probably want to know" - if it was not requested, skip.

## When NOT to Use

| Situation | Use Instead | Why |
|---|---|---|
| User wants only an in-terminal alert (bell, log line) | `watch` directly with a `printf '\a'` action | No phone push needed |
| One-shot reminder ("ping me at 3pm") | `CronCreate` with `recurring: false` + curl ntfy action | No condition to poll |
| User wants persistent notifications without a condition | Direct curl in a /loop or cron | `notify-me` is condition-driven |

## ntfy.sh Background

ntfy.sh is a simple HTTP push service. Anyone who knows the topic name can publish; anyone subscribed receives. The user installs the ntfy app on their phone, subscribes to a topic name, and any HTTP POST to `https://ntfy.sh/<topic>` becomes a push notification.

- Free, no auth required for public topics.
- Topic names should be **long, random, hard to guess** since they're publicly addressable. Treat them as a shared secret.
- Self-hosted ntfy works the same way with a different base URL.

## Workflow

```
┌────────────────────────────────────────────────────────────┐
│ Phase 1: Resolve ntfy topic                                │
│   - Read ~/.claude/notify-me-config (one-line: topic name) │
│   - If missing, ask user for topic + persist               │
│   - If user has self-hosted ntfy, also read base URL       │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 2: Clarify the condition + message                   │
│   - What event triggers the notification?                  │
│   - What should the push message say?                      │
│   - What polling cadence (defer to watch skill table)      │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 3: Compose watch invocation                          │
│   - Build the check command                                │
│   - Build the action command:                              │
│       curl -d "<msg>" -H "Title: <title>" \                │
│            -H "Priority: <p>" <base>/<topic>               │
│   - Hand off to the `watch` skill (or call CronCreate      │
│     directly using watch's pattern)                        │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Phase 4: Confirm + report job ID, topic, cadence           │
└────────────────────────────────────────────────────────────┘
```

## Phase 1: Resolve the Topic

Config file: `~/.claude/notify-me-config`

Format (two lines, second optional):

```
topic=<topic-name>
base_url=https://ntfy.sh
```

Steps:

1. `cat ~/.claude/notify-me-config` (or equivalent Read).
2. If missing or empty, ask the user via `AskUserQuestion`:
   - "What ntfy topic should I publish to? (Pick something long and random - it's publicly addressable. Subscribe on your phone with the same name.)"
   - Optionally ask if they want a custom base URL (default `https://ntfy.sh`).
3. Persist as the file above. Mention the topic is treated as a shared secret.

The user need only do this once. Subsequent invocations read silently.

## Phase 2: Clarify

Ask the user (use `AskUserQuestion` if anything is genuinely ambiguous - don't quiz them about every detail):

- **Condition**: what to watch (PR merge, CI conclusion, Jira state, background task completion, file appearance, etc.). If the user already stated this clearly, skip.
- **Message**: short text the push will show. Default: derive from condition (e.g. "PR #5334 merged", "CI failed on branch X").
- **Title** (optional): bold header for the push. Default: "Claude Code".
- **Priority** (optional): 1 (min) - 5 (max). Default: 3.
- **Cadence**: defer to the cron-interval table in the `watch` skill. Don't reinvent.

## Phase 3: Compose

The cron prompt has the same skeleton as a `watch` cron, but the action step is:

```bash
curl -s -d "<message>" \
     -H "Title: <title>" \
     -H "Priority: <p>" \
     -H "Tags: <emoji-tag>" \
     "<base_url>/<topic>"
```

Useful tags (ntfy renders as emoji):

- PR merged / success: `white_check_mark`
- CI failure / build broken: `x`
- Jira state change: `eyes`
- Background task done: `bell`

Then **always include the watch self-cleanup step** (CronList → CronDelete by tag) so the watch stops after the first hit. This is a hard requirement of `watch`.

### Template Cron Prompt

```
Tag: notify-<short-uuid>

Check <CONDITION>. Use <CHECK COMMAND>.

If condition MET:
  1. Send notification:
     curl -s -d "<MESSAGE>" \
          -H "Title: <TITLE>" \
          -H "Priority: <PRIORITY>" \
          -H "Tags: <TAGS>" \
          "<BASE_URL>/<TOPIC>"
  2. CronList → find job with tag "notify-<short-uuid>" → CronDelete it.
  3. Tell the user the watch fired and what was pushed.

If NOT met: exit silently.
```

## Phase 4: Report Back

After `CronCreate` returns:

```
Watching <CONDITION> every <INTERVAL>; will push to ntfy topic "<TOPIC>".
Job ID: <returned-id>
Tag: notify-<uuid>
Cancel anytime with CronDelete or `/loop` controls.
```

## Common Recipes

### Notify when a PR merges

```
Tag: notify-pr-5757-merge

Check `gh pr view 5757 --repo ROCm/rocm-systems --json state -q .state`.

If output is "MERGED":
  1. curl -s -d "PR #5757 merged" -H "Title: GitHub" -H "Tags: white_check_mark" "https://ntfy.sh/<TOPIC>"
  2. CronList → find tag "notify-pr-5757-merge" → CronDelete.

Else: exit silently.
```

Schedule: `7-59/5 * * * *`, durable: true.

### Notify when CI finishes (green or red)

```
Tag: notify-ci-5757

Check `gh pr checks 5757 --repo ROCm/rocm-systems --watch=false --json conclusion,name`.

If every check has a non-empty conclusion:
  1. If all SUCCESS:
       curl -s -d "CI green on PR #5757" -H "Title: GitHub" -H "Tags: white_check_mark" "https://ntfy.sh/<TOPIC>"
  2. Else (any FAILURE):
       curl -s -d "CI failed on PR #5757 (N failed)" -H "Title: GitHub" -H "Priority: 5" -H "Tags: x" "https://ntfy.sh/<TOPIC>"
  3. CronList → find tag "notify-ci-5757" → CronDelete.

If any check still pending: exit silently.
```

Schedule: `2-59/5 * * * *`.

### Notify when a background bash task completes

```
Tag: notify-build-bdexslltb

Use TaskOutput with task_id "bdexslltb", block: false.

If status == "completed":
  1. exit_code 0:
       curl -s -d "Build done (exit 0)" -H "Title: Local" -H "Tags: bell" "https://ntfy.sh/<TOPIC>"
     non-zero:
       curl -s -d "Build failed (exit <N>)" -H "Title: Local" -H "Priority: 5" -H "Tags: x" "https://ntfy.sh/<TOPIC>"
  2. CronList → find tag "notify-build-bdexslltb" → CronDelete.

If status == "running": exit silently.
```

Schedule: `*/2 * * * *` (local task, fast cadence).

## Common Mistakes

| Mistake | Fix |
|---|---|
| Hardcoding `ntfy.sh/test` topic | Use the user's persisted topic. Public topics with guessable names get spam. |
| Forgetting `CronDelete` in the recurring prompt | Inherits the same problem as `watch` - notification fires forever. Always include self-cleanup. |
| Picking minute `0` or `30` for the schedule | Adds load to ntfy + upstream APIs at the same instant as everyone else. Pick an off minute. |
| Sending plaintext credentials in the message | Topic is publicly addressable. Don't echo PR bodies, secrets, or paths in the push. |
| Storing the topic in the prompt every time | Persist in `~/.claude/notify-me-config` once. Future invocations read silently. |

## Integration with Other Skills

| Trigger | Compose with |
|---|---|
| PR / CI condition | `git-pull-request-status` for the check, then notify |
| Watch a Jira state | `mcp__mcp-atlassian__jira_get_issue`, then notify |
| Local background task | `TaskOutput` with `block: false` in the check |
| Multiple conditions | One `notify-me` per condition; don't bundle |

## No Planning Required

Like `watch`, `notify-me` is a one-step setup. Don't open `planning-feature` for it - configure, fire, report.
