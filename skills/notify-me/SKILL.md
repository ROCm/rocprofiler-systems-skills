---
name: notify-me
description: Send a push notification to the user's phone via ntfy.sh when a condition is met, by composing a watch cron whose action is a curl POST.
---

# Notify Me Skill

Compose a recurring cron whose action is `curl POST https://ntfy.sh/<topic>` so the user gets a phone push when a condition is met. Use only when the user has asked for one.

## How it works

The whole mechanism is one HTTP POST. ntfy.sh delivers the request body as a push notification to every device subscribed to the topic.

```bash
curl -s -d "your message body" \
     -H "Title: short header" \
     -H "Priority: 1-5" \
     -H "Tags: white_check_mark" \
     "https://ntfy.sh/<topic>"
```

The skill wraps that call in a `watch`-style cron: poll a condition, and only fire the curl when the condition is met. Self-hosted ntfy works the same way - swap `https://ntfy.sh` for the user's `base_url`.

## Configure (one-time)

Persist the topic in `~/.claude/notify-me-config`:

```
topic=<long-random-name>
base_url=https://ntfy.sh
```

If the file is missing, ask once via `AskUserQuestion`:

> "What ntfy topic should I publish to? Pick a long random string - it is publicly addressable, treat it as a shared secret. Subscribe on your phone with the same name."

`base_url` is optional (default `https://ntfy.sh`); set only for self-hosted ntfy. Subsequent invocations read silently.

User-side: install the ntfy app on the phone, subscribe to the same topic.

## Use

When the user asks "notify me when X":

1. Read the topic from the config (ask once if missing).
2. Decide a unique tag for the cron, e.g. `notify-pr-5757-merge`.
3. Build a check command for the condition (gh, jq, TaskOutput, etc.).
4. `CronCreate` with this prompt:

```
Tag: notify-<short-uuid>

Check <CONDITION> with <CHECK COMMAND>.

If MET:
  curl -s -d "<MSG>" \
       -H "Title: <T>" \
       -H "Priority: <1-5>" \
       -H "Tags: <emoji>" \
       "<base_url>/<topic>"
  CronList -> find tag "notify-<short-uuid>" -> CronDelete it.

Else: exit silently.
```

5. Tell the user the cron job ID + the tag so they can cancel later.

Cadence: defer to the `watch` skill's interval table. Pick a non-zero, non-`30` minute (avoids load spikes). Long-running PR/CI watches: `durable: true` so the cron survives session restarts.

Tag emojis: `white_check_mark` (success), `x` (failure), `bell` (generic done), `eyes` (state change).

The `CronDelete` self-cleanup is mandatory - without it the cron fires forever.

## Recipes

### PR merged

```
Tag: notify-pr-N-merge

Check `gh pr view N --repo <repo> --json state -q .state`.

If "MERGED":
  curl -s -d "PR #N merged" -H "Title: GitHub" -H "Tags: white_check_mark" "https://ntfy.sh/<TOPIC>"
  CronList -> CronDelete tag "notify-pr-N-merge".

Else: silent.
```
Schedule: `7-59/5 * * * *`, durable: true.

### CI finishes (green or red)

```
Tag: notify-ci-N

Check `gh pr checks N --repo <repo> --watch=false --json conclusion,name`.

If every check has a non-empty conclusion:
  All SUCCESS:
    curl -s -d "CI green on PR #N" -H "Title: GitHub" -H "Tags: white_check_mark" "https://ntfy.sh/<TOPIC>"
  Any FAILURE:
    curl -s -d "CI failed on PR #N (M failed)" -H "Title: GitHub" -H "Priority: 5" -H "Tags: x" "https://ntfy.sh/<TOPIC>"
  CronList -> CronDelete tag.

Else: silent.
```
Schedule: `2-59/5 * * * *`.

### Background bash task done

```
Tag: notify-build-<id>

Use TaskOutput with task_id "<id>", block: false.

If status == "completed":
  exit 0  -> curl -s -d "Build done" -H "Tags: bell" "https://ntfy.sh/<TOPIC>"
  non-zero -> curl -s -d "Build failed (exit N)" -H "Priority: 5" -H "Tags: x" "https://ntfy.sh/<TOPIC>"
  CronList -> CronDelete tag.

Else: silent.
```
Schedule: `*/2 * * * *`.

## Reminders

- Topic is publicly addressable: don't echo PR bodies, secrets, or paths in the push.
- Always include the `CronDelete` self-cleanup.
- One cron per condition; don't bundle multiple watches in one prompt.
