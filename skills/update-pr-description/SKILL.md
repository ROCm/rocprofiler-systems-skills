---
name: update-pr-description
description: Use when user says 'update PR description', 'refresh PR description', 'fix PR description', 'rewrite PR body', 'update my PR', or types /update-pr-description
---

# Update PR Description

Read the current PR description and branch changes, then produce an updated description that accurately reflects what is on the branch. Always edit in-place — never recreate the PR.

## Process

### Phase 0: Verify GitHub CLI

```bash
gh auth status
```

### Phase 1: Load PR Template and Read Current PR State

**FIRST: discover the PR template in the current working repository.** Do not hardcode rocm-systems or any other repo path.

```bash
# Check standard GitHub template locations (first match wins)
TEMPLATE=""
for path in \
  .github/pull_request_template.md \
  .github/PULL_REQUEST_TEMPLATE.md \
  .github/PULL_REQUEST_TEMPLATE/pull_request_template.md \
  .github/PULL_REQUEST_TEMPLATE/default.md; do
  if [ -f "$path" ]; then
    TEMPLATE="$path"
    break
  fi
done

# Multiple templates in directory — prefer pull_request_template.md, else ask user
if [ -z "$TEMPLATE" ] && [ -d .github/PULL_REQUEST_TEMPLATE ]; then
  TEMPLATE=$(ls .github/PULL_REQUEST_TEMPLATE/*.md 2>/dev/null | head -1)
fi

# Read template if found
[ -n "$TEMPLATE" ] && cat "$TEMPLATE"
```

Extract all `##` section headings from the template — these define the required structure. If no template file exists, use the fallback structure in Phase 4.

Then read the PR:

```bash
gh pr view --json number,title,body,baseRefName,headRefName
```

Extract: PR number, existing body (may be empty), base branch, head branch.

**NEVER hardcode `main` as base branch.** Always read `baseRefName` from the PR.

### Phase 2: Analyze Branch Changes

```bash
BASE=$(gh pr view --json baseRefName -q .baseRefName)
HEAD=$(gh pr view --json headRefName -q .headRefName)

git log --oneline "$BASE".."$HEAD"        # Commit history → Motivation
git diff --stat "$BASE".."$HEAD"          # File stats → Technical Details
git diff --name-only "$BASE".."$HEAD"     # File list → Test Plan
```

### Phase 3: Decide How to Handle Existing Description

Match sections by `##` heading from the repo template (or fallback). Treat a section as **placeholder** when it is empty or contains only HTML comments / boilerplate from the template.

| Section | Action |
|---------|--------|
| Body is empty or all placeholders | Generate fresh using template structure |
| **Motivation** | Preserve if real content; otherwise regenerate from commits |
| **Technical Details** | Always regenerate from diff |
| **Issue Tracking** | **Always preserve** — JIRA IDs and issue links are user-provided |
| **Test Plan** | Regenerate from diff and verification performed |
| **Test Result** | **Always preserve** — outcomes are user-provided |
| **Submission Checklist** | **Always preserve** checkbox state |
| Any other template section | Preserve if real content; regenerate only if clearly stale vs diff |

Do NOT discard user-written Motivation or metadata sections — they capture domain context the code cannot express.

### Phase 4: Draft the Description

Use the repo template's section order and headings. When no template file exists, use this fallback:

```markdown
## Motivation
<Why this change — problem being solved, user need, or context>

## Technical Details
<Key implementation decisions, trade-offs, architecture changes>

## Test Plan
- [ ] <how this was tested>
- [ ] <edge cases verified>
```

When a repo template exists (e.g. rocm-systems), follow its full structure:

```markdown
## Motivation
<Why this change — problem being solved, user need, or context>

## Technical Details
<Key implementation decisions, trade-offs, architecture changes; include relevant GitHub links>

## Issue Tracking
<!-- Preserve from existing body, or leave placeholder comments from template -->

## Test Plan
- [ ] <how this was tested>
- [ ] <edge cases verified>

## Test Result
<!-- Preserve from existing body, or leave placeholder comments from template -->

## Submission Checklist
<!-- Preserve checkbox state from existing body, or copy unchecked items from template -->
```

Reference actual commits, files, and decisions — never use generic filler text.

**Do NOT wrap prose at 80 characters.** Write each paragraph as a single continuous line. Hard line breaks inside sentences make the rendered GitHub description look broken. Only break lines at natural paragraph boundaries (blank line between sections).

### Phase 5: Show Before → After, Then Apply

**ALWAYS show the diff before applying.** Never silently overwrite.

```
Current description:
──────────────────────────────────────────────
<current body, or "(empty)" if blank>
──────────────────────────────────────────────

Proposed description:
──────────────────────────────────────────────
<new body>
──────────────────────────────────────────────
```

Use `AskUserQuestion` with a Yes/No question before applying:

```
Question: "Apply this description to PR #<NUMBER>?"
Options:  Yes | No
```

Only proceed if the user selects **Yes**. If **No**, ask what to change and re-draft.

Apply using the GitHub API directly:

```bash
gh api --method PATCH repos/{owner}/{repo}/pulls/<NUMBER> \
  --field body='## Motivation
...

## Technical Details
...

## Test Plan
- [ ] ...'
```

Resolve `{owner}/{repo}` with:
```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

To also update the title, add `--field title='...'` to the same call.

Verify the update:
```bash
gh pr view <NUMBER>
```

## Red Flags — Stop and Correct

- About to call `gh pr create` — that recreates the PR. Use `gh api --method PATCH`.
- Using `main` as the base branch without reading `baseRefName` from the PR.
- Overwriting the body without reading and displaying the current content first.
- Applying changes without showing before/after and using `AskUserQuestion` Yes/No.
- Ignoring `.github/pull_request_template.md` when it exists in the repo.
- Dropping Issue Tracking, Test Result, or Submission Checklist from an existing description.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `gh pr edit` or `gh pr create` | Use `gh api --method PATCH repos/{owner}/{repo}/pulls/<NUMBER>` |
| Hardcoding base branch as `main` | Read `baseRefName` from `gh pr view` |
| Hardcoding a 3-section template | Read `.github/pull_request_template.md` from the current repo first |
| Overwriting user-written motivation | Read existing body first, preserve domain context |
| Overwriting Issue Tracking / Test Result | Always preserve metadata sections |
| Skipping confirmation | Show before/after diff, then use `AskUserQuestion` Yes/No |
| Generic description | Reference actual commits, files, and decisions from the diff |
| Hard-wrapping lines at 80 chars | Write prose as continuous lines; only break at paragraph boundaries |
