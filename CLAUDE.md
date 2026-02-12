# Radisha

AI-assisted development with structured workflows.

## How to Use Skills

**In Claude Code CLI:** Just ask naturally in plain English:
- "commit these changes" → uses `git-commit` skill
- "plan this feature" → uses `planning-feature` skill
- "review the PR" → uses `git-review-pull-request` skill
- "create a test plan" → uses `testing-testplan` skill

Skills are automatically loaded from `~/.claude/skills/` and applied when relevant.

## Available Skills

| Task | Skill Used |
|------|------------|
| Plan a new feature | `planning-feature` |
| Plan a bug fix | `planning-bugfix` |
| Plan refactoring | `planning-refactor` |
| Document architecture | `planning-architecture` |
| Create a commit | `git-commit` |
| Prepare a pull request | `git-prepare-pull-request` |
| Review a pull request | `git-review-pull-request` |
| Create test plan | `testing-testplan` |
| Explore unfamiliar code | `exploration-explore-code` |
| List all skills | `radisha-skills` |
| Update radisha | `radisha-update` |

## Core Rules

### Planning First
Before starting ANY non-trivial task (more than 2 steps), invoke the appropriate planning skill (`planning-feature`, `planning-bugfix`, `planning-refactor`, or `planning-docs`).

### Step-by-Step Validation
After completing EACH implementation step:
1. Run autonomous verification (tests, linter)
2. Show summary of changes
3. Ask user for validation before proceeding

### English Output
ALL output MUST be in English, regardless of input language.

### Skill Invocation
If there is even a 1% chance a skill might apply to your task, you MUST invoke it. Use the `Skill` tool with the skill name (e.g., `planning-feature`).

### Simplicity First
Make every change as simple as possible. Only touch what's necessary. No over-engineering.

## How to Find Skills

Skills are located in `~/.claude/skills/` (global) or the project's `skills/` directory.

**Prefixes:**
- `planning-` - Feature, bugfix, refactor, docs, architecture planning
- `programming-` - Language-specific coding (cpp, python, cmake)
- `testing-` - Test plans and test frameworks
- `git-` - Pull requests and reviews
- `exploration-` - Code exploration
- `libraries-` - Library-specific knowledge (amd-smi)
- `radisha-` - Radisha management (update, help, skills)

**For full workflow reference:** Invoke the `radisha-help` skill.
