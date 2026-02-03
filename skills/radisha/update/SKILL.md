---
name: radisha/update
description: Update radisha skills to the latest version - works with symlinks, git clones, and submodules
---

# Update Radisha

Use this skill when the user asks to update radisha skills.

## Overview

**Default Repository:** `https://github.com/adjordje-amd/radisha.git`

**Auto-Update:** On first skill invocation in a session, radisha automatically checks for updates and pulls the latest version before executing any skill. This ensures you always have the latest skills.

Radisha can be installed in different ways:
- **Symlink** - `~/.claude/skills` or `.cursor/skills` points to radisha repo
- **Git clone** - Radisha cloned directly into skills folder
- **Git submodule** - Radisha added as submodule
- **Copy** - Files copied (no git, cannot auto-update)

## Update Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    User asks to update radisha                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Detect Setup │
                    │ - Find skills location│
                    │ - Check if symlink    │
                    │ - Check if git repo   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Update       │
                    │ - Pull latest changes │
                    │ - Handle conflicts    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 3: Report       │
                    │ - Show what changed   │
                    │ - List new skills     │
                    └───────────────────────┘
```

## Phase 1: Detect Setup

### Find Skills Location

Check these locations in order:

```bash
# 1. Check if ~/.claude/skills is a symlink (Claude Code)
if [ -L ~/.claude/skills ]; then
    RADISHA_PATH=$(readlink -f ~/.claude/skills)
    echo "Symlink found: ~/.claude/skills -> $RADISHA_PATH"
# 2. Check if ~/.claude/skills exists (Claude Code direct)
elif [ -d ~/.claude/skills ]; then
    RADISHA_PATH=~/.claude/skills
    echo "Direct install: $RADISHA_PATH"
# 3. Check project .cursor/skills (Cursor)
elif [ -L .cursor/skills/radisha ]; then
    RADISHA_PATH=$(readlink -f .cursor/skills/radisha)
    echo "Symlink found: .cursor/skills/radisha -> $RADISHA_PATH"
elif [ -d .cursor/skills/radisha ]; then
    RADISHA_PATH=.cursor/skills/radisha
    echo "Direct install: $RADISHA_PATH"
# 4. Check user .cursor/skills (Cursor global)
elif [ -d ~/.cursor/skills/radisha ]; then
    RADISHA_PATH=~/.cursor/skills/radisha
    echo "User install: $RADISHA_PATH"
fi
```

### Check if Git Repo

```bash
cd "$RADISHA_PATH" && git status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Git repository detected"
    git remote -v
else
    echo "Not a git repository - cannot auto-update"
fi
```

## Phase 2: Update

### Standard Update (no local changes)

```bash
cd "$RADISHA_PATH"

# Fetch and show what will change
git fetch origin
echo "Changes to be pulled:"
git log --oneline HEAD..origin/main

# Pull changes
git pull origin main
```

### If Local Changes Exist

If `git status` shows uncommitted changes:

```markdown
**Local changes detected in radisha:**

```
[show git status output]
```

**Options:**
1. **Stash and update** - Temporarily save changes, update, restore
2. **Reset to remote** - Discard local changes, match remote exactly
3. **Cancel** - Don't update, keep current state

Which option?
```

Use `AskUserQuestion` tool to let user choose.

**Option 1: Stash and update**
```bash
git stash
git pull origin main
git stash pop
```

**Option 2: Reset to remote**
```bash
git fetch origin
git reset --hard origin/main
```

### If Conflicts Occur

```bash
# After stash pop, if conflicts:
git status  # Show conflicted files

# Report to user
echo "Conflicts detected in:"
git diff --name-only --diff-filter=U
```

Ask user how to resolve.

## Phase 3: Report

### Show What Changed

```bash
# Show commits pulled
git log --oneline HEAD@{1}..HEAD 2>/dev/null || echo "Fresh pull"

# Show changed files
git diff --stat HEAD@{1}..HEAD 2>/dev/null
```

### Check for New Skills

```bash
# List all skill directories
find "$RADISHA_PATH" -name "SKILL.md" -type f | \
    sed 's|/SKILL.md||' | \
    sed "s|$RADISHA_PATH/||"
```

### Report Format

```markdown
## Radisha Updated Successfully

**Location:** [path]
**Previous:** [commit hash before]
**Current:** [commit hash after]

### Commits Pulled
- [commit 1]
- [commit 2]
- [commit 3]

### Files Changed
- [file 1]
- [file 2]

### Available Skills
[List all skills currently available]
```

## Execution Script

Complete script to run:

```bash
#!/bin/bash

# Detect radisha location
RADISHA_PATH=""

if [ -L ~/.claude/skills ]; then
    RADISHA_PATH=$(readlink -f ~/.claude/skills)
elif [ -d ~/.claude/skills/.git ]; then
    RADISHA_PATH=~/.claude/skills
elif [ -L .cursor/skills/radisha ]; then
    RADISHA_PATH=$(readlink -f .cursor/skills/radisha)
elif [ -d .cursor/skills/radisha/.git ]; then
    RADISHA_PATH=.cursor/skills/radisha
elif [ -d ~/.cursor/skills/radisha/.git ]; then
    RADISHA_PATH=~/.cursor/skills/radisha
fi

if [ -z "$RADISHA_PATH" ]; then
    echo "ERROR: Could not find radisha installation"
    exit 1
fi

echo "Found radisha at: $RADISHA_PATH"
cd "$RADISHA_PATH"

# Check if git repo
if ! git status >/dev/null 2>&1; then
    echo "ERROR: Not a git repository, cannot update"
    exit 1
fi

# Check for local changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "WARNING: Local changes detected"
    git status --short
    exit 1  # Let AI handle with user interaction
fi

# Fetch and update
BEFORE=$(git rev-parse HEAD)
git fetch origin
git pull origin main
AFTER=$(git rev-parse HEAD)

if [ "$BEFORE" = "$AFTER" ]; then
    echo "Already up to date"
else
    echo "Updated from $BEFORE to $AFTER"
    echo ""
    echo "Changes:"
    git log --oneline $BEFORE..$AFTER
fi
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "Not a git repository" | Radisha was copied, not cloned. Re-clone from `https://github.com/adjordje-amd/radisha.git` |
| "Permission denied" | Check file permissions on skills directory |
| "Merge conflicts" | Ask user to resolve or reset to remote |
| "Symlink broken" | Re-create symlink to radisha repo |
| "Cannot find radisha" | Check all possible locations, ask user |

## Manual Installation Options

If radisha is not installed or needs fresh install:

### Claude Code (recommended: symlink)

```bash
# Clone radisha repo
git clone https://github.com/adjordje-amd/radisha.git ~/work/radisha

# Create symlink
ln -sf ~/work/radisha/skills ~/.claude/skills
```

### Cursor (recommended: symlink)

```bash
# Clone radisha repo
git clone https://github.com/adjordje-amd/radisha.git ~/work/radisha

# Create symlink for project
ln -sf ~/work/radisha/skills .cursor/skills/radisha

# Or global
ln -sf ~/work/radisha/skills ~/.cursor/skills/radisha
```

### Direct Clone

```bash
# Claude Code
git clone https://github.com/adjordje-amd/radisha.git ~/.claude/skills-repo
ln -sf ~/.claude/skills-repo/skills ~/.claude/skills

# Cursor
git clone https://github.com/adjordje-amd/radisha.git .cursor/skills/radisha
```
