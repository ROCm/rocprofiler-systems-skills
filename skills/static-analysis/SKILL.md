---
name: static-analysis
description: Run static analysis tools on changed files and generate a report
---

# Static Analysis Skill

Run available static analysis tools on changed files and produce a structured report.

## When to Use

| Context | Trigger |
|---------|---------|
| **Standalone** | User asks to run static analysis, linters, or check code quality |
| **PR Review** | Invoked by `pr-review` before manual code review |
| **Pre-commit** | User wants to check code before committing |

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 1: Get Changed Files                     │
│         Determine scope (PR, staged, or all changes)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 2: Detect Available Tools                │
│         Check which tools are installed on the system           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 3: Run Tools on Changed Files            │
│         Execute each tool, capture output                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 4: Generate Report                       │
│         Parse output, categorize by severity, format report     │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Get Changed Files

### Determine Scope

Ask user or detect automatically:

| Scope | Command | Use When |
|-------|---------|----------|
| PR changes | `git diff --name-only <base>...HEAD` | Reviewing a PR |
| Staged | `git diff --name-only --cached` | Pre-commit check |
| Unstaged | `git diff --name-only` | Check current work |
| All uncommitted | `git diff --name-only HEAD` | Local changes review |
| Specific files | User-provided list | Targeted analysis |

```bash
# Get base branch (for PR scope)
base_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$base_branch" ] && base_branch="main"

# Get changed files based on scope
case "$scope" in
    pr)      changed_files=$(git diff --name-only "$base_branch"...HEAD) ;;
    staged)  changed_files=$(git diff --name-only --cached) ;;
    all)     changed_files=$(git diff --name-only HEAD) ;;
esac
```

### Filter by Language

```bash
cpp_files=$(echo "$changed_files" | grep -E '\.(cpp|cc|cxx|c|hpp|h)$' | tr '\n' ' ')
py_files=$(echo "$changed_files" | grep -E '\.py$' | tr '\n' ' ')
sh_files=$(echo "$changed_files" | grep -E '\.(sh|bash)$' | tr '\n' ' ')
cmake_files=$(echo "$changed_files" | grep -E '(CMakeLists\.txt|\.cmake)$' | tr '\n' ' ')
```

## Phase 2: Detect Available Tools

```bash
# C++ tools
which clang-tidy >/dev/null 2>&1 && echo "clang-tidy: available"
which cppcheck >/dev/null 2>&1 && echo "cppcheck: available"

# Python tools
which ruff >/dev/null 2>&1 && echo "ruff: available"
which pylint >/dev/null 2>&1 && echo "pylint: available"
which mypy >/dev/null 2>&1 && echo "mypy: available"

# Shell tools
which shellcheck >/dev/null 2>&1 && echo "shellcheck: available"

# CMake tools
which cmake-lint >/dev/null 2>&1 && echo "cmake-lint: available"
```

### Check for compile_commands.json (C++)

```bash
# Required for clang-tidy
if [ -f "build/compile_commands.json" ]; then
    echo "compile_commands.json: build/"
elif [ -f "compile_commands.json" ]; then
    echo "compile_commands.json: ./"
else
    echo "compile_commands.json: NOT FOUND (clang-tidy may not work)"
fi
```

### Use IDE Diagnostics (if available)

If running in VS Code with MCP:
```
Use mcp__ide__getDiagnostics to get real-time diagnostics
```

## Phase 3: Run Tools on Changed Files

### C++ Tools

**clang-tidy:**
```bash
if [ -n "$cpp_files" ] && which clang-tidy >/dev/null 2>&1; then
    compile_db=""
    [ -f "build/compile_commands.json" ] && compile_db="-p build/"
    [ -f "compile_commands.json" ] && compile_db="-p ."

    for file in $cpp_files; do
        [ -f "$file" ] && clang-tidy "$file" $compile_db 2>&1
    done
fi
```

**cppcheck:**
```bash
if [ -n "$cpp_files" ] && which cppcheck >/dev/null 2>&1; then
    cppcheck --enable=warning,style,performance $cpp_files 2>&1
fi
```

### Python Tools

**ruff (recommended - fast):**
```bash
if [ -n "$py_files" ] && which ruff >/dev/null 2>&1; then
    ruff check $py_files 2>&1
fi
```

**pylint:**
```bash
if [ -n "$py_files" ] && which pylint >/dev/null 2>&1; then
    pylint --output-format=text $py_files 2>&1
fi
```

**mypy:**
```bash
if [ -n "$py_files" ] && which mypy >/dev/null 2>&1; then
    mypy $py_files 2>&1
fi
```

### Shell Tools

**shellcheck:**
```bash
if [ -n "$sh_files" ] && which shellcheck >/dev/null 2>&1; then
    shellcheck $sh_files 2>&1
fi
```

### CMake Tools

**cmake-lint:**
```bash
if [ -n "$cmake_files" ] && which cmake-lint >/dev/null 2>&1; then
    cmake-lint $cmake_files 2>&1
fi
```

## Phase 4: Generate Report

### Severity Mapping

| Tool | Check/Code | Severity |
|------|------------|----------|
| **clang-tidy** | `bugprone-*`, `clang-analyzer-*` | Critical (100) |
| **clang-tidy** | `performance-*` | Should Fix (50) |
| **clang-tidy** | `modernize-*`, `readability-*` | Nitpick (20) |
| **cppcheck** | error | Critical (100) |
| **cppcheck** | warning | Must Fix (80) |
| **cppcheck** | style, performance | Should Fix (50) |
| **ruff** | E (error), F (pyflakes) | Must Fix (80) |
| **ruff** | W (warning) | Should Fix (50) |
| **ruff** | C, N (convention, naming) | Nitpick (20) |
| **pylint** | E, F (error, fatal) | Critical (100) |
| **pylint** | W (warning) | Should Fix (50) |
| **pylint** | C, R (convention, refactor) | Nitpick (20) |
| **mypy** | error | Must Fix (80) |
| **shellcheck** | error | Must Fix (80) |
| **shellcheck** | warning | Should Fix (50) |
| **shellcheck** | info, style | Nitpick (20) |

### Report Format

```markdown
# Static Analysis Report

**Scope:** [PR #123 / staged changes / all uncommitted]
**Files analyzed:** X files
**Tools run:** clang-tidy, ruff, shellcheck

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | X |
| 🟠 Must Fix | X |
| 🟡 Should Fix | X |
| 🔵 Nitpick | X |

**Total issues:** X

---

## 🔴 Critical Issues (X)

### 1. bugprone-use-after-move

**File:** `src/parser.cpp:42`
**Tool:** clang-tidy
**Severity:** Critical (100)

**Message:**
```
'data' used after it was moved
```

**Context:**
```cpp
auto result = std::move(data);
process(data);  // Bug: data was moved
```

---

## 🟠 Must Fix (X)

### 2. performance-unnecessary-copy-initialization

**File:** `src/handler.cpp:78`
**Tool:** clang-tidy
**Severity:** Should Fix (50)

**Message:**
```
The copy 'config' is only used as const reference; consider making it a const reference
```

---

## 🟡 Should Fix (X)

...

---

## 🔵 Nitpicks (X)

...

---

## Tools Not Available

The following tools were not found and could not be run:
- `cppcheck` - Install with: `apt install cppcheck`
- `mypy` - Install with: `pip install mypy`

---

## No Issues Found

✅ No issues detected by static analysis tools.
```

## Integration with pr-review

When invoked from `pr-review`:

1. `pr-review` calls `static-analysis` with PR scope
2. `static-analysis` runs tools and generates report
3. Report is included in PR review under "Static Analysis Results"
4. Issues are merged with manual review findings by severity

```markdown
## How pr-review uses this skill:

1. Invoke static-analysis skill with scope=pr
2. Get the generated report
3. Include report in Phase 4 (Code Review) findings
4. Critical/Must Fix issues from tools → Must Fix in review
5. Should Fix from tools → Should Fix in review
6. Nitpicks from tools → Nitpick in review
```

## Standalone Usage

When run standalone, output the full report to the user.

**Example invocations:**
- "run static analysis" → analyze all uncommitted changes
- "run static analysis on staged files" → pre-commit check
- "run clang-tidy on the PR" → C++ analysis only
- "check code quality" → full analysis with report

## Tool Installation Reference

| Tool | Language | Install Command |
|------|----------|-----------------|
| clang-tidy | C++ | `apt install clang-tidy` or comes with LLVM |
| cppcheck | C++ | `apt install cppcheck` |
| ruff | Python | `pip install ruff` |
| pylint | Python | `pip install pylint` |
| mypy | Python | `pip install mypy` |
| shellcheck | Shell | `apt install shellcheck` |
| cmake-lint | CMake | `pip install cmakelint` |
