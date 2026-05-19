---
name: pr-review-interactive
description: Walk through a PR review interactively, one finding at a time. Generate review via pr-review, then for each issue present analysis + proposed inline comment, let user accept/edit/skip, accumulate into a PENDING GitHub review, submit at end.
---

# PR Review Interactive Skill

Run a PR review and triage every finding with the user before any
comment lands on GitHub. Comments are accumulated in a single PENDING
review and submitted as one batch.

<IMPORTANT>
**Never auto-submit.** The review stays in PENDING state until the user
explicitly chooses an event (COMMENT / REQUEST_CHANGES / APPROVE) at
step 7. Never call `gh api PUT .../reviews/<id>/events` without an
explicit user confirmation in this session.

**Never use `gh pr comment` or `gh pr review --comment` for inline
comments.** Both silently drop the body on rocm-systems and similar
orgs due to a known Projects-classic GraphQL bug. Always use
`gh api POST /repos/$O/$R/pulls/$N/comments` with
`pull_request_review_id` to attach to the PENDING review.

**Comment format is short.** 1-3 sentences, root cause first, fix
snippet only when non-obvious. ASCII hyphen only. No praise, no
recap, no Claude attribution.
</IMPORTANT>

## When to Use

- User asks "interactive pr review", "walk me through the PR
  review", `/pr-review-interactive`, or invokes this skill by name.
- User wants tight control over what lands on a PR vs. just
  generating a report.

Do NOT use for:
- Quick local review with no GitHub posting: use `pr-review`.
- Posting a fixed set of pre-written comments: use `gh api` directly.

## Inputs

- PR URL or `<owner>/<repo>#<number>` or repo + PR number.
- Optional: pre-existing report path (skip step 2 if provided and
  fresh).

## Workflow

### Step 1. Resolve PR

Parse `owner`, `repo`, PR number. Verify with
`gh api /repos/$O/$R/pulls/$N`. Fetch head SHA. Save SHA to
`$CLAUDE_JOB_DIR/pr-review-interactive/head-sha.txt`.

### Step 2. Generate report

Invoke `pr-review` skill against the PR. If user already has a
report file, ask whether to reuse or regenerate. Save report path to
state.

### Step 3. Parse findings

Read the report and extract a list of findings. Each finding has:

| Field | Source |
|---|---|
| `id` | `MF-1`, `SF-3`, `N-7`, ... from report headings |
| `severity` | Must-Fix / Should-Fix / Nit |
| `path`, `line` | from "Location:" line |
| `title` | finding heading |
| `body` | finding text body (full analysis) |

Store as JSON at `$CLAUDE_JOB_DIR/pr-review-interactive/findings.json`.

### Step 4. Cache diff line set

`gh api /repos/$O/$R/pulls/$N/files` and parse patches. Build a set
of `(path, line, side)` tuples that are valid review-comment
targets. Inline review comments must target lines in the diff;
others get the `subject_type=file` fallback (see step 6e).

### Step 5. PENDING review

Detect existing PENDING review by current user on this PR:
`gh api /repos/$O/$R/pulls/$N/reviews --jq '.[] | select(.state=="PENDING" and .user.login==env.USER_LOGIN) | .id'`.

- Found: reuse, save id.
- Not found: create empty PENDING review:
  ```
  gh api -X POST /repos/$O/$R/pulls/$N/reviews \
    -F commit_id=$SHA
  ```
  Save returned `id` to `$CLAUDE_JOB_DIR/pr-review-interactive/review-id.txt`.

### Step 6. Iterate findings

Order: Must-Fix -> Should-Fix -> Nits. For each finding:

**a. Present:**

```
[MF-1] Must-Fix
location: <path>:<line>
title:    <title>

analysis:
<2-4 lines distilled from the report body, plain prose>

proposed comment:
<the short body, code fence only when needed>
```

**b. Ask user via `AskUserQuestion`:**

| Option | Action |
|---|---|
| accept | Post comment to PENDING review as-is |
| edit | Open user-edit prompt; user supplies replacement body; then post |
| skip | Record skip; move on |
| quit | Jump to step 7 |

**c. Accept path:**

```bash
gh api -X POST /repos/$O/$R/pulls/$N/comments \
  -f commit_id="$SHA" \
  -f path="$PATH" \
  -F line=$LINE \
  -f side=RIGHT \
  -F pull_request_review_id=$REVIEW_ID \
  -f body="$BODY"
```

On 422 "line is not part of the diff": retry as file-level comment
(`subject_type=file`, no `line`).

**d. Edit path:** prompt user for new body; validate non-empty; then
take accept path with new body.

**e. Skip path:** append to `skipped.json` with `{id, reason}`.

**f. State persistence:** after every action append to
`$CLAUDE_JOB_DIR/pr-review-interactive/accepted.json` so a session
crash does not lose work.

### Step 7. Wrap-up summary

When loop done (or user `quit`):

```
Accepted: <N>
Skipped:  <M>
Pending:  <K> (not yet reviewed)
```

Ask user via `AskUserQuestion`:

| Option | Event |
|---|---|
| Request changes | REQUEST_CHANGES |
| Comment only | COMMENT |
| Approve | APPROVE |
| Keep pending | (no submit) |
| Discard review | DELETE the PENDING review |

### Step 8. Submit (or hold)

If user picked an event:

```bash
gh api -X POST /repos/$O/$R/pulls/$N/reviews/$REVIEW_ID/events \
  -f event="$EVENT" \
  -f body="$OPTIONAL_OVERALL"
```

Print URL of submitted review.

If Discard: `gh api -X DELETE /repos/$O/$R/pulls/$N/reviews/$REVIEW_ID`.

If Keep pending: leave id in state file for resume next session.

## Comment Format Rules

| Rule | Why |
|---|---|
| 1-3 sentences | Author scans; long comments are skipped |
| Root cause first, fix snippet only when non-obvious | Fix is often obvious once cause is known |
| ASCII hyphen `-` only | radisha global rule, no em/en dash |
| No praise, no recap | Adds noise |
| Code fences only for the proposed change | Author already sees their own diff |
| Line-anchored when possible | Threading + suggested-change UI works |

Good (MF-1 example):

```
`ROCPROFSYS_GPU_PERF_COUNTERS` is never registered via
`ROCPROFSYS_CONFIG_SETTING`, so `find(...)` returns `end()` and the
env var is a no-op. SDK PMC source gated on this so feature only
reachable via JSON injection.

\`\`\`cpp
ROCPROFSYS_CONFIG_SETTING(std::string, "ROCPROFSYS_GPU_PERF_COUNTERS",
    "...", "", "backend", "rocprofiler-sdk", "pmc");
\`\`\`
```

Bad: 12-line paragraph recapping the diff and listing every downstream
caller.

## State Files

All under `$CLAUDE_JOB_DIR/pr-review-interactive/`:

| File | Content |
|---|---|
| `head-sha.txt` | PR head SHA at session start |
| `review-id.txt` | Active PENDING review id |
| `findings.json` | Parsed findings list |
| `diff-lines.json` | Cached valid-line set |
| `accepted.json` | Posted comments |
| `skipped.json` | Skipped findings + reason |

Resume on next session: read all state files, skip past last
accepted/skipped index, continue.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Posting via `gh pr comment` | Silently fails on rocm-systems (Projects-classic GraphQL bug). Use `gh api POST .../pulls/N/comments` with `pull_request_review_id` |
| Posting one standalone review per finding | Spams email. One PENDING review + N attached comments + one submit |
| Auto-submitting after last finding | Always ask for event verb explicitly |
| Skipping line-not-in-diff comments | Fall back to `subject_type=file` |
| Long comments | 1-3 sentences max, fix snippet only when non-obvious |
| Forgetting to save state | Persist after every accept/skip |
| Re-creating PENDING review on resume | Detect existing PENDING by current user first |

## Integration with Other Skills

| After This Skill | Use |
|---|---|
| Author addresses comments, want re-review | `pr-review` (fresh report), then `pr-review-interactive` again |
| Just want a report file, no posting | `pr-review` only |
| Post a single, prepared inline comment | `gh api` directly, skip this skill |

## Dependencies

- `pr-review` - generates the report this skill walks through
- `git-gh-client` - core gh CLI helpers
