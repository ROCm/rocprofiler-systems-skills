# Radisha - Cursor Skills Repository

A comprehensive skills system for AI-assisted software development (C++, Python, and more). Skills are reusable AI behavior definitions that standardize and automate development workflows.

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
5. Track progress using platform's task tracking tool
6. Execute step-by-step with verification and user validation
7. Offer unit tests after completion

### Plan Mode Workflow

**Complete planning phases before implementation:**

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

This ensures plans persist in files and can be resumed later.

### English Output

All output is in English, regardless of input language. This ensures consistency across documentation, plans, code comments, and conversations.

## Complete Workflow

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
                           │                │
                           ▼                ├── feature ──→ planning/feature
                       RESPOND              ├── bugfix ───→ planning/bugfix
                                           ├── refactor ─→ planning/refactor
                                           └── docs ─────→ planning/docs
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
                                    │  - Create TodoWrite list      │
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

## Skill Categories

### Entry Point

| Skill | Description |
|-------|-------------|
| `using-radisha` | **Start here.** Defines how to use all skills, workflow rules, validation process |

### Planning Skills

All planning skills extend `planning/base` which provides core planning phases.

| Skill | Use Case | Changelog | Tests |
|-------|----------|-----------|-------|
| `planning/feature` | New functionality | Required | Asks after completion |
| `planning/bugfix` | Fix broken behavior | Asks user | Asks for regression test |
| `planning/refactor` | Improve existing code | Asks user | Asks after completion |
| `planning/docs` | Documentation | No | No |

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

Domain-specific knowledge for working with specific libraries and APIs.

| Skill | Description |
|-------|-------------|
| `libraries/amd-smi` | AMD SMI C++ library for GPU/CPU monitoring and management |

### Git Skills

| Skill | Description |
|-------|-------------|
| `git/pull-request` | PR planning, size guidelines, splitting strategy, PR template |

### Radisha Skills

| Skill | Description |
|-------|-------------|
| `radisha/update` | Update radisha to latest version in current project |

### Exploration Skills

| Skill | Description |
|-------|-------------|
| `exploration/explore-code` | Systematic exploration of unfamiliar codebases before extraction |

### Other Skills

| Skill | Description |
|-------|-------------|
| `ask` | Questions without actions - explanations, clarifications |

## Skill Details

### Planning Skills

#### `planning/base`
Shared planning rules - **do not invoke directly**. Provides:
- **Phase 0**: Check for existing plans in `planning/` folder
- **Phase 1**: Analyze (understand, scope, dependencies, risks)
- **Phase 2**: Assess PR scope (split if > 800 lines)
- **Phase 3**: Decompose into actionable steps
- **Phase 4**: Create TodoWrite list
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

#### `git/pull-request`
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

**Integration with Planning:**
- PR scope is assessed during Phase 2 of planning
- Large tasks are split into multiple PRs upfront
- Each PR is planned as a logical, reviewable unit

## Step-by-Step Validation

After completing EACH implementation step that modifies code:

### 1. Autonomous Verification First

Before asking user, verify autonomously (if possible):
- Run relevant tests if they exist
- Check for linter errors
- Verify the change works as expected
- Note any issues found

### 2. Then Ask User

Present summary with verification results and options:

> "I've completed [step description].
>
> **Changes:**
> - [List of changes made]
>
> **Verification:**
> - ✅ All existing tests pass
> - ✅ No linter errors
>
> **Please review and choose:**
> 1. ✅ **Continue** - Implementation is good, proceed to next step
> 2. ⬅️ **Revert & Stop** - Revert to previous state and stop
> 3. 🔄 **Improve** - Try to improve this implementation

## Re-planning When Things Go Wrong

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

## Subagent Strategy

Use subagents liberally to keep the main context window clean and focused.

**When to use subagents:**
- Research and exploration tasks
- Parallel analysis of multiple files/components
- Complex problems that benefit from more compute
- Tasks that can be isolated and delegated

**Subagent rules:**
| Rule | Description |
|------|-------------|
| One task per subagent | Keep execution focused |
| Offload research | Don't clutter main context with exploration |
| Parallel analysis | Spin up multiple subagents for independent investigations |
| Clear handoff | Provide subagent with all necessary context upfront |

**Example use cases:**
- "Explore how authentication works in this codebase" → subagent
- "Find all usages of deprecated API" → subagent
- "Analyze performance of these 3 modules" → 3 parallel subagents

## Elegance Check

For non-trivial changes, pause before completing and ask: "Is there a more elegant way?"

**When to apply:**
- Changes that affect multiple files
- New abstractions or patterns being introduced
- Refactoring existing code
- Architectural decisions

**Skip this for:**
- Simple, obvious fixes
- One-line changes
- Typo corrections
- Config updates

**If a fix feels hacky:**
> "Knowing everything I know now, is there a more elegant solution?"

Challenge your own work before presenting it to the user.

## Plan Persistence

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

## Directory Structure

```
skills/
├── using-radisha/              # Entry point - how to use all skills
│   └── SKILL.md
├── ask/                        # Questions without actions
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
│   └── docs/                   # Documentation planning
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
├── exploration/                # Code exploration skills
│   └── explore-code/           # Systematic codebase exploration
│       └── SKILL.md
├── git/                        # Git workflow skills
│   └── pull-request/           # PR creation guidelines
│       └── SKILL.md
└── radisha/                    # Radisha management skills
    └── update/                 # Update radisha to latest version
        └── SKILL.md
```

## How to Use

### In Claude Code

1. Add skills to your project's `skills/` directory or `~/.claude/skills/` for global access
2. Use the `Skill` tool to invoke skills by name (e.g., `planning/feature`)
3. **Fallback:** If skills are not found, manually read from `~/.claude/skills/` using the `Read` tool

### In Cursor

1. Add skills to your project's `.cursor/skills/` directory or user skills folder
2. In Chat/Composer, type `@skill-name` to invoke a skill
3. The AI loads and follows the skill's instructions

### Platform Tool Mapping

| Action | Claude Code | Cursor |
|--------|-------------|--------|
| Ask user question | `AskUserQuestion` tool | Built-in question UI |
| Create/track tasks | `TaskCreate`, `TaskUpdate`, `TaskList` | `TodoWrite` |
| Enter planning mode | `EnterPlanMode` tool | Switch to Plan Mode |
| Invoke skill | `Skill` tool | `@skill-name` mention |

### Adding from GitHub

```
https://github.com/adjordje-amd/radisha
```

Or link to specific skill:
```
https://github.com/adjordje-amd/radisha/blob/main/skills/planning/feature/SKILL.md
```

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
