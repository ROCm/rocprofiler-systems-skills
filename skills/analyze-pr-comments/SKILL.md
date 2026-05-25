---
name: analyze-pr-comments
description: Use when user wants to list, analyze, review, or summarize GitHub PR comments on a pull request number or URL
---

# Analyze PR Comments

Fetch every comment on a GitHub PR, format them uniformly, distill reviewer intent, and provide a code-backed fix for each.

## Triggering

- "analyze PR comments", "list comments on PR #N", "summarize PR feedback"
- User shares a PR URL or number and asks to review what reviewers said

## Workflow

### Step 1 — Resolve PR target

If PR number/URL not provided, detect from current branch:

```bash
gh pr view --json number,url
```

### Step 2 — Fetch ALL comment types

GitHub has three distinct comment sources. Fetch all three:

```bash
# 1. Inline review comments (attached to code lines)
gh api repos/{owner}/{repo}/pulls/{PR}/comments \
  --jq '.[] | {id, author: .user.login, body, path, line}'

# 2. PR conversation comments (not attached to code)
gh api repos/{owner}/{repo}/issues/{PR}/comments \
  --jq '.[] | {id, author: .user.login, body}'

# 3. Review-level summary comments (review body text)
gh api repos/{owner}/{repo}/pulls/{PR}/reviews \
  --jq '.[] | select(.body != "") | {id, author: .user.login, body, state}'
```

Use `{owner}` and `{repo}` from `gh repo view --json nameWithOwner`.

### Step 3 — Merge and number

Combine all three sets. Sort by `created_at` ascending. Assign sequential `#N` starting at 1. Skip bot accounts (e.g. `github-actions[bot]`, `dependabot[bot]`).

### Step 4 — Format each comment

Output exactly this structure for every comment:

```
#<N> <Author>

#<Original Comment>
<verbatim text — do NOT paraphrase, trim, or reformat>

#<Comment simplified>
<1-2 sentences: what the reviewer actually wants, not what they said>

#<Proposed fix with proof>
<code block that demonstrates the fix>
<if reviewer already included a code suggestion: propose a DIFFERENT valid implementation>
```

Inline comments: prepend file context before the block:
```
File: path/to/file.go (line 42)
```

---

## Rules — DO NOT VIOLATE

| Rule | Violation |
|------|-----------|
| Quote original comment verbatim | Paraphrasing, trimming, summarizing |
| Proposed fix = actual code | "You should rename the function" (no code) |
| Alternative fix if reviewer proposed one | Copying or slightly rewording their suggestion |
| All 3 comment sources | Only fetching `gh pr view --comments` |
| Skip bots | Including CI/bot noise in the numbered list |

## Red Flags (stop and correct)

- Writing "The reviewer suggests X" in the Original Comment section — that is paraphrase
- Proposed fix that contains no code block
- Less comments than expected — you likely missed inline review threads
- Proposed fix mirrors the reviewer's own code sample word-for-word

## Example Output

```
File: internal/auth/session.go (line 87)

#1 alice

#Original Comment
This function is doing too much. It handles both validation and persistence in the same call which makes it hard to unit test.

#Comment simplified
Split the function into separate validation and save steps so each can be tested in isolation.

#Proposed fix with proof
```go
// Before
func saveSession(s Session) error {
    if s.Token == "" {
        return errors.New("token required")
    }
    return db.Save(s)
}

// After — two responsibilities, two functions
func validateSession(s Session) error {
    if s.Token == "" {
        return errors.New("token required")
    }
    return nil
}

func persistSession(s Session) error {
    return db.Save(s)
}

// Caller composes them
func handleSave(s Session) error {
    if err := validateSession(s); err != nil {
        return err
    }
    return persistSession(s)
}
```
```

## Required Background

Uses `gh` CLI — if unavailable, invoke **git-gh-client** first to verify installation and authentication.
