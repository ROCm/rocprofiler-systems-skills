---
name: planning-feature
description: Planning skill for new features - includes changelog summary and test case consideration
---

# Feature Planning

Use this skill when implementing NEW functionality or capabilities.

<IMPORTANT>
Follow all base planning rules from `planning/base`, plus the feature-specific rules below.
</IMPORTANT>

## Feature-Specific Requirements

### Changelog Summary

Every new feature MUST include a changelog summary. After analysis, create a concise summary:

```markdown
## Changelog Entry

### Added
- <Brief description of the new feature>
- <User-facing benefit or capability>
```

This summary will be added to CHANGELOG.md upon completion.

### Test Case Consideration

After decomposing the feature into tasks, ASK the user:

> "Should I create test cases for this feature? Consider:
> - Unit tests for new functions/methods
> - Integration tests for component interactions
> - E2E tests for user workflows
>
> Which test types would you like? (all/unit/integration/e2e/none)"

If user requests tests, add them as tasks in the plan.

## Plan File Format

Save to `planning/feature-<name>.md`:

```markdown
# Feature: <Feature Name>

## Goal
<Original user request>

## Changelog Summary
### Added
- <Feature description>

## Analysis
<Key findings, scope, dependencies, risks>

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
- [ ] Update CHANGELOG.md

## Test Cases
- [ ] <Test type>: <Test description>
(or "No tests requested")

## Notes
<Any additional context or decisions>
```

## Example

**User request:** "Add user profile avatar upload"

**Planning output:**

```markdown
# Feature: User Profile Avatar Upload

## Goal
Add ability for users to upload and display profile avatars

## Changelog Summary
### Added
- User profile avatar upload with image preview
- Support for JPG, PNG, and WebP formats up to 5MB

## Analysis
- Scope: ProfileSettings component, user API, storage service
- Dependencies: existing file upload utility, image processing library
- Risks: Large file handling, image format validation

## Tasks
- [ ] Add avatar upload endpoint to user API
- [ ] Create AvatarUpload component with preview
- [ ] Implement image validation and resizing
- [ ] Update ProfileSettings to include avatar section
- [ ] Add avatar display to user profile header
- [ ] Update CHANGELOG.md

## Test Cases
- [ ] Unit: Avatar validation (size, format)
- [ ] Unit: Image resizing function
- [ ] Integration: Upload flow end-to-end

## Notes
- Max file size: 5MB
- Supported formats: JPG, PNG, WebP
- Avatar stored in /uploads/avatars/
```
