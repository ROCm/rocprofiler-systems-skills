---
name: git/create-pull-request
description: Create well-structured Pull Requests - split large changes into logical PRs, write clear descriptions with Motivation, Technical Details, and Test Plan
---

# Create Pull Request Skill

Use this skill when planning and creating Pull Requests. For reviewing PRs, use `git/review-pull-request` instead.

<IMPORTANT>
**PR planning happens DURING task planning, not after.**

When using `planning/feature`, `planning/bugfix`, or `planning/refactor`, consider:
- Is this too big for one PR?
- Can this be logically split?
- Will reviewers understand each PR independently?
</IMPORTANT>

## PR Size Guidelines

### Ideal PR Size
- **< 400 lines changed** - Easy to review, quick turnaround
- **400-800 lines** - Acceptable for complex features
- **> 800 lines** - Should be split into multiple PRs

### When to Split

Split into multiple PRs when:
- Changes touch multiple unrelated systems
- Refactoring can be separated from feature work
- Infrastructure changes can land independently
- Tests can be added before implementation

### Split Strategy

```
Large Feature
     │
     ├── PR 1: Refactoring (prepare codebase)
     │         - Extract interfaces
     │         - Move code to better locations
     │         - No behavior change
     │
     ├── PR 2: Infrastructure
     │         - Add new dependencies
     │         - Create base classes/interfaces
     │         - Add configuration
     │
     ├── PR 3: Core Implementation
     │         - Main feature logic
     │         - Unit tests
     │
     └── PR 4: Integration
              - Wire everything together
              - Integration tests
              - Documentation
```

## PR Structure

Every PR MUST have these sections:

### 1. Motivation

**Why** is this change needed?

```markdown
## Motivation

[Explain the problem or need this PR addresses]

- What issue does this solve?
- What feature does this enable?
- What improvement does this bring?

Related issue: #123 (if applicable)
```

### 2. Technical Details

**What** does this PR change and **how**?

```markdown
## Technical Details

[Explain the implementation approach]

### Changes
- [List key changes]
- [Explain architectural decisions]
- [Note any trade-offs made]

### Files Changed
- `src/module/file.cpp` - [Brief description]
- `include/module/file.hpp` - [Brief description]
```

### 3. Test Plan

**How** was this tested?

```markdown
## Test Plan

### Unit Tests
- [ ] `test_feature_basic` - Tests basic functionality
- [ ] `test_feature_edge_cases` - Tests boundary conditions
- [ ] `test_feature_error_handling` - Tests error paths

### Manual Testing
- [ ] [Step-by-step manual test if applicable]

### Verification
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] No new warnings introduced
```

## PR Template

Use this template for all PRs:

```markdown
## Motivation

[Why is this change needed? What problem does it solve?]

## Technical Details

### Summary
[One paragraph summary of the changes]

### Key Changes
- [Change 1]
- [Change 2]
- [Change 3]

### Design Decisions
[Explain any significant design choices and their rationale]

## Test Plan

### Automated Tests
- [ ] Unit tests added/updated
- [ ] All tests passing

### Manual Verification
- [ ] [Describe manual testing performed]

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added only for non-obvious logic (no meaningless/obvious comments)
- [ ] Documentation updated (if applicable)
- [ ] No unrelated changes included
```

## Integration with Planning

### During Task Planning

When creating a plan in `planning/feature-*.md` or `planning/refactor-*.md`:

1. **Assess total scope** - How many lines will change?
2. **Identify logical boundaries** - What can be separated?
3. **Plan PR sequence** - Which PRs depend on others?
4. **Document in plan file**:

```markdown
## PR Strategy

### PR 1: [Title]
**Scope:** [What's included]
**Dependencies:** None
**Estimated size:** ~200 lines

### PR 2: [Title]
**Scope:** [What's included]
**Dependencies:** PR 1
**Estimated size:** ~350 lines
```

### Before Creating PR

1. **Review changes** - Are they logically cohesive?
2. **Check size** - Is it reviewable?
3. **Verify tests** - Does test plan cover changes?
4. **Write description** - Fill in all three sections

## Creating the PR

After implementation is complete and user approves:

```bash
# Create branch (if not already on feature branch)
git checkout -b feature/descriptive-name

# Stage and commit (use conventional commits if project uses them)
git add .
git commit -m "feat: add user avatar upload

- Add avatar upload endpoint
- Create AvatarUpload component
- Add image validation"

# Push and create PR
git push -u origin HEAD

# Create PR with gh CLI
gh pr create --title "feat: Add user avatar upload" --body "$(cat <<'EOF'
## Motivation

Users need the ability to upload profile avatars to personalize their accounts.
This feature was requested in #123.

## Technical Details

### Summary
Adds avatar upload functionality with client-side preview and server-side validation.

### Key Changes
- Added `POST /api/users/avatar` endpoint
- Created `AvatarUpload` React component with drag-and-drop
- Implemented image validation (size, format)
- Added image resizing to reduce storage

### Design Decisions
- Chose to resize on server to ensure consistent dimensions
- Using WebP format for storage to reduce size

## Test Plan

### Automated Tests
- [x] `test_avatar_upload_valid_image` - Upload succeeds with valid JPG
- [x] `test_avatar_upload_invalid_format` - Rejects non-image files
- [x] `test_avatar_upload_too_large` - Rejects files > 5MB
- [x] `test_avatar_resize` - Verifies resizing to 256x256

### Manual Verification
- [x] Upload works in Chrome, Firefox, Safari
- [x] Drag-and-drop works correctly
- [x] Preview displays before upload

EOF
)"
```

## PR Review Checklist

Before requesting review, verify:

- [ ] PR title is clear and descriptive
- [ ] Motivation section explains the "why"
- [ ] Technical Details explain the "what" and "how"
- [ ] Test Plan shows coverage
- [ ] No unrelated changes included
- [ ] Branch is up to date with main
- [ ] All CI checks pass
- [ ] Self-review completed

## Examples

### Good PR: Focused and Clear

```markdown
## Motivation

Session timeout is incorrectly set to 5 minutes instead of 30 minutes,
causing users to be logged out unexpectedly. Fixes #456.

## Technical Details

### Summary
Fixed token refresh timing comparison that caused premature session expiry.

### Key Changes
- Fixed comparison operator in `tokenService.ts:45` (`>` → `>=`)
- Added constant `SESSION_TIMEOUT_MS` to centralize configuration

### Design Decisions
- Moved timeout value to config for easier adjustment in future

## Test Plan

### Automated Tests
- [x] `test_token_refresh_at_boundary` - Tests exact timeout boundary
- [x] `test_session_persists_29_minutes` - Verifies no early logout

### Manual Verification
- [x] Logged in and waited 25 minutes - session persisted
- [x] Verified refresh token request at expected time
```

### Bad PR: Too Large, Unfocused

```markdown
## Changes

- Fixed session timeout bug
- Refactored auth module
- Added user preferences feature
- Updated dependencies
- Fixed typos in README
```

**Problem:** Multiple unrelated changes. Should be 4-5 separate PRs.

## References

- [How to Write a Git Commit Message](https://cbea.ms/git-commit/)
- [GitHub Pull Request Documentation](https://docs.github.com/en/pull-requests)
