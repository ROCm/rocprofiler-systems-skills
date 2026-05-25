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
| PR # | #123 (omit for Full-repo audit) |
| Title | [PR title] (omit for Full-repo audit) |
| Author | @username (omit for Full-repo audit) |
| Target branch | main (omit for Full-repo audit) |
| Base SHA | abc1234 (omit for Full-repo audit) |
| Head SHA | def5678 (omit for Full-repo audit) |
| Files changed | X (in-scope file count for Full-repo audit) |
| Lines | +Y / -Z (omit for Full-repo audit) |
| Commits | N (omit for Full-repo audit) |
| **Mode** | `Diff review` / `Full-repo audit` / `Re-review (delta)` |
| **Agents spawned** | comma-separated agent IDs that actually ran |
| **Orchestrator sweeps** | `1.6.a doc-drift`, `1.6.b repo-meta`, or `none (triggers not matched)` |
| **Report status** | `COMPLETE` / `PARTIAL (gates failed: A,C)` |

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

**Coverage:** In-scope file count: N. Files reviewed: N. Gaps: `none` OR explicit list of unreviewed files. Empty `Gaps:` value is forbidden — write `Gaps: none` when there are none.

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

## [REQUIRED when Full-repo audit OR docs touched] Doc-vs-Code Drift

Sourced from Phase 1.6.a sweep. Mark `N/A — no docs in scope` when neither
trigger fires.

| Doc location | Claim | Current reality | Severity |
|---|---|---|---|
| `README.md:N` | "All endpoints require authentication" | One or more routes lack an auth check | Must Fix |
| `docs/ARCHITECTURE.md:N` | "3-tier architecture (frontend / API / DB)" | No frontend module; monolithic layout | Should Fix |
| `docs/ARCHITECTURE.md:N` | "100% test coverage" | Coverage not measured | Should Fix |
| `CHANGELOG.md:N` | Last entry version 2.0 | Packaging declares 1.4 | Should Fix |

Per the Per-site enumeration rule, each row above also appears as an
individual finding in the main Issues section.

---

## [REQUIRED when Full-repo audit OR meta files touched] Repo Hygiene & Process

Sourced from Phase 1.6.b sweep. Mark `N/A — no meta files in scope` when
neither trigger fires.

| Check | Present? | Quality | Severity if missing/poor |
|---|---|---|---|
| `LICENSE` | Yes / No | matches README claim? | Must Fix (when README claims one) |
| `CONTRIBUTING.md` | Yes / No | — | Should Fix |
| `CODEOWNERS` | Yes / No | — | Should Fix (shared repos) |
| `SECURITY.md` | Yes / No | — | Must Fix (when security findings ≥ 1) |
| `.gitignore` | Yes / No | language-appropriate entries? | Should Fix per missing class |
| `.pre-commit-config.yaml` | Yes / No | format + lint hooks? | Should Fix |
| Packaging (`pyproject.toml` / `Cargo.toml` / `CMakeLists.txt` / `package.json`) | Yes / No | modern format? deps pinned? | Should Fix |
| Matrix runner (`tox.ini` / `noxfile.py` / CI matrix) | Yes / No | covers supported versions? | Should Fix |
| `.editorconfig` | Yes / No | — | Nitpick |
| `.github/ISSUE_TEMPLATE/` | Yes / No | — | Nitpick (GitHub repos) |
| `.github/pull_request_template.md` | Yes / No | — | Nitpick (GitHub repos) |
| CI workflow quality | — | pinned actions, real secrets, deploy gated on success, matrix, cache, supported language versions | Must Fix per security/correctness gap |
| Dockerfile quality (if present) | — | pinned base, layer hygiene, non-root, no baked secrets, `.dockerignore` | Must Fix per security gap |

Per the Per-site enumeration rule, every missing or substandard item also
appears as an individual finding in the main Issues section. This table is
the orchestrator-sweep summary, not a replacement for per-item rows.

---

## [OPTIONAL] Cleanup Confirmation

- [ ] Local clone restored to original branch (`<orig_branch>`)
- [ ] Stash popped (if one was created) - no leftover
      `pr-review-skill autostash` entry in `git stash list`
- [ ] `git status` matches pre-review state
- [ ] No detached HEAD, no leftover PR branch checkout

---

## [OPTIONAL] Previous Review Comments (GitHub PRs)

| Status | Comment | Author |
|--------|---------|--------|
| Resolved | "Add null check in parser" | @reviewer1 |
| Open | "Consider using std::optional" | @reviewer2 |

---

## [REQUIRED] Checklist

- [ ] All files reviewed
- [ ] Correctness verified
- [ ] Language-specific best practices checked
- [ ] Code quality/smells checked
- [ ] Tests adequate
- [ ] No security issues
- [ ] Architecture sound

### Pre-publish gates (SKILL.md Phase 4)

- [ ] **Gate A — File coverage:** every in-scope file Read; Files Reviewed row count = in-scope file count; gaps enumerated explicitly (`Gaps: none` or list).
- [ ] **Gate B — Per-site enumeration:** ≥ 2-site classes have one row per site; cross-cutting summaries are additive only.
- [ ] **Gate C — Mode-fit:** spawned agents match Phase 0 mode + Phase 1.5 gate; Phase 1.6 sweeps fired when triggered.
- [ ] **Gate D — Reconciliation:** sum(agent rows) + sum(sweep rows) = merged rows + named duplicates.

If any gate is unchecked, the Header `Report status` MUST be `PARTIAL (gates failed: ...)`.

---

## [OPTIONAL] Questions for Author

- [Clarifying questions if any]
