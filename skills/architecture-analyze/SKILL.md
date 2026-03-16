---
name: architecture-analyze
description: Analyze architectural changes - review module boundaries, dependencies, testability, and suggest simplifications. Used by pr-review and planning skills.
---

# Architecture Analyze Skill

Analyze proposed architectural changes or validate designs before implementation.

<IMPORTANT>
This skill:
1. **Reads memory first** - Check what you already know about this codebase's architecture
2. **Spawns an Explore agent** - Only for areas not covered by memory
3. **Updates memory after** - Persist new architectural knowledge for future reviews

Memory location: `~/.claude/projects/<project>/memory/agents/architecture.md`
</IMPORTANT>

## When to Use

| Context | Trigger |
|---------|---------|
| **PR Review** | Invoked by `pr-review` when architectural changes detected |
| **Planning** | Invoked by `planning-feature` to validate design before coding |
| **Standalone** | User asks to analyze architecture of proposed changes |

## Detecting Architectural Changes

Invoke this skill when PR/changes include:

| Signal | Example |
|--------|---------|
| New directories | `src/new_module/` created |
| New/changed interfaces | Abstract class added, virtual methods changed |
| Factory/DI changes | Object creation patterns modified |
| New CMake targets | `add_library(new_component ...)` |
| Cross-module changes | 5+ files across different directories |
| New dependencies | External library added |
| Base class changes | Core/foundation classes modified |

## Analysis Process

```
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 0: Read Architecture Memory                │
│         Load existing knowledge about this codebase              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 1: Explore (if needed)                     │
│         Spawn Explore agent only for unknown areas               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 2: Analyze Module Boundaries               │
│         Where does new code belong? Proper separation?           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 3: Analyze Dependencies                    │
│         Direction correct? Cycles? Coupling level?               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 4: Assess Testability                      │
│         Isolation possible? Dependencies injectable?             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 5: Simplicity Check                        │
│         Over-engineered? Simpler alternative exists?             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 6: Generate Report                         │
│         Findings, concerns, recommendations                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Phase 7: Update Architecture Memory              │
│         Persist new knowledge for future reviews                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 0: Read Architecture Memory

**Before exploring, check what you already know:**

```bash
# Memory file location
~/.claude/projects/<project>/memory/agents/architecture.md
```

**If memory exists:**
1. Read the memory file
2. Check if relevant modules are already documented
3. Only explore areas NOT covered by memory
4. Use memory to provide context for new analysis

**If memory doesn't exist:**
1. Proceed to full exploration (Phase 1)
2. Create memory file after analysis

## Phase 1: Explore Existing Architecture

**Spawn an Explore agent** with thoroughness "medium" or "very thorough":

```
Prompt for Explore agent:
"Analyze the existing architecture of this codebase focusing on:
1. Module/directory structure and their responsibilities
2. Key interfaces and abstract classes
3. Dependency patterns (how modules connect)
4. Factory/creation patterns used
5. How similar features were implemented before

Context: [describe the proposed changes or feature]

Return:
- Module map with responsibilities
- Key abstractions and interfaces
- Dependency graph (which modules depend on which)
- Patterns used for similar features"
```

### What to Learn

| Aspect | Questions to Answer |
|--------|---------------------|
| **Module structure** | What are the main modules? What does each do? |
| **Boundaries** | Where are the clear separation points? |
| **Interfaces** | What abstractions exist? How are they used? |
| **Dependencies** | How do modules communicate? Direct or via interfaces? |
| **Patterns** | What patterns are used? Factory? Strategy? Observer? |
| **Conventions** | How were similar features added before? |

## Phase 2: Analyze Module Boundaries

### Check Placement

| Question | Good | Bad |
|----------|------|-----|
| Is code in the right module? | Feature X in `features/x/` | Feature X scattered across unrelated modules |
| Single responsibility? | Module does one thing well | Module handles multiple unrelated concerns |
| Clear boundaries? | Well-defined public API | Internal details exposed everywhere |

### Boundary Violations

Look for:
- Code that should be in a different module
- Module doing too many things
- Missing module that should exist
- Duplicate functionality across modules

### Report Format

```markdown
### Module Boundary Analysis

**Proposed location:** `src/module_name/`

**Assessment:** [Appropriate / Needs Discussion / Wrong Location]

**Findings:**
- [Finding 1]
- [Finding 2]

**Recommendation:** [Where code should go and why]
```

## Phase 3: Analyze Dependencies

### Dependency Direction

```
Good: High-level → Low-level
      UI → Business Logic → Data Access

Bad:  Low-level → High-level (inverted)
      Data Access → Business Logic
```

### Check for Issues

| Issue | How to Detect | Impact |
|-------|---------------|--------|
| **Circular dependency** | A → B → C → A | Build issues, tight coupling |
| **Wrong direction** | Core depends on feature | Core becomes unstable |
| **Missing abstraction** | Concrete class dependency | Hard to test, rigid |
| **Over-coupling** | Module depends on 10+ others | Fragile, hard to change |

### Dependency Analysis Commands

```bash
# For C++ - find includes from changed files
grep -r "#include" <changed_files> | grep -v "test"

# For Python - find imports
grep -r "^import\|^from" <changed_files>

# Visualize with existing tools if available
# cmake --graphviz=deps.dot build/
```

### Report Format

```markdown
### Dependency Analysis

**New dependencies introduced:**
- `module_a` → `module_b` (via `InterfaceX`)
- `module_a` → `external_lib`

**Dependency direction:** [Correct / Inverted / Needs Abstraction]

**Circular dependencies:** [None found / Found: A → B → A]

**Coupling assessment:** [Low / Medium / High]

**Concerns:**
- [Concern 1]

**Recommendations:**
- [How to fix dependency issues]
```

## Phase 4: Assess Testability

### Testability Criteria

| Criterion | Testable | Not Testable |
|-----------|----------|--------------|
| **Dependencies** | Injected via constructor/interface | Hard-coded, global state |
| **Side effects** | Isolated, controllable | File I/O, network in core logic |
| **State** | Explicit, observable | Hidden, implicit |
| **Interfaces** | Abstract, mockable | Concrete classes only |

### Questions to Answer

1. **Can this be unit tested in isolation?**
   - Are dependencies injectable?
   - Can we mock collaborators?

2. **What's the mocking complexity?**
   - How many mocks needed?
   - Are mocks simple or complex?

3. **Are there test-hostile patterns?**
   - Singletons?
   - Static methods with side effects?
   - Global state?

### Report Format

```markdown
### Testability Assessment

**Can be unit tested in isolation:** [Yes / Partially / No]

**Dependencies:**
| Dependency | Injectable? | Mockable? |
|------------|-------------|-----------|
| `DatabaseClient` | Yes (constructor) | Yes (interface) |
| `Logger` | No (global) | No |

**Mocking complexity:** [Low / Medium / High]
- Mocks needed: [count]
- Complex mocks: [list]

**Test-hostile patterns found:**
- [Pattern and location]

**Recommendations:**
- [How to improve testability]
```

## Phase 5: Simplicity Check

### Over-Engineering Signals

| Signal | Example |
|--------|---------|
| **Premature abstraction** | Interface with single implementation, no plans for more |
| **Unnecessary indirection** | Factory that creates one type, never extended |
| **Speculative generality** | "We might need this later" code |
| **Gold plating** | Features beyond requirements |
| **Pattern overuse** | Design pattern where simple code works |

### Questions to Ask

1. **What's the simplest solution that works?**
   - Can this be a function instead of a class?
   - Can this be one class instead of three?

2. **Is the abstraction earning its keep?**
   - Does the interface have multiple implementations?
   - Will it realistically be extended?

3. **YAGNI check**
   - Is this solving a current problem or a hypothetical one?
   - What's the cost of adding this later if needed?

### Simpler Alternatives

For each abstraction/pattern, consider:

| Current | Alternative | When to Prefer Alternative |
|---------|-------------|---------------------------|
| Abstract factory | Simple factory function | Single product family |
| Strategy pattern | Switch statement | 2-3 strategies, won't grow |
| Observer pattern | Direct callback | Single observer |
| Dependency injection | Direct instantiation | Leaf classes, no testing need |

### Report Format

```markdown
### Simplicity Check

**Over-engineering concerns:**
- [Concern 1: what and why]
- [Concern 2: what and why]

**Simpler alternatives:**

| Current Approach | Simpler Alternative | Recommendation |
|------------------|---------------------|----------------|
| [What's proposed] | [Simpler option] | [Keep / Simplify] |

**YAGNI violations:**
- [Code that solves hypothetical problems]

**Verdict:** [Appropriate complexity / Over-engineered / Under-engineered]
```

## Phase 6: Generate Report

### Full Architecture Review Report

```markdown
# Architecture Review

## Summary

**Scope:** [PR #X / Feature Y planning]

**Verdict:** [Approve / Concerns / Needs Rework]

**Key findings:**
- [1-3 bullet summary]

---

## 1. Existing Architecture Context

[Summary from Explore agent]

- **Relevant modules:** [list]
- **Key interfaces:** [list]
- **Patterns used:** [list]

---

## 2. Module Boundaries

**Assessment:** [Appropriate / Needs Discussion / Wrong Location]

[Details from Phase 2]

---

## 3. Dependencies

**Assessment:** [Clean / Minor Issues / Major Issues]

[Details from Phase 3]

---

## 4. Testability

**Assessment:** [Good / Acceptable / Poor]

[Details from Phase 4]

---

## 5. Simplicity

**Assessment:** [Appropriate / Over-engineered / Under-engineered]

[Details from Phase 5]

---

## Recommendations

### Must Address (Blocking)

1. [Critical architectural issue]

### Should Address (Non-blocking)

1. [Important improvement]

### Consider (Optional)

1. [Nice-to-have suggestion]

---

## Questions for Author

- [Clarifying questions about design decisions]
```

## Phase 7: Update Architecture Memory

**After completing analysis, update your memory:**

```markdown
# Architecture Memory

## Project: [project name]
Last updated: [date]

## Module Map
<!-- List all discovered modules and their responsibilities -->

| Module | Responsibility | Key Files |
|--------|----------------|-----------|
| src/core/ | Core business logic | core.cpp, engine.cpp |
| src/api/ | External API layer | handler.cpp, router.cpp |

## Key Interfaces
<!-- Important abstractions that define boundaries -->

- `IProcessor` - Main processing interface (src/core/processor.h)
- `IStorage` - Storage abstraction (src/storage/storage.h)

## Dependency Patterns
<!-- How modules connect to each other -->

```
api/ → core/ → storage/
     ↘ utils/
```

## Architectural Decisions
<!-- Design choices and their rationale -->

- **Why X instead of Y**: [reason]
- **Pattern used for Z**: [pattern and why]

## Known Issues
<!-- Architectural debt or areas needing improvement -->

- Circular dependency between X and Y
- Core module is getting too large
```

**Memory update rules:**
1. Only add confirmed patterns (not speculation)
2. Update existing entries if they change
3. Remove outdated information
4. Keep memory concise and useful

## Integration with Other Skills

### From pr-review

```markdown
pr-review detects architectural changes:
  → Invoke architecture-analyze
  → Include architecture report in PR review
  → Architectural issues become "Must Fix" items
  → Memory is updated with new architectural knowledge
```

### From planning-feature

```markdown
planning-feature validates design:
  → Invoke architecture-analyze with proposed design
  → Catch issues before coding starts
  → Adjust plan based on findings
  → Memory helps understand existing architecture faster
```

## Quick Architecture Checklist

For fast reviews, at minimum verify:

- [ ] Code is in the appropriate module
- [ ] No circular dependencies introduced
- [ ] Dependencies go in the right direction (high → low level)
- [ ] New code can be unit tested
- [ ] No obvious over-engineering

## References

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [YAGNI](https://martinfowler.com/bliki/Yagni.html)
