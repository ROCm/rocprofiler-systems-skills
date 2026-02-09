---
name: radisha-create-skill
description: Use when creating a new skill for radisha - validates content, checks for conflicts, and integrates with existing skills
---

# Create Skill

Meta-skill for creating new radisha skills. Validates proposed skill content, checks for conflicts with existing skills, and handles integration.

## When to Use

Use this skill when:
- User provides content for a new skill
- User asks to create a skill for a specific purpose
- Converting existing documentation into a skill

## Process Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  User provides skill content                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 1: Analyze      │
                    │ - Usefulness          │
                    │ - Alignment           │
                    │ - Conflicts           │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Phase 2: Report       │
                    │ Present findings to   │
                    │ user, suggest fixes   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ User approves?        │
                    └───────────────────────┘
                          │           │
                         no          yes
                          │           │
                          ▼           ▼
                    ┌─────────┐ ┌───────────────────────┐
                    │  Stop   │ │ Phase 3: Create skill │
                    └─────────┘ └───────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │ Phase 4: Integrate    │
                              │ - Update radisha-help │
                              │ - Update README       │
                              │ - Update related skills│
                              └───────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │ Report completion     │
                              └───────────────────────┘
```

## Phase 1: Analyze Skill Content

When user provides skill content, analyze these aspects:

### 1.1 Usefulness Assessment

Answer: **Will this skill help the AI perform better?**

| Question | Good Sign | Bad Sign |
|----------|-----------|----------|
| Does it provide structure? | Clear phases, checkpoints | Vague guidelines |
| Does it reduce ambiguity? | Explicit triggers, outputs | "Use when appropriate" |
| Does it prevent mistakes? | Common mistakes section | No anti-patterns |
| Is it actionable? | Specific steps to follow | Abstract principles only |

### 1.2 Alignment Check

Check how the skill fits with existing radisha skills:

| Relationship | Check |
|--------------|-------|
| **Precursor** | Does it come before other skills? (e.g., exploration → planning) |
| **Successor** | Does it come after other skills? (e.g., planning → programming) |
| **Parallel** | Does it work alongside other skills? |
| **Independent** | Is it standalone? |

### 1.3 Conflict Detection

Check for conflicts with existing skills:

```
For each existing skill:
  - Does the new skill overlap in purpose?
  - Are there contradictory instructions?
  - Is there ambiguity about when to use which?
```

**Common conflicts to check:**

| Existing Skill | Potential Conflict |
|----------------|-------------------|
| `ask` | Quick explanations vs. structured analysis |
| `planning-*` | Which planning type applies? |
| `programming-*` | Language-specific overlap? |
| `testing-*` | Testing approach conflicts? |

### 1.4 Consistency Check

Verify the skill follows radisha patterns:

| Pattern | Check |
|---------|-------|
| Tool names | Uses `AskUserQuestion` not `AskQuestion` |
| Task tracking | References platform's task tools |
| Plan mode | Platform-agnostic language |
| Output location | Follows `planning/` convention if applicable |
| Formatting | Tables, ASCII diagrams, not prose-heavy |
| Checkpoints | User validation at key points |

## Phase 2: Report Findings

Present analysis to user in this format:

```markdown
## Skill Analysis: [Skill Name]

### Usefulness
| Aspect | Assessment |
|--------|------------|
| Structure | [Clear/Vague] |
| Triggers | [Explicit/Ambiguous] |
| Anti-patterns | [Present/Missing] |
| Actionability | [High/Medium/Low] |

**Verdict:** [Useful / Needs work / Not recommended]

### Alignment
- **Relationship:** [Precursor to X / Successor to Y / Independent]
- **Workflow position:** [Where it fits in the skill chain]

### Conflicts
| Existing Skill | Conflict | Resolution |
|----------------|----------|------------|
| [skill] | [overlap description] | [how to fix] |

### Issues to Fix
1. [Issue 1 with suggested fix]
2. [Issue 2 with suggested fix]

### Recommended Category
`skills/[category]/[skill-name]/SKILL.md`

---

**Proceed with creation?** (with fixes applied)
```

Wait for user approval before proceeding.

## Phase 3: Create Skill File

### 3.1 Determine Location

Choose category based on skill purpose:

| Purpose | Category prefix | Path |
|---------|----------------|------|
| Planning workflows | `planning-` | `skills/planning-[name]/` |
| Language-specific coding | `programming-` | `skills/programming-[lang]/` |
| Testing approaches | `testing-` | `skills/testing-[name]/` |
| Code exploration | `exploration-` | `skills/exploration-[name]/` |
| Library-specific | `libraries-` | `skills/libraries-[name]/` |
| Git workflows | `git-` | `skills/git-[name]/` |
| Radisha management | `radisha-` | `skills/radisha-[name]/` |
| Standalone utility | Top-level | `skills/[name]/` |

### 3.2 Apply Template

Ensure skill follows this structure:

```markdown
---
name: category/skill-name
description: One-line description - when to use this skill
---

# Skill Title

Brief overview (1-2 sentences).

<IMPORTANT>
Critical rules that must always be followed.
</IMPORTANT>

## When to Use

Clear triggers for invoking this skill:
- Trigger 1
- Trigger 2

## Process / Phases

Step-by-step workflow with:
- Numbered phases
- Checkpoints for user validation
- Clear deliverables

## Output

What gets produced:
- File location (if applicable)
- Format/structure

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| [anti-pattern] | [correct approach] |

## Integration with Other Skills

| After This Skill | Use |
|------------------|-----|
| [scenario] | [next skill] |
```

### 3.3 Apply Fixes

Before creating, apply all fixes identified in Phase 2:

- Fix tool names
- Add missing sections
- Convert diagrams to ASCII
- Add checkpoints if missing
- Standardize formatting

### 3.4 Create Directory and File

```bash
mkdir -p skills/[category]/[skill-name]
```

Write `SKILL.md` to the directory.

## Phase 4: Integrate with Radisha

After creating the skill, update these files:

### 4.1 Update `radisha-help/SKILL.md`

Add to appropriate section:

```markdown
**[Category] skills:**
- `category/skill-name` - Brief description
```

### 4.2 Update `README.md`

Three updates required:

**A. Skill Categories table:**
```markdown
### [Category] Skills

| Skill | Description |
|-------|-------------|
| `category/skill-name` | Description |
```

**B. Detailed section:**
```markdown
#### `category/skill-name`
[Detailed description with key features]
```

**C. Directory structure:**
```markdown
├── [category]/
│   └── [skill-name]/
│       └── SKILL.md
```

### 4.3 Update Related Skills (if needed)

If conflicts were found, update related skills to disambiguate:

**Example:** When creating `exploration-explore-code`, we updated `ask` skill:
```markdown
## When NOT to Use
- **Systematic code exploration** → use `exploration-explore-code`
```

## Phase 5: Report Completion

After all integration:

```markdown
## Skill Created: [category/skill-name]

**Files created:**
- `skills/[category]/[skill-name]/SKILL.md`

**Files updated:**
- `skills/radisha-help/SKILL.md` - Added to skill list
- `README.md` - Added to tables and directory structure
- [Other updated files if any]

**Integration:**
- Workflow position: [where it fits]
- Related skills: [how it connects]

The skill is now ready to use.
```

## Validation Checklist

Before completing, verify:

- [ ] Skill file created in correct location
- [ ] Frontmatter has correct `name` and `description`
- [ ] Tool names are platform-correct (`AskUserQuestion`, etc.)
- [ ] No conflicts with existing skills (or conflicts resolved)
- [ ] `radisha-help` updated with skill reference
- [ ] `README.md` tables updated
- [ ] `README.md` detailed section added
- [ ] `README.md` directory structure updated
- [ ] Related skills updated if disambiguation needed

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating without analysis | Always do Phase 1-2 first |
| Skipping conflict check | Read existing skills before creating |
| Wrong tool names | Use `AskUserQuestion`, `TaskCreate`, etc. |
| Forgetting README updates | Update all three sections |
| Forgetting radisha-help update | Add skill reference to radisha-help/SKILL.md |
| No user approval | Always present analysis, wait for approval |
| Wrong category | Match purpose to existing categories |

## Skill Categories Reference

| Category prefix | Purpose | Examples |
|----------------|---------|----------|
| `planning-` | Task planning workflows | planning-feature, planning-bugfix, planning-refactor |
| `programming-` | Language-specific coding | programming-cpp, programming-python, programming-cmake-best-practices |
| `testing-` | Testing approaches | testing-testplan, testing-gtest-gmock, testing-pytest |
| `exploration-` | Code understanding | exploration-explore-code |
| `libraries-` | Library-specific knowledge | libraries-amd-smi |
| `git-` | Git workflows | git-prepare-pull-request, git-review-pull-request |
| `radisha-` | Radisha management | radisha-update, radisha-create-skill |
| `ask` | Quick explanations | (standalone) |
