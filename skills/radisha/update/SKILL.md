---
name: radisha/update
description: Update radisha skills to the latest version in the current project
---

# Update Radisha

Use this skill when the user asks to update radisha skills.

## Update Process

1. **Check current setup** - Find where radisha skills are located
2. **Pull latest changes** - Update from the repository
3. **Report changes** - Show what was updated

## Commands

### If radisha is a git submodule

```bash
# Navigate to radisha directory and pull
cd .cursor/skills/radisha && git pull origin main

# Or update all submodules
git submodule update --remote --merge
```

### If radisha is a separate clone

```bash
# Find radisha location (usually .cursor/skills/radisha or ~/.cursor/skills/radisha)
cd <radisha-location> && git pull origin main
```

### If radisha is symlinked

```bash
# Follow symlink and update the source
cd $(readlink -f .cursor/skills/radisha) && git pull origin main
```

## Execution Steps

1. **Locate radisha:**
   ```bash
   # Check project skills
   ls -la .cursor/skills/radisha 2>/dev/null || \
   ls -la ~/.cursor/skills/radisha 2>/dev/null
   ```

2. **Check current version (if VERSION file exists):**
   ```bash
   cat <radisha-path>/VERSION 2>/dev/null || echo "No VERSION file"
   ```

3. **Pull latest:**
   ```bash
   cd <radisha-path> && git fetch origin && git pull origin main
   ```

4. **Show changes:**
   ```bash
   git log --oneline HEAD@{1}..HEAD
   ```

5. **Report to user:**
   > "Radisha updated successfully.
   > 
   > **Changes:**
   > - [list of commits pulled]
   > 
   > **New/Updated skills:**
   > - [list if any new skills added]"

## If Update Fails

If git pull fails (local changes, conflicts):

```bash
# Option 1: Stash local changes
git stash && git pull origin main && git stash pop

# Option 2: Reset to remote (loses local changes)
git fetch origin && git reset --hard origin/main
```

Ask user which option they prefer before proceeding.
