---
name: git/pull-request-status
description: Check pull request status, CI/CD checks, and explain failures with actionable recommendations
---

# Pull Request Status Check Skill

Comprehensive PR status checking - verifies CI/CD checks, review status, and provides detailed explanations of failures.

## Overview

This skill:
- ✅ Checks all PR status checks (CI/CD, tests, linting)
- 🔍 Fetches logs and error details for failed checks
- 💡 Explains failures in plain English with fix suggestions
- 📊 Provides summary of PR readiness for merge

<IMPORTANT>
**ALWAYS invoke `git/gh-client` first** to verify gh CLI is available and authenticated.
</IMPORTANT>

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 0: Verify gh CLI                          │
│              Invoke: git/gh-client                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 1: Get PR Number                          │
│    Ask user for PR number or auto-detect current branch         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Phase 2: Fetch PR Status Data                       │
│    - Basic PR info (state, reviews)                              │
│    - Status check rollup (all CI/CD checks)                      │
│    - Review status                                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│           Phase 3: Analyze Status Checks                         │
│    - Parse check results                                         │
│    - Identify failures/errors                                    │
│    - Categorize by type                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│        Phase 4: Fetch Failure Details                            │
│    For each failed check:                                        │
│    - Get check run details                                       │
│    - Fetch logs (if GitHub Actions)                              │
│    - Extract error messages                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│         Phase 5: Explain and Recommend                           │
│    - Explain each failure in plain English                       │
│    - Suggest fixes                                               │
│    - Provide merge readiness summary                             │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 0: Verify GitHub CLI

```markdown
**FIRST ACTION: Invoke `git/gh-client` skill**

This ensures gh CLI is installed and authenticated.
If not available, git/gh-client provides installation instructions.
```

## Phase 1: Get PR Number

### Option 1: User Provides PR Number

Ask user: "Which PR do you want to check? (Enter PR number)"

### Option 2: Auto-detect from Current Branch

```bash
# Get current branch
current_branch=$(git branch --show-current)

# Find PR for current branch
gh pr list --head "$current_branch" --json number --jq '.[0].number'
```

If found, ask user: "Found PR #123 for branch `feature-branch`. Check this PR?"

## Phase 2: Fetch PR Status Data

### Get Comprehensive PR Status

**Use a combination of commands for complete status information.**

```bash
# 1. Get PR metadata (avoid deprecated fields)
# NOTE: Do NOT request deprecated fields (projectCards, projectItems)
gh pr view <PR_NUMBER> --json \
  number,title,state,isDraft,\
  author,baseRefName,headRefName,\
  statusCheckRollup,reviewDecision,\
  mergeable,mergeStateStatus,\
  createdAt,updatedAt

# 2. Get check status (IMPORTANT: Handle exit code!)
# Exit code 1 means checks failed, NOT command failed
gh pr checks <PR_NUMBER> 2>&1 || true

# Or capture for later analysis
check_output=$(gh pr checks <PR_NUMBER> 2>&1 || true)
check_exit_code=$?
```

**CRITICAL:** Always use `|| true` or handle exit code when using `gh pr checks`:
- Exit code 0 = All checks passed
- Exit code 1 = Some checks failed (this is NORMAL, not an error!)
- The output is valid regardless of exit code

### Parse Response

The response contains:

| Field | Description |
|-------|-------------|
| `state` | OPEN, CLOSED, MERGED |
| `isDraft` | Is this a draft PR? |
| `reviewDecision` | APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED |
| `mergeable` | MERGEABLE, CONFLICTING, UNKNOWN |
| `mergeStateStatus` | Overall merge status |
| `statusCheckRollup` | Array of all status checks |

## Phase 3: Analyze Status Checks

### Parse Status Check Rollup

```bash
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '
  .statusCheckRollup[] |
  {
    name: (.name // .context),
    conclusion: .conclusion,
    status: .status,
    detailsUrl: .detailsUrl,
    checkType: (if .workflowName then "GitHub Actions" else "External Check" end),
    workflowName: .workflowName
  }
'
```

### Categorize Results

Group checks by conclusion:

```bash
# Count by status
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '
  .statusCheckRollup |
  group_by(.conclusion) |
  map({
    conclusion: .[0].conclusion,
    count: length,
    checks: [.[].name]
  })
'
```

### Check Conclusions

| Conclusion | Status | Action Required |
|------------|--------|-----------------|
| `SUCCESS` | ✅ Passed | None |
| `FAILURE` | ❌ Failed | **Investigate** |
| `ERROR` | ⚠️ Error | **Investigate** |
| `PENDING` | 🔄 Running | Wait |
| `SKIPPED` | ⏭️ Skipped | Verify if intentional |
| `CANCELLED` | 🚫 Cancelled | Re-run if needed |
| `TIMED_OUT` | ⏱️ Timeout | Optimize or re-run |

## Phase 4: Fetch Failure Details

For each FAILURE or ERROR:

### Step 4.1: Get Check Run ID

```bash
# Get check run ID for failed check
gh api repos/{owner}/{repo}/commits/<HEAD_SHA>/check-runs \
  --jq '.check_runs[] | select(.name == "<CHECK_NAME>") | {id, name, conclusion, html_url}'
```

### Step 4.2: Get Check Run Details

```bash
# Get detailed output for a check run
gh api repos/{owner}/{repo}/check-runs/<CHECK_RUN_ID> --jq '
  {
    name: .name,
    conclusion: .conclusion,
    output: {
      title: .output.title,
      summary: .output.summary,
      text: .output.text
    },
    html_url: .html_url
  }
'
```

### Step 4.3: Get Workflow Run Logs (GitHub Actions)

If the check is a GitHub Actions workflow:

```bash
# Get workflow run ID from check
gh api repos/{owner}/{repo}/check-runs/<CHECK_RUN_ID> --jq '.check_suite.id'

# Get logs for failed jobs
gh run view <RUN_ID> --log-failed
```

### Step 4.4: Extract Error Messages

Common error patterns to look for in logs:

| Pattern | Meaning |
|---------|---------|
| `FAILED` / `ERROR` | Test or build failure |
| `Compilation failed` | Build error |
| `Test failed:` | Specific test failure |
| `AssertionError` | Test assertion failure |
| `SyntaxError` | Code syntax error |
| `lint: error` | Linting error |
| `coverage: failed` | Code coverage below threshold |
| `timeout` | Operation timed out |

## Phase 5: Explain and Recommend

### Complete Example Workflow

```bash
# Complete workflow for checking PR status
PR_NUMBER=<PR_NUMBER>

echo "Checking PR #$PR_NUMBER status..."

# 1. Get PR metadata
pr_data=$(gh pr view $PR_NUMBER --json \
  number,title,state,isDraft,author,\
  statusCheckRollup,reviewDecision,mergeable)

# 2. Get human-readable check output (HANDLE EXIT CODE!)
echo -e "\n=== Check Status ==="
gh pr checks $PR_NUMBER 2>&1 || true
check_status=$?

# 3. Analyze results
if [ $check_status -eq 0 ]; then
    echo -e "\n✅ All checks passed!"
else
    echo -e "\n⚠️  Some checks failed (see details above)"

    # Get failed checks from JSON
    echo -e "\nFailed checks:"
    echo "$pr_data" | jq -r '.statusCheckRollup[] |
      select(.conclusion == "FAILURE" or .conclusion == "ERROR") |
      "- \(.name): \(.conclusion)"'
fi

# 4. Check review status
review_status=$(echo "$pr_data" | jq -r '.reviewDecision // "REVIEW_REQUIRED"')
echo -e "\n=== Review Status ==="
echo "Status: $review_status"

# 5. Check merge status
mergeable=$(echo "$pr_data" | jq -r '.mergeable')
echo -e "\n=== Merge Status ==="
echo "Mergeable: $mergeable"
```

### Generate Status Report

```markdown
# PR Status Report: #<PR_NUMBER> - <PR_TITLE>

## Overall Status

**Merge Readiness:** [Ready ✅ | Not Ready ❌ | Waiting 🔄]

| Check Category | Status |
|----------------|--------|
| CI/CD Checks | <STATUS> |
| Code Reviews | <STATUS> |
| Merge Conflicts | <STATUS> |
| Draft Status | <STATUS> |

---

## Status Checks Summary

**Total:** X checks | ✅ Y passed | ❌ Z failed | 🔄 W pending

### ✅ Passed Checks (Y)

- Check name 1
- Check name 2

### ❌ Failed Checks (Z)

#### 1. Check Name

**Status:** FAILURE
**Type:** [GitHub Actions / External Check]
**Details URL:** <url>

**Error:**
```
<extracted error message>
```

**Explanation:**
<Plain English explanation of what went wrong>

**Recommended Fix:**
<Actionable steps to fix the issue>

**Related Files:**
- file1.cpp:42
- file2.py:15

---

#### 2. Another Failed Check

...

### 🔄 Pending Checks (W)

- Check name (waiting for completion)

---

## Review Status

**Decision:** [APPROVED ✅ | CHANGES_REQUESTED ❌ | REVIEW_REQUIRED 🔍]

<Summary of review status>

---

## Merge Status

**Mergeable:** [Yes ✅ | No (Conflicts) ❌ | Unknown ⚠️]

<Details about merge conflicts if any>

---

## Recommendations

1. <Recommendation 1>
2. <Recommendation 2>

## Next Steps

- [ ] Fix failing checks
- [ ] Resolve merge conflicts (if any)
- [ ] Address review comments (if any)
- [ ] Re-run failed checks
```

### Common Failure Explanations

#### Build Failures

```markdown
**Compilation Error**

The C++ build failed due to compilation errors.

**Common causes:**
- Missing header files
- Syntax errors  - Undefined symbols
- Incompatible types

**Fix:**
1. Check the error message for the specific file and line
2. Review recent changes to that file
3. Ensure all dependencies are properly included
4. Run build locally: `cmake --build build`
```

#### Test Failures

```markdown
**Unit Test Failure**

Test suite failed - X out of Y tests failed.

**Common causes:**
- Logic errors in new code
- Broken assumptions
- Missing test data
- Flaky tests (intermittent failures)

**Fix:**
1. Run the specific test locally: `./build/test_binary --gtest_filter=TestName`
2. Check test output for assertion failures
3. Debug the failing test case
4. If flaky, check for timing issues or race conditions
```

#### Lint/Style Failures

```markdown
**Code Style Check Failed**

Code doesn't meet style guidelines.

**Common causes:**
- Formatting issues (indentation, spacing)
- Naming violations
- Missing documentation

**Fix:**
1. Run linter locally: `clang-format -i file.cpp`
2. Check linter output for specific violations
3. Apply auto-fix if available
4. Review style guide for manual fixes
```

#### Coverage Failures

```markdown
**Code Coverage Below Threshold**

New code lacks sufficient test coverage.

**Current coverage:** X%
**Required:** Y%

**Fix:**
1. Identify untested code paths
2. Add unit tests for new functions/branches
3. Run coverage report locally: `gcov` or `pytest --cov`
4. Ensure edge cases are tested
```

## Integration with Other Skills

### After PR Creation (from prepare-pull-request)

```markdown
After creating a PR with `git/prepare-pull-request`:
→ Invoke `git/pr-status` to check initial CI/CD results
→ Wait for checks to complete
→ Address any immediate failures
```

### During PR Review (from review-pull-request)

```markdown
While reviewing with `git/review-pull-request`:
→ Invoke `git/pr-status` to verify checks before review
→ Ensure CI/CD passes before detailed code review
→ Check for merge conflicts
```

## Advanced: Custom Status Checks

### Adding Required Status Checks

Some repos require specific checks to pass. List them:

```bash
# Get required status checks for a branch
gh api repos/{owner}/{repo}/branches/<BRANCH>/protection \
  --jq '.required_status_checks.contexts'
```

### Re-running Failed Checks

```bash
# Re-run failed GitHub Actions workflow
gh run rerun <RUN_ID> --failed

# Re-run all checks
gh run rerun <RUN_ID>
```

## Error Handling

### PR Not Found

```markdown
❌ PR #<NUMBER> not found.

**Possible causes:**
- Invalid PR number
- PR is in different repository
- Insufficient permissions

**Fix:**
- Verify PR number: `gh pr list`
- Check you're in correct repository
- Ensure gh is authenticated: `gh auth status`
```

### No Status Checks

```markdown
ℹ️ No status checks configured for this PR.

This repository may not have CI/CD pipelines set up.
The PR can be merged without automated checks (if allowed by repo settings).
```

### Checks Still Running

```markdown
🔄 Some checks are still running...

**Pending:**
- Check 1 (GitHub Actions)
- Check 2 (External)

**Recommendation:** Wait for checks to complete before merging.

Would you like me to:
1. Wait and re-check in 1 minute
2. Show current results only
```

## Quick Reference

```bash
# Full status check workflow
gh pr view <PR_NUMBER> --json statusCheckRollup,reviewDecision,mergeable

# Get only failed checks
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion == "FAILURE")'

# Check if PR is ready to merge
gh pr view <PR_NUMBER> --json mergeable,statusCheckRollup --jq '
  if .mergeable == "MERGEABLE" and
     (.statusCheckRollup | all(.conclusion == "SUCCESS"))
  then "✅ Ready to merge"
  else "❌ Not ready to merge"
  end
'
```

## References

- [GitHub Check Runs API](https://docs.github.com/en/rest/checks/runs)
- [gh pr view documentation](https://cli.github.com/manual/gh_pr_view)
- [GitHub Actions Workflow Runs](https://docs.github.com/en/rest/actions/workflow-runs)
