---
name: pr-review
description: Reviews Pull Requests or local diffs with a 7-agent fan-out covering static analysis, dead code, code smells + quality (naming, complexity, single-responsibility, magic numbers), language rules (C++/Python/CMake), architecture, simplification, and performance (hot-path classification, allocations, locks, I/O). Use when the user asks to "review this PR", "review the diff", "audit this branch", "/pr-review", or when staging changes before push.
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

Apply to every invocation of this skill. Full text in [HYGIENE.md](HYGIENE.md). Summary:

- **Local-only by default**: do NOT post to GitHub unless the user explicitly says "post" / "submit" / "comment on the PR".
- **Fresh-eyes rule**: when this skill runs inside a sub-agent, the brief is the only context - no project memory, no prior reviews, no conversation history.
- **Required report sections**: Header, Intent vs Implementation, Per-File Walkthrough, Findings by Severity, Static Analysis, Security Audit, Performance, API/ABI Compatibility, Documentation, Verdict (`APPROVE` / `REQUEST CHANGES` / `NEEDS DISCUSSION`), Cleanup Confirmation. Full layout in `REPORT_TEMPLATE.md`.
- **Local clone hygiene**: record starting branch, stash if dirty, restore on exit via trap/finally - never leave the clone on a detached HEAD or PR branch.

## Review Process

| Phase | Purpose |
|-------|---------|
| 0. Determine target | PR# / URL -> GitHub PR; nothing -> local diff vs main; "re-review" -> changes since last review |
| 1. Gather + read | Changed files, full diff, commit messages, CI status; read each file ONCE; build Data Package |
| 1.5. Spawn 7 agents in parallel | Static, Dead Code, Code Smells + Quality, Language Rules, Architecture (conditional), Simplify, Performance |
| 2. Aggregate | Merge findings, map to severity, deduplicate, sort, classify change type |
| 3. Review tests | Coverage, edge cases, naming, independence, assertions; suggest missing tests |
| 4. Final report | Severity-sorted, agent-sourced, with code fixes; chat-only by default, save .md only if asked |

## Phase 0: Determine Review Target

**Do NOT ask the user what to review. Determine automatically:**

| User Input | Action |
|------------|--------|
| PR number (e.g., `123`, `#123`) | Review GitHub PR #123 |
| PR URL (e.g., `github.com/.../pull/123`) | Review that GitHub PR |
| "re-review" or "review again" | Re-review mode (show only new changes) |
| Nothing / just "review" | Review local changes vs main branch |

### GitHub PR

Invoke `git-gh-client` to verify `gh` is available, then fetch via `gh pr view` / `gh pr diff` / `gh pr checks`.

### Local changes (default)

```bash
base=$(git rev-parse --verify main 2>/dev/null && echo main || echo master)
git diff --name-only "$base"...HEAD
git diff "$base"...HEAD
git log "$base"...HEAD --oneline
```

### Re-review mode

Diff from the last reviewed SHA (`git diff <last>...HEAD` or `gh pr view N --json commits,reviews`). Focus on NEW changes; note which prior issues were addressed.

## Phase 1: Gather Information + Read Files

Collect data ONCE and package for agents - minimize redundant file reads.

### GitHub PR

Fetch via `git-gh-client` commands: `gh pr view N --json ...` for metadata, `gh pr diff N` for the diff, `gh pr checks N` for CI, `gh api repos/{o}/{r}/pulls/N/comments` + `gh pr view N --json reviews` for prior comments. Note CI failures in the report; do not block review on them unless the user asks.

### Local diff (default)

`git diff --name-only <base>...HEAD`, `git diff <base>...HEAD`, `git log <base>...HEAD --oneline`.

### 1.1 Read each file ONCE

Read the full body (not just changed lines) with the Read tool. Reading once here vs N times across agents = N-fold token savings.

### 1.2 Identify languages

| Extension | Language | Used by |
|-----------|----------|---------|
| `.cpp` / `.hpp` / `.h` / `.cc` | C++ | language-rules-agent, code-smells-agent |
| `.py` | Python | language-rules-agent, code-smells-agent |
| `CMakeLists.txt` / `.cmake` | CMake | language-rules-agent |

### 1.3 Build the Data Package

One package, passed to every spawned agent. Required sections: Files Changed (path + language), Full Diff, File Contents (full body, tagged with language), Commit Messages, PR Context (title, description, author, CI status - if GitHub).

## Phase 1.5: Spawn Parallel Analysis Agents

**Goal:** Launch up to 7 specialized agents in parallel to analyze the packaged data from Phase 1.

<IMPORTANT>
**Use general-purpose agents** (not Explore agents) since they receive pre-loaded context.
All agents run in parallel - invoke all of them in a single tool call block.
Each agent has a unique identity, loads its skill, and maintains memory.
</IMPORTANT>

### Lite mode gate

Before spawning all agents, check the diff scope. Agent IDs match the table in "Agent Identity & Memory System" below.

- **Diff < 50 lines added/removed AND** no logic changes (docs / comments / formatting / imports / type aliases only): spawn ONLY Agents 1 (`static-analysis-agent`) and 2 (`dead-code-agent`). Skip 3, 4, 5, 6, 7.
- **Diff < 200 lines AND** affects only one file: spawn Agents 1, 2, 3 (`code-smells-agent`), 4 (`language-rules-agent`), 7 (`performance-agent`). Skip 5 (architecture) and 6 (simplify).
- **Otherwise**: full 7-agent fan-out (Agent 5 still gated by the architectural-signal table below).

Document the chosen mode and the spawned agent IDs in the final report's Header section.

### Agent Identity & Memory System

Each agent has:
- **Unique ID**: Used in Agent tool `description` field for identification
- **Skill to Load**: Agent invokes this skill using the Skill tool before analysis
- **Memory File**: Project-specific learnings persisted across reviews

| # | Agent ID | Skill to Load | Memory File |
|---|----------|---------------|-------------|
| 1 | `static-analysis-agent` | `static-analysis` | `agents/static-analysis.md` |
| 2 | `dead-code-agent` | *(none)* | `agents/dead-code.md` |
| 3 | `code-smells-agent` | `code-smells` + load `QUALITY.md` from this skill | `agents/code-smells.md` |
| 4 | `language-rules-agent` | `programming-cpp` or `programming-python` | `agents/language-rules.md` |
| 5 | `architecture-agent` | `architecture-analyze` | `agents/architecture.md` |
| 6 | `simplify-agent` | `simplify` | `agents/simplify.md` |
| 7 | `performance-agent` | *(none, loads `PERFORMANCE.md` from this skill)* | `agents/performance.md` |

**Memory location:** `~/.claude/projects/<project>/memory/agents/`

### The 7 Analysis Agents (purpose + memory topic)

| # | Agent ID | Purpose | Memory topic |
|---|----------|---------|--------------|
| 1 | `static-analysis-agent` | Run linters/tools (clang-tidy, ruff, etc.) on full file contents | Tool configs, false positives, suppressions |
| 2 | `dead-code-agent` | Unused code, comments, unreachable code, comment hygiene | Intentionally-unused code, reserved APIs |
| 3 | `code-smells-agent` | 22 smells + 4 quality dimensions per `QUALITY.md` | Project thresholds, quality-dim overrides |
| 4 | `language-rules-agent` | C++ / Python / CMake best practices per `programming-*` skills | Project conventions, intentional deviations |
| 5 | `architecture-agent` | Module boundaries, dependencies, testability (conditional - see signal table) | Module map, interfaces, dependency patterns |
| 6 | `simplify-agent` | Reuse, unnecessary complexity, verbose patterns per `simplify` skill | Project utilities, intentional verbosity |
| 7 | `performance-agent` | Hot-path classification + alloc/complexity/locks/IO per `PERFORMANCE.md` | Hot files, accepted alloc patterns, benchmarks |

### Agent Execution Pattern

**Spawn all selected agents in parallel using the Agent tool** (one tool block, multiple `Agent` calls). For each spawn:
- `description`: the agent ID from the table in "Agent Identity & Memory System"
- `subagent_type`: `general-purpose`
- prompt body: contents of the matching file under `agents/prompts/` (see "Agent Prompt Templates" below) + the Data Package from Phase 1

Agent 5 only spawns when the architectural-signal table matches. Lite mode (above) further trims the set.

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

If no architectural signals → Skip Agent 5, run Agents 1-4, 6, 7.

### Agent Prompt Templates

Each agent's full prompt lives in its own file under `agents/prompts/`. The orchestrator passes the file's contents + Data Package to the spawned agent.

| Agent ID | Prompt file |
|----------|-------------|
| `static-analysis-agent` | [agents/prompts/agent-1-static-analysis.md](agents/prompts/agent-1-static-analysis.md) |
| `dead-code-agent` | [agents/prompts/agent-2-dead-code.md](agents/prompts/agent-2-dead-code.md) |
| `code-smells-agent` | [agents/prompts/agent-3-code-smells-quality.md](agents/prompts/agent-3-code-smells-quality.md) |
| `language-rules-agent` | [agents/prompts/agent-4-language-rules.md](agents/prompts/agent-4-language-rules.md) |
| `architecture-agent` | [agents/prompts/agent-5-architecture.md](agents/prompts/agent-5-architecture.md) |
| `simplify-agent` | [agents/prompts/agent-6-simplification.md](agents/prompts/agent-6-simplification.md) |
| `performance-agent` | [agents/prompts/agent-7-performance.md](agents/prompts/agent-7-performance.md) |

Architecture Agent fires only when the architectural-signal table below matches. All others fire per the lite-mode gate.

## Phase 2: Aggregate Agent Findings

Wait for all spawned agents from Phase 1.5. Then:

### 2.1 Severity scale (used by every agent)

| Category | Score | Criteria |
|----------|-------|----------|
| Critical | 100 | Security vulnerability, data loss, crash, UB |
| Must Fix | 80 | Incorrect behavior, logic bugs, resource leaks, tool errors |
| Should Fix | 50 | Best practices, code smells, maintainability |
| Nitpick | 20 | Style, minor improvements, suggestions |

### 2.2 Merge

Collect every issue. Group by severity (Critical -> Must Fix -> Should Fix -> Nitpick). Sort within each group by file path then line number. Tag each finding with the source agent ID.

### 2.3 Deduplicate

- Same file:line, same issue -> keep highest severity, merge descriptions
- Same file:line, different issues -> keep both
- Different agents, same general category, different specifics -> keep both

### 2.4 Classify change type

Feature / Bugfix / Refactor / Docs - put it in the report header.

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

If new code lacks tests, list per-function the cases to add. Checklist:

- [ ] Happy path
- [ ] Empty/null input
- [ ] Invalid input
- [ ] Boundary values
- [ ] Error handling

Use the project's test framework (GTest/GMock for C++, pytest for Python) and follow the naming convention found in nearby tests.

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
