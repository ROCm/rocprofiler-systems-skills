---
name: testing-testplan
description: Create test plan files for developer verification and QA handoff - use after implementation is complete
---

# Test Plan Skill

Use this skill to create a test plan file that documents what needs to be verified for a change. The test plan serves both developers (for self-verification) and QA teams (for formal testing).

<IMPORTANT>
**When to create a test plan:**
- After implementation is complete
- Before or alongside writing unit tests
- Before creating a Pull Request

**Where to save:**
`planning/testplan-<feature-name>.md`

The test plan file should be created even if automated tests exist - it documents the full verification scope including manual checks.
</IMPORTANT>

## Test Plan Template

```markdown
# Test Plan: <Feature/Change Name>

## Summary

**Change:** <Brief description of what changed>
**PR:** <Link when available>

## What to Test

### Automated Tests

| Test | Description | Status |
|------|-------------|--------|
| `test_name_1` | What it verifies | ⬜ |
| `test_name_2` | What it verifies | ⬜ |

### Manual Verification

| # | Scenario | Steps | Expected Result | ✓ |
|---|----------|-------|-----------------|---|
| 1 | Happy path | 1. Do X → 2. Do Y | Z happens | ⬜ |
| 2 | Error case | 1. Invalid input | Error shown | ⬜ |
| 3 | Edge case | 1. Empty/max values | Handled gracefully | ⬜ |

## Regression Check

- [ ] <Related feature 1> still works
- [ ] <Related feature 2> still works

## Notes

<Any special setup, test data, or considerations for QA>
```

## How to Fill the Template

### Summary Section

- **Change:** One sentence describing what was implemented or fixed
- **PR:** Add the PR link once created (can be empty initially)

### Automated Tests

List all unit and integration tests that cover this change:

```markdown
| Test | Description | Status |
|------|-------------|--------|
| `test_user_create_valid` | Creates user with valid data | ✅ |
| `test_user_create_duplicate` | Rejects duplicate username | ✅ |
| `test_user_create_invalid_email` | Validates email format | ⬜ |
```

Status:
- ⬜ = Not written yet
- ✅ = Written and passing
- ❌ = Failing (needs fix)

### Manual Verification

Document scenarios that require human verification:

```markdown
| # | Scenario | Steps | Expected Result | ✓ |
|---|----------|-------|-----------------|---|
| 1 | Create user | 1. Go to /users/new → 2. Fill form → 3. Submit | User created, redirect to profile | ✅ |
| 2 | Duplicate username | 1. Try existing username → 2. Submit | Error: "Username taken" | ✅ |
| 3 | Long username | 1. Enter 100+ chars → 2. Submit | Truncated or error shown | ⬜ |
```

**Good scenarios to include:**
- Happy path (normal usage)
- Error cases (invalid input, missing data)
- Edge cases (empty, maximum, special characters)
- UI/UX verification (if applicable)

### Regression Check

List related features that might be affected:

```markdown
## Regression Check

- [x] Login still works after user changes
- [x] User list displays correctly
- [ ] Admin can still edit users
```

### Notes

Add anything QA needs to know:
- Required test data or accounts
- Environment setup
- Known limitations
- Areas of higher risk

## Example: Complete Test Plan

```markdown
# Test Plan: User Avatar Upload

## Summary

**Change:** Users can upload profile avatars (JPG, PNG, max 5MB)
**PR:** #234

## What to Test

### Automated Tests

| Test | Description | Status |
|------|-------------|--------|
| `test_avatar_upload_jpg` | Upload valid JPG | ✅ |
| `test_avatar_upload_png` | Upload valid PNG | ✅ |
| `test_avatar_upload_too_large` | Reject files > 5MB | ✅ |
| `test_avatar_upload_invalid_type` | Reject non-image files | ✅ |
| `test_avatar_resize` | Resize to 256x256 | ✅ |

### Manual Verification

| # | Scenario | Steps | Expected Result | ✓ |
|---|----------|-------|-----------------|---|
| 1 | Upload JPG | 1. Go to profile → 2. Click avatar → 3. Select JPG | Preview shown, saves on confirm | ✅ |
| 2 | Upload PNG | Same as above with PNG | Works same as JPG | ✅ |
| 3 | Large file | Upload 10MB image | Error: "File too large (max 5MB)" | ✅ |
| 4 | Wrong format | Upload PDF | Error: "Only JPG and PNG allowed" | ✅ |
| 5 | Drag and drop | Drag image onto avatar area | Preview shown | ✅ |
| 6 | Cancel upload | Start upload → click Cancel | Returns to previous avatar | ✅ |

## Regression Check

- [x] Profile page loads correctly
- [x] User settings still work
- [x] Other users can see updated avatar

## Notes

- Test with various image dimensions (square, landscape, portrait)
- Avatar should display correctly in header, profile, and comments
- Test on Chrome, Firefox, Safari
```

## Workflow Integration

After completing implementation:

1. **Create test plan file:** `planning/testplan-<feature>.md`
2. **Fill in automated tests:** List tests you'll write or have written
3. **Add manual scenarios:** What needs human verification
4. **Identify regression areas:** What existing features might be affected
5. **Verify manually:** Check off items as you verify
6. **Write automated tests:** Invoke `testing-gtest-gmock` or `testing-pytest`
7. **Update status:** Mark all items as verified
8. **Include in PR:** Reference the test plan in PR description
