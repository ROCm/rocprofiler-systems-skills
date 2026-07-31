# PR Review Report Template

Sections marked `[REQUIRED]` must appear in every written review report.
Sections marked `[OPTIONAL]` may be omitted only when genuinely not applicable;
when omitted, state why (e.g. "No public API touched - N/A") rather than
silently dropping the section.

## Contents

- [REQUIRED] Header
- [REQUIRED] Summary
- [OPTIONAL] Intent vs Implementation
- [OPTIONAL] Per-File Walkthrough
- [OPTIONAL] Agent Analysis Summary
- [OPTIONAL] Architecture (if applicable)
- [OPTIONAL] What's Good
- [REQUIRED] Issues Found (sorted by severity)
- [OPTIONAL] Test Coverage
- [REQUIRED] Files Reviewed
- [OPTIONAL] Static Analysis Pass
- [OPTIONAL] Security Audit
- [OPTIONAL] Performance Review
- [OPTIONAL] Undefined Behaviour
- [OPTIONAL] API / ABI Compatibility
- [OPTIONAL] Documentation Review
- [OPTIONAL] Cleanup Confirmation
- [OPTIONAL] Previous Review Comments (GitHub PRs)
- [REQUIRED] Checklist
- [OPTIONAL] Questions for Author

---

## [REQUIRED] Header

| Field | Value |
|-------|-------|
| PR # | #123 |
| Title | [PR title] |
| Author | @username |
| Target branch | main |
| Base SHA | abc1234 |
| Head SHA | def5678 |
| Files changed | X |
| Lines | +Y / -Z |
| Commits | N |

## [REQUIRED] Summary

**Verdict:** `APPROVE` / `REQUEST CHANGES` / `NEEDS DISCUSSION`

**Overview:** [1-2 sentence summary]

**Total issues:** X critical, Y must-fix, Z should-fix, W nitpicks

**CI Status:** [Passed / Failed / Pending] (GitHub PRs only)

---

## [OPTIONAL] Intent vs Implementation

**Stated intent (from PR description / commits):**
[Summary]

**What the diff actually does:**
[Summary]

**Mismatches / scope creep:** [None | List]

---

## [OPTIONAL] Per-File Walkthrough

### `path/to/file1.cpp`
[1 short paragraph: what changed and why]

### `path/to/file2.py`
[1 short paragraph: what changed and why]

---

## [OPTIONAL] Agent Analysis Summary

**Up to 8 agents analyzed the changes in parallel:**

| Agent | Purpose | Issues Found |
|-------|---------|--------------|
| Static Analysis | Linter/tool findings | X issues |
| Dead Code Detection | Unused code, comments | Y issues |
| Code Smells + Quality | Anti-patterns, long functions, naming/complexity/SRP/magic numbers | Z issues |
| Language Rules | C++/Python best practices | W issues |
| Architecture | Module boundaries, dependencies | V issues (or N/A) |
| Simplification | Reuse, complexity reduction | U issues |
| Performance | Hot-path classification, allocations, locks, I/O | P issues |
| UB Detection | Undefined behaviour (C/C++/unsafe-Rust) | T issues (or N/A) |

**All findings below are sourced from agent analysis.**

---

## [OPTIONAL] Architecture (if applicable)

[Summary from architecture-analyze, or "No architectural changes"]

---

## [OPTIONAL] What's Good

- [Positive aspect 1]
- [Positive aspect 2]

---

## [REQUIRED] Issues Found (sorted by severity)

### Critical (Score: 100) - Security/Crash

#### 1. SQL Injection in `handler.cpp:78`
**Source:** Static Analysis Agent (Semgrep)

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
**Source:** Static Analysis Agent (clang-tidy)

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
**Source:** Language Rules Agent (C++ Best Practices)

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

#### 4. Long function in `handler.cpp:processRequest()`
**Source:** Code Smells Agent

**Lines 120-195 (75 lines):** Function is too long and does too much.

**Suggested refactoring:**
```cpp
// Split into smaller functions:
- extractHeaders()
- validateRequest()
- routeToHandler()
- buildResponse()
```

**Why:** Long functions are hard to understand, test, and maintain.

---

### Nitpicks (Score: 20) - Style

#### 5. Unused variable in `config.py:45`
**Source:** Dead Code Detection Agent

```python
# Current: x = 3  # Declared but never used
# Fix: Remove this line
```

---

#### 6. Commented-out code in `parser.cpp:67-72`
**Source:** Dead Code Detection Agent

```cpp
// Remove these commented lines:
// auto old_parser = createParser();
// old_parser.parse(input);
// return old_parser.result();
```

**Why:** Commented code creates clutter. Use version control instead.

---

## [OPTIONAL] Test Coverage

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

## [REQUIRED] Files Reviewed

| File | Status | Issues (by severity) |
|------|--------|----------------------|
| `src/parser.cpp` | OK | 0 critical, 1 must-fix, 0 should-fix |
| `src/handler.cpp` | OK | 1 critical, 0 must-fix, 1 should-fix |
| `tests/parser_test.cpp` | OK | Clean |

---

## [OPTIONAL] Static Analysis Pass

[Summary of Static Analysis Agent findings: tools run, totals,
notable suppressions. "Clean" if nothing to report.]

---

## [OPTIONAL] Security Audit

| Area | Result |
|------|--------|
| Input validation | [OK / Issue at file:line] |
| Injection (SQL/shell/etc.) | [OK / Issue] |
| AuthN / AuthZ | [OK / N/A / Issue] |
| Secrets / credentials | [OK / Issue] |
| Unsafe deserialization | [OK / N/A / Issue] |
| Path traversal | [OK / N/A / Issue] |
| Crypto usage | [OK / N/A / Issue] |

---

## [OPTIONAL] Performance Review

| Aspect | Result |
|--------|--------|
| Algorithmic complexity | [OK / Concern at file:line] |
| Hot-path allocations | [OK / Concern] |
| Unnecessary copies | [OK / Concern] |
| Lock contention / threading | [OK / N/A / Concern] |
| I/O patterns | [OK / N/A / Concern] |

---

## [OPTIONAL] Undefined Behaviour

(C/C++ / unsafe-Rust only. State "N/A - no C/C++/unsafe-Rust changes" otherwise.)

| UB class | File:Line | Snippet | Std citation | Fix | Severity |
|----------|-----------|---------|--------------|-----|----------|
| [class]  | [file:N]  | [code]  | [ref]        | [fix] | Critical (100) |

### Sanitizer Coverage

| Sanitizer | In CI? | Recommendation |
|-----------|--------|----------------|
| UBSan | [Yes / No] | [N/A or "Add `-fsanitize=undefined`"] |
| ASan  | [Yes / No] | [N/A or "Add `-fsanitize=address`"] |
| TSan  | [Yes / No / N/A] | [N/A or "Add separate `-fsanitize=thread` job"] |
| MSan  | [Yes / No / N/A] | [N/A or "Add separate clang `-fsanitize=memory` job"] |

---

## [OPTIONAL] API / ABI Compatibility

**Public API touched?** [Yes / No]
**ABI impact:** [None / Additive / Deprecating / Breaking]
**Migration notes:** [N/A or details]

---

## [OPTIONAL] Documentation Review

| Doc Surface | Updated? |
|-------------|----------|
| README | [Yes / No / N/A] |
| Doc comments / docstrings | [Yes / No / N/A] |
| Changelog / release notes | [Yes / No / N/A] |
| Man pages / API docs | [Yes / No / N/A] |

---

## [REQUIRED] Cleanup Confirmation

Applies to **every** run, not only PR checkouts.

- [ ] `git status` matches pre-review state — no edits, new files, or staged changes left by the orchestrator or any analysis agent
- [ ] If the tree differed from pre-run state, stray changes were reverted and noted in the report
- [ ] If a PR was checked out: local clone restored to original branch (`<orig_branch>`)
- [ ] If a stash was created: stash popped — no leftover `pr-review-skill autostash` entry in `git stash list`
- [ ] No detached HEAD, no leftover PR branch checkout

---

## [OPTIONAL] Previous Review Comments (GitHub PRs)

| Status | Comment | Author |
|--------|---------|--------|
| Resolved | "Add null check in parser" | @reviewer1 |
| Open | "Consider using std::optional" | @reviewer2 |

---

## [REQUIRED] Checklist

- [x] All files reviewed
- [ ] Correctness verified - **1 issue found**
- [ ] Language-specific best practices checked - **2 issues found**
- [ ] Code quality/smells checked
- [x] Tests adequate - **1 function missing tests**
- [ ] No security issues - **1 critical issue found**
- [x] Architecture sound

---

## [OPTIONAL] Questions for Author

- [Clarifying questions if any]
