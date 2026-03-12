---
name: pr-review
description: Review Pull Requests or local changes - check code quality, correctness, tests, and provide actionable feedback
---

# PR Review Skill

Review Pull Requests or local changes with structured, thorough analysis.

<IMPORTANT>
**Determine review target automatically:**
- If user provides PR number or URL → Review that GitHub PR
- If no PR specified → Review local changes vs main branch (no questions asked)

**Invoke relevant programming skills during review:**
- C++ code → `programming-cpp`, `programming-cpp-design-patterns`, `programming-cpp-stl-algorithms`
- Python code → `programming-python`
- CMake files → `programming-cmake-best-practices`
</IMPORTANT>

## Review Process

```
┌─────────────────────────────────────────────────────────────────┐
│              Phase 0: Determine Review Target                    │
│    - PR number/URL provided? → Review GitHub PR                  │
│    - Nothing provided? → Review local changes vs main            │
│    - Re-review? → Show only changes since last review            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Gather Info  │
                    │ - Changed files       │
                    │ - Commit history      │
                    │ - CI status (GitHub)  │
                    │ - Existing comments   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Detect Scope │
                    │ - Architectural?      │
                    │ - Which languages?    │
                    │ - Change type?        │
                    └───────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
┌──────────────────────────┐        ┌───────────────────────┐
│ Phase 3A: Architecture   │        │ Phase 3B: Load Skills │
│ (if architectural)       │        │ Programming skills    │
│ Invoke architecture-     │        │ for languages in PR   │
│ analyze skill            │        │                       │
└──────────────────────────┘        └───────────────────────┘
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 4: Review Code  │
                    │ - Read context around │
                    │ - Apply skill rules   │
                    │ - Score by severity   │
                    │ - Provide fix code    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 5: Summarize    │
                    │ - Severity-sorted     │
                    │ - With code fixes     │
                    │ - Actionable feedback │
                    └───────────────────────┘
```

## Phase 0: Determine Review Target

**Do NOT ask the user what to review. Determine automatically:**

| User Input | Action |
|------------|--------|
| PR number (e.g., `123`, `#123`) | Review GitHub PR #123 |
| PR URL (e.g., `github.com/.../pull/123`) | Review that GitHub PR |
| "re-review" or "review again" | Re-review mode (show only new changes) |
| Nothing / just "review" | Review local changes vs main branch |

### For GitHub PR:

**Invoke `git-gh-client`** to verify gh CLI is available.
Then fetch PR data using gh commands.

### For Local Changes (default):

Automatically compare against `main` branch (or `master` if main doesn't exist):

```bash
# Determine base branch
base_branch=$(git rev-parse --verify main 2>/dev/null && echo "main" || echo "master")

# Get changed files
git diff --name-only $base_branch...HEAD

# Get the diff
git diff $base_branch...HEAD

# Get commit messages
git log $base_branch...HEAD --oneline
```

### Re-review Mode

When user asks to "re-review" or "review again":

1. Check for previous review commits/comments
2. Identify what changed since last review:
   ```bash
   # If you know the last reviewed commit
   git diff <last-reviewed-commit>...HEAD

   # For GitHub PRs - check commits since last review
   gh pr view <PR_NUMBER> --json commits,reviews
   ```
3. Focus review on NEW changes only
4. Note which previous issues were addressed

## Phase 1: Gather Information

Based on the review type selected in Phase 0:

### For GitHub PR Review

Use commands from `git-gh-client` to fetch PR data:
- `gh pr view <PR_NUMBER> --json ...` for metadata
- `gh pr diff <PR_NUMBER>` for changes
- See `git-gh-client` Phase 2 for full command reference

#### 1.1 Check CI Status First

**Before reviewing code, check if CI passed:**

```bash
# Check CI status (invoke git-pull-request-status skill)
gh pr checks <PR_NUMBER> || true
```

| CI Status | Action |
|-----------|--------|
| All passed | Proceed with review |
| Some failed | Note failures, still review code but mention CI issues |
| All failed | Consider waiting for fixes before detailed review |

#### 1.2 Fetch Existing Review Comments

**Check what's already been discussed:**

```bash
# Get existing review comments
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments --jq '.[] | {path: .path, line: .line, body: .body}'

# Get review threads
gh pr view <PR_NUMBER> --json reviews --jq '.reviews[] | {author: .author.login, state: .state, body: .body}'
```

**Use existing comments to:**
- Avoid duplicating feedback already given
- Check if previous issues were addressed
- Understand ongoing discussions

### For Local Changes Review

```bash
# Get list of changed files
git diff --name-only <base-branch>...HEAD

# Get the full diff
git diff <base-branch>...HEAD

# Get commit messages for this branch
git log <base-branch>...HEAD --oneline
```

### Identify Languages

Scan changed files to determine which programming skills to invoke:

| File Extension | Programming Skill |
|----------------|-------------------|
| `.cpp`, `.hpp`, `.h`, `.cc` | `programming-cpp` |
| `.py` | `programming-python` |
| `CMakeLists.txt`, `.cmake` | `programming-cmake-best-practices` |

## Phase 2: Detect Scope and Type

Before reviewing code, understand and classify:

### 2.1 Understand the Goal

- Read PR description/motivation
- Check linked issues
- Identify affected subsystems

### 2.2 Classify Change Type

| Type | Description |
|------|-------------|
| Feature | New functionality |
| Bugfix | Correcting behavior |
| Refactor | Improving structure |
| Docs | Documentation only |

### 2.3 Detect Architectural Changes

**Check if PR involves architectural changes:**

| Signal | Indicates Architecture |
|--------|------------------------|
| New directories created | New module/component |
| New/modified interfaces or abstract classes | API boundaries changing |
| Changes to factories, DI, object creation | Dependency structure changing |
| New CMake targets (`add_library`, `add_executable`) | New build units |
| Changes across 5+ files in different modules | Cross-cutting change |
| New external dependencies | Integration points |
| Changes to base/core classes | Foundation shifting |

**If ANY architectural signal detected → Proceed to Phase 3A**

## Phase 3A: Architecture Analysis (if architectural)

<IMPORTANT>
**If architectural changes detected, invoke `architecture-analyze` skill BEFORE code review.**

Architectural issues are harder to fix later - catch them early.
</IMPORTANT>

The `architecture-analyze` skill will:
1. Spawn an Explore agent to understand existing architecture
2. Analyze module boundaries
3. Check dependency direction and cycles
4. Assess testability
5. Check for over-engineering

**Include architecture findings in final review report as "Must Fix" or "Should Fix" items.**

## Phase 3B: Load Programming Skills

**MANDATORY: Invoke relevant programming skills before reviewing code.**

For each language in the PR:
1. Invoke the programming skill
2. **Use its rules as the source of truth** - not existing codebase patterns
3. Apply its best practices strictly

Example for C++ PR:
```
Invoke: programming-cpp
Invoke: programming-cpp-design-patterns (if architectural changes)
Invoke: programming-cpp-stl-algorithms (if loops/algorithms present)
Invoke: programming-cpp-naming-rules
```

<IMPORTANT>
**Programming skills define the standard, not existing code.**

If existing codebase violates best practices, new code should still follow the skills.
Do not propagate bad patterns just because "that's how it's done here."
</IMPORTANT>

## Phase 4: Review Code Changes

<IMPORTANT>
**Systematic review: enumerate all changes, then review each one.**

Do NOT skim. Go through every changed file and every hunk methodically.
</IMPORTANT>

### 4.1 Enumerate Changes

First, create a list of all changes to review:

```markdown
## Changes to Review

| # | File | Type | Lines | Status |
|---|------|------|-------|--------|
| 1 | `src/parser.cpp` | Modified | +45 -12 | Pending |
| 2 | `src/parser.hpp` | Modified | +8 -2 | Pending |
| 3 | `src/utils/helper.cpp` | New | +120 | Pending |
| 4 | `tests/parser_test.cpp` | Modified | +35 -5 | Pending |
```

### 4.2 Review Each Change

**For EACH file in the list, analyze systematically:**

#### Step 1: Read Context Around Changes

**Don't just read the diff - understand the context.**

```bash
# Read the full file, not just changed lines
# Use Read tool to see surrounding code

# For each changed function, understand:
# - What does this function do?
# - What calls it?
# - What does it call?
```

Understanding context helps catch:
- Changes that break callers
- Missing updates to related code
- Inconsistencies with surrounding code

#### Step 2: Apply Language-Specific Rules

**Apply rules from programming skills strictly. These are the standard.**

**For C++ files** (from `programming-cpp`, `programming-cpp-naming-rules` skills):

| Category | Check |
|----------|-------|
| **Naming** | Follows project conventions? Class/function/variable names clear? |
| **const** | Parameters `const&` where appropriate? Member functions `const`? Variables `const` when not modified? |
| **auto** | Used appropriately? Not hiding important types? Iterator/lambda OK, avoid for simple types in APIs |
| **References** | `const&` for input params? `&` or `&&` for output? No dangling references? |
| **Pointers** | Smart pointers used? No raw `new`/`delete`? Null checks where needed? |
| **RAII** | Resources managed by objects? No manual cleanup needed? |
| **Move semantics** | `std::move` for transferring ownership? No use-after-move? |
| **noexcept** | Destructors, move ops, swap marked `noexcept`? |
| **[[nodiscard]]** | Functions with important return values marked? |
| **Error handling** | Exceptions or error codes used consistently? All error paths handled? |
| **STL algorithms** | `std::find`, `std::transform` instead of raw loops where applicable? |
| **Initialization** | All variables initialized? In-class member initializers used? |

**For Python files** (from `programming-python` skill):

| Category | Check |
|----------|-------|
| **Naming** | snake_case for functions/variables? PascalCase for classes? |
| **Type hints** | All function parameters and returns typed? |
| **Docstrings** | Public functions/classes documented? |
| **Defaults** | No mutable default arguments (`def f(x=[])`)?  |
| **Context managers** | `with` used for files, locks, connections? |
| **Exceptions** | Specific exceptions caught? No bare `except:`? |
| **F-strings** | Used instead of `.format()` or `%`? |
| **Comprehensions** | Used where clearer than loops? Not overly complex? |

**For CMake files** (from `programming-cmake-best-practices` skill):

| Category | Check |
|----------|-------|
| **Targets** | `target_*` commands instead of global? |
| **Visibility** | `PUBLIC`/`PRIVATE`/`INTERFACE` used correctly? |
| **Modern CMake** | No deprecated commands (`include_directories`, `link_directories`)? |
| **Variables** | Proper scoping? No pollution of parent scope? |

#### Step 3: Check Code Quality (All Languages)

| Smell | What to Look For |
|-------|------------------|
| **Long function** | >50 lines? Should be split? |
| **Long parameter list** | >5 params? Use struct/object? |
| **Deep nesting** | >3 levels? Refactor with early returns? |
| **Magic numbers** | Unexplained literals? Should be named constants? |
| **Dead code** | Unreachable code? Commented-out code? |
| **Duplicate code** | Same logic repeated? Extract to function? |
| **God class** | Class doing too much? Single responsibility? |
| **Feature envy** | Method using other class's data excessively? |
| **Primitive obsession** | Using primitives instead of small objects? |
| **Inappropriate intimacy** | Classes too tightly coupled? |
| **Long if/else chain** | 3+ branches? See refactoring patterns below |
| **Type-based branching** | `dynamic_cast` or `typeid` chains? Use polymorphism |

#### Step 3.1: Detect Bad if/else Patterns

**Flag these patterns for refactoring:**

| Pattern | Threshold | Suggested Fix |
|---------|-----------|---------------|
| if/else chain | 3+ branches | Lookup table, polymorphism, or command map |
| switch statement | 5+ cases | Same as above |
| Nested if/else | 3+ levels deep | Early return (guard clauses) |
| `dynamic_cast` chain | Any | `std::variant` + `std::visit` or polymorphism |
| Repeated null checks | Same var 3+ times | Null Object pattern |
| Boolean flag parameters | `if (flag)` dispatch | Split into two functions or use strategy |

**Example issue report:**

```markdown
#### Issue: Long if/else chain (Score: 50 - Should Fix)

**Lines 45-78:**
```cpp
// Current: 6-branch if/else chain
if (type == "json") {
    parseJson(data);
} else if (type == "xml") {
    parseXml(data);
} else if (type == "csv") {
    parseCsv(data);
} else if (type == "yaml") {
    parseYaml(data);
} else if (type == "toml") {
    parseToml(data);
} else {
    throw std::runtime_error("Unknown type");
}

// Fixed: Command map
const std::unordered_map<std::string, std::function<void(Data&)>> PARSERS = {
    {"json", parseJson},
    {"xml",  parseXml},
    {"csv",  parseCsv},
    {"yaml", parseYaml},
    {"toml", parseToml}
};

auto it = PARSERS.find(type);
if (it == PARSERS.end()) {
    throw std::runtime_error("Unknown type: " + type);
}
it->second(data);
```

**Why:** Long if/else chains are hard to maintain and extend. Adding a new type requires modifying the function. With a map, just add an entry.

**See:** `programming-cpp` skill → "Eliminating if/else Branching" for more patterns.
```

#### Step 4: Check Correctness

| Check | Questions |
|-------|-----------|
| **Logic** | Does the code do what it claims? |
| **Edge cases** | Empty input? Max values? Null? Zero? |
| **Error handling** | All error paths covered? Resources cleaned up on error? |
| **Concurrency** | Race conditions? Proper locking? Deadlock potential? |
| **Overflow** | Integer overflow possible? Buffer bounds checked? |

#### Step 5: Check Security

| Check | Questions |
|-------|-----------|
| **Input validation** | User input validated/sanitized? |
| **Injection** | SQL/command/path injection possible? |
| **Secrets** | Hardcoded credentials? API keys in code? |
| **Permissions** | Proper access control? Privilege escalation? |

#### Step 6: Score and Record Findings

**Assign severity scores to prioritize issues:**

| Severity | Score | Criteria | Examples |
|----------|-------|----------|----------|
| **Critical** | 100 | Security vulnerability, data loss, crash | SQL injection, use-after-free, null deref |
| **Must Fix** | 80 | Incorrect behavior, UB, resource leak | Logic bug, memory leak, race condition |
| **Should Fix** | 50 | Best practice violation, maintainability | Missing const, raw loop, poor naming |
| **Nitpick** | 20 | Style, minor improvements | Line length, comment wording |

**For each issue, provide actual fix code:**

```markdown
### File: `src/parser.cpp`

**Status:** Reviewed

---

#### Issue 1: Missing null check (Score: 80 - Must Fix)

**Line 42:**
```cpp
// Current code:
auto result = ptr->getValue();

// Fixed code:
if (!ptr) {
    return std::nullopt;
}
auto result = ptr->getValue();
```

**Why:** Dereferencing null pointer causes undefined behavior.

---

#### Issue 2: Raw loop instead of algorithm (Score: 50 - Should Fix)

**Lines 67-72:**
```cpp
// Current code:
for (int i = 0; i < items.size(); i++) {
    if (items[i].name == target) {
        return i;
    }
}
return -1;

// Fixed code:
auto it = std::find_if(items.begin(), items.end(),
    [&target](const auto& item) { return item.name == target; });
return it != items.end() ? std::distance(items.begin(), it) : -1;
```

**Why:** STL algorithms are more expressive and less error-prone.

---

#### Issue 3: Unclear variable name (Score: 20 - Nitpick)

**Line 89:**
```cpp
// Current: int x = 0;
// Fixed:   int tokenIndex = 0;
```

---

**Good:**
- Clean error handling with `std::expected`
- Proper use of `const`
```

### 4.3 Review Tests

| Check | Questions |
|-------|-----------|
| **Coverage** | New code paths tested? |
| **Quality** | Tests verify behavior, not implementation? |
| **Edge cases** | Boundary conditions tested? |
| **Naming** | Test names describe what's being tested? |
| **Independence** | Tests can run in isolation? No order dependency? |
| **Assertions** | Clear, specific assertions? Good error messages? |

#### Suggest Missing Tests

**If new code lacks tests, suggest specific tests to add:**

```markdown
### Missing Tests for `parser.cpp`

#### 1. `Parser::parseToken` needs tests for:

```cpp
// Test empty input
TEST(ParserTest, ParseToken_EmptyInput_ReturnsNullopt) {
    Parser parser;
    auto result = parser.parseToken("");
    EXPECT_FALSE(result.has_value());
}

// Test invalid input
TEST(ParserTest, ParseToken_InvalidToken_ReturnsError) {
    Parser parser;
    auto result = parser.parseToken("@#$%");
    EXPECT_FALSE(result.has_value());
}

// Test boundary - max length token
TEST(ParserTest, ParseToken_MaxLengthToken_Succeeds) {
    Parser parser;
    std::string maxToken(MAX_TOKEN_LENGTH, 'a');
    auto result = parser.parseToken(maxToken);
    EXPECT_TRUE(result.has_value());
}
```

#### 2. `Handler::process` needs tests for:

```cpp
// Test null input
TEST(HandlerTest, Process_NullInput_ThrowsInvalidArgument) {
    Handler handler;
    EXPECT_THROW(handler.process(nullptr), std::invalid_argument);
}
```
```

**Test suggestion checklist:**
- [ ] Happy path test
- [ ] Empty/null input test
- [ ] Invalid input test
- [ ] Boundary values test
- [ ] Error handling test

### 4.4 Cross-File Analysis

After reviewing individual files, check cross-cutting concerns:

| Check | Questions |
|-------|-----------|
| **Consistency** | Same patterns used across new files? |
| **API coherence** | Public APIs follow programming skill guidelines? |
| **Dependencies** | New dependencies justified? Properly integrated? |
| **Documentation** | README/docs updated if needed? |

<IMPORTANT>
**Do NOT follow existing codebase patterns blindly.**

Existing code may be poorly written. Always apply rules from programming skills (`programming-cpp`, `programming-python`, etc.) even if existing code does it differently.

If new code is better than existing patterns, that's good - don't "dumb it down" to match bad existing code.
</IMPORTANT>

## Phase 5: Summarize Review

After reviewing all changes, compile the final report:

```markdown
# PR Review: [PR Title]

## Summary

**Verdict:** [Approve / Request Changes / Comment]

**Overview:** [1-2 sentence summary]

**Files reviewed:** X files, +Y/-Z lines

**Total issues:** X critical, Y must-fix, Z should-fix, W nitpicks

**CI Status:** [Passed ✅ / Failed ❌ / Pending 🔄] (GitHub PRs only)

---

## Architecture (if applicable)

[Summary from architecture-analyze, or "No architectural changes"]

---

## What's Good

- [Positive aspect 1]
- [Positive aspect 2]

---

## Issues Found (sorted by severity)

### Critical (Score: 100) - Security/Crash

#### 1. SQL Injection in `handler.cpp:78`

```cpp
// Current code:
std::string query = "SELECT * FROM users WHERE name = '" + userInput + "'";

// Fixed code:
auto stmt = db.prepare("SELECT * FROM users WHERE name = ?");
stmt.bind(1, userInput);
```

**Why:** User input directly concatenated into SQL allows injection attacks.

---

### Must Fix (Score: 80) - Incorrect Behavior

#### 2. Null pointer dereference in `parser.cpp:42`

```cpp
// Current code:
auto result = ptr->getValue();

// Fixed code:
if (!ptr) {
    return std::nullopt;
}
auto result = ptr->getValue();
```

**Why:** Crashes if ptr is null.

---

### Should Fix (Score: 50) - Best Practices

#### 3. Raw loop in `utils.cpp:23`

```cpp
// Current code:
for (int i = 0; i < items.size(); i++) {
    process(items[i]);
}

// Fixed code:
std::for_each(items.begin(), items.end(), process);
// Or: for (const auto& item : items) { process(item); }
```

**Why:** Range-for or algorithms are more expressive and less error-prone.

---

### Nitpicks (Score: 20) - Style

#### 4. Unclear variable name in `config.py:45`

```python
# Current: x = 3
# Fixed:   retry_count = 3
```

---

## Test Coverage

| New Code | Has Tests | Missing Tests |
|----------|-----------|---------------|
| `parser.cpp:parseToken()` | Yes | - |
| `handler.cpp:process()` | **No** | See suggested tests below |

### Suggested Tests for `handler.cpp:process()`

```cpp
TEST(HandlerTest, Process_ValidInput_ReturnsSuccess) {
    Handler h;
    auto result = h.process(validInput);
    EXPECT_TRUE(result.ok());
}

TEST(HandlerTest, Process_NullInput_ReturnsError) {
    Handler h;
    auto result = h.process(nullptr);
    EXPECT_FALSE(result.ok());
    EXPECT_EQ(result.error(), Error::InvalidInput);
}

TEST(HandlerTest, Process_EmptyInput_ReturnsError) {
    Handler h;
    auto result = h.process("");
    EXPECT_FALSE(result.ok());
}
```

---

## Files Reviewed

| File | Status | Issues (by severity) |
|------|--------|----------------------|
| `src/parser.cpp` | ✅ | 0 critical, 1 must-fix, 0 should-fix |
| `src/handler.cpp` | ✅ | 1 critical, 0 must-fix, 1 should-fix |
| `tests/parser_test.cpp` | ✅ | Clean |

---

## Previous Review Comments (GitHub PRs)

| Status | Comment | Author |
|--------|---------|--------|
| ✅ Resolved | "Add null check in parser" | @reviewer1 |
| ⏳ Open | "Consider using std::optional" | @reviewer2 |

---

## Checklist

- [x] All files reviewed
- [ ] Correctness verified - **1 issue found**
- [ ] Language-specific best practices checked - **2 issues found**
- [ ] Code quality/smells checked
- [x] Tests adequate - **1 function missing tests**
- [ ] No security issues - **1 critical issue found**
- [x] Architecture sound

---

## Questions for Author

- [Clarifying questions if any]
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
| Architectural changes | `architecture-analyze` (Phase 3A) |
| C++ PR | `programming-cpp`, optionally `design-patterns`, `stl-algorithms` |
| Python PR | `programming-python` |
| CMake changes | `programming-cmake-best-practices` |
| Test files | `testing-gtest-gmock` or `testing-pytest` |
| AMD SMI code | `library-amd-smi` |

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

**Per-file:**
- [ ] Read the full diff (don't skim)
- [ ] `const` used appropriately?
- [ ] Naming clear and consistent?
- [ ] Error handling complete?
- [ ] No obvious bugs or edge case misses?

**Overall:**
- [ ] All files reviewed (not just glanced at)?
- [ ] Tests exist for new code?
- [ ] No security red flags?
- [ ] Follows programming skill rules (not existing bad patterns)?

## References

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [How to Do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-1/)
