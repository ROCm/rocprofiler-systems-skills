# PR Review Report Template

Sections marked `[REQUIRED]` must appear in every written review report.
Sections marked `[OPTIONAL]` may be omitted only when genuinely not applicable;
when omitted, state why (e.g. "No public API touched - N/A") rather than
silently dropping the section.

**Numbered-list rule.** Use numbered lists, not tables, throughout this
report - every section that enumerates items (findings, files, checklist
entries, or anything else) uses a numbered list. Numbering makes it
possible to refer back to a specific item (e.g. "see #4") and numbered
prose reads far better than a table in a raw markdown/text file. Number
sequentially within each section; do not restart or reuse numbers across
sections.

## Contents

This list is the canonical required-sections definition for pr-review reports;
`SKILL.md` and `HYGIENE.md` both point here rather than restating it.
`[REQUIRED]` sections must appear in every report (state "N/A" with a reason
when genuinely inapplicable, e.g. Undefined Behaviour on a pure-Python diff -
that still counts as present). `[OPTIONAL]` sections may be silently omitted.

- [REQUIRED] Header
- [REQUIRED] Summary
- [REQUIRED] Intent vs Implementation
- [REQUIRED] Per-File Walkthrough
- [OPTIONAL] Agent Analysis Summary
- [OPTIONAL] Architecture (if applicable)
- [OPTIONAL] What's Good
- [REQUIRED] Issues Found (sorted by severity)
- [OPTIONAL] Test Coverage
- [REQUIRED] Files Reviewed
- [REQUIRED] Static Analysis Pass
- [REQUIRED] Security Audit
- [REQUIRED] Performance Review
- [REQUIRED] Undefined Behaviour (N/A for pure docs/Python/CMake diffs)
- [REQUIRED] API / ABI Compatibility
- [REQUIRED] Documentation Review
- [REQUIRED] Cleanup Confirmation
- [OPTIONAL] Previous Review Comments (GitHub PRs)
- [REQUIRED] Checklist
- [OPTIONAL] Questions for Author

---

## [REQUIRED] Header

1. **PR #:** #123
2. **Title:** [PR title]
3. **Author:** @username
4. **Target branch:** main
5. **Base SHA:** abc1234
6. **Head SHA:** def5678
7. **Files changed:** X
8. **Lines:** +Y / -Z
9. **Commits:** N

## [REQUIRED] Summary

**Verdict:** `APPROVE` / `REQUEST CHANGES` / `NEEDS DISCUSSION`

**Overview:** [1-2 sentence summary]

**Total issues:** X critical, Y must-fix, Z should-fix, W nitpicks

**CI Status:** [Passed / Failed / Pending] (GitHub PRs only)

---

## [REQUIRED] Intent vs Implementation

**Stated intent (from PR description / commits):**
[Summary]

**What the diff actually does:**
[Summary]

**Mismatches / scope creep:** [None | List]

---

## [REQUIRED] Per-File Walkthrough

### `path/to/file1.cpp`
[1 short paragraph: what changed and why]

### `path/to/file2.py`
[1 short paragraph: what changed and why]

---

## [OPTIONAL] Agent Analysis Summary

**Up to 8 agents analyzed the changes in parallel:**

1. **Static Analysis** — Linter/tool findings: X issues
2. **Dead Code Detection** — Unused code, comments: Y issues
3. **Code Smells + Quality** — Anti-patterns, long functions, naming/complexity/SRP/magic numbers: Z issues
4. **Language Rules** — C++/Python best practices: W issues
5. **Architecture** — Module boundaries, dependencies: V issues (or N/A)
6. **Simplification** — Reuse, complexity reduction: U issues
7. **Performance** — Hot-path classification, allocations, locks, I/O: P issues
8. **UB Detection** — Undefined behaviour (C/C++/unsafe-Rust): T issues (or N/A)

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

1. `parser.cpp:parseToken()` — Has tests: Yes
2. `handler.cpp:process()` — Has tests: **No**. See suggested tests below

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

1. `src/parser.cpp` — OK — 0 critical, 1 must-fix, 0 should-fix
2. `src/handler.cpp` — OK — 1 critical, 0 must-fix, 1 should-fix
3. `tests/parser_test.cpp` — OK — Clean

---

## [REQUIRED] Static Analysis Pass

[Summary of Static Analysis Agent findings: tools run, totals,
notable suppressions. "Clean" if nothing to report.]

---

## [REQUIRED] Security Audit

1. **Input validation:** [OK / Issue at file:line]
2. **Injection (SQL/shell/etc.):** [OK / Issue]
3. **AuthN / AuthZ:** [OK / N/A / Issue]
4. **Secrets / credentials:** [OK / Issue]
5. **Unsafe deserialization:** [OK / N/A / Issue]
6. **Path traversal:** [OK / N/A / Issue]
7. **Crypto usage:** [OK / N/A / Issue]

---

## [REQUIRED] Performance Review

1. **Algorithmic complexity:** [OK / Concern at file:line]
2. **Hot-path allocations:** [OK / Concern]
3. **Unnecessary copies:** [OK / Concern]
4. **Lock contention / threading:** [OK / N/A / Concern]
5. **I/O patterns:** [OK / N/A / Concern]

---

## [REQUIRED] Undefined Behaviour

(C/C++ / unsafe-Rust only. State "N/A - no C/C++/unsafe-Rust changes" otherwise.)

1. **[UB class]** in `file:line` (Severity: Critical (100))
   **Snippet:** `[code]`
   **Std citation:** [ref]
   **Fix:** [fix]

### Sanitizer Coverage

1. **UBSan** — In CI? [Yes / No]. [N/A or "Add `-fsanitize=undefined`"]
2. **ASan** — In CI? [Yes / No]. [N/A or "Add `-fsanitize=address`"]
3. **TSan** — In CI? [Yes / No / N/A]. [N/A or "Add separate `-fsanitize=thread` job"]
4. **MSan** — In CI? [Yes / No / N/A]. [N/A or "Add separate clang `-fsanitize=memory` job"]

---

## [REQUIRED] API / ABI Compatibility

**Public API touched?** [Yes / No]
**ABI impact:** [None / Additive / Deprecating / Breaking]
**Migration notes:** [N/A or details]

---

## [REQUIRED] Documentation Review

1. **README:** [Yes / No / N/A]
2. **Doc comments / docstrings:** [Yes / No / N/A]
3. **Changelog / release notes:** [Yes / No / N/A]
4. **Man pages / API docs:** [Yes / No / N/A]

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

1. **Resolved:** "Add null check in parser" — @reviewer1
2. **Open:** "Consider using std::optional" — @reviewer2

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
