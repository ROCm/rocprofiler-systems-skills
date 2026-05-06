---
name: pr-review
description: Review Pull Requests or local changes - check code quality, correctness, tests, and provide actionable feedback
---

# PR Review Skill

Review Pull Requests or local changes with structured, thorough analysis.

<IMPORTANT>
**BE THOROUGH AND PICKY:**
- Review ENTIRE changed files, not just changed lines
- Report ALL issues found - do not skip or filter anything
- Apply programming skill rules strictly
- Check every function, class, and code block in changed files

**Determine review target automatically:**
- If user provides PR number or URL → Review that GitHub PR
- If no PR specified → Review local changes vs main branch (no questions asked)

**Persist the review (opt-in):** Do NOT write a markdown file by default. The report goes to chat output. Save the full markdown to `.claude/pr-review-summaries/` ONLY when the user explicitly asks ("save the review", "write a summary file", "persist this", or equivalent). See Phase 4 for filename rules when saving.

**Invoke relevant programming skills during review:**
- C++ code → `programming-cpp`, `programming-cpp-design-patterns`, `programming-cpp-stl-algorithms`
- Python code → `programming-python`
- CMake files → `programming-cmake-best-practices`
</IMPORTANT>

> **Workspace-level overrides.** Workspaces may define additional
> defaults in `<workspace>/workflows/pr-review.md`; that file
> overrides anything in this skill (e.g. clone locations, project
> routing, report destination paths).

## Universal Hygiene Rules

These rules apply to **every** invocation of this skill, regardless
of workspace.

### Default destination: local artifact only

**Do NOT post to GitHub by default.** A review run produces a local
written report (file or chat output) only. Post to the PR (review
comment, line comment, or `gh pr review`) **only** if the user
explicitly says "post", "submit", "comment on the PR", or
equivalent. When in doubt, save locally and ask.

### Fresh-eyes rule (sub-agent invocations)

When this skill is invoked from inside a sub-agent (i.e. the agent
was spawned specifically to review a PR), treat the brief as the
**only** context:

- Do **not** load project memory, prior feedback logs, or
  conversation history about the PR.
- Do **not** read previous review reports for this PR unless the
  brief explicitly tells you to (e.g. re-review mode).
- Form an independent opinion from the diff, files, and PR
  description alone.

This keeps sub-agent reviews unbiased by prior conclusions. The
parent orchestrator can still cross-reference past reviews
afterwards.

### Report content rules

A written report (as opposed to inline chat feedback) MUST contain
all of the following sections, in roughly this order. Omit a
section's body only if it is genuinely N/A, and say so explicitly
("No public API touched - N/A").

1. **Header** - PR number, title, author, target branch, base SHA,
   head SHA, files changed count, +/- line counts, commit count.
2. **Intent vs implementation** - what the PR claims to do (from
   description / commits) vs what the diff actually does. Flag
   mismatches.
3. **Per-file walkthrough** - one short paragraph per changed file
   explaining what changed and why, in reviewer's own words.
4. **Findings ranked by severity** - Critical -> Must Fix -> Should
   Fix -> Nitpick (already covered by agent aggregation).
5. **Static analysis pass** - summary of linter/tool findings (from
   Static Analysis Agent).
6. **Security audit** - input validation, injection, auth, secrets,
   unsafe deserialization, path traversal, crypto misuse.
7. **Performance review** - algorithmic complexity, hot-path
   allocations, unnecessary copies, lock contention, I/O patterns.
8. **API/ABI compatibility** - does the PR change a public API or
   ABI? If yes, is the change additive, deprecating, or breaking?
   Migration notes?
9. **Documentation review** - are README, doc comments, changelog,
   man pages updated to match behavior changes?
10. **Verdict** - one of `APPROVE`, `REQUEST CHANGES`, or
    `NEEDS DISCUSSION` (use these exact labels).
11. **Cleanup confirmation** - confirm the local clone was restored
    to its starting branch, any stash was popped, and `git status`
    matches the pre-review state. (See "Local clone hygiene" below.)

### Local clone hygiene (when checking out a PR)

If reviewing requires checking out the PR into a local clone:

1. **Prefer a clean clone.** Pick a clone whose `git status` is
   empty (no staged/unstaged changes, no untracked files that
   matter). This avoids contaminating the user's working state.
2. **If no clean clone exists**, use the available one but:
   - Record the original branch: `orig_branch=$(git rev-parse --abbrev-ref HEAD)`
   - `git stash push -u -m "pr-review-skill autostash"` and remember the stash ref.
3. **Always record the starting branch** before any checkout:
   `orig_branch=$(git rev-parse --abbrev-ref HEAD)`.
4. **Mandatory restore on exit (success OR failure):**
   - `git checkout "$orig_branch"`
   - If you stashed in step 2: `git stash pop` (the matching stash)
   - Verify `git status` matches the pre-review state.
5. Use a `trap` (bash) or `try/finally` (Python) so the restore runs
   even on error or interrupt. Never leave the user's clone on a
   detached HEAD or PR branch.

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
┌─────────────────────────────────────────────────────────────────┐
│        Phase 1: Gather Info + Read Files (ONCE)                 │
│    - Get changed files, diff, commits                            │
│    - Read each changed file's full content                       │
│    - Identify languages (C++, Python, CMake)                     │
│    - Package data for agents                                     │
│    - Check CI status (GitHub PRs)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│      Phase 1.5: Spawn 6 Parallel Analysis Agents                │
│    All agents receive pre-loaded context from Phase 1            │
│                                                                   │
│    ┌──────────────────┐  ┌──────────────────┐                   │
│    │ Agent 1: Static  │  │ Agent 2: Dead    │                   │
│    │ Analysis (tools) │  │ Code Detection   │                   │
│    └──────────────────┘  └──────────────────┘                   │
│    ┌──────────────────┐  ┌──────────────────┐                   │
│    │ Agent 3: Code    │  │ Agent 4: Language│                   │
│    │ Smells           │  │ Rules (C++/Py)   │                   │
│    └──────────────────┘  └──────────────────┘                   │
│    ┌──────────────────┐                                          │
│    │ Agent 5: Arch    │ (conditional - if architectural changes) │
│    │ (via skill)      │                                          │
│    └──────────────────┘                                          │
│    ┌──────────────────┐                                          │
│    │ Agent 6: Simplify│                                          │
│    │ (reuse/reduce)   │                                          │
│    └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Aggregate    │
                    │ - Merge agent results │
                    │ - Map to severity     │
                    │ - Deduplicate issues  │
                    │ - Sort by severity    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 3: Manual       │
                    │ - Review tests        │
                    │ - Check coverage      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 4: Generate     │
                    │ Final Report          │
                    │ - Severity-sorted     │
                    │ - Agent sources cited │
                    │ - With code fixes     │
                    │ - Actionable feedback │
                    │ - Save .md to disk    │
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

## Phase 1: Gather Information + Read Files

**Goal:** Collect all data ONCE and package for agents - minimize redundant file reads.

Based on the review type selected in Phase 0:

### For GitHub PR Review

Use commands from `git-gh-client` to fetch PR data:
- `gh pr view <PR_NUMBER> --json ...` for metadata
- `gh pr diff <PR_NUMBER>` for changes
- See `git-gh-client` Phase 2 for full command reference

#### Check CI Status First

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

#### Fetch Existing Review Comments

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

### 1.1 Read Changed Files (ONCE)

**Read each changed file's full content now - agents will reuse this data:**

```markdown
For each file in changed files list:
- Use Read tool to get full file content
- Track file path, language, and content
- Package into structured format for agents
```

**Why read now?**
- Agents need file context to analyze
- Reading once (here) vs 5 times (in each agent) = 5x token savings
- Main context grows slightly, but net savings is significant

### 1.2 Identify Languages

Scan changed files to determine language breakdown:

| File Extension | Language | Used By Agents |
|----------------|----------|----------------|
| `.cpp`, `.hpp`, `.h`, `.cc` | C++ | Language Rules Agent, Code Smells |
| `.py` | Python | Language Rules Agent, Code Smells |
| `CMakeLists.txt`, `.cmake` | CMake | Language Rules Agent |

### 1.3 Package Data for Agents

**Create structured data package containing:**

```markdown
## Changed Files Data Package

### Files Changed
[List of file paths with language tags]

### Full Diff
[Complete git diff output]

### File Contents
For each changed file:
---
File: path/to/file.cpp
Language: C++
Lines: 1-150

[Full file content from Read tool]
---

### Commit Messages
[git log output]

### PR Context (if GitHub)
- Title: [PR title]
- Description: [PR description]
- Author: [author]
- CI Status: [status]
```

**This package will be passed to all agents in Phase 1.5.**

## Phase 1.5: Spawn Parallel Analysis Agents

**Goal:** Launch 5 specialized agents in parallel to analyze the packaged data from Phase 1.

<IMPORTANT>
**Use general-purpose agents** (not Explore agents) since they receive pre-loaded context.
All agents run in parallel - invoke all 6 in a single tool call block.
Each agent has a unique identity, loads its skill, and maintains memory.
</IMPORTANT>

### Lite mode gate

Before spawning all 5 agents, check the diff scope:

- **Diff < 50 lines added/removed AND** no changes to logic (only docs,
  comments, formatting, imports, or type aliases): spawn ONLY correctness
  and tests agents. Skip security, performance, architecture.
- **Diff < 200 lines AND** affects only one file: spawn correctness +
  tests + style. Skip security and architecture.
- **Otherwise**: full 5-agent fan-out as documented below.

Document the chosen mode in the final report's Header section.

### Agent Identity & Memory System

Each agent has:
- **Unique ID**: Used in Agent tool `description` field for identification
- **Skill to Load**: Agent invokes this skill using the Skill tool before analysis
- **Memory File**: Project-specific learnings persisted across reviews

| # | Agent ID | Skill to Load | Memory File |
|---|----------|---------------|-------------|
| 1 | `static-analysis-agent` | `static-analysis` | `agents/static-analysis.md` |
| 2 | `dead-code-agent` | *(none)* | `agents/dead-code.md` |
| 3 | `code-smells-agent` | `code-smells` | `agents/code-smells.md` |
| 4 | `language-rules-agent` | `programming-cpp` or `programming-python` | `agents/language-rules.md` |
| 5 | `architecture-agent` | `architecture-analyze` | `agents/architecture.md` |
| 6 | `simplify-agent` | `simplify` | `agents/simplify.md` |

**Memory location:** `~/.claude/projects/<project>/memory/agents/`

### What Agents Learn

| Agent | Learns About |
|-------|--------------|
| Static Analysis | Tool configs, false positive patterns, suppression rules |
| Dead Code | Intentionally unused code, debug scaffolding, reserved APIs |
| Code Smells | Project-specific thresholds, acceptable patterns |
| Language Rules | Project conventions, intentional deviations from standards |
| Architecture | Module boundaries, key interfaces, dependency patterns, decisions |
| Simplify | Reuse opportunities, unnecessary complexity, verbose patterns |

### The 5 Analysis Agents

| # | Agent Type | Purpose | Returns |
|---|------------|---------|---------|
| 1 | Static Analysis | Run linters/tools on changed files | Structured table of tool findings |
| 2 | Dead Code Detection | Find unused code, comments, unreachable code | Table of dead code issues |
| 3 | Code Smells Detection | Detect anti-patterns (long functions, deep nesting, etc.) | Table of code smell findings |
| 4 | Language Rules Enforcement | Apply C++/Python/CMake best practices | Table of best practice violations |
| 5 | Architecture Review | Analyze module boundaries, dependencies (if architectural changes detected) | Architecture assessment |
| 6 | Simplification | Find reuse opportunities, unnecessary complexity, verbose code | Table of simplification suggestions |

### Agent Execution Pattern

**Spawn all agents in parallel using the Agent tool:**

```markdown
Agent 1: Static Analysis Agent
- description: "static-analysis-agent"
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1

Agent 2: Dead Code Detection Agent
- description: "dead-code-agent"
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1

Agent 3: Code Smells Agent
- description: "code-smells-agent"
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1

Agent 4: Language Rules Agent
- description: "language-rules-agent"
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1

Agent 5: Architecture Agent (conditional)
- description: "architecture-agent"
- Only spawn if architectural changes detected (see criteria below)
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1

Agent 6: Simplification Agent
- description: "simplify-agent"
- subagent_type: "general-purpose"
- Prompt: [See template below] + Data Package from Phase 1
```

### Conditional Architecture Analysis

**Only run Architecture Agent if ANY of these signals present:**

| Signal | Indicates Architecture |
|--------|------------------------|
| New directories created | New module/component |
| New/modified interfaces or abstract classes | API boundaries changing |
| Changes to factories, DI, object creation | Dependency structure changing |
| New CMake targets (`add_library`, `add_executable`) | New build units |
| Changes across 5+ files in different modules | Cross-cutting change |
| New external dependencies | Integration points |
| Changes to base/core classes | Foundation shifting |

If no architectural signals → Skip Agent 5, run only Agents 1-4.

### Agent Prompt Templates

See "Agent Prompt Templates" section below for detailed prompts to use for each agent.

## Phase 2: Aggregate Agent Findings

**Goal:** Collect results from all agents, merge by severity, deduplicate, and prepare for final report.

### 2.1 Wait for All Agents

Wait for all agents from Phase 1.5 to complete:
- Agent 1: Static Analysis results
- Agent 2: Dead Code Detection results
- Agent 3: Code Smells results
- Agent 4: Language Rules results
- Agent 5: Architecture analysis (if ran)
- Agent 6: Simplification suggestions

### 2.2 Severity Mapping

**Map agent findings to review severity levels:**

| Agent Severity | Review Category | Score | Criteria |
|----------------|-----------------|-------|----------|
| Critical | **Critical** | 100 | Security vulnerability, data loss, crash, UB |
| Must Fix | **Must Fix** | 80 | Incorrect behavior, logic bugs, resource leaks, tool errors |
| Should Fix | **Should Fix** | 50 | Best practices, code smells, maintainability |
| Nitpick | **Nitpick** | 20 | Style, minor improvements, suggestions |

### 2.3 Merge Findings

**Combine findings from all agents:**

1. **Collect all issues** from each agent's output
2. **Group by severity**: Critical (100) → Must Fix (80) → Should Fix (50) → Nitpick (20)
3. **Sort within each group**: By file path, then line number
4. **Add agent source**: Tag each finding with which agent found it

**Example merged finding:**

```markdown
#### Issue: Null pointer dereference (Score: 80 - Must Fix)
**Source:** Static Analysis Agent (clang-tidy)
**File:** src/parser.cpp:42

[Issue details and fix code]
```

### 2.4 Deduplicate Issues

**If multiple agents flag the same issue:**

| Scenario | Action |
|----------|--------|
| Same file:line, same issue | Keep highest severity, merge descriptions |
| Same file:line, different issues | Keep both as separate findings |
| Different agents, same general category | Keep both if specific issues differ |

**Example deduplication:**

```
Agent 2 (Dead Code): "Line 45: Unused variable 'count'"
Agent 4 (Language Rules): "Line 45: Variable 'count' declared but not used"

→ Deduplicate to single finding with highest severity
```

### 2.5 Classify Change Type

Based on aggregated findings and changes, classify the PR:

| Type | Description |
|------|-------------|
| Feature | New functionality |
| Bugfix | Correcting behavior |
| Refactor | Improving structure |
| Docs | Documentation only |

## Phase 3: Review Tests (Manual Check)

<IMPORTANT>
Agents handle code analysis, but test review requires human judgment.
Manually check test coverage and quality.
</IMPORTANT>

### 3.1 Test Coverage Check

| Check | Questions |
|-------|-----------|
| **Coverage** | New code paths tested? |
| **Quality** | Tests verify behavior, not implementation? |
| **Edge cases** | Boundary conditions tested? |
| **Naming** | Test names describe what's being tested? |
| **Independence** | Tests can run in isolation? No order dependency? |
| **Assertions** | Clear, specific assertions? Good error messages? |

### 3.2 Suggest Missing Tests

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
```

**Test suggestion checklist:**
- [ ] Happy path test
- [ ] Empty/null input test
- [ ] Invalid input test
- [ ] Boundary values test
- [ ] Error handling test

### 3.3 Cross-File Consistency (Optional)

If agents missed cross-cutting concerns, manually check:

| Check | Questions |
|-------|-----------|
| **Consistency** | Same patterns used across new files? |
| **API coherence** | Public APIs coherent and well-designed? |
| **Dependencies** | New dependencies justified? Properly integrated? |
| **Documentation** | README/docs updated if needed? |

## Phase 4: Generate Final Report

**Compile aggregated findings from all phases into a comprehensive review.**

### Save final report to disk (opt-in)

Default behaviour: do NOT write a markdown file. The report is delivered as chat output. Saving to disk happens ONLY when the user explicitly asks ("save the review", "write a summary file to disk", "persist this report", "drop a markdown under the project", or equivalent).

When the user has asked, persist the report under the **git repository root** of the project being reviewed.

**Finding `<repo-root>`:** Run `git rev-parse --show-toplevel` from the project you are reviewing (works when the current working directory is anywhere inside that clone). If the reviewed tree is not a git work tree, fall back to the workspace root you were given for that review.

**Paths in the user message:** Prefer a path **relative to `<repo-root>`** (e.g. `.claude/pr-review-summaries/123-fix-bug.md`) so it is copy-paste friendly across machines. Use an absolute path only if the user context has no single repo root.

| Item | Rule |
|------|------|
| **Directory** | `<repo-root>/.claude/pr-review-summaries/` (create with `mkdir -p` if it does not exist) |
| **Full path** | `<repo-root>/.claude/pr-review-summaries/<filename>.md` |

**Filename**

- **GitHub PR review:** `<pr-number>-<pr-title-slug>.md`
  - `pr-number`: the PR number (digits only, no `#`).
  - `pr-title-slug`: slug derived from the PR **title** — lowercase, replace spaces and punctuation with single hyphens, strip leading/trailing hyphens, ASCII only; collapse repeated hyphens; **max 60 characters** so paths stay reasonable. If the title slug is empty, use `review`.
- **Local review (no PR):** `local-<branch-slug>-<short-slug>.md`
  - `branch-slug`: current branch name slugified the same way (max 40 chars), or `detached` if not on a branch.
  - `short-slug`: from the first line of `git log -1 --pretty=%s` (slugified, max 40 chars), or `changes` if unavailable.

**File contents:** Write the **entire** Phase 4 report (the full markdown document), not an excerpt. Use the Write tool or equivalent so the file is created or overwritten idempotently for that review run.

**User message:** After saving, briefly state the path to the saved file (e.g. `.claude/pr-review-summaries/123-fix-parser-null-handling.md`).

---

Report must include the sections marked [REQUIRED] in REPORT_TEMPLATE.md. See Universal Hygiene Rules > Report content rules for the full list and rationale.

### Report template

See `REPORT_TEMPLATE.md` in this skill directory for the full report
structure. The template covers Header, Summary, Intent vs Implementation,
Per-File Walkthrough, Agent Analysis, Architecture, Issues by Severity,
Test Coverage, Static Analysis, Security, Performance, API/ABI, Docs,
Cleanup, Previous Comments, Checklist, Questions.

When generating a review, copy the template structure and fill in
evidence per section.

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
- [ ] If user asked to save the report: persisted under `.claude/pr-review-summaries/` (see Phase 4); otherwise chat-only delivery is the default.

## Agent Prompt Templates

**Use these prompts when spawning the 5 analysis agents in Phase 1.5.**

### Agent 1: Static Analysis Agent

```markdown
You are the **Static Analysis Agent** (ID: static-analysis-agent).

## Step 1: Load Your Skill
First, invoke the `static-analysis` skill using the Skill tool.

## Step 2: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/static-analysis.md`

Apply any learned patterns:
- Known false positives to skip
- Project-specific tool configurations
- Suppression rules that are intentional

## Step 3: Analyze

[Input: Data Package from Phase 1]

1. **Identify available tools** based on file languages:
   - C++: clang-tidy, cppcheck, clang-analyzer
   - Python: ruff, pylint, mypy, bandit
   - Shell: shellcheck
   - CMake: cmake-lint

2. **Run tools** on all changed files (full file content, not just changed lines)

3. **Report ALL findings** - do not skip or filter out issues

4. **Map tool severity** to review categories:
   - error/critical → Critical (100)
   - warning/high → Must Fix (80)
   - info/medium → Should Fix (50)
   - style/low → Nitpick (20)

## Step 4: Return Findings

| File:Line | Tool | Severity | Issue | Fix (if available) |
|-----------|------|----------|-------|-------------------|
| parser.cpp:42 | clang-tidy | Must Fix (80) | Null pointer dereference | Add null check before use |

## Step 5: Update Memory (if new learnings)

If you discover patterns worth remembering (e.g., tool doesn't work well with this codebase),
note them for memory update:

**New Learnings:**
- [Pattern discovered]
```

### Agent 2: Dead Code Detection Agent

```markdown
You are the **Dead Code Detection Agent** (ID: dead-code-agent).

## Step 1: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/dead-code.md`

Apply any learned patterns:
- Intentionally unused code (reserved APIs, deprecation paths)
- Debug/test scaffolding that looks unused but is needed
- False positive patterns specific to this project

## Step 2: Analyze

[Input: Data Package from Phase 1]

Analyze changed files for:

1. **Unused variables**: declared but never used.
2. **Commented-out code**: code in comments (not doc comments).
3. **Unreachable code**: after `return` / `throw` / `break`.
4. **Unused imports / includes**: `#include` or `import` statements for unused libraries.
5. **Unused function parameters**: parameters never referenced in body.

#### 6. Comment hygiene

Apply these checks to every comment in the diff. The full rule set lives in `programming-cpp` skill (Documentation & Comments). Severity is **Nitpick** unless the comment is misleading (then **Should Fix**).

**Restating comments**: comment paraphrases code on the same or next line. Always flag.

```cpp
i++;                       // increment i           BAD
m_count = 0;               // initialize count      BAD
result.clear();            // clear the result      BAD
return value;              // return value          BAD
```

**Meaningless / decorative comments**: banners, separators, file headers re-stating the filename, "TODO" without a ticket or owner.

```cpp
// =================== Helpers ===================   BAD: decoration only
// foo.cpp                                           BAD: filename echo
// TODO: fix this                                    BAD: no ticket, no owner, no date
```

**Doxygen blocks paraphrasing the signature**: Doxygen body = function name + parameter names retold in prose. Flag - delete the block.

```cpp
/**
 * Returns true if value is positive.        BAD: signature already says it
 * @param value The value to check.
 * @return True if positive.
 */
bool is_positive(int value);
```

**Long-form preambles without long-term value**: multi-line `// ...` blocks above tests / helpers / files that re-tell story already in the diff, the test name, the PR description, the commit message, or the bug tracker. Flag - delete or compress to one line.

```cpp
// Background. Three sites construct ...    BAD: 30+ line preamble
// Site 1: ...                              BAD: banner above helper
// Site 2: ...                              BAD: banner above helper
// See foo.cpp:123-145 for context          BAD: line refs rot
// This was broken because X; now does Y    BAD: commit message owns it
```

**Missing Doxygen on non-obvious public API**: public function or class where the name + signature alone do NOT tell a caller how to use it (units, ownership, throws, nullopt semantics, threading, pre/post-conditions). Flag - suggest a javadoc-style `/** @param @return @throws */` block.

**Do NOT flag** these (good comments worth keeping):

- Hidden invariants: `// caller holds m_mutex`
- Workarounds with ticket + sunset: `// workaround for FOO-1234; remove when bar.so >= 2.5`
- Non-obvious unit / ownership notes: `// nanoseconds, monotonic`, `// caller takes ownership`
- Domain quirks: `// protocol spec sets MSB on negative flag`
- Doxygen on public APIs that documents what the type system cannot

**Rule of thumb for the agent**: ask "would removing this comment confuse a competent reader of this codebase a year from now?" If no, it is noise - flag it.

Report ALL findings - be thorough and picky.

## Step 3: Return Format

For each finding:

| File:Line | Issue Type | Code Snippet | Severity | Fix |
|-----------|------------|--------------|----------|-----|
| parser.cpp:45 | Unused variable | `int count = 0;` | Nitpick (20) | Remove variable |
| utils.py:12 | Commented code | `# old_func()` | Nitpick (20) | Remove comment |
| handler.cpp:67 | Unreachable code | Code after `return` | Must Fix (80) | Remove or fix logic |

**Review the ENTIRE changed file, not just the changed lines.**

Check the full context of all modified functions, classes, and modules.
Report ALL issues found in changed files, even in unchanged lines that have problems.

## Step 4: Update Memory (if new learnings)

If you discover code that looks unused but is intentional (confirmed by comments, patterns, or context),
note it for memory update:

**New Learnings:**
- [Pattern to remember as intentionally unused]
```

### Agent 3: Code Smells Agent

```markdown
You are the **Code Smells Detection Agent** (ID: code-smells-agent).

## Step 1: Load Your Skill
First, invoke the `code-smells` skill using the Skill tool.
This provides the comprehensive catalog of 22 code smells across 5 categories.

## Step 2: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/code-smells.md`

Apply any learned patterns:
- Project-specific thresholds (maybe 60 lines is OK for this project)
- Patterns that look like smells but are intentional
- Acceptable deviations documented in the project

## Step 3: Analyze

[Input: Data Package from Phase 1]

**Your Tasks:**

Detect code smells from these categories:

**Bloaters:**
- Long Method (>50 lines: Should Fix, >100 lines: Must Fix)
- Large Class (>500 lines: Should Fix, >1000 lines: Must Fix)
- Primitive Obsession (using primitives instead of domain objects)
- Long Parameter List (>4 params: Should Fix, >6 params: Must Fix)
- Data Clumps (same parameters appearing together)

**Object-Orientation Abusers:**
- Switch Statements (complex switch/if-else based on type)
- Temporary Field (fields used only sometimes)
- Refused Bequest (subclass ignoring parent methods)

**Change Preventers:**
- Divergent Change (class changes for multiple unrelated reasons)
- Shotgun Surgery (single change touches 5+ classes: Must Fix)
- Parallel Inheritance Hierarchies

**Dispensables:**
- Comments (explaining what instead of why)
- Duplicate Code (>10 identical lines: Should Fix)
- Lazy Class, Data Class, Dead Code, Speculative Generality

**Couplers:**
- Feature Envy (method uses >3 external getters)
- Inappropriate Intimacy (classes accessing each other's internals: Must Fix)
- Message Chains (>3 chained calls)
- Middle Man (class only delegates)

## Return Format

| File:Line | Smell Type | Category | Severity | Suggested Refactoring |
|-----------|------------|----------|----------|----------------------|
| handler.cpp:120-195 | Long Method (75 lines) | Bloater | Should Fix (50) | Extract Method: split into extractHeaders, validateRequest, routeToHandler, buildResponse |
| config.cpp:45 | Magic Number | Bloater | Should Fix (50) | Replace Magic Number: `const int MAX_RETRIES = 42;` |
| parser.cpp:30 | Feature Envy | Coupler | Should Fix (50) | Move Method: move to class whose data it uses |

Provide specific refactoring suggestions for each smell. See `code-smells` skill for detailed refactoring techniques.

## Step 4: Update Memory (if new learnings)

If you discover patterns that are acceptable in this project (confirmed by existing code or comments):

**New Learnings:**
- [Pattern that looks like a smell but is intentional]
- [Project-specific threshold adjustments]
```

### Agent 4: Language Rules Enforcement Agent

```markdown
You are the **Language Rules Enforcement Agent** (ID: language-rules-agent).

## Step 1: Load Your Skills
Based on the languages in the changed files, invoke the appropriate skill(s) using the Skill tool:
- C++ files → `programming-cpp` skill
- Python files → `programming-python` skill
- CMake files → `programming-cmake-best-practices` skill

## Step 2: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/language-rules.md`

Apply any learned patterns:
- Project conventions that deviate from standards
- Intentional exceptions documented in the project
- Style choices specific to this codebase

## Step 3: Analyze

[Input: Data Package from Phase 1]

**Your Tasks:**

**For C++ files**, check (from `programming-cpp` skill):

| Rule | Check |
|------|-------|
| const correctness | Parameters const& where appropriate? Member functions const? |
| Smart pointers | No raw new/delete? unique_ptr/shared_ptr used? |
| RAII | Resources managed by objects? No manual cleanup? |
| noexcept | Destructors, move ops, swap marked noexcept? |
| [[nodiscard]] | Important return values marked? |
| STL algorithms | std::find, std::transform instead of raw loops? |
| Initialization | All variables initialized? |
| Move semantics | std::move for ownership transfer? |

**For Python files**, check (from `programming-python` skill):

| Rule | Check |
|------|-------|
| Type hints | All function parameters and returns typed? |
| Context managers | `with` used for files, locks, connections? |
| F-strings | Used instead of .format() or %? |
| No mutable defaults | def f(x=[]) is forbidden |
| Specific exceptions | No bare `except:` |
| Comprehensions | Used where clearer than loops? |

**For CMake files**, check (from `programming-cmake-best-practices` skill):

| Rule | Check |
|------|-------|
| Modern targets | target_* commands instead of global? |
| Visibility | PUBLIC/PRIVATE/INTERFACE used correctly? |
| No deprecated commands | No include_directories, link_directories? |

## Return Format

| File:Line | Rule Violated | Current Code | Fixed Code | Severity |
|-----------|---------------|--------------|------------|----------|
| parser.cpp:42 | Missing const& | `void foo(string s)` | `void foo(const string& s)` | Should Fix (50) |
| utils.py:12 | Missing type hint | `def parse(data):` | `def parse(data: str) -> dict:` | Should Fix (50) |

Apply best practices strictly - these are the standard, not existing codebase patterns.
**Report ALL violations** - be thorough and picky about every rule from the programming skills.

## Step 4: Update Memory (if new learnings)

If you discover project-specific conventions (confirmed by existing code patterns or comments):

**New Learnings:**
- [Convention that differs from standard]
- [Reason why this project does it differently]
```

### Agent 5: Architecture Review Agent (Conditional)

```markdown
You are the **Architecture Review Agent** (ID: architecture-agent).

**Only spawn this agent if architectural changes are detected (see criteria below).**

## Step 1: Load Your Skill
First, invoke the `architecture-analyze` skill using the Skill tool.
This provides the full architecture analysis methodology.

## Step 2: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/architecture.md`

This is your most valuable memory - it contains:
- Module boundaries and responsibilities learned from previous reviews
- Key interfaces and abstractions in this codebase
- Dependency patterns and architectural decisions
- Common architectural issues in this project

## Step 3: Analyze

[Input: Data Package from Phase 1]

**Your Tasks:**

1. **Module boundaries**: Is new code in the right place?
2. **Dependencies**: Are dependency directions correct? Any cycles?
3. **Testability**: Can new code be unit tested in isolation?
4. **Simplicity**: Is the design over-engineered?

Use your memory to understand existing architecture before judging new code.

## Step 4: Return Assessment

```markdown
### Architecture Assessment

**Verdict:** [Appropriate / Needs Discussion / Major Concerns]

**Module Placement:** [Correct / Suggest moving to X]

**Dependencies:** [Clean / Issues found]

**Testability:** [Good / Needs improvement]

**Simplicity:** [Appropriate / Over-engineered / Under-engineered]

**Findings:**
| Location | Issue | Severity | Recommendation |
|----------|-------|----------|----------------|
| src/new_module/ | Wrong location | Should Fix (50) | Move to src/core/ |
```

## Step 5: Update Memory (IMPORTANT)

**Always update your memory** with new architectural knowledge:

**New Learnings:**
- **Modules discovered:** [New modules and their responsibilities]
- **Key interfaces:** [Important abstractions found]
- **Dependency patterns:** [How modules connect]
- **Architectural decisions:** [Design choices and rationale]
```

### Agent 6: Simplification Agent

```markdown
You are the **Simplification Agent** (ID: simplify-agent).

## Step 1: Load Your Skill
First, invoke the `simplify` skill using the Skill tool.

## Step 2: Read Your Memory
Read your memory file (if it exists): `~/.claude/projects/<project>/memory/agents/simplify.md`

Apply any learned patterns:
- Existing utility functions/helpers available in this codebase
- Project-specific patterns that look verbose but are intentional
- Libraries/frameworks already in use that provide relevant utilities

## Step 3: Analyze

[Input: Data Package from Phase 1]

**Your Tasks:**

Analyze changed files for simplification opportunities:

1. **Reuse opportunities**: Code that reimplements existing functionality
   - Utility functions already available in the codebase
   - Standard library functions that replace manual implementations
   - Framework/library helpers that are already dependencies

2. **Unnecessary complexity**: Code that can be written more simply
   - Overly complex conditionals that can be flattened
   - Unnecessary wrapper functions or indirection layers
   - Over-engineered abstractions for simple operations
   - Verbose patterns where concise idioms exist

3. **Redundant code**: Within the changed files
   - Similar logic repeated that could share a common implementation
   - Redundant checks or validations already guaranteed by callers
   - Unnecessary type conversions or temporary variables

4. **Verbose patterns**: Language-specific simplifications
   - C++: Range-for instead of index loops, structured bindings, std::optional instead of sentinel values, algorithm calls instead of manual loops
   - Python: Comprehensions instead of loops, unpacking, walrus operator, pathlib instead of os.path
   - General: Early returns to reduce nesting, guard clauses

**Do NOT flag:**
- Intentional verbosity for clarity or debugging
- Code that matches established project conventions
- Simplifications that would hurt readability

## Step 4: Return Findings

| File:Line | Type | Current Pattern | Simplified Version | Severity |
|-----------|------|-----------------|-------------------|----------|
| utils.cpp:30-45 | Reuse | Manual string split implementation | Use `absl::StrSplit()` already in deps | Should Fix (50) |
| handler.py:67 | Verbose | `if x is not None and x != ""` | `if x` (truthy check sufficient here) | Nitpick (20) |
| parser.cpp:89-110 | Complexity | Nested if-else chain (4 levels) | Early returns reduce to 1 level | Should Fix (50) |
| config.cpp:23 | Redundant | `std::string s = std::string(input)` | `std::string s{input}` | Nitpick (20) |

**For each finding, provide:**
- The current code snippet
- The simplified version
- Why the simplification is safe (no behavior change)

## Step 5: Update Memory (if new learnings)

If you discover reusable utilities or project conventions:

**New Learnings:**
- [Utility functions available for reuse]
- [Patterns that look verbose but are intentional]
```

**Spawn Architecture Agent if ANY of these signals present:**

| Signal | Indicates |
|--------|-----------|
| New directories created | New module/component |
| New/modified interfaces or abstract classes | API boundaries changing |
| Changes to factories, DI, object creation | Dependency structure changing |
| New CMake targets (add_library, add_executable) | New build units |
| Changes across 5+ files in different modules | Cross-cutting change |
| New external dependencies | Integration points |
| Changes to base/core classes | Foundation shifting |

If no architectural signals → Skip Agent 5, run only Agents 1-4.

## Agent Memory File Format

Each agent's memory file follows this structure:

```markdown
# [Agent Name] Memory

## Project: [auto-detected]
Last updated: [date]

## Learned Patterns
<!-- Patterns confirmed across multiple reviews -->

## False Positives
<!-- Issues flagged that turned out to be intentional -->

## Project-Specific Rules
<!-- Deviations from defaults that are acceptable -->

## Key Knowledge
<!-- For Architecture Agent: module map, interfaces, dependencies -->
<!-- For others: important context about this codebase -->
```

## References

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [How to Do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-1/)
