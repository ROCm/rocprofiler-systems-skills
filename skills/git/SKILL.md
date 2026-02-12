---
name: git
description: Git workflow dispatcher - routes to specialized git skills for commits, PRs, and reviews
---

# Git Skills Dispatcher

**DO NOT use this skill directly.** Instead, use one of the specialized git skills below based on the user's request.

## Available Git Skills

### Commit Management

**`git/commit`** - Create meaningful git commits
- **When:** User wants to commit changes
- **Triggers:** "commit", "save changes", "create commit"
- **Location:** `~/.claude/skills/git/commit/SKILL.md`

### Pull Request Workflows

**`git/prepare-pull-request`** - Prepare and create pull requests
- **When:** User wants to create a PR
- **Triggers:** "create PR", "make pull request", "prepare PR"
- **Location:** `~/.claude/skills/git/prepare-pull-request/SKILL.md`

**`git/review-pull-request`** - Review pull requests with comprehensive checklist
- **When:** User wants to review a PR
- **Triggers:** "review PR", "check pull request"
- **Location:** `~/.claude/skills/git/review-pull-request/SKILL.md`

**`git/pull-request-status`** - Check PR status and CI results
- **When:** User wants to check PR status
- **Triggers:** "PR status", "check CI", "PR checks"
- **Location:** `~/.claude/skills/git/pull-request-status/SKILL.md`

### GitHub Operations

**`git/gh-client`** - GitHub CLI operations
- **When:** User needs GitHub-specific operations
- **Triggers:** "GitHub", "gh", "issues", "releases"
- **Location:** `~/.claude/skills/git/gh-client/SKILL.md`

## How to Use

When the user requests a git-related task:

1. **Identify the appropriate sub-skill** from the list above
2. **Load that specific skill** (if nested skills are supported)
3. **OR notify the user** that nested skills aren't currently loaded

## Fallback

If nested skills aren't recognized by Claude Code, you should inform the user that they need to:
- Use symlinks at the top level, OR
- Flatten the skill directory structure

## Example Routing

| User Request | Route To |
|--------------|----------|
| "commit my changes" | `git/commit` |
| "create a pull request" | `git/prepare-pull-request` |
| "review PR #123" | `git/review-pull-request` |
| "check PR status" | `git/pull-request-status` |
| "create GitHub issue" | `git/gh-client` |
