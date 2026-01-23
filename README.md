# Radisha - Cursor Skills Repository

A comprehensive skills system for AI-assisted C++ development. Skills are reusable AI behavior definitions that standardize and automate development workflows.

## Philosophy

### Planning First, Always

**Every non-trivial task starts with planning.** The AI must:

1. Analyze the request and identify scope
2. Create a structured plan with tasks
3. Save the plan to `planning/` folder (persistence)
4. Track progress using TodoWrite
5. Execute step-by-step with user validation
6. Offer unit tests after completion

### Stay in Agent Mode

**Never switch to Plan mode.** Always stay in Agent mode and use planning skills. This ensures:
- Full tool access during planning AND execution
- Plans persist in files (can resume later)
- Single continuous workflow

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
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 1: PLANNING            │
                                    │  - Analyze scope & risks      │
                                    │  - Assess PR scope (split?)   │
                                    │  - Decompose into tasks       │
                                    │  - Save plan to planning/     │
                                    └───────────────────────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────────┐
                                    │  PHASE 2: IMPLEMENTATION      │
                                    │  - Load programming skills    │
                                    │  - Execute step by step       │
                                    │  - Ask validation each step   │
                                    │  - Mark progress in plan      │
                                    └───────────────────────────────┘
                                                    │
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

Applied during implementation phase. For refactoring, ALL are mandatory.

| Skill | Description |
|-------|-------------|
| `programming/cpp` | C++ Core Guidelines, C++17 features, performance, testability |
| `programming/cpp/design-patterns` | Suggests applicable patterns when code matches a problem |
| `programming/cpp/stl-algorithms` | Suggests STL algorithms to replace manual loops |
| `programming/cmake-best-practices` | Modern CMake (3.15+), target-based approach |

### Testing Skills

| Skill | Description |
|-------|-------------|
| `testing/unit-tests` | GTest/GMock patterns, test planning, one-by-one implementation |

### Git Skills

| Skill | Description |
|-------|-------------|
| `git/pull-request` | PR planning, size guidelines, splitting strategy, PR template |

### Radisha Skills

| Skill | Description |
|-------|-------------|
| `radisha/update` | Update radisha to latest version in current project |

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
- **Phase 2**: Decompose into actionable steps
- **Phase 3**: Create TodoWrite list
- **Phase 4**: Save plan to `planning/` folder
- **Phase 5**: Optional confirmation for high-risk changes

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

#### `programming/cmake-best-practices`
Modern CMake (3.15+) following official guidelines:
- Target-based approach (`target_*()` instead of global variables)
- Visibility keywords (`PUBLIC`, `PRIVATE`, `INTERFACE`)
- Generator expressions
- FetchContent for dependencies
- Proper install/export

### Testing Skills

#### `testing/unit-tests`
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

After completing EACH implementation step, present options:

> "I've completed [step description].
>
> **Please review and choose:**
> 1. ✅ **Continue** - Implementation is good, proceed to next step
> 2. ⬅️ **Revert & Stop** - Revert to previous state and stop
> 3. 🔄 **Improve** - Try to improve this implementation
>
> Which option?"

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
│   ├── cpp/                    # C++ Core Guidelines
│   │   ├── SKILL.md
│   │   ├── design-patterns/    # Design pattern suggestions
│   │   │   └── SKILL.md
│   │   └── stl-algorithms/     # STL algorithm suggestions
│   │       └── SKILL.md
│   └── cmake-best-practices/   # Modern CMake
│       └── SKILL.md
├── testing/                    # Testing skills
│   └── unit-tests/             # GTest/GMock
│       └── SKILL.md
├── git/                        # Git workflow skills
│   └── pull-request/           # PR creation guidelines
│       └── SKILL.md
└── radisha/                    # Radisha management skills
    └── update/                 # Update radisha to latest version
        └── SKILL.md
```

## How to Use

### In Cursor

1. Add skills to your project's `.cursor/skills/` directory or user skills folder
2. In Chat/Composer, type `@skill-name` to invoke a skill
3. The AI loads and follows the skill's instructions

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

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Refactoring.Guru - Design Patterns](https://refactoring.guru/design-patterns/cpp)
- [CppReference](https://en.cppreference.com/)
- [GoogleTest Documentation](https://google.github.io/googletest/)
- [Modern CMake](https://cliutils.gitlab.io/modern-cmake/)
- [Cursor Skills Documentation](https://cursor.com/docs/context/skills)
