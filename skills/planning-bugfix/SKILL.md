---
name: planning-bugfix
description: Use when fixing a bug - root-cause hypothesis, fix scope, optional changelog update. Triggers on "bug", "fix", "regression", or any defect report. Skip for typos, single-line obvious fixes, or behavior changes that aren't a defect (use planning-feature). Composes with: programming-cpp / programming-python (the implementation), testing (REQUIRED - every bug fix gets a regression test that would have caught the bug), debugging-rocprof-sys (when the bug surfaces in rocprofiler-systems output).
---

# Bugfix Planning

Use this skill when fixing bugs, errors, or unexpected behavior.

<IMPORTANT>
**Prerequisites:** Invoke `planning-base` skill first if not already loaded. It provides the core planning phases (0-5) AND the mandatory programming-skill consultation rules.

Follow all base planning rules, plus the bugfix-specific rules below.

**Mandatory programming-skill invocation** (from planning-base, restated for visibility):

- C++ bug → invoke `programming-cpp`; add
  `programming-cpp-naming-rules` if the fix renames anything; add
  `programming-cpp-stl-algorithms` if the fix replaces hand-rolled
  iteration with STL.
- Python bug → invoke `programming-python`.
- CMake-touching → invoke `programming-cmake-best-practices`.

Invoke BEFORE drafting the fix so the proposed change conforms to
language rules from the start (e.g., constants in screaming snake case,
no `tim::*`, RAII over raw resource management).

**Mandatory `debugging-rocprof-sys`** when the bug surfaces in
rocprofiler-systems output (crash, hang, wrong trace contents,
instrumentation failure, GPU/MPI/threading misbehavior during
profiling).

**Mandatory regression test.** Every bug fix gets a test that fails
before the fix and passes after. No exceptions. Invoke `testing` (the
dispatcher) to decide scope and route to `testing-gtest-gmock` or
`testing-pytest`.
</IMPORTANT>

## Bugfix-Specific Requirements

### Root Cause Analysis

Before proposing fixes, identify:

1. **What is the bug?** - Exact symptoms and error messages
2. **Where does it occur?** - Specific file, function, line
3. **Why does it happen?** - Root cause, not just symptoms
4. **When was it introduced?** - If known, helps understand context

### Changelog Consideration

After analysis, ASK the user:

> "Should this bugfix be added to the changelog?
> - Yes: If it's a user-facing bug that affected functionality
> - No: If it's an internal fix or minor issue
>
> Add to changelog? (yes/no)"

If yes, include changelog entry:

```markdown
## Changelog Entry

### Fixed
- <Brief description of what was broken and how it's fixed>
```

### Test Plan

After COMPLETING the bugfix:

1. **Create test plan file:** `planning/testplan-<bugfix-name>.md`
2. Invoke `testing-testplan` skill for the template
3. Document how the fix was verified
4. Include regression check for related functionality

### Regression Prevention

Then ASK the user:

> "Bugfix is complete. Would you like me to add a regression test to prevent this bug from recurring?"

If user agrees:
1. Invoke the testing skill: `testing-gtest-gmock` (C++) or `testing-pytest` (Python)
2. Create a test that specifically reproduces the bug scenario
3. Verify the test would have failed before the fix
4. Wait for user approval of the test
5. Update test plan file with test status

### Pull Request

After tests (if any), ASK the user:

> "Ready to create a Pull Request. Should I proceed?"

If yes, invoke `git-create-pull-request` skill and create PR with:
- **Motivation** - What bug was fixed and its impact
- **Technical Details** - Root cause and fix
- **Test Plan** - Regression test that prevents recurrence

## Plan File Format

Save to `planning/bugfix-<name>.md`:

```markdown
# Bugfix: <Bug Description>

## Problem
<What is broken, error messages, symptoms>

## Root Cause
<Why the bug occurs>

## Analysis
<Affected files, related code, risks of fix>

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Verify fix works

## Changelog
<Entry if requested, or "Not added to changelog">

## Regression Test
<Test description if requested, or "No regression test">

## Notes
<Any additional context>
```

## Example

**User request:** "Fix login timeout - users getting logged out after 5 minutes"

**Planning output:**

```markdown
# Bugfix: Premature Session Timeout

## Problem
Users are being logged out after 5 minutes instead of the expected 30 minutes.
Error: "Session expired" toast appears unexpectedly.

## Root Cause
Token refresh interval was set to 5 minutes (300000ms) but the condition 
checked for token age > 5 minutes, causing immediate refresh failure loop.

## Analysis
- File: src/auth/tokenService.ts, line 45
- The refresh check uses `>` instead of `>=`, causing edge case failure
- Risk: Low - isolated fix in token handling

## Tasks
- [ ] Fix comparison operator in tokenService.ts
- [ ] Verify token refresh works correctly
- [ ] Update CHANGELOG.md

## Changelog
### Fixed
- Session timeout now correctly respects 30-minute duration

## Regression Test
- [ ] Unit: Token refresh timing edge cases

## Notes
- Also found: TOKEN_REFRESH_INTERVAL constant should be moved to config
```
