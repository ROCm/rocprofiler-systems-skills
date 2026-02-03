---
name: exploration/explore-code
description: Use when user wants to understand unfamiliar code before extracting functionality - exploring database layers, API usage, library patterns, or any code to be extracted into a reusable component
---

# Explore Code

Deep exploration of **unfamiliar codebases** to understand usage patterns before extraction or integration.

## Overview

This skill helps users understand code they don't know, specifically when preparing to **extract** functionality into reusable libraries or components.

**MANDATORY: User must specify what usage type to explore** (e.g., "database reading patterns", "authentication flow", "API client usage").

The exploration answers three questions:
1. **What is used** - Which tables, APIs, components, functions
2. **How it is used** - Patterns, conditions, parameters, transformations
3. **Where to use it** - Call sites, contexts, triggering conditions

**Key assumption:** The project is unknown to the user. They're learning to extract, not verifying known behavior.

**Output:** A structured markdown file at `planning/exploration-<topic>.md` with precise usage inventory for extraction planning.

## Process Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                     User asks exploration question              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Ask scoping questions │◄────┐
                    └───────────────────────┘     │
                                │                 │
                                ▼                 │
                    ┌───────────────────────┐     │
                    │     Scope clear?      │─────┘
                    └───────────────────────┘ no
                                │ yes
                                ▼
                    ┌───────────────────────┐
                    │ Initial exploration   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ CHECKPOINT 1: Report  │
                    │ Ask: Focus areas?     │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Deep dive on areas    │◄────┐
                    └───────────────────────┘     │
                                │                 │
                                ▼                 │
                    ┌───────────────────────┐     │
                    │ CHECKPOINT 2: Report  │     │
                    │ Ask: Skip/add areas?  │     │
                    └───────────────────────┘     │
                                │                 │
                                ▼                 │
                    ┌───────────────────────┐     │
                    │   More areas?         │─────┘
                    └───────────────────────┘ yes
                                │ no
                                ▼
                    ┌───────────────────────┐
                    │ Synthesize findings   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ CHECKPOINT 3: Draft   │
                    │ Ask: Adjust format?   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Generate final doc    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Deliver document   │
                    └───────────────────────┘
```

## Phase 1: Scoping Questions

**MANDATORY: Ask these BEFORE any exploration.**

Use the `AskUserQuestion` tool to understand:

1. **Usage type** (REQUIRED): "What specific usage do you want to explore?"
   - Examples: "database reading layer", "REST API client", "authentication flow", "file I/O patterns"
   - This MUST be specified - do not proceed without it

2. **Extraction goal**: "What are you planning to extract or create?"
   - Options: Standalone library, Internal module, API wrapper, Understanding only (no extraction)

3. **Scope boundaries**: "Which parts of the codebase are relevant?"
   - Options: Specific directories, Specific file types, Everything, Not sure (I'll explore)

4. **Depth**: "How detailed should the inventory be?"
   - Options: High-level patterns only, Detailed with all call sites, Exhaustive with parameters/conditions

## Phase 2: Initial Exploration

After scoping, perform initial pass:

1. **Find relevant files** using Glob patterns based on scope
2. **Identify key entry points** - main files, exports, public APIs
3. **Map top-level structure** - directories, modules, packages

**CHECKPOINT 1: Present initial findings to user**

```markdown
## Initial Scan Results

**Files found:** N files matching criteria
**Key entry points:** [list]
**Main directories:** [list]

**Potential focus areas:**
1. [Area A] - appears to handle X
2. [Area B] - appears to handle Y
3. [Area C] - appears to handle Z

**Which areas should I focus on?** (can select multiple or suggest others)
```

Wait for user response before continuing.

## Phase 3: Deep Exploration

For each selected area, answer the three core questions:

### 3.1 What Is Used

Inventory everything the code interacts with for the specified usage type:

- Classes, structs, functions accessed
- External libraries or APIs called
- Resources (files, connections, handles)
- Data structures and their members

```cpp
// Example inventory for "file I/O layer"
// Classes: FileReader, BufferedStream, PathResolver
// Functions: open(), read(), seek(), close()
// Types: std::ifstream, std::filesystem::path
```

### 3.2 How It Is Used

Document the patterns and conditions:

- Function signatures and parameter patterns
- Return value handling (error codes, exceptions, optionals)
- Conditional logic (when is X called vs Y?)
- Resource lifecycle (RAII patterns, manual management)
- Configuration and parameterization

```cpp
// Example: "How is connection pooling used?"
// - Pool initialized with max_connections from config
// - get_connection() blocks if pool exhausted
// - Connections auto-returned via RAII wrapper
// - Timeout triggers reconnect logic
```

### 3.3 Where To Use It

Map call sites and triggering contexts:

- Which functions/methods initiate the usage?
- What's the call hierarchy? (entry point → ... → actual usage)
- What conditions trigger each pattern?
- Lifecycle timing (initialization, request handling, shutdown)

```cpp
// Example call hierarchy for "data fetching"
// main()
//   → Application::run()
//     → RequestHandler::process()
//       → DataService::fetch()      // <-- actual usage
//         → Repository::query()
```

**CHECKPOINT 2: Present findings for each area**

```markdown
## Deep Dive: [Area Name]

### What Is Used
| Component | Type | Purpose |
|-----------|------|---------|
| DataReader | class | Reads records from source |
| Config::timeout | member | Connection timeout in ms |
| fetch() | method | Retrieves data with filters |

### How It Is Used
| Pattern | Signature/Example | Conditions |
|---------|-------------------|------------|
| Filtered fetch | fetch(Filter f) | When user specifies criteria |
| Batch read | fetchBatch(size_t n) | For bulk operations |
| Retry on error | 3 retries with backoff | On connection failure |

### Where To Use It
| Call Site | Context | Trigger |
|-----------|---------|---------|
| Processor::run() | Main loop | Each iteration |
| Importer::load() | Startup | Once on init |

**Should I continue to next area, go deeper here, or adjust scope?**
```

Wait for user response.

## Phase 4: Synthesis

After all areas explored:

**CHECKPOINT 3: Present draft document structure**

```markdown
## Proposed Document Structure

1. **What Is Used** (Complete inventory)
   - [components to include]

2. **How It Is Used** (Patterns and conditions)
   - [patterns to document]

3. **Where To Use It** (Call sites and contexts)
   - [call hierarchies to include]

4. **Extraction Recommendations**
   - [interface suggestions, dependencies to handle]

**Adjustments needed?** (add sections, remove sections, change focus)
```

Wait for user approval before generating.

## Phase 5: Generate Document

Create the final markdown file with:

### Required Sections

**1. What Is Used**
Complete inventory of components for the explored usage type:

| Component | Type | Purpose | Dependencies |
|-----------|------|---------|--------------|
| ClassName | class | Brief purpose | lib1, lib2 |
| functionName() | function | Brief purpose | ClassName |

**2. How It Is Used**
Patterns, signatures, and conditions:

| Pattern | Signature/Example | When Used | Notes |
|---------|-------------------|-----------|-------|
| Pattern name | `func(param1, param2)` | Condition | Gotchas |

**3. Where To Use It**
Call sites and triggering contexts:

| Entry Point | Call Chain | Trigger | Frequency |
|-------------|------------|---------|-----------|
| main() | → App::run() → Service::fetch() | On request | Per-request |

**4. Extraction Recommendations**
- Suggested interface for extracted library
- Dependencies to bundle or abstract
- Breaking changes to anticipate
- Specific answers to user's original question

## Output File Location

Default: `planning/exploration-<topic>.md`

This integrates with the planning workflow - exploration documents feed into `planning/feature` or `planning/refactor` skills.

## Subagent Usage

For large codebases, use subagents for parallel exploration:

- Spawn separate subagents for independent areas
- Each subagent reports back with What/How/Where for its area
- Main agent synthesizes findings

**Example:** "Explore database layer" might spawn:
- Subagent 1: Read operations
- Subagent 2: Write operations
- Subagent 3: Connection management

```
Main Agent
    │
    ├── Subagent: "Explore read operations"
    │   └── Returns: What/How/Where for reads
    │
    ├── Subagent: "Explore write operations"
    │   └── Returns: What/How/Where for writes
    │
    └── Subagent: "Explore connection management"
        └── Returns: What/How/Where for connections

Main Agent synthesizes into single document
```

## Red Flags - STOP and Check

- **No usage type specified** - User MUST specify what to explore (e.g., "database reading", "logging layer")
- **Exploring without scoping** - Go back and ask questions first
- **Long silence** - If you've read more than 5 files without user update, pause and report
- **Missing what/how/where** - Every finding should answer at least one of the three questions
- **Generating without checkpoint** - Always present draft structure before final document

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Starting without usage type | Ask: "What specific usage do you want to explore?" |
| Diving into code without asking scope | Always run Phase 1 scoping questions first |
| Listing "what" without "how" or "where" | Every component needs usage patterns and call sites |
| Producing final doc without checkpoints | Stop at each checkpoint, wait for user |
| Prose-heavy output | Use tables, lists, diagrams - scannable format |
| Missing call hierarchies | Trace from entry point to actual usage |

## Rationalizations to Reject

| Excuse | Reality |
|--------|---------|
| "User seems busy, I'll skip scoping" | Scoping saves time. Ask the questions. |
| "Usage type is obvious from context" | Confirm anyway. "Database" could mean read/write/schema/migrations. |
| "I found what's used, that's enough" | Without how/where, user can't extract safely. Complete all three. |
| "Checkpoints slow things down" | Checkpoints prevent wasted work. Do them. |
| "I'll figure out call sites later" | Call sites ARE the extraction boundary. Find them now. |
| "The code is simple, no doc needed" | User is unfamiliar with it. Document everything found. |

## Integration with Other Skills

| After Exploration | Use This Skill |
|-------------------|----------------|
| Extract as new library | `planning/feature` |
| Refactor existing code | `planning/refactor` |
| Just needed understanding | Done - no further action |

The exploration document (`planning/exploration-<topic>.md`) serves as input to planning skills.
