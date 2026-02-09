---
name: git-commit
description: Create meaningful git commits with well-structured messages - analyzes changes, generates descriptive subject and body, follows conventional commits
---

# Git Commit Skill

Use this skill when committing changes to create meaningful, well-structured commit messages.

<IMPORTANT>
**A good commit message explains WHY, not just WHAT.**

Before committing:
1. Analyze all staged changes
2. Understand the purpose of the changes
3. Write a message that helps future developers understand the context
</IMPORTANT>

## Commit Process

```
┌─────────────────────────────────────────────────────────────────┐
│                   User asks to commit changes                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Analyze      │
                    │ - Review staged files │
                    │ - Understand changes  │
                    │ - Identify type       │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Categorize   │
                    │ - Group related files │
                    │ - Check for mixed     │
                    │   concerns            │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 3: Draft        │
                    │ - Write subject line  │
                    │ - Write body          │
                    │ - Add footer          │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 4: Review       │
                    │ - Present to user     │
                    │ - Get approval        │
                    │ - Commit              │
                    └───────────────────────┘
```

## Phase 1: Analyze Changes

### Get Staged Changes

```bash
# See what's staged
git status --short

# See staged diff
git diff --cached

# See staged file names
git diff --cached --name-only

# Get stats
git diff --cached --stat
```

### Understand the Changes

For each changed file, determine:
- What was added/removed/modified?
- Why was this change made?
- What problem does it solve?
- What behavior changes?

## Phase 2: Categorize

### Identify Commit Type

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | Adding user authentication |
| `fix` | Bug fix | Fixing null pointer crash |
| `refactor` | Code restructure (no behavior change) | Extracting method |
| `perf` | Performance improvement | Caching query results |
| `docs` | Documentation only | Updating README |
| `test` | Adding/fixing tests | Adding unit tests |
| `build` | Build system changes | CMake configuration |
| `ci` | CI/CD changes | GitHub Actions workflow |
| `chore` | Maintenance tasks | Updating dependencies |
| `style` | Code style (formatting, no logic change) | Fixing indentation |

### Check for Mixed Concerns

<IMPORTANT>
If changes touch multiple unrelated concerns, suggest splitting into multiple commits.
</IMPORTANT>

**Signs of mixed concerns:**
- Feature code + unrelated refactoring
- Bug fix + new feature
- Multiple independent fixes
- Code changes + documentation updates (sometimes OK)

**Ask user if mixed:**

```json
{
  "questions": [{
    "question": "Changes include both a bug fix and a new feature. Split into separate commits?",
    "header": "Mixed changes",
    "options": [
      {"label": "Split commits", "description": "Create separate commits for each concern (recommended)"},
      {"label": "Single commit", "description": "Commit everything together"},
      {"label": "Show me", "description": "Show the different concerns first"}
    ],
    "multiSelect": false
  }]
}
```

## Phase 3: Draft Commit Message

### Message Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Subject Line Rules

| Rule | Good | Bad |
|------|------|-----|
| Imperative mood | "Add validation" | "Added validation" |
| No period at end | "Fix memory leak" | "Fix memory leak." |
| Max 50 characters | "Add user auth" | "Add user authentication with OAuth2 support and session management" |
| Capitalize first letter | "Fix crash" | "fix crash" |
| Be specific | "Fix null check in parser" | "Fix bug" |

### Type and Scope

```
feat(auth): add OAuth2 login support
fix(parser): handle null input gracefully
refactor(api): extract validation logic
docs(readme): add installation instructions
test(auth): add login failure tests
```

**Scope** is optional but helpful - identifies the module/component affected.

### Body Guidelines

The body explains **WHY** the change was made:

```markdown
The previous implementation crashed when users provided empty input
because the parser assumed non-null strings. This fix adds explicit
null checks before processing.

This was discovered in production logs showing ~50 crashes/day
from the /api/parse endpoint.
```

**Body rules:**
- Wrap at 72 characters
- Explain motivation and context
- Explain what and why, not how (code shows how)
- Use bullet points for multiple items

### Footer

Used for:
- Issue references: `Fixes #123`, `Closes #456`
- Breaking changes: `BREAKING CHANGE: API signature changed`

## Phase 4: Review and Commit

### Present to User

Show the proposed commit message:

```markdown
**Proposed commit message:**

---
feat(gpu): add temperature monitoring for MI300 GPUs

Add support for reading GPU temperature sensors on MI300 hardware.
The existing implementation only supported MI200 series.

Key changes:
- Add MI300-specific temperature sensor IDs
- Update device detection to recognize MI300 variants
- Add fallback for unsupported sensor types

This enables rocm-smi to display temperature for the latest hardware.

Fixes #234
---

**Files to be committed:**
- src/gpu/temperature.cpp (modified)
- src/gpu/device_info.cpp (modified)
- include/gpu/sensors.hpp (modified)
- tests/temperature_test.cpp (added)
```

### Ask for Approval

```json
{
  "questions": [{
    "question": "Commit with this message?",
    "header": "Commit",
    "options": [
      {"label": "Commit", "description": "Create commit with this message"},
      {"label": "Edit message", "description": "I want to modify the message"},
      {"label": "Cancel", "description": "Don't commit yet"}
    ],
    "multiSelect": false
  }]
}
```

### Execute Commit

```bash
git commit -m "$(cat <<'EOF'
feat(gpu): add temperature monitoring for MI300 GPUs

Add support for reading GPU temperature sensors on MI300 hardware.
The existing implementation only supported MI200 series.

Key changes:
- Add MI300-specific temperature sensor IDs
- Update device detection to recognize MI300 variants
- Add fallback for unsupported sensor types

This enables rocm-smi to display temperature for the latest hardware.

Fixes #234
EOF
)"
```

## Commit Message Templates

### Feature

```
feat(<scope>): <what was added>

<Why this feature is needed>

<Key implementation details if complex>

<Issue reference if applicable>
```

**Example:**

```
feat(api): add batch processing endpoint

Users frequently need to process multiple items at once.
The current API requires individual requests, causing
unnecessary latency for bulk operations.

- Add POST /api/batch endpoint
- Support up to 100 items per request
- Return partial results on individual failures

Closes #567
```

### Bug Fix

```
fix(<scope>): <what was fixed>

<What was the bug / symptoms>

<Root cause explanation>

<How it was fixed>

<Issue reference>
```

**Example:**

```
fix(parser): handle empty input without crashing

The application crashed when users submitted empty forms.
Stack trace showed null pointer dereference in validate().

Root cause: Input validation assumed non-empty strings
and called .length() without null check.

Added explicit null/empty checks before processing.

Fixes #789
```

### Refactor

```
refactor(<scope>): <what was restructured>

<Why refactoring was needed>

<What changed structurally>

<Behavior should be unchanged>
```

**Example:**

```
refactor(auth): extract token validation to separate class

Token validation logic was duplicated across 4 endpoints
and becoming difficult to maintain.

- Extract TokenValidator class
- Move all validation logic to single location
- Update endpoints to use new validator

No behavior changes. All existing tests pass.
```

### Performance

```
perf(<scope>): <what was optimized>

<Previous performance characteristics>

<New performance characteristics>

<How the improvement was achieved>
```

**Example:**

```
perf(query): add caching for user lookup

User lookup was hitting database on every request,
causing ~200ms latency per API call.

Added Redis cache with 5-minute TTL:
- Cache hit: ~2ms
- Cache miss: ~200ms (unchanged)

Reduces average response time by 60% based on
typical access patterns (80% cache hit rate).
```

## Quick Reference

### The Seven Rules

1. Separate subject from body with blank line
2. Limit subject to 50 characters
3. Capitalize subject line
4. Do not end subject with period
5. Use imperative mood in subject
6. Wrap body at 72 characters
7. Use body to explain what and why, not how

### Good vs Bad Examples

| Bad | Good |
|-----|------|
| "fixed bug" | "fix(auth): prevent session timeout on active users" |
| "updates" | "refactor(api): simplify error handling logic" |
| "WIP" | "feat(ui): add loading spinner (partial)" |
| "asdfasdf" | (Don't commit with meaningless messages) |
| "Fixed the thing John mentioned" | "fix(export): handle special characters in filenames" |

### When NOT to Commit

- Unfinished work (use branches or stash)
- Broken code that doesn't compile
- Failed tests without good reason
- Debugging code (console.log, print statements)
- Credentials or secrets

## Integration with Other Skills

| After Commit | Consider |
|--------------|----------|
| Multiple commits ready | `git-prepare-pull-request` to create PR |
| Need to group commits | `git rebase -i` to squash/reorder |
| Wrong commit | `git commit --amend` (only if not pushed) |

## Command Alias

Add `/commit` as a quick command in `radisha-skills`:

```
/commit → git-commit
```

## References

- [How to Write a Git Commit Message](https://cbea.ms/git-commit/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Documentation](https://git-scm.com/docs/git-commit)
