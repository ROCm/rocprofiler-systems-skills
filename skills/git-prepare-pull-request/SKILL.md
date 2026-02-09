---
name: git-prepare-pull-request
description: Prepare well-structured Pull Requests - verify code quality, check for issues, split large changes, write clear descriptions with Motivation, Technical Details, and Test Plan
---

# Prepare Pull Request Skill

Use this skill when planning and preparing Pull Requests. For reviewing PRs, use `git-review-pull-request` instead.

<IMPORTANT>
**Before creating a PR, run comprehensive code verification.**

This skill includes a mandatory verification phase that:
- Checks code against programming standards
- Finds unused code, TODOs, and cleanup opportunities
- Identifies code duplication and improvement opportunities
- Validates architecture and design patterns

**Invoke relevant programming skills for verification:**
- C++ code → `programming-cpp`, `programming-cpp-design-patterns`, `programming-cpp-stl-algorithms`
- Python code → `programming-python`
- CMake files → `programming-cmake-best-practices`

**ALSO invoke `git-gh-client`** to verify GitHub CLI is available for PR creation.
</IMPORTANT>

## PR Preparation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                   User asks to prepare PR                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 0: Verify gh    │
                    │ Invoke: git-gh-client │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Gather       │
                    │ - Get changed files   │
                    │ - Identify languages  │
                    │ - Load relevant skills│
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Code Review  │
                    │ - Standards check     │
                    │ - Unused code/TODOs   │
                    │ - Duplication check   │
                    │ - Architecture review │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 3: Report       │
                    │ - Present findings    │
                    │ - Ask user decisions  │
                    │ - Apply fixes         │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 4: Size Check   │
                    │ - Count lines changed │
                    │ - Split if needed     │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 5: Create PR    │
                    │ - Write description   │
                    │ - Push and submit     │
                    └───────────────────────┘
```

## Phase 0: Verify GitHub CLI

**FIRST ACTION: Invoke `git-gh-client` skill**

This ensures gh CLI is installed and authenticated for PR creation.
If not available, git-gh-client provides installation instructions.

## Phase 1: Gather Information

### Get Changed Files

```bash
# Get list of changed files
git diff --name-only HEAD~1..HEAD  # or vs main branch
git diff --stat

# Identify file types
git diff --name-only | xargs -I{} basename {} | sed 's/.*\.//' | sort | uniq -c
```

### Load Programming Skills

Based on file types, invoke relevant skills:

| File Extension | Skills to Load |
|----------------|----------------|
| `.cpp`, `.hpp`, `.h` | `programming-cpp`, `programming-cpp-design-patterns`, `programming-cpp-stl-algorithms`, `programming-cpp-naming-rules` |
| `.py` | `programming-python` |
| `CMakeLists.txt`, `.cmake` | `programming-cmake-best-practices` |

## Phase 2: Code Verification

<IMPORTANT>
This phase is **MANDATORY** before creating a PR. Catch problems before reviewers do.
</IMPORTANT>

### 2.1 Standards Compliance Check

For each changed file, verify against loaded programming skills:

**C++ Checks:**
- [ ] Follows C++ Core Guidelines
- [ ] Uses modern C++17 features appropriately
- [ ] Const correctness (`const`, `constexpr` where applicable)
- [ ] Proper use of `noexcept`, `[[nodiscard]]`
- [ ] RAII for resource management
- [ ] No raw `new`/`delete` (use smart pointers)
- [ ] Proper error handling

**Python Checks:**
- [ ] PEP 8 compliance
- [ ] Type hints on all functions
- [ ] Docstrings where needed
- [ ] No bare `except:` clauses
- [ ] Proper use of context managers

**CMake Checks:**
- [ ] Target-based approach
- [ ] Proper visibility keywords
- [ ] No deprecated commands

### 2.2 Unused Code and TODOs

Search for and report:

```bash
# Find TODOs in changed files
git diff --name-only | xargs grep -n "TODO\|FIXME\|XXX\|HACK" 2>/dev/null

# Find commented-out code (heuristic)
git diff --name-only | xargs grep -n "^[[:space:]]*//.*[;{}]" 2>/dev/null
```

**For each TODO/FIXME found, ask user:**

Use `AskUserQuestion` tool:

```json
{
  "questions": [{
    "question": "Found TODO in file.cpp:42: 'TODO: implement error handling'. What should we do?",
    "header": "TODO found",
    "options": [
      {"label": "Fix now", "description": "Implement the TODO before creating PR"},
      {"label": "Remove", "description": "Delete the TODO comment (if no longer needed)"},
      {"label": "Keep", "description": "Leave as-is, will address in future PR"},
      {"label": "Convert to issue", "description": "Create GitHub issue to track this"}
    ],
    "multiSelect": false
  }]
}
```

**For unused code (commented out, dead code):**

```json
{
  "questions": [{
    "question": "Found commented-out code in file.cpp:78-85. What should we do?",
    "header": "Dead code",
    "options": [
      {"label": "Remove", "description": "Delete the commented code (recommended)"},
      {"label": "Keep", "description": "Leave as-is (explain why in PR)"},
      {"label": "Restore", "description": "Uncomment and use the code"}
    ],
    "multiSelect": false
  }]
}
```

### 2.3 Code Duplication Check

Analyze changed files for:

**Within-file duplication:**
- Similar code blocks (>10 lines)
- Repeated logic patterns
- Copy-paste signatures

**Cross-file duplication:**
- Same function in multiple files
- Repeated utility code
- Patterns that should be abstracted

**Report format:**

```markdown
### Duplication Found

**Location 1:** `src/module_a/handler.cpp:45-60`
**Location 2:** `src/module_b/processor.cpp:120-135`
**Similarity:** ~90%

**Suggested action:** Extract to common utility function in `src/common/utils.cpp`
```

**Ask user:**

```json
{
  "questions": [{
    "question": "Found duplicate code in handler.cpp and processor.cpp. Extract to shared utility?",
    "header": "Duplication",
    "options": [
      {"label": "Extract now", "description": "Create shared function and refactor both usages"},
      {"label": "Keep separate", "description": "Leave as-is (intentional duplication)"},
      {"label": "Track for later", "description": "Create issue to address in future refactor"}
    ],
    "multiSelect": false
  }]
}
```

### 2.4 Architecture and Design Review

Check for:

**Structural issues:**
- [ ] Functions too long (>50 lines)
- [ ] Classes with too many responsibilities
- [ ] Deep nesting (>3 levels)
- [ ] Long parameter lists (>5 params)
- [ ] Circular dependencies

**Design pattern opportunities:**
- Could Factory pattern simplify object creation?
- Could Strategy pattern replace conditionals?
- Could Observer pattern decouple components?

**C++ specific:**
- Could templates reduce duplication?
- Could `constexpr` move computation to compile-time?
- Could STL algorithms replace manual loops?

**Report improvements:**

```markdown
### Improvement Opportunities

| Location | Issue | Suggestion | Priority |
|----------|-------|------------|----------|
| `parser.cpp:validate()` | Function is 80 lines | Split into smaller functions | Medium |
| `handler.cpp:process()` | 6 parameters | Use parameter object or builder | Low |
| `utils.cpp:findItem()` | Manual loop | Use `std::find_if` | Low |
| `factory.cpp` | Switch on type | Consider Factory pattern | Medium |
```

**Ask user for each significant improvement:**

```json
{
  "questions": [{
    "question": "validate() in parser.cpp is 80 lines. Should we refactor before PR?",
    "header": "Long function",
    "options": [
      {"label": "Refactor now", "description": "Split into smaller functions in this PR"},
      {"label": "Separate PR", "description": "Create refactoring PR first, then this PR"},
      {"label": "Keep as-is", "description": "Leave for now, note in PR description"}
    ],
    "multiSelect": false
  }]
}
```

### 2.5 Potential Bug Detection

Check for common issues:

**Memory/Resource:**
- Uninitialized variables
- Missing null checks
- Resource leaks (files, connections)
- Use-after-move

**Logic:**
- Off-by-one errors
- Missing break in switch
- Incorrect operator precedence
- Floating-point comparison with `==`

**Concurrency:**
- Race conditions
- Missing locks
- Deadlock potential

**Security:**
- SQL injection risks
- Command injection
- Buffer overflows
- Hardcoded credentials

### 2.6 Test Coverage Check

```bash
# Check if new code has tests
git diff --name-only | grep -v "_test\|test_\|_spec" | while read f; do
    testfile=$(echo "$f" | sed 's/\.cpp/_test.cpp/' | sed 's/\.py/test_&/')
    if [ ! -f "$testfile" ]; then
        echo "Missing tests for: $f"
    fi
done
```

**Ask if tests are missing:**

```json
{
  "questions": [{
    "question": "No tests found for new_feature.cpp. Add tests before PR?",
    "header": "Missing tests",
    "options": [
      {"label": "Add tests now", "description": "Write unit tests before creating PR"},
      {"label": "PR without tests", "description": "Create PR, add tests as follow-up"},
      {"label": "Not needed", "description": "Code doesn't require tests (explain why)"}
    ],
    "multiSelect": false
  }]
}
```

## Phase 3: Verification Report

Present comprehensive findings to user:

```markdown
## PR Preparation Report

### Standards Compliance
| Check | Status | Notes |
|-------|--------|-------|
| C++ Core Guidelines | ✅ Pass | |
| Const correctness | ⚠️ Warning | 2 functions missing const |
| Error handling | ✅ Pass | |

### Code Quality Issues

**Must Fix (blocking):**
1. ❌ Uninitialized variable in `parser.cpp:45`
2. ❌ Missing null check in `handler.cpp:78`

**Should Fix (recommended):**
1. ⚠️ TODO in `utils.cpp:23` - decide: fix/remove/keep
2. ⚠️ Commented code in `old_impl.cpp:100-120`
3. ⚠️ Duplicate code in `module_a/` and `module_b/`

**Suggestions (optional):**
1. 💡 Long function `validate()` could be split
2. 💡 Manual loop could use `std::find_if`
3. 💡 Consider Factory pattern for object creation

### Test Coverage
- New files: 3
- Files with tests: 2
- Missing tests: `new_feature.cpp`

### Summary
- **Blocking issues:** 2
- **Warnings:** 3
- **Suggestions:** 3
```

**Then ask:**

```json
{
  "questions": [{
    "question": "How should we proceed with the 2 blocking issues?",
    "header": "Blocking issues",
    "options": [
      {"label": "Fix all", "description": "Fix all blocking issues before PR"},
      {"label": "Show details", "description": "Show me each issue to decide individually"},
      {"label": "Override", "description": "Create PR anyway (not recommended)"}
    ],
    "multiSelect": false
  }]
}
```

## Phase 4: PR Size Check

### Ideal PR Size
- **< 400 lines changed** - Easy to review, quick turnaround
- **400-800 lines** - Acceptable for complex features
- **> 800 lines** - Should be split into multiple PRs

### When to Split

Split into multiple PRs when:
- Changes touch multiple unrelated systems
- Refactoring can be separated from feature work
- Infrastructure changes can land independently
- Tests can be added before implementation

### Split Strategy

```
Large Feature
     │
     ├── PR 1: Refactoring (prepare codebase)
     │         - Extract interfaces
     │         - Move code to better locations
     │         - No behavior change
     │
     ├── PR 2: Infrastructure
     │         - Add new dependencies
     │         - Create base classes/interfaces
     │         - Add configuration
     │
     ├── PR 3: Core Implementation
     │         - Main feature logic
     │         - Unit tests
     │
     └── PR 4: Integration
              - Wire everything together
              - Integration tests
              - Documentation
```

## Phase 5: Create the PR

### PR Structure

Every PR MUST have these sections:

#### 1. Motivation

**Why** is this change needed?

```markdown
## Motivation

[Explain the problem or need this PR addresses]

- What issue does this solve?
- What feature does this enable?
- What improvement does this bring?

Related issue: #123 (if applicable)
```

#### 2. Technical Details

**What** does this PR change and **how**?

```markdown
## Technical Details

[Explain the implementation approach]

### Changes
- [List key changes]
- [Explain architectural decisions]
- [Note any trade-offs made]

### Files Changed
- `src/module/file.cpp` - [Brief description]
- `include/module/file.hpp` - [Brief description]
```

#### 3. Test Plan

**How** was this tested?

```markdown
## Test Plan

### Unit Tests
- [ ] `test_feature_basic` - Tests basic functionality
- [ ] `test_feature_edge_cases` - Tests boundary conditions
- [ ] `test_feature_error_handling` - Tests error paths

### Manual Testing
- [ ] [Step-by-step manual test if applicable]

### Verification
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] No new warnings introduced
```

### PR Template

```markdown
## Motivation

[Why is this change needed? What problem does it solve?]

## Technical Details

### Summary
[One paragraph summary of the changes]

### Key Changes
- [Change 1]
- [Change 2]
- [Change 3]

### Design Decisions
[Explain any significant design choices and their rationale]

## Test Plan

### Automated Tests
- [ ] Unit tests added/updated
- [ ] All tests passing

### Manual Verification
- [ ] [Describe manual testing performed]

## Pre-PR Verification

- [x] Code verified against programming standards
- [x] No blocking issues found
- [x] TODOs addressed or tracked
- [x] No unnecessary code duplication

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added only for non-obvious logic
- [ ] Documentation updated (if applicable)
- [ ] No unrelated changes included
```

### Creating the PR

After verification is complete and user approves:

```bash
# Create branch (if not already on feature branch)
git checkout -b feature/descriptive-name

# Stage and commit (use conventional commits if project uses them)
git add .
git commit -m "feat: add user avatar upload

- Add avatar upload endpoint
- Create AvatarUpload component
- Add image validation"

# Push and create PR
git push -u origin HEAD

# Create PR with gh CLI
gh pr create --title "feat: Add user avatar upload" --body "$(cat <<'EOF'
## Motivation

Users need the ability to upload profile avatars to personalize their accounts.
This feature was requested in #123.

## Technical Details

### Summary
Adds avatar upload functionality with client-side preview and server-side validation.

### Key Changes
- Added `POST /api/users/avatar` endpoint
- Created `AvatarUpload` React component with drag-and-drop
- Implemented image validation (size, format)
- Added image resizing to reduce storage

### Design Decisions
- Chose to resize on server to ensure consistent dimensions
- Using WebP format for storage to reduce size

## Test Plan

### Automated Tests
- [x] `test_avatar_upload_valid_image` - Upload succeeds with valid JPG
- [x] `test_avatar_upload_invalid_format` - Rejects non-image files
- [x] `test_avatar_upload_too_large` - Rejects files > 5MB
- [x] `test_avatar_resize` - Verifies resizing to 256x256

### Manual Verification
- [x] Upload works in Chrome, Firefox, Safari
- [x] Drag-and-drop works correctly
- [x] Preview displays before upload

## Pre-PR Verification

- [x] Code verified against C++ Core Guidelines
- [x] No blocking issues found
- [x] All TODOs addressed
- [x] No code duplication

EOF
)"
```

## Verification Checklist Summary

Before creating PR, ensure:

### Blocking (must fix)
- [ ] No uninitialized variables
- [ ] No null pointer risks
- [ ] No resource leaks
- [ ] No security vulnerabilities
- [ ] All tests pass

### Important (should fix)
- [ ] TODOs addressed (fixed, removed, or tracked)
- [ ] No commented-out code
- [ ] No significant duplication
- [ ] Functions not excessively long
- [ ] Test coverage adequate

### Optional (nice to have)
- [ ] STL algorithms used where applicable
- [ ] Design patterns applied where beneficial
- [ ] Compile-time computation where possible
- [ ] Documentation complete

## Integration with Planning

### During Task Planning

When creating a plan in `planning/feature-*.md` or `planning/refactor-*.md`:

1. **Assess total scope** - How many lines will change?
2. **Identify logical boundaries** - What can be separated?
3. **Plan PR sequence** - Which PRs depend on others?
4. **Document in plan file**:

```markdown
## PR Strategy

### PR 1: [Title]
**Scope:** [What's included]
**Dependencies:** None
**Estimated size:** ~200 lines

### PR 2: [Title]
**Scope:** [What's included]
**Dependencies:** PR 1
**Estimated size:** ~350 lines
```

## Examples

### Good PR: Focused and Clean

```markdown
## Motivation

Session timeout is incorrectly set to 5 minutes instead of 30 minutes,
causing users to be logged out unexpectedly. Fixes #456.

## Technical Details

### Summary
Fixed token refresh timing comparison that caused premature session expiry.

### Key Changes
- Fixed comparison operator in `tokenService.ts:45` (`>` → `>=`)
- Added constant `SESSION_TIMEOUT_MS` to centralize configuration

### Design Decisions
- Moved timeout value to config for easier adjustment in future

## Test Plan

### Automated Tests
- [x] `test_token_refresh_at_boundary` - Tests exact timeout boundary
- [x] `test_session_persists_29_minutes` - Verifies no early logout

### Manual Verification
- [x] Logged in and waited 25 minutes - session persisted
- [x] Verified refresh token request at expected time

## Pre-PR Verification

- [x] Code verified against standards
- [x] No TODOs or commented code
- [x] No duplication introduced
```

### Bad PR: Unverified, Messy

```markdown
## Changes

- Fixed session timeout bug
- TODO: add more tests later
- Left old implementation commented out just in case
- Also refactored auth module while I was there
```

**Problems:**
- No verification performed
- Contains TODO
- Contains commented-out code
- Multiple unrelated changes

## References

- [How to Write a Git Commit Message](https://cbea.ms/git-commit/)
- [GitHub Pull Request Documentation](https://docs.github.com/en/pull-requests)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
