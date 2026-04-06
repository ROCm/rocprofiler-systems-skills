---
name: radisha-skills
description: List all available radisha skills with their command aliases, organized by category
---

# Skills Listing

Displays all available radisha skills with descriptions and command aliases.

## When to Use

- User asks what skills are available
- User wants to discover radisha capabilities
- User types `/skills`

## Quick Commands

These shortcuts invoke common skills directly:

| Command | Description | Skill |
|---------|-------------|-------|
| `/plan` | Start planning (asks which type) | Smart menu |
| `/plan-feature` | Plan a new feature | `planning-feature` |
| `/plan-bugfix` | Plan a bug fix | `planning-bugfix` |
| `/plan-refactor` | Plan refactoring | `planning-refactor` |
| `/commit` | Create a commit | `git-commit` |
| `/pr` | Prepare a pull request | `git-prepare-pull-request` |
| `/review` | Review a pull request | `pr-review` |
| `/testplan` | Create a test plan | `testing-testplan` |
| `/explore` | Explore unfamiliar code | `exploration-explore-code` |
| `/skills` | List all skills (this) | `radisha-skills` |
| `/update` | Update radisha | `radisha-update` |
| `/improve-skill` | Improve an existing skill | `radisha-improve-skill` |

## All Skills by Category

### Entry Point

| Skill | Description |
|-------|-------------|
| `radisha-help` | Core skill - how to use radisha, workflow rules, validation |

### Planning

| Skill | Description |
|-------|-------------|
| `planning-feature` | Plan new features (includes changelog + tests) |
| `planning-bugfix` | Plan bug fixes (root cause analysis) |
| `planning-refactor` | Plan refactoring (best practices focus) |
| `planning-docs` | Plan documentation (no changelog/tests) |
| `planning-base` | Shared rules - do not invoke directly |

### Programming

| Skill | Description |
|-------|-------------|
| `programming-cpp` | C++ Core Guidelines, C++17, performance |
| `programming-cpp-design-patterns` | Suggests applicable design patterns |
| `programming-cpp-stl-algorithms` | STL algorithms instead of manual loops |
| `programming-cpp-naming-rules` | File/class naming conventions |
| `programming-cmake-best-practices` | Modern CMake 3.15+ |
| `programming-python` | PEP 8, type hints, modern Python 3.8+ |

### Testing

| Skill | Description |
|-------|-------------|
| `testing-testplan` | Create test plans for QA handoff |
| `testing-gtest-gmock` | GTest/GMock for C++ testing |
| `testing-pytest` | Pytest for Python testing |

### Libraries

| Skill | Description |
|-------|-------------|
| `library-amd-smi` | AMD SMI library for GPU/CPU/NIC monitoring |

### Projects

| Skill | Description |
|-------|-------------|
| `rocprofsys` | ROCm Systems Profiler workflows (main entry point) |
| `rocprofsys-configure` | Configure rocprofiler-systems build |
| `rocprofsys-build` | Build and install rocprofiler-systems |

### Git

| Skill | Description |
|-------|-------------|
| `git-commit` | Create meaningful commit messages |
| `git-prepare-pull-request` | Prepare reviewable PRs |
| `pr-review` | Structured PR review |

### Exploration

| Skill | Description |
|-------|-------------|
| `exploration-explore-code` | Systematic codebase exploration |

### Code Quality

| Skill | Description |
|-------|-------------|
| `code-smells` | Detect code smells (refactoring.guru catalog) |
| `refactoring-techniques` | Apply 60+ refactoring techniques (Extract Method, Move Field, etc.) |
| `static-analysis` | Run linters and static analysis tools |
| `review-architecture` | Architecture documentation (iterative, chapter-by-chapter) |
| `architecture-analyze` | Analyze module boundaries, dependencies |

### Radisha Management

| Skill | Description |
|-------|-------------|
| `radisha-update` | Update radisha to latest version |
| `radisha-create-skill` | Create new skills with validation |
| `radisha-improve-skill` | Improve existing skills when gaps found |
| `radisha-skills` | List all skills (this skill) |

### Utility

| Skill | Description |
|-------|-------------|
| `ask` | Questions without actions |

## After Listing

After presenting this list, ask:

> Would you like me to invoke any of these skills?

If user specifies a skill, invoke it immediately.
