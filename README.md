# Cursor Skills Repository

This repository stores Cursor Skills used across our project. Skills are reusable AI behavior definitions that help standardize and automate development workflows.

## Core Philosophy: Planning First

**Every task starts with planning.** Before any implementation, the AI must:

1. Analyze the request and identify scope
2. Create a structured plan with tasks
3. Save the plan to `planning/` folder in the project root
4. Track progress using TodoWrite and update the plan file

This ensures consistent, well-thought-out implementations that can be resumed later.

## Skill Organization

```
skills/
├── using-radisha/          # Entry point - how to use all skills
│   └── SKILL.md
├── ask/                    # Questions without actions
│   └── SKILL.md
├── planning/               # Planning skills (always run first for actions)
│   ├── base/               # Shared planning rules
│   │   └── SKILL.md
│   ├── feature/            # New feature planning
│   │   └── SKILL.md
│   ├── bugfix/             # Bug fix planning
│   │   └── SKILL.md
│   └── docs/               # Documentation planning
│       └── SKILL.md
├── programming/            # Implementation skills
├── documentation/          # Documentation skills
└── testing/                # Testing skills
```

### Available Skills

| Skill | Use Case | Planning | Changelog |
|-------|----------|----------|-----------|
| `ask` | Questions, explanations | No | No |
| `planning/feature` | New functionality | Yes | Required |
| `planning/bugfix` | Bug fixes | Yes | Asks user |
| `planning/docs` | Documentation | Yes | No |

### Workflow

```
User Request
    │
    ▼
┌──────────────────────┐
│ Question only?       │──── yes ───→ ask skill → Respond
│ (no action needed)   │
└──────────────────────┘
    │ no
    ▼
┌──────────────────────┐
│ Is type clear?       │──── no ────→ Offer skill options
└──────────────────────┘              (let user choose)
    │ yes                                    │
    ▼                                        ▼
┌──────────────────────┐              ┌──────────────────┐
│ Is task non-trivial? │              │ User selects     │
│ (>2 steps)           │              │ skill type       │
└──────────────────────┘              └──────────────────┘
    │ yes              │ no                  │
    ▼                  ▼                     │
Determine type    Execute directly ←─────────┘
    │
    ├── feature → planning/feature
    ├── bugfix  → planning/bugfix
    └── docs    → planning/docs
            │
            ▼
    Create plan file in planning/
            │
            ▼
    Create TodoWrite tasks
            │
            ▼
    Execute with tracking
            │
            ▼
    Mark completed in plan file
```

### When Unclear: Offer Options

If the AI is unsure which skill applies, it will ask:

> "Which best describes what you need?
> 1. **New feature** - Add new functionality
> 2. **Bug fix** - Fix something broken
> 3. **Documentation** - Create or update docs
> 4. **Just a question** - No action needed"

### Plan Persistence

Plans are saved to the `planning/` folder in your project root:
- `planning/feature-<name>.md` - Feature plans
- `planning/bugfix-<name>.md` - Bug fix plans
- `planning/docs-<name>.md` - Documentation plans

This allows:
- **Resuming work** - Continue from where you left off
- **Tracking progress** - See which tasks are done (`[x]`) vs pending (`[ ]`)
- **Reusing plans** - Similar requests can adapt existing plans

## What are Cursor Skills?

Cursor Skills are `.mdc` (Markdown with Configuration) files that define reusable AI behaviors. When you invoke a skill using `@skill-name` in Cursor's chat, the AI loads those instructions and follows the defined workflow.

## How to Add Skills to Cursor

For detailed and up-to-date instructions, refer to the official Cursor documentation:
**[https://cursor.com/docs/context/skills](https://cursor.com/docs/context/skills)**

### Quick Setup Guide

#### Project Skills (Shared with Team)

1. Create a `.cursor/skills` directory in your project root
2. Add skill folders with `SKILL.md` files to this directory
3. Commit these files to your repository so the entire team can use them

```
your-project/
├── .cursor/
│   └── skills/
│       ├── code-review/
│       │   └── SKILL.md
│       ├── documentation/
│       │   └── SKILL.md
│       └── testing/
│           └── SKILL.md
└── ...
```

#### User Skills (Personal)

For personal skills that apply to all your projects:

1. Create a skills directory in your Cursor user configuration:
   - **Linux/macOS:** `~/.cursor/skills/`
   - **Windows:** `%APPDATA%\Cursor\skills\`
2. Add your skill folders with `SKILL.md` files to this directory

### Skill File Format

Skills use the `.md` format with YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill does
---

# Skill Name

Your skill instructions go here. Write them as if you're instructing an AI assistant on how to perform a specific task.

## Guidelines

- Step-by-step instructions
- Best practices to follow
- Examples if needed
```

### Using Skills

To use a skill in Cursor:

1. Open the Chat or Composer panel
2. Type `@` followed by the skill name (e.g., `@planning-feature`)
3. The skill's instructions will be loaded and the AI will follow them

## Adding Skills from This Repository

### Method 1: Copy to Local Project

1. Clone or copy the skills you need from this repository
2. Place them in your project's `.cursor/skills/` directory
3. The skills will be immediately available in Cursor

### Method 2: Add Directly from GitHub URL

You can add skills directly from GitHub without downloading them manually:

1. Open Cursor Settings (`Ctrl+,` or `Cmd+,`)
2. Navigate to **Skills** section
3. Click **"Add from GitHub"** or the **+** button
4. Enter the GitHub URL to the skill file

**Use this repository URL:**

```
https://github.com/adjordje-amd/radisha
```

**Or link to a specific skill file:**

```
https://github.com/adjordje-amd/radisha/blob/main/skills/planning/feature/SKILL.md
```

**Benefits of GitHub integration:**
- No need to manually download or copy files
- Skills stay synchronized when updated in the repository
- Easy access to community-contributed skills
- Share skills across multiple projects without duplication

## Contributing

When adding new skills to this repository:

1. Create a new folder with a descriptive name under the appropriate category
2. Add a `SKILL.md` file with frontmatter (name, description)
3. Write detailed instructions that the AI can follow
4. Test the skill in Cursor before committing
5. Submit a pull request with your changes

## Resources

- [Official Cursor Skills Documentation](https://cursor.com/docs/context/skills)
- [Cursor Documentation](https://docs.cursor.com)
