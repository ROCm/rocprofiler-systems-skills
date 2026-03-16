---
name: radisha-improve-skill
description: Automatically detect and improve skills when gaps are noticed during work - proactively proposes updates
---

# Improve Skill

**Proactive skill improvement.** When you notice a gap in a skill during work, this skill automatically:
1. Detects which skill is responsible
2. Drafts an improvement
3. Proposes the update to the user

<IMPORTANT>
**This skill should be invoked AUTOMATICALLY when:**
- You're using a skill and notice it's missing something
- A pattern/rule you need isn't documented
- The skill gave incorrect or incomplete guidance
- You had to figure something out that should be in the skill

**DO NOT wait for the user to ask.** Propose improvements immediately.
</IMPORTANT>

## Automatic Detection

### How to Detect the Responsible Skill

When you notice a gap, identify the skill by:

| Signal | Responsible Skill |
|--------|-------------------|
| Currently loaded skill (via Skill tool) | That skill |
| Agent prompt references a skill | That skill |
| Task type matches a skill category | See mapping below |
| Pattern/rule domain | Domain-specific skill |

### Task-to-Skill Mapping

| Task You're Doing | Likely Responsible Skill |
|-------------------|-------------------------|
| PR review, code quality | `pr-review`, `code-smells`, `static-analysis` |
| C++ implementation | `programming-cpp`, `programming-cpp-design-patterns` |
| Python implementation | `programming-python` |
| CMake work | `programming-cmake-best-practices` |
| Planning features | `planning-feature`, `planning-base` |
| Architecture analysis | `architecture-analyze` |
| Writing tests (C++) | `testing-gtest-gmock` |
| Writing tests (Python) | `testing-pytest` |
| Git operations | `git-commit`, `git-prepare-pull-request` |
| AMD SMI code | `library-amd-smi` |
| Debugging profiler | `debugging-rocprof-sys` |

### Gap Detection Triggers

Automatically propose improvement when:

```
IF (using skill X) AND (any of these occur):
  - You need a rule that doesn't exist
  - The skill's threshold seems wrong for this case
  - A pattern you encountered isn't documented
  - You found a better way to do something
  - The skill's guidance was incomplete
  - You had to look up something externally
THEN:
  - Invoke this skill
  - Propose the improvement
```

## Automatic Process

```
┌─────────────────────────────────────────────────────────────────┐
│     AUTOMATIC: Gap Detected During Work                         │
│   "I need X but the skill doesn't cover it"                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│     AUTOMATIC: Identify Responsible Skill                        │
│   Use task-to-skill mapping + context                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│     AUTOMATIC: Draft Improvement Proposal                        │
│   Match skill style, find right section                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│     PROPOSE TO USER                                              │
│   "I noticed X is missing from skill Y. Add this?"              │
└─────────────────────────────────────────────────────────────────┘
                          │           │
                         no          yes
                          │           │
                          ▼           ▼
                    ┌─────────┐ ┌───────────────────────┐
                    │Continue │ │ Apply + Report        │
                    │ work    │ └───────────────────────┘
                    └─────────┘
```

## Proposal Format

When proposing an improvement to the user, use this format:

```markdown
---
**Skill Improvement Detected**

**Skill:** `[skill-name]`
**Gap:** [What's missing or wrong]
**Context:** [How you discovered this]

**Proposed Addition:**

[Show the exact content to add, in skill's style]

**Location:** [Section where it would go]

---
Apply this improvement? (y/n)
```

### Example Proposal

```markdown
---
**Skill Improvement Detected**

**Skill:** `code-smells`
**Gap:** Missing "Parallel Inheritance Hierarchies" detection criteria
**Context:** During PR review, found this smell but skill didn't have clear thresholds

**Proposed Addition:**

### Parallel Inheritance Hierarchies

**Detection:**
- Every time you create a subclass of one class, you need to create a subclass of another
- Prefixes in class names match across hierarchies (e.g., `PhoneDevice`/`PhoneDialer`)

**Severity:** Should Fix (50)

**Location:** Category 3: Change Preventers section

---
Apply this improvement? (y/n)
```

## Phase 1: Locate the Skill

Skills can be in multiple locations:

| Location | Path | Priority |
|----------|------|----------|
| Global skills | `~/.claude/skills/<skill-name>/SKILL.md` | Check first |
| Radisha project | `~/work/radisha/skills/<skill-name>/SKILL.md` | Primary source |
| Current project | `./skills/<skill-name>/SKILL.md` | Project-specific |

**To find a skill:**

```bash
# Check global skills (symlinked from radisha)
ls -la ~/.claude/skills/<skill-name>/

# Find the actual source
readlink -f ~/.claude/skills/<skill-name>/SKILL.md
```

**Always edit the source file** in radisha project, not the symlink.

## Phase 2: Analyze Current Content

Before making changes:

1. **Read the full skill** - understand its structure and style
2. **Identify the section** where your addition belongs
3. **Check for conflicts** - does your addition contradict existing content?
4. **Match the style** - use same formatting (tables, code blocks, etc.)

### Skill Structure (typical)

```markdown
---
name: skill-name
description: ...
---

# Skill Title

<IMPORTANT> key rules </IMPORTANT>

## When to Use
## Process/Phases
## Detailed Instructions
## Common Mistakes (if applicable)
## References
```

## Phase 3: Draft Improvement

### Types of Improvements

| Type | What to Add | Where |
|------|-------------|-------|
| **Missing rule** | New check or guideline | Appropriate phase/section |
| **Missing pattern** | New detection criteria | Pattern/detection section |
| **Better example** | Code snippet or scenario | Examples section |
| **Clarification** | Explanation of edge case | Related rule section |
| **New trigger** | When skill should activate | "When to Use" section |
| **Threshold adjustment** | Different numeric value | Threshold/criteria section |

### Writing Guidelines

1. **Be concise** - skills should be scannable
2. **Use tables** - easier to read than paragraphs
3. **Include examples** - show, don't just tell
4. **Add rationale** - explain WHY, not just WHAT
5. **Match existing tone** - consistent style throughout

### Improvement Template

```markdown
## [Section Name]

### [New Rule/Pattern Name]

**Why:** [Brief rationale]

**Detection:**
- [Criteria 1]
- [Criteria 2]

**Example:**
```code
// Bad
[bad example]

// Good
[good example]
```

**Severity:** [Critical/Must Fix/Should Fix/Nitpick]
```

## Phase 4: Apply Change

### Edit Checklist

- [ ] Found the source file (not symlink)
- [ ] Read surrounding context
- [ ] Matched existing style
- [ ] Added to appropriate section
- [ ] No contradictions with existing content
- [ ] Used Edit tool (not Write) for existing files

### Common Edit Locations

| Skill Type | Typical Sections to Update |
|------------|---------------------------|
| Programming skills | Rules tables, code examples |
| Planning skills | Phase checklists, task lists |
| Review skills | Detection criteria, severity tables |
| Debugging skills | Troubleshooting steps, symptoms |

## Phase 5: Report

After making the change, report:

```markdown
## Skill Improved: [skill-name]

**What was missing:** [Description of the gap]

**What was added:**
- [Summary of addition]

**Location:** [File:Line or Section name]

**Reason:** [Why this improvement helps]
```

## Examples of Automatic Detection

### Example 1: During PR Review

**Situation:** Reviewing C++ code, you encounter a pattern that looks wrong but isn't in `code-smells`.

**Internal thought:** "This is a 'Refused Bequest' - subclass doesn't use parent methods. The skill mentions it but has no detection criteria."

**Automatic action:**
```markdown
---
**Skill Improvement Detected**

**Skill:** `code-smells`
**Gap:** "Refused Bequest" lacks detection criteria
**Context:** Found during PR review of inheritance hierarchy

**Proposed Addition:**

**Detection criteria:**
- Subclass overrides parent method to do nothing or throw
- Subclass uses <30% of inherited interface
- Subclass only uses parent for type compatibility

**Severity:** Should Fix (50) - indicates wrong inheritance

**Location:** Object-Orientation Abusers section

---
Apply this improvement? (y/n)
```

### Example 2: During Implementation

**Situation:** Writing C++ code, you need a pattern for optional parameters but `programming-cpp` doesn't cover it.

**Internal thought:** "I know std::optional is the right choice here, but the skill doesn't mention it."

**Automatic action:**
```markdown
---
**Skill Improvement Detected**

**Skill:** `programming-cpp`
**Gap:** No guidance on optional parameters
**Context:** Needed while implementing function with optional config

**Proposed Addition:**

### Optional Parameters

| Pattern | Use Case |
|---------|----------|
| `std::optional<T>` | Value may or may not be present |
| Default argument | Always has a sensible default |
| Overloads | Different behavior, not just presence |

```cpp
// Good: explicit optionality
void configure(std::optional<Config> config = std::nullopt);

// Bad: using pointer for optionality
void configure(Config* config = nullptr);
```

**Location:** Parameters section

---
Apply this improvement? (y/n)
```

### Example 3: After Debugging

**Situation:** Spent time debugging a rocprofiler-systems issue. The solution should be in the debugging skill.

**Internal thought:** "I figured out that `ROCPROFSYS_VERBOSE=3` helps diagnose this. Others will hit this too."

**Automatic action:**
```markdown
---
**Skill Improvement Detected**

**Skill:** `debugging-rocprof-sys`
**Gap:** Missing verbose logging troubleshooting step
**Context:** Discovered while debugging instrumentation failure

**Proposed Addition:**

### Enable Verbose Logging

When standard troubleshooting doesn't reveal the issue:

```bash
export ROCPROFSYS_VERBOSE=3
rocprof-sys-run -- ./app
```

Levels: 1 (errors), 2 (warnings), 3 (info), 4+ (debug)

**Location:** General Troubleshooting section

---
Apply this improvement? (y/n)
```

## When NOT to Use This Skill

| Situation | What to Do Instead |
|-----------|---------------------|
| Creating a new skill | Use `radisha-create-skill` |
| Major skill rewrite | Plan it as a feature |
| Project-specific rules | Add to project's CLAUDE.md |
| One-time exception | Just note it in the review |

## Quick Reference

```bash
# Find skill source
readlink -f ~/.claude/skills/<name>/SKILL.md

# Edit skill
# Use Edit tool on the source file

# After editing, changes are immediately available
# (skills are symlinked, no need to "deploy")
```

## Integration

This skill works with:
- `radisha-create-skill` - for new skills
- `radisha-update` - for updating radisha itself
- `radisha-skills` - to list available skills
