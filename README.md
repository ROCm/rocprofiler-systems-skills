# Radisha - AI Development Skills

A comprehensive skills system for AI-assisted software development. Skills are reusable AI behavior definitions that guide Claude to follow consistent, professional development workflows.

## Table of Contents

- [What is Radisha?](#what-is-radisha)
- [Philosophy](#philosophy)
  - [Core Principles](#core-principles)
  - [Planning First, Always](#planning-first-always)
  - [Complete Workflow](#complete-workflow)
- [Installation](#installation)
- [How to Use](#how-to-use)
  - [Claude Code CLI](#claude-code-cli)
  - [Cursor IDE](#cursor-ide)
  - [Quick Reference](#quick-reference)
- [Skill Categories](#skill-categories)
  - [Planning Skills](#planning-skills)
  - [Programming Skills](#programming-skills)
  - [Testing Skills](#testing-skills)
  - [Library Skills](#library-skills)
  - [Git Skills](#git-skills)
  - [Exploration Skills](#exploration-skills)
  - [Radisha Skills](#radisha-skills)
- [Key Concepts](#key-concepts)
  - [Step-by-Step Validation](#step-by-step-validation)
  - [Re-planning When Things Go Wrong](#re-planning-when-things-go-wrong)
  - [Plan Persistence](#plan-persistence)
  - [Platform Tool Mapping](#platform-tool-mapping)
- [Directory Structure](#directory-structure)
- [Skill Details](#skill-details)
  - [Planning Skills Details](#planning-skills-1)
  - [Programming Skills Details](#programming-skills-1)
  - [Testing Skills Details](#testing-skills-1)
  - [Library Skills Details](#library-skills-1)
  - [Exploration Skills Details](#exploration-skills-1)
  - [Git Skills Details](#git-skills-1)
  - [Radisha Skills Details](#radisha-skills-1)
- [Contributing](#contributing)
- [Resources](#resources)

## What is Radisha?

Radisha is a skill library that teaches AI assistants how to:
- **Plan before coding** - Structured planning phases before implementation
- **Follow best practices** - Language-specific guidelines (C++17, Python, CMake)
- **Write meaningful commits** - Well-structured commit messages
- **Create reviewable PRs** - Proper PR scope and documentation
- **Test thoroughly** - Comprehensive test plans and implementation

Think of it as a **senior developer's handbook** encoded as AI instructions.

## Philosophy

### Core Principles

**Simplicity First** - Make every change as simple as possible. Impact minimal code.

**No Laziness** - Find root causes. No temporary fixes. Senior developer standards.

**Minimal Impact** - Changes should only touch what's necessary. Avoid introducing bugs.

**Every Plan Leads to a Pull Request** - Keep PR reviewability in mind from the start.

### Planning First, Always

**Every non-trivial task starts with planning.** The AI must:

1. Complete planning phases before implementation
2. Analyze the request and identify scope
3. Create a structured plan with tasks
4. Save the plan to `planning/` folder
5. Execute step-by-step with verification and user validation
6. Offer unit tests after completion

### Plan Mode Workflow

```
Planning Phase (phases 0-4)     Execution Phase
┌─────────────────────┐         ┌─────────────────────┐
│ - Analyze request   │         │ - Save plan to file │
│ - Identify scope    │ ──────► │ - Execute tasks     │
│ - Decompose tasks   │         │ - Verify & validate │
│ - Create task list  │         │ - Mark progress     │
└─────────────────────┘         └─────────────────────┘
```

**Platform-specific:**
- **Cursor:** Use Plan Mode for planning, then switch to Agent Mode
- **Claude Code:** Use `EnterPlanMode` tool or simply complete planning before coding

### Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     Is it just a question?    │
                    └───────────────────────────────┘
                           │                │
                          yes               no
                           │                │
                           ▼                ▼
                    ┌─────────┐    ┌────────────────────┐
                    │   ask   │    │  Determine type    │
                    │  skill  │    │  (if unclear, ask) │
                    └─────────┘    └────────────────────┘
                                            │
                                            ├── feature ──→ planning/feature
                                            ├── bugfix ───→ planning/bugfix
                                            ├── refactor ─→ planning/refactor
                                            ├── docs ─────→ planning/docs
                                            └── architecture → planning/architecture
                                                    │
                                         ┌──────────┴──────────┐
                                         │     PLAN MODE       │
                                         └─────────────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 1: PLANNING            │
                                    │  - Analyze scope & risks      │
                                    │  - Assess PR scope (split?)   │
                                    │  - Decompose into tasks       │
                                    │  - Create task list           │
                                    └───────────────────────────────┘
                                                    │
                                         ┌──────────┴──────────┐
                                         │    AGENT MODE       │
                                         │ (save plan first!)  │
                                         └─────────────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 2: IMPLEMENTATION      │
                                    │  - Save plan to planning/     │
                                    │  - Load programming skills    │
                                    │  - Execute step by step       │
                                    │  - Verify autonomously        │
                                    │  - Ask user validation        │
                                    │  - Mark progress in plan      │
                                    └───────────────────────────────┘
                                                    │
                                          ┌────────┴────────┐
                                          │ Things go wrong?│
                                          └────────┬────────┘
                                                   │
                                         yes ◄─────┴─────► no
                                          │                │
                                          ▼                │
                                    ┌───────────┐          │
                                    │ STOP and  │          │
                                    │ RE-PLAN   │──────────┤
                                    └───────────┘          │
                                                           ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 3: TESTING             │
                                    │  - Ask: "Want unit tests?"    │
                                    │  - Create test plan           │
                                    │  - Write test by test         │
                                    │  - Wait for approval each     │
                                    └───────────────────────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 4: PULL REQUEST        │
                                    │  - Ask: "Create PR?"          │
                                    │  - Write: Motivation          │
                                    │  - Write: Technical Details   │
                                    │  - Write: Test Plan           │
                                    └───────────────────────────────┘
                                                    │
                                                    ▼
                                                RESPOND
```

### English Output

All output is in English, regardless of input language. This ensures consistency across documentation, plans, code comments, and conversations.

## Installation

### Quick Install (For public repos)

**Note:** This repo is currently private. The one-liner won't work without authentication. Use manual installation below.

```bash
curl -fsSL https://raw.githubusercontent.com/ROCm/rocprofiler-systems-skills/main/install.sh | bash
```

### Manual Installation (Recommended)

1. **Clone the repository:**
   ```bash
   git clone git@github.com:ROCm/rocprofiler-systems-skills.git ~/work/radisha
   ```

2. **Run the installer:**
   ```bash
   cd ~/work/radisha
   ./install.sh
   ```

3. **Or manually create symlink:**
   ```bash
   # For Claude Code
   ln -sf ~/work/radisha/skills ~/.claude/skills

   # For Cursor (global)
   ln -sf ~/work/radisha/skills ~/.cursor/skills
   ```

### Project Setup

After global installation, set up individual projects:

1. Copy `CLAUDE.md` to your project root (for Claude Code)
2. Copy `.cursorrules` to your project root (for Cursor)

Or run `./install.sh` from your project directory and answer "y" to project setup.

## How to Use

### Claude Code CLI

Just ask naturally - skills are automatically applied:
- "commit these changes" → uses `git/commit` skill
- "plan this feature" → uses `planning/feature` skill
- "review the PR" → uses `git/review-pull-request` skill

**How it works:**
1. Skills are auto-loaded from `~/.claude/skills/`
2. Core rules are loaded from `CLAUDE.md` in your project root
3. When you make requests, Claude reads the appropriate skill and follows it
4. No special commands needed - just natural language

### Cursor IDE

Use `@skill-name` mentions:
- `@git/commit` - Create a commit
- `@planning/feature` - Plan a feature
- `@git/prepare-pull-request` - Prepare a PR

**How it works:**
1. Skills are loaded from `.cursor/skills/` or user skills folder
2. Core rules are loaded from `.cursorrules` in your project root
3. Type `@skill-name` in Chat/Composer to invoke a skill
4. The AI loads and follows the skill's instructions

### Quick Reference

**Claude Code CLI:**

| What you say | Skill used |
|--------------|------------|
| "plan this feature" | `planning/feature` |
| "plan this bugfix" | `planning/bugfix` |
| "commit these changes" | `git/commit` |
| "prepare a pull request" | `git/prepare-pull-request` |
| "review this PR" | `git/review-pull-request` |
| "create a test plan" | `testing/testplan` |
| "explore this code" | `exploration/explore-code` |

**Cursor IDE:**

| Command | Skill |
|---------|-------|
| `@planning/feature` | Plan a new feature |
| `@planning/bugfix` | Plan a bug fix |
| `@git/commit` | Create a commit |
| `@git/prepare-pull-request` | Prepare a PR |
| `@git/review-pull-request` | Review a PR |
| `@testing/testplan` | Create test plan |
| `@exploration/explore-code` | Explore code |

## Skill Categories

### Planning Skills

All planning skills extend `planning/base` which provides core planning phases.

| Skill | Use Case | Changelog | Tests |
|-------|----------|-----------|-------|
| `planning/feature` | New functionality | Required | Asks after completion |
| `planning/bugfix` | Fix broken behavior | Asks user | Asks for regression test |
| `planning/refactor` | Improve existing code | Asks user | Asks after completion |
| `planning/docs` | Documentation | No | No |
| `planning/architecture` | Architecture documentation | No | No |

### Programming Skills

Applied during implementation phase. For refactoring, ALL language-specific skills are mandatory.

#### C++ Skills

| Skill | Description |
|-------|-------------|
| `programming/cpp` | C++ Core Guidelines, C++17 features, performance, testability |
| `programming/cpp/design-patterns` | Suggests applicable patterns when code matches a problem |
| `programming/cpp/stl-algorithms` | Suggests STL algorithms to replace manual loops |
| `programming/cpp/naming-rules` | File/class naming conventions, folder structure = namespace |
| `programming/cmake-best-practices` | Modern CMake (3.15+), target-based approach |

#### Python Skills

| Skill | Description |
|-------|-------------|
| `programming/python` | PEP 8 style guide, type hints, modern Python 3.8+ best practices |

### Testing Skills

| Skill | Description |
|-------|-------------|
| `testing/testplan` | Create test plan files for developer verification and QA handoff |
| `testing/gtest-gmock` | GTest/GMock patterns for C++ testing, one-by-one implementation |
| `testing/pytest` | Pytest patterns for Python testing, fixtures, parametrization |

### Library Skills

| Skill | Description |
|-------|-------------|
| `libraries/amd-smi` | AMD SMI C++ library for GPU/CPU monitoring and management |

### Project Skills

| Skill | Description |
|-------|-------------|
| `rocprofsys` | ROCm Systems Profiler workflows - main entry point for configure/build/test |
| `rocprofsys-configure` | Configure rocprofiler-systems build with CMake presets |
| `rocprofsys-build` | Build, test, and install rocprofiler-systems |

### Git Skills

| Skill | Description |
|-------|-------------|
| `git/gh-client` | Core GitHub CLI operations - check availability, list/filter PRs, get details, check status (base skill) |
| `git/commit` | Create meaningful commits with well-structured messages |
| `git/prepare-pull-request` | Prepare PRs - size guidelines, splitting strategy, PR template |
| `git/review-pull-request` | Review PRs - code quality, correctness, tests, actionable feedback |
| `pr-review-interactive` | Walk through PR review findings one by one, accumulate inline comments in a PENDING review, submit at end |
| `git/pull-request-status` | Check PR CI/CD status, explain failures, provide fix recommendations |

### Exploration Skills

| Skill | Description |
|-------|-------------|
| `exploration/explore-code` | Systematic exploration of unfamiliar codebases before extraction |

### Radisha Skills

| Skill | Description |
|-------|-------------|
| `radisha/update` | Update radisha to latest version in current project |
| `radisha/help` | Full workflow reference and detailed rules |
| `radisha/create-skill` | Create new skills with validation and integration |
| `radisha/skills` | List all available skills with aliases |

### Code Quality Skills

| Skill | Description |
|-------|-------------|
| `code-smells` | Detect anti-patterns and refactoring opportunities based on refactoring.guru catalog |

### Other Skills

| Skill | Description |
|-------|-------------|
| `ask` | Questions without actions - explanations, clarifications |
| `watch` | Schedule a recurring poll of an external condition (PR merge, CI green, Jira state, background build); runs a follow-up action when met and self-stops |

## Key Concepts

### Step-by-Step Validation

After completing EACH implementation step that modifies code:

**1. Autonomous Verification First**

Before asking user, verify autonomously (if possible):
- Run relevant tests if they exist
- Check for linter errors
- Verify the change works as expected
- Note any issues found

**2. Then Ask User**

Present summary with verification results and options:

> "I've completed [step description].
>
> **Changes:**
> - [List of changes made]
>
> **Verification:**
> - All existing tests pass
> - No linter errors
>
> **Please review and choose:**
> 1. **Continue** - Implementation is good, proceed to next step
> 2. **Revert & Stop** - Revert to previous state and stop
> 3. **Improve** - Try to improve this implementation

### Re-planning When Things Go Wrong

If something goes sideways during implementation, **STOP and re-plan immediately**. Don't keep pushing forward hoping it will work out.

**When to stop and re-plan:**
- Multiple unexpected errors or failures
- The approach reveals unforeseen complexity
- Tests fail in ways that suggest the design is wrong
- You find yourself making "just one more fix" repeatedly

**How to re-plan:**
1. Stop current implementation
2. Document what went wrong and what was learned
3. Switch back to Plan Mode
4. Create a revised plan incorporating the new understanding
5. Get user confirmation before resuming

### Plan Persistence

Plans are saved to the `planning/` folder in your project root:

```
planning/
├── feature-user-avatar.md
├── bugfix-session-timeout.md
├── refactor-parser-module.md
└── docs-auth-flow.md
```

Benefits:
- **Resume work** - Continue from where you left off
- **Track progress** - `[x]` done vs `[ ]` pending
- **Reuse plans** - Similar requests can adapt existing plans

### Platform Tool Mapping

| Action | Claude Code | Cursor |
|--------|-------------|--------|
| Ask user question | `AskUserQuestion` tool | Built-in question UI |
| Create/track tasks | `TaskCreate`, `TaskUpdate`, `TaskList` | `TodoWrite` |
| Enter planning mode | `EnterPlanMode` tool | Switch to Plan Mode |
| Invoke skill | Natural language | `@skill-name` mention |

## Directory Structure

```
skills/
├── ask/                        # Questions without actions
│   └── SKILL.md
├── watch/                      # Recurring poll of an external condition; runs action on match and self-stops
│   └── SKILL.md
├── code-smells/                # Code smell detection catalog
│   └── SKILL.md
├── planning/                   # Planning skills (run first)
│   ├── base/                   # Shared planning rules (don't invoke directly)
│   │   └── SKILL.md
│   ├── feature/                # New feature planning
│   │   └── SKILL.md
│   ├── bugfix/                 # Bug fix planning
│   │   └── SKILL.md
│   ├── refactor/               # Refactoring planning
│   │   └── SKILL.md
│   ├── docs/                   # Documentation planning
│   │   └── SKILL.md
│   └── architecture/           # Architecture documentation
│       └── SKILL.md
├── programming/                # Implementation skills
│   ├── cpp/                    # C++ programming
│   │   ├── SKILL.md            # C++ Core Guidelines
│   │   ├── design-patterns/    # Design pattern suggestions
│   │   │   └── SKILL.md
│   │   ├── stl-algorithms/     # STL algorithm suggestions
│   │   │   └── SKILL.md
│   │   └── naming-rules/       # File/class naming conventions
│   │       └── SKILL.md
│   ├── python/                 # Python programming (PEP 8)
│   │   └── SKILL.md
│   └── cmake-best-practices/   # Modern CMake
│       └── SKILL.md
├── testing/                    # Testing skills
│   ├── testplan/               # Test plan creation for QA handoff
│   │   └── SKILL.md
│   ├── gtest-gmock/            # GTest/GMock for C++
│   │   └── SKILL.md
│   └── pytest/                 # Pytest for Python
│       └── SKILL.md
├── libraries/                  # Library-specific skills
│   └── amd-smi/                # AMD SMI library
│       └── SKILL.md
├── rocprofsys/                 # ROCm Systems Profiler project
│   └── SKILL.md                # Main entry point
├── rocprofsys-configure/       # Configure rocprofsys builds
│   └── SKILL.md
├── rocprofsys-build/           # Build rocprofsys project
│   └── SKILL.md
├── exploration/                # Code exploration skills
│   └── explore-code/           # Systematic codebase exploration
│       └── SKILL.md
├── git/                        # Git workflow skills
│   ├── commit/                 # Meaningful commit messages
│   │   └── SKILL.md
│   ├── prepare-pull-request/   # PR preparation guidelines
│   │   └── SKILL.md
│   └── review-pull-request/    # PR review guidelines
│       └── SKILL.md
├── pr-review-interactive/      # Walk PR review findings one by one, accumulate in PENDING review
│   └── SKILL.md
└── radisha/                    # Radisha management skills
    ├── update/                 # Update radisha to latest version
    │   └── SKILL.md
    ├── help/                   # Full workflow reference
    │   └── SKILL.md
    ├── create-skill/           # Create new skills with validation
    │   └── SKILL.md
    └── skills/                 # List all available skills
        └── SKILL.md
```

## Skill Details

### Planning Skills

#### `planning/base`
Shared planning rules - **do not invoke directly**. Provides:
- **Phase 0**: Check for existing plans in `planning/` folder
- **Phase 1**: Analyze (understand, scope, dependencies, risks)
- **Phase 2**: Assess PR scope (split if > 800 lines)
- **Phase 3**: Decompose into actionable steps
- **Phase 4**: Create task list
- **Phase 5**: Save plan to `planning/` folder (immediately after switching to Agent Mode)
- **Phase 6**: Optional confirmation for high-risk changes

#### `planning/feature`
For new functionality. Adds:
- **Changelog entry** - Required summary for CHANGELOG.md
- **Test consideration** - Asks about unit tests after completion

Plan file format: `planning/feature-<name>.md`

#### `planning/bugfix`
For fixing bugs. Adds:
- **Root cause analysis** - What, where, why, when
- **Changelog consideration** - Asks if user-facing
- **Regression test** - Asks about preventing recurrence

Plan file format: `planning/bugfix-<name>.md`

#### `planning/refactor`
For improving existing code without changing behavior. Adds:
- **Code smell detection** - Duplication, complexity, poor abstractions
- **Design pattern opportunities** - Strategy, Factory, Adapter, etc.
- **STL algorithm opportunities** - Replace loops with algorithms
- **Mandatory programming skills** - Must read ALL programming skills

Goals:
| Goal | Description |
|------|-------------|
| Best Practices | C++ Core Guidelines, modern C++17 |
| Reduce Duplication | DRY principle, extract common code |
| Improve Readability | Better naming, smaller functions |
| Testability | Dependency injection, policy-based design |
| Performance | Compile-time, cache-friendly |

Plan file format: `planning/refactor-<name>.md`

#### `planning/docs`
For documentation. No changelog, no tests.

Plan file format: `planning/docs-<name>.md`

#### `planning/architecture`
For architecture documentation. Produces iterative, user-guided documents describing component behavior, interactions, hierarchy, expansion points, and weaknesses. No code snippets -- prose and tables only.

**Process:**
1. Silent codebase analysis
2. Ask scope (single component / multiple components / whole system)
3. Present discovered components, ask what to cover
4. Propose chapter outline, ask user before generating
5. Generate ONE chapter at a time with user approval between each
6. Full document review after all chapters approved

Output file: `planning/architecture-<scope-name>.md`

### Programming Skills

#### `programming/cpp`
Comprehensive C++17 guidelines based on [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).

Key principles:
- **Compile-time execution is PRIORITY** - `constexpr`, `if constexpr`, templates
- **Performance is critical** - Zero-cost abstractions, cache-friendly
- **All code MUST be unit testable** - Dependency Injection or Policy-based design

Covers:
- Philosophy, Interfaces, Functions, Classes
- Resource Management (RAII, smart pointers)
- Error Handling (exceptions, RAII)
- Performance (allocations, copies, cache)
- Testability (DI, Policy-based design)
- Code Style (`const`, `constexpr`, `noexcept`, `[[nodiscard]]`)
- C++17 Features (what to use, what NOT to use)

#### `programming/cpp/design-patterns`
Reference from [Refactoring.Guru](https://refactoring.guru/design-patterns/cpp).

Actively suggests patterns when code matches a problem:
- **Creational**: Factory Method, Abstract Factory, Builder, Prototype, Singleton
- **Structural**: Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy
- **Behavioral**: Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor

#### `programming/cpp/stl-algorithms`
Suggests STL algorithms instead of manual loops:

| Manual Loop | STL Algorithm |
|-------------|---------------|
| Find element | `std::find`, `std::find_if` |
| Check condition | `std::any_of`, `std::all_of`, `std::none_of` |
| Count elements | `std::count`, `std::count_if` |
| Transform | `std::transform` |
| Accumulate | `std::accumulate`, `std::reduce` |
| Remove | `std::remove_if` + `erase` |
| Sort | `std::sort`, `std::stable_sort` |
| Min/Max | `std::min_element`, `std::max_element` |

Also covers container selection (vector vs map vs unordered_map, etc.)

#### `programming/cpp/naming-rules`
File and class naming conventions for C++:
- **Folder structure = namespace** - Don't repeat namespace prefixes in filenames
- **No redundant prefixes** - `amd_smi/driver.hpp` not `amd_smi/amd_smi_driver.hpp`
- **Class name = file name** - `driver.hpp` contains `class driver`
- **One class per file** (when practical)

Uses C++17 nested namespace syntax.

#### `programming/cmake-best-practices`
Modern CMake (3.15+) following official guidelines:
- Target-based approach (`target_*()` instead of global variables)
- Visibility keywords (`PUBLIC`, `PRIVATE`, `INTERFACE`)
- Generator expressions
- FetchContent for dependencies
- Proper install/export

#### `programming/python`
Python best practices based on [PEP 8](https://peps.python.org/pep-0008/).

Key principles:
- **Python 3.8+ standard** - Use modern features (dataclasses, type hints, walrus operator)
- **Type hints are REQUIRED** - All functions, methods, and class attributes must have type annotations
- **Readability counts** - Follow the Zen of Python (PEP 20)
- **All code MUST be unit testable** - Dependency injection, avoid global state

Covers:
- Naming conventions (PascalCase classes, snake_case functions/variables)
- Type annotations and mypy
- Exception handling
- Dataclasses and modern Python features
- Performance best practices
- Testability patterns

### Testing Skills

#### `testing/testplan`
Create test plan files that document what needs to be verified for a change.

**When to create:**
- After implementation is complete
- Before or alongside writing unit tests
- Before creating a Pull Request

**Test plan file:** `planning/testplan-<feature-name>.md`

Includes:
- Automated tests (unit/integration)
- Manual verification scenarios
- Regression checklist
- Notes for QA

#### `testing/gtest-gmock`
GTest/GMock patterns for C++ testing.

**Workflow:**
1. After feature/bugfix/refactor completion, ask about tests
2. Create test plan with:
   - Test cases for each function/class
   - Edge cases (boundaries, errors, state)
   - Required mocks
3. Write tests ONE BY ONE
4. **Wait for user approval after EACH test**
5. Only proceed to next test after approval

Covers:
- Test fixtures, parameterized tests
- Mock creation with GMock
- Matchers (value, string, container, pointer)
- Exception testing
- Edge case checklist
- Test naming conventions
- CMake configuration

#### `testing/pytest`
Pytest patterns for Python testing.

**Key principles:**
- **Tests MUST be isolated** - Each test independent, no execution order dependencies
- **Fixtures over setup/teardown** - Use pytest fixtures for test dependencies
- **Parametrize for data-driven tests** - Use `@pytest.mark.parametrize`
- **Test behavior, not implementation** - Focus on what code does, not how

Covers:
- Test discovery and naming conventions
- Fixtures (scope, autouse, factory patterns)
- Parametrization
- Mocking with `pytest-mock` and `unittest.mock`
- Markers and custom markers
- Async testing with `pytest-asyncio`
- Coverage configuration
- conftest.py organization

### Library Skills

#### `libraries/amd-smi`
AMD System Management Interface (SMI) library for GPU/CPU monitoring.

**Use when:**
- Working with AMD hardware monitoring
- GPU temperature, power, memory, clocks
- PCIe, XGMI topology
- Any `amdsmi.h` functions

Covers:
- Initialization and shutdown patterns
- Device handle hierarchy (socket → processor → GPU/CPU)
- GPU metrics (temperature, power, memory, clocks, utilization)
- PCIe information and XGMI links
- Error handling patterns
- Common pitfalls and best practices

### Project Skills

#### `rocprofsys`
Main entry point for ROCm Systems Profiler (rocprofiler-systems) workflows.

**Use when:**
- User asks about rocprofiler-systems or rocprof-sys
- User wants to configure, build, or work with the project
- User needs guidance on project structure or workflows

**Features:**
- Project overview and structure
- Workflow dispatcher (configure → build → test)
- CMake presets reference
- Common issues and troubleshooting
- Routes to specialized sub-skills

#### `rocprofsys-configure`
Configure rocprofiler-systems build with CMake presets and custom options.

**Use when:**
- Setting up build for first time
- Switching between debug/release builds
- Changing CMake options or dependencies

**Features:**
- Dynamic project location detection (supports git worktrees)
- CMake preset selection (ci, debug, release, debug-optimized)
- Dependency management (Dyninst, TBB, Boost, elfutils)
- Optional features (Python, MPI, PAPI)
- Build directory configuration

**Covers:**
- Monorepo structure awareness
- CMakePresets.json usage
- Building dependencies from source vs system packages
- Common configuration errors

#### `rocprofsys-build`
Build, test, and install rocprofiler-systems after configuration.

**Use when:**
- Project is already configured
- User wants to compile rocprofsys
- Running tests or installing

**Features:**
- Incremental and full builds
- Parallel build job optimization
- Test execution with CTest
- Installation to prefix
- Build error diagnosis

**Covers:**
- Memory-aware parallel builds
- Build error handling (OOM, dependencies, linker errors)
- Test result analysis
- Installation and environment setup

### Exploration Skills

#### `exploration/explore-code`
Systematic exploration of unfamiliar codebases before extraction.

**When to use:**
- Understanding code before extracting it into a library
- Learning how a database layer, API client, or subsystem works
- Preparing for refactoring by mapping dependencies

**The What/How/Where framework:**
1. **What is used** - Components, functions, resources
2. **How it is used** - Patterns, conditions, parameters
3. **Where to use it** - Call sites, contexts, triggers

**Output:** `planning/exploration-<topic>.md`

**Process:**
1. Scoping questions (mandatory)
2. Initial exploration with checkpoint
3. Deep dive with checkpoints per area
4. Synthesize and generate document

The exploration document feeds into `planning/feature` or `planning/refactor` skills.

### Git Skills

#### `git/gh-client`
Core GitHub CLI operations (base skill invoked by other git skills).

**Purpose:**
- ✅ Check if gh CLI is installed and authenticated
- 🔍 Search and filter pull requests
- 📋 Get PR details and metadata
- ✅ Check PR status checks and CI/CD results
- 📝 Create and manage pull requests

**Key capabilities:**
- Installation verification and setup instructions
- PR search by author, label, date, status
- Status check parsing (SUCCESS, FAILURE, PENDING, etc.)
- Workflow run logs retrieval
- GraphQL API access for complex queries

**Invoked by:**
- `git/prepare-pull-request` - Verify gh before creating PRs
- `git/review-pull-request` - Access PR data for reviews
- `git/pull-request-status` - Check CI/CD status and failures

#### `git/commit`
Create meaningful git commits with well-structured messages.

**Process:**
1. Analyze staged changes and understand purpose
2. Categorize commit type (feat, fix, refactor, etc.)
3. Draft commit message following conventional commits
4. Present to user for approval
5. Execute commit

**Message structure:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Key rules:**
- Subject line: imperative mood, max 50 chars, no period
- Body: explains WHY (72 char wrap)
- Footer: issue references, breaking changes

#### `git/prepare-pull-request`
Guidelines for creating reviewable Pull Requests.

**PR Size Guidelines:**
- **< 400 lines** - Ideal, easy to review
- **400-800 lines** - Acceptable
- **> 800 lines** - Must split

**When to Split:**
- Changes touch multiple unrelated systems
- Refactoring can be separated from features
- Infrastructure changes can land independently

**Every PR MUST have:**
1. **Motivation** - Why is this change needed?
2. **Technical Details** - What changed and how?
3. **Test Plan** - How was this tested?

#### `git/review-pull-request`
Structured approach to reviewing Pull Requests.

**Process:**
1. Ask user what to review (GitHub PR or local changes)
2. Invoke `git/gh-client` to verify gh availability (if GitHub PR selected)
3. Gather PR info (description, files, commits)
4. Understand the change (goal, scope, type)
5. Load relevant programming skills for the languages in the PR
6. Review across dimensions (correctness, best practices, tests, security, design)
7. Summarize with categorized issues

**Review options:**
- **GitHub PR** - Review specific PR by number/URL (requires gh CLI)
- **Local changes** - Review changes in current directory vs branch (git only)

**Issue Categories:**
- **Must Fix** - Blocking issues (bugs, security, missing tests)
- **Should Fix** - Non-blocking improvements
- **Nitpicks** - Optional suggestions

#### `pr-review-interactive`
Walk through PR review findings one by one with the user before any comment lands on GitHub.

**Process:**
1. Resolve PR (URL or owner/repo#N), fetch head SHA
2. Generate report via `pr-review` skill (or reuse existing)
3. Parse findings into ordered list (Must-Fix -> Should-Fix -> Nits)
4. Create empty PENDING review on PR
5. For each finding: show location + analysis + proposed short inline comment; user picks accept / edit / skip / quit
6. Append accepted comments to the PENDING review (one batch)
7. Wrap-up: user picks COMMENT / REQUEST_CHANGES / APPROVE / keep pending / discard
8. Submit (or hold) review with chosen event

**Key rules:**
- Never auto-submit (review stays PENDING until explicit user confirmation)
- Never use `gh pr comment` (silently drops body on Projects-classic orgs)
- Comments are 1-3 sentences, root cause first, fix snippet only when non-obvious
- State persisted under `$CLAUDE_JOB_DIR/pr-review-interactive/` for resume

**State files:** `head-sha.txt`, `review-id.txt`, `findings.json`, `diff-lines.json`, `accepted.json`, `skipped.json`

#### `git/pull-request-status`
Check pull request CI/CD status and explain failures with actionable fixes.

**Process:**
1. Invoke `git/gh-client` to verify gh availability
2. Get PR number (from user or auto-detect current branch)
3. Fetch all status checks (CI/CD, tests, linting)
4. Analyze failures and errors
5. Fetch detailed logs for failed checks
6. Explain failures in plain English
7. Provide fix recommendations

**Status checks:**
- ✅ **SUCCESS** - Check passed
- ❌ **FAILURE** - Check failed (investigate required)
- ⚠️ **ERROR** - Check encountered error
- 🔄 **PENDING** - Check still running
- ⏭️ **SKIPPED** - Check was skipped
- ⏱️ **TIMED_OUT** - Check timed out

**Report includes:**
- Overall merge readiness
- Summary of all checks (passed/failed/pending)
- Detailed failure explanations with error messages
- Recommended fixes for each failure
- Review and merge conflict status

### Radisha Skills

#### `radisha/help`
Full workflow reference with detailed rules for using radisha effectively.

#### `radisha/create-skill`
Meta-skill for creating new radisha skills with validation and integration.

**Process:**
1. User provides skill content
2. AI analyzes for usefulness, alignment, and conflicts
3. AI presents findings and suggests fixes
4. User approves
5. AI creates skill and integrates with radisha

**What it checks:**
- Usefulness (structure, triggers, anti-patterns)
- Alignment with existing skills
- Conflicts/overlaps with other skills
- Consistency (tool names, formatting, conventions)

**What it updates:**
- Creates `skills/[category]/[name]/SKILL.md`
- Updates `radisha/help` skill
- Updates `README.md` (tables, details, directory tree)
- Updates related skills if disambiguation needed

#### `radisha/update`
Update radisha to the latest version by pulling from the git repository.

#### `radisha/skills`
List all available skills with their descriptions and command aliases.

### Code Quality Skills

#### `code-smells`
Comprehensive catalog of code smells for detecting anti-patterns and identifying refactoring opportunities. Based on the [Refactoring.Guru Code Smells Catalog](https://refactoring.guru/refactoring/smells).

**Categories covered (22 smells total):**

| Category | Smells |
|----------|--------|
| Bloaters | Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps |
| Object-Orientation Abusers | Switch Statements, Temporary Field, Refused Bequest, Alternative Classes with Different Interfaces |
| Change Preventers | Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies |
| Dispensables | Comments, Duplicate Code, Lazy Class, Data Class, Dead Code, Speculative Generality |
| Couplers | Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man, Incomplete Library Class |

**Severity levels:**
- Critical (100): Causes bugs, crashes, security issues
- Must Fix (80): Significantly harms maintainability
- Should Fix (50): Reduces code quality
- Nitpick (20): Minor improvement opportunity

**Key thresholds:**
- Long Method: >50 lines (Should Fix), >100 lines (Must Fix)
- Large Class: >500 lines (Should Fix), >1000 lines (Must Fix)
- Long Parameter List: >4 params (Should Fix), >6 params (Must Fix)
- Deep Nesting: >3 levels (Should Fix), >5 levels (Must Fix)

**Used by:**
- `pr-review` Agent 3 (Code Smells Agent)
- `planning-refactor` for identifying improvement targets

## Contributing

1. Create a folder under appropriate category
2. Add `SKILL.md` with frontmatter (name, description)
3. Write detailed, actionable instructions
4. Test the skill before committing
5. Submit a pull request

## Resources

### C++
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Refactoring.Guru - Design Patterns](https://refactoring.guru/design-patterns/cpp)
- [CppReference](https://en.cppreference.com/)
- [GoogleTest Documentation](https://google.github.io/googletest/)
- [Modern CMake](https://cliutils.gitlab.io/modern-cmake/)

### Python
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 20 - Zen of Python](https://peps.python.org/pep-0020/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)

### AMD
- [AMD SMI Documentation](https://rocm.docs.amd.com/projects/amdsmi/en/latest/)

### Tools
- [Cursor Skills Documentation](https://cursor.com/docs/context/skills)
