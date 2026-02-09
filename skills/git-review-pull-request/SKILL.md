---
name: git-review-pull-request
description: Review Pull Requests thoroughly - check code quality, correctness, tests, and provide actionable feedback using language-specific programming skills
---

# Review Pull Request Skill

Use this skill when reviewing Pull Requests. For preparing PRs, use `git-prepare-pull-request` instead.

## Overview

This skill provides a structured approach to PR review that:
- Leverages language-specific programming skills for code quality checks
- Ensures thorough review across multiple dimensions
- Produces actionable, constructive feedback

<IMPORTANT>
**Invoke relevant programming skills during review:**
- C++ code → Invoke `programming-cpp`, `programming-cpp-design-patterns`, `programming-cpp-stl-algorithms`
- Python code → Invoke `programming-python`
- CMake files → Invoke `programming-cmake-best-practices`

**ALSO invoke `git-gh-client`** when reviewing GitHub PRs to verify gh CLI availability.

These skills contain the standards against which code should be reviewed.
</IMPORTANT>

## Review Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 0: Ask User                             │
│          What do you want to review?                             │
│    - GitHub PR (requires gh CLI)                                 │
│    - Local changes vs branch                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   User provides PR to review                     │
│              (URL, PR number, or local branch)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Gather Info  │
                    │ - PR description      │
                    │ - Changed files       │
                    │ - Commit history      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Understand   │
                    │ - What is the goal?   │
                    │ - What changed?       │
                    │ - What's the scope?   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 3: Load Skills  │
                    │ Invoke programming    │
                    │ skills for languages  │
                    │ in the PR             │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 4: Review Code  │
                    │ - Correctness         │
                    │ - Best practices      │
                    │ - Tests               │
                    │ - Security            │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 5: Summarize    │
                    │ - Overall assessment  │
                    │ - Categorized issues  │
                    │ - Actionable feedback │
                    └───────────────────────┘
```

## Phase 0: Determine Review Type

**IMPORTANT: When this skill is invoked, ALWAYS start by asking the user what they want to review.**

Use the `AskUserQuestion` tool to present these options:

### Option 1: Review GitHub Pull Request
- **Description**: Review a specific PR from GitHub (by PR number or URL)
- **Requirements**: Requires `gh` CLI tool to be installed and authenticated
- **Typical use**: When reviewing PRs from teammates or external contributors

### Option 2: Review Local Changes
- **Description**: Review uncommitted or committed changes in the current directory compared to a base branch (e.g., `develop`, `main`)
- **Requirements**: Only requires git
- **Typical use**: Self-review before creating a PR

### Implementation

Ask the user:
```
Question: "What would you like to review?"
Options:
  1. "GitHub Pull Request (requires gh CLI)"
     → Proceed to ask for PR number/URL
  2. "Local changes compared to a branch"
     → Proceed to ask for base branch (default: develop)
```

### If GitHub PR is selected:

1. **Check if `gh` CLI is available:**
   ```bash
   which gh
   ```

2. **If `gh` is not found**, inform the user:
   ```
   The GitHub CLI (`gh`) is required to review GitHub PRs.

   Installation instructions:

   **Linux (Debian/Ubuntu):**
   ```bash
   sudo apt install gh
   gh auth login
   ```

   **Linux (Fedora/RHEL):**
   ```bash
   sudo dnf install gh
   gh auth login
   ```

   **macOS:**
   ```bash
   brew install gh
   gh auth login
   ```

   **Other platforms:**
   Visit https://cli.github.com/manual/installation

   After installation, authenticate with:
   ```bash
   gh auth login
   ```

   Then re-run this skill.
   ```

3. **If `gh` is available**, ask for PR number or URL

### If Local Changes is selected:

1. Ask which base branch to compare against (default: `develop`)
2. Use git commands to gather changes:
   ```bash
   # Get list of changed files
   git diff --name-only <base-branch>...HEAD

   # Get the actual diff
   git diff <base-branch>...HEAD

   # Get commit messages
   git log <base-branch>...HEAD --oneline
   ```

## Phase 1: Gather Information

Based on the review type selected in Phase 0:

### For GitHub PR Review

```bash
# Get PR info
gh pr view <PR_NUMBER> --json title,body,author,baseRefName,headRefName,files,commits

# Get changed files
gh pr diff <PR_NUMBER>

# Get commit messages
gh pr view <PR_NUMBER> --json commits --jq '.commits[].messageHeadline'
```

### For Local Changes Review

```bash
# Get list of changed files
git diff --name-only <base-branch>...HEAD

# Get the full diff
git diff <base-branch>...HEAD

# Get commit messages for this branch
git log <base-branch>...HEAD --oneline

# Show summary of changes
git diff --stat <base-branch>...HEAD
```

### Identify Languages

Scan changed files to determine which programming skills to invoke:

| File Extension | Programming Skill |
|----------------|-------------------|
| `.cpp`, `.hpp`, `.h`, `.cc` | `programming-cpp` |
| `.py` | `programming-python` |
| `CMakeLists.txt`, `.cmake` | `programming-cmake-best-practices` |

## Phase 2: Understand the Change

Before reviewing code, understand:

1. **Goal**: What is this PR trying to achieve?
   - Read PR description/motivation
   - Check linked issues

2. **Scope**: What files/components are affected?
   - List changed files
   - Identify affected subsystems

3. **Type**: What kind of change is this?
   - Feature (new functionality)
   - Bugfix (correcting behavior)
   - Refactor (improving structure)
   - Docs (documentation only)

## Phase 3: Load Programming Skills

**MANDATORY: Invoke relevant programming skills before reviewing code.**

For each language in the PR:
1. Invoke the programming skill
2. Use its guidelines as review criteria
3. Check against its best practices

Example for C++ PR:
```
Invoke: programming-cpp
Invoke: programming-cpp-design-patterns (if architectural changes)
Invoke: programming-cpp-stl-algorithms (if loops/algorithms present)
```

## Phase 4: Review Dimensions

Review each dimension systematically:

### 4.1 Correctness

| Check | Questions |
|-------|-----------|
| Logic | Does the code do what it claims? |
| Edge cases | Are boundaries handled? |
| Error handling | Are errors caught and handled appropriately? |
| Null/empty | Are null/empty cases considered? |
| Concurrency | Are there race conditions? (if applicable) |

### 4.2 Best Practices (from programming skills)

**For C++ (from `programming-cpp`):**
- RAII for resource management?
- `const` correctness?
- `noexcept` where appropriate?
- Move semantics used correctly?
- No raw `new`/`delete`?
- STL algorithms instead of raw loops?

**For Python (from `programming-python`):**
- Type hints present?
- PEP 8 compliant?
- Docstrings for public functions?
- No mutable default arguments?
- Context managers for resources?

**For CMake (from `programming-cmake-best-practices`):**
- Target-based approach?
- Proper visibility (PUBLIC/PRIVATE/INTERFACE)?
- No deprecated commands?

### 4.3 Tests

| Check | Questions |
|-------|-----------|
| Coverage | Are new code paths tested? |
| Quality | Do tests verify behavior, not implementation? |
| Edge cases | Are boundary conditions tested? |
| Naming | Are test names descriptive? |
| Independence | Can tests run in isolation? |

### 4.4 Security

| Check | Questions |
|-------|-----------|
| Input validation | Is user input validated? |
| Injection | SQL/command injection possible? |
| Secrets | Any hardcoded credentials? |
| Overflow | Buffer/integer overflow risks? |
| Dependencies | New dependencies vetted? |

### 4.5 Design

| Check | Questions |
|-------|-----------|
| Simplicity | Is this the simplest solution? |
| Coupling | Are components loosely coupled? |
| Cohesion | Does each unit have single responsibility? |
| Extensibility | Is it easy to extend/modify? |
| Consistency | Does it match existing patterns? |

### 4.6 Documentation

| Check | Questions |
|-------|-----------|
| PR description | Is motivation clear? |
| Code comments | Are comments meaningful (explain why, not what)? No obvious/trivial comments? |
| API docs | Are public APIs documented? |
| README | Updated if needed? |

## Phase 5: Summarize Review

Present findings in structured format:

```markdown
# PR Review: [PR Title]

## Summary

**Overall:** [Approve / Request Changes / Comment]

**Verdict:** [1-2 sentence summary of the PR quality and readiness]

## What's Good

- [Positive aspect 1]
- [Positive aspect 2]

## Issues Found

### Must Fix (Blocking)

| Location | Issue | Suggestion |
|----------|-------|------------|
| `file.cpp:42` | [Description] | [How to fix] |

### Should Fix (Non-blocking)

| Location | Issue | Suggestion |
|----------|-------|------------|
| `file.cpp:87` | [Description] | [How to fix] |

### Nitpicks (Optional)

| Location | Issue | Suggestion |
|----------|-------|------------|
| `file.cpp:15` | [Description] | [How to fix] |

## Checklist

- [ ] Correctness verified
- [ ] Best practices followed
- [ ] Tests adequate
- [ ] No security issues
- [ ] Design appropriate
- [ ] Documentation sufficient

## Questions for Author

- [Any clarifying questions]
```

## Issue Categories

### Must Fix (Blocking)

Issues that must be resolved before merge:
- Bugs / incorrect behavior
- Security vulnerabilities
- Missing critical tests
- Breaking changes without migration
- Violations of core guidelines

### Should Fix (Non-blocking)

Issues worth addressing but not blocking:
- Minor best practice violations
- Missing edge case handling
- Suboptimal performance
- Missing non-critical tests
- Minor code style issues

### Nitpicks (Optional)

Suggestions for improvement:
- Naming preferences
- Code organization
- Documentation improvements
- Alternative approaches

## Providing Feedback

### Be Constructive

**Good:**
> "Consider using `std::find_if` here instead of the manual loop - it's more expressive and less error-prone."

**Bad:**
> "This loop is wrong."

### Be Specific

**Good:**
> "In `parser.cpp:45`, the error case when `input.empty()` isn't handled. Consider returning `std::nullopt` or throwing."

**Bad:**
> "Error handling is missing."

### Explain Why

**Good:**
> "Using `auto` here hides the type and makes the code harder to understand. Since this is a public API, explicit types improve readability."

**Bad:**
> "Don't use auto."

### Suggest Solutions

**Good:**
> "This could cause a race condition if called from multiple threads. Consider using `std::mutex` or making this thread-local."

**Bad:**
> "Not thread-safe."

## Integration with Other Skills

| Scenario | Skills to Invoke |
|----------|-----------------|
| C++ PR | `programming-cpp`, optionally `design-patterns`, `stl-algorithms` |
| Python PR | `programming-python` |
| CMake changes | `programming-cmake-best-practices` |
| Test files | `testing-gtest-gmock` or `testing-pytest` |
| AMD SMI code | `libraries-amd-smi` |

## Common Review Mistakes

| Mistake | Fix |
|---------|-----|
| Reviewing without understanding goal | Read PR description first |
| Not invoking programming skills | Always load relevant skills |
| Only checking style, not logic | Review correctness first |
| Blocking on nitpicks | Categorize issues properly |
| Vague feedback | Be specific with file:line |
| No positive feedback | Acknowledge what's done well |
| Reviewing too fast | Take time for large PRs |

## Quick Review Checklist

For fast reviews, at minimum check:

- [ ] Does the code do what the PR claims?
- [ ] Are there obvious bugs?
- [ ] Are there tests?
- [ ] Any security red flags?
- [ ] Does it follow project conventions?

## References

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [How to Do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-1/)
