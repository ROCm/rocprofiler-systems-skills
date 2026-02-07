---
name: git/gh-client
description: Core GitHub CLI operations - check availability, search PRs, get PR details, check status. Invoked by other git skills.
---

# GitHub CLI (gh) Client Skill

Base skill for interacting with GitHub via the `gh` CLI tool. This skill is invoked by other git skills that need GitHub operations.

## Purpose

Provides reusable GitHub CLI functionality:
- ✅ Check if `gh` is installed and authenticated
- 📋 **List all PRs for the repository**
- 🔍 **Search and filter PRs** (by author, label, date, state, etc.)
- 📄 Get PR details and metadata
- ✅ Check PR status checks and CI/CD results
- 📝 Create and manage pull requests

## Common Use Cases

This skill is used both **directly** (when user asks to list/filter PRs) and **indirectly** (invoked by other skills):

**Direct usage:**
- "List all open PRs" → Shows all open PRs in current repo
- "Find PRs by username" → Filters PRs by author
- "Show PRs with label 'bug'" → Filters by label
- "List recent PRs" → Shows PRs sorted by date

**Invoked by other skills:**
- `git/prepare-pull-request` - Creating PRs
- `git/review-pull-request` - Reviewing PRs
- `git/pull-request-status` - Checking PR status and CI/CD

## Phase 1: Check gh CLI Availability

**ALWAYS check if gh is installed before attempting gh commands.**

### Check Installation

```bash
which gh
```

### Check Authentication

```bash
gh auth status
```

### If Not Installed

Provide installation instructions:

```markdown
The GitHub CLI (`gh`) is required for this operation.

## Installation

**Linux (Debian/Ubuntu):**
```bash
sudo apt install gh
```

**Linux (Fedora/RHEL/CentOS):**
```bash
sudo dnf install gh
```

**macOS:**
```bash
brew install gh
```

**Windows:**
```powershell
winget install --id GitHub.cli
```

**Other platforms:**
Visit https://cli.github.com/manual/installation

## Authentication

After installation, authenticate with:
```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.
```

### If Not Authenticated

```bash
gh auth login
```

## Phase 2: List and Filter Pull Requests

**This is a CORE capability - used both directly by users and by other skills.**

### Basic PR Listing

```bash
# List all PRs in the repository (defaults to open PRs)
gh pr list

# Show more PRs (default is 30)
gh pr list --limit 100

# List with specific columns
gh pr list --json number,title,author,createdAt,state

# Pretty table format (human-readable)
gh pr list | column -t
```

### Filter by State

```bash
# Open PRs only (default)
gh pr list --state open

# All closed PRs
gh pr list --state closed

# Only merged PRs
gh pr list --state merged

# All PRs (open, closed, merged)
gh pr list --state all
```

### Filter by Author

```bash
# PRs by specific user
gh pr list --author <username>

# PRs by current user
gh pr list --author @me

# PRs by multiple authors (using search)
gh pr list --search "author:user1 author:user2"
```

### Filter by Label

```bash
# PRs with single label
gh pr list --label bug

# PRs with multiple labels (ANY match)
gh pr list --label "bug,priority:high"

# PRs with specific label pattern
gh pr list --search "label:enhancement"
```

### Filter by Assignee/Reviewer

```bash
# PRs assigned to user
gh pr list --assignee <username>

# PRs assigned to me
gh pr list --assignee @me

# PRs requesting review from user
gh pr list --search "review-requested:username"

# PRs reviewed by user
gh pr list --search "reviewed-by:username"
```

### Search by Keywords

```bash
# Search in title and body
gh pr list --search "keyword"

# Search in title only
gh pr list --search "in:title keyword"

# Search in body only
gh pr list --search "in:body keyword"

# Multiple keywords (AND logic)
gh pr list --search "keyword1 keyword2"
```

### Filter by Date

```bash
# PRs created in last 7 days
gh pr list --search "created:>$(date -d '7 days ago' +%Y-%m-%d)"

# PRs updated in last 24 hours
gh pr list --search "updated:>$(date -d '1 day ago' +%Y-%m-%d)"

# PRs created in specific date range
gh pr list --search "created:2024-01-01..2024-01-31"

# PRs created before a date
gh pr list --search "created:<2024-01-01"
```

### Advanced Filtering

```bash
# Draft PRs
gh pr list --search "is:draft"
gh pr list --draft

# PRs ready for review (not draft)
gh pr list --search "is:open -is:draft"

# PRs with merge conflicts
gh pr list --search "is:open conflicts:>0"

# PRs without tests
gh pr list --search "is:open -label:has-tests"

# PRs needing review
gh pr list --search "is:open review:required"

# Approved PRs
gh pr list --search "is:open review:approved"

# PRs with changes requested
gh pr list --search "is:open review:changes_requested"

# PRs by base branch
gh pr list --base main
gh pr list --base develop

# PRs by head branch pattern
gh pr list --search "head:feature/*"
```

### Combined Filters (Real-World Examples)

```bash
# My open PRs that need review
gh pr list --author @me --state open --search "review:required"

# Bug fixes waiting for approval
gh pr list --label bug --search "is:open review:approved"

# Recent PRs by specific author
gh pr list --author username --search "created:>$(date -d '7 days ago' +%Y-%m-%d)"

# High priority PRs with failures
gh pr list --label "priority:high" --search "is:open status:failure"

# PRs ready to merge (approved, no conflicts, checks passing)
gh pr list --search "is:open review:approved status:success -conflicts:>0"
```

### Sort and Format Output

```bash
# Sort by creation date (newest first)
gh pr list --json number,title,createdAt --jq 'sort_by(.createdAt) | reverse | .[] | "#\(.number) - \(.title)"'

# Sort by updated date
gh pr list --json number,title,updatedAt --jq 'sort_by(.updatedAt) | reverse | .[] | "#\(.number) - \(.title) (updated: \(.updatedAt))"'

# Custom formatted output
gh pr list --json number,title,author,state,createdAt --jq '.[] |
  "#\(.number) [\(.state)] \(.title) by @\(.author.login) (\(.createdAt[:10]))"'

# CSV format for export
gh pr list --json number,title,author,state,createdAt --jq -r '
  ["Number","Title","Author","State","Created"],
  (.[] | [.number, .title, .author.login, .state, .createdAt]) |
  @csv'

# Count PRs by label
gh pr list --json labels --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length})'
```

### Get PR Details

```bash
# View PR summary (human-readable)
gh pr view <PR_NUMBER>

# IMPORTANT: Avoid deprecated fields
# DO NOT request: projectCards, projectItems (deprecated)
# Safe fields to request:
gh pr view <PR_NUMBER> --json number,title,body,author,state,baseRefName,headRefName,createdAt,updatedAt,labels,reviews,files,commits

# Get PR diff
gh pr diff <PR_NUMBER>

# Get PR commits
gh pr view <PR_NUMBER> --json commits --jq '.commits[] | "\(.oid[0:7]) \(.messageHeadline)"'

# Get changed files
gh pr view <PR_NUMBER> --json files --jq '.files[] | .path'

# Get PR checks (CI/CD status)
gh pr view <PR_NUMBER> --json statusCheckRollup
```

**Common Error:** If you see "Projects (classic) is being deprecated" error:
- This means you're requesting deprecated fields (projectCards, projectItems)
- Solution: Only request the safe fields listed above

## Phase 3: PR Status Checks

### Using `gh pr checks`

**IMPORTANT:** `gh pr checks` returns exit code 1 when ANY check fails. This is NORMAL behavior, NOT an error.

**ALWAYS handle the exit code when using this command:**

```bash
# ✅ RECOMMENDED: Use || true to ignore exit code
gh pr checks <PR_NUMBER> || true

# ✅ Or capture both output and exit code
if gh pr checks <PR_NUMBER> 2>&1; then
    echo "All checks passed!"
else
    echo "Some checks failed (see output above)"
fi

# ✅ Or capture output for parsing
checks_output=$(gh pr checks <PR_NUMBER> 2>&1 || true)
echo "$checks_output"

# ✅ Store exit code separately
gh pr checks <PR_NUMBER>
check_exit_code=$?
if [ $check_exit_code -eq 0 ]; then
    echo "All checks passed"
else
    echo "Some checks failed (exit code: $check_exit_code)"
fi
```

**Exit code behavior:**
- Exit code 0 = All checks passed ✅
- Exit code 1 = One or more checks failed ❌ (this is NOT a command error!)
- The output is always valid and shows check status regardless of exit code

### Alternative: Get Status Checks via JSON

If you need programmatic parsing, use JSON:

```bash
# Get status checks as JSON (doesn't use exit codes for check status)
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '.statusCheckRollup'
```

### Parse Status Check Results

The `statusCheckRollup` contains all CI/CD checks. Parse it to find failures:

```bash
# Get failed checks
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '
  .statusCheckRollup[] |
  select(.conclusion == "FAILURE" or .conclusion == "ERROR") |
  {
    name: .name,
    conclusion: .conclusion,
    detailsUrl: .detailsUrl
  }
'
```

### Status Check Conclusions

| Conclusion | Meaning |
|------------|---------|
| `SUCCESS` | Check passed |
| `FAILURE` | Check failed |
| `ERROR` | Check encountered an error |
| `PENDING` | Check is running |
| `SKIPPED` | Check was skipped |
| `CANCELLED` | Check was cancelled |
| `TIMED_OUT` | Check timed out |

### Get Check Run Details

```bash
# List all check runs for a PR
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/checks --jq '.check_runs[] | {name, conclusion, output: .output.title}'
```

### Get Workflow Run Logs

If a GitHub Actions check failed, get the logs:

```bash
# Get workflow runs for the PR's head SHA
gh run list --branch <branch-name> --limit 10

# Get logs for a specific run
gh run view <RUN_ID> --log

# Get logs for failed jobs only
gh run view <RUN_ID> --log-failed
```

## Phase 4: Creating Pull Requests

### Create PR with Details

```bash
# Interactive PR creation
gh pr create

# Create with title and body
gh pr create --title "PR Title" --body "Description"

# Create with template (heredoc for multi-line)
gh pr create --title "Feature: Add new capability" --body "$(cat <<'EOF'
## Summary
- Added feature X
- Updated documentation

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass

🤖 Generated with Claude Code
EOF
)"

# Create draft PR
gh pr create --draft --title "WIP: Feature" --body "Work in progress"

# Create with reviewers and assignees
gh pr create --title "Fix bug" --body "..." --reviewer user1,user2 --assignee user3

# Create with labels
gh pr create --title "Fix bug" --body "..." --label bug,priority:high

# Create to different base branch
gh pr create --base develop --head feature-branch --title "..." --body "..."
```

### Auto-fill PR Details

```bash
# Use commit messages to pre-fill
gh pr create --fill

# Use first commit as template
gh pr create --fill-first
```

## Phase 5: PR Management

### Update PR

```bash
# Edit PR title/body
gh pr edit <PR_NUMBER> --title "New title"
gh pr edit <PR_NUMBER> --body "New description"

# Add labels
gh pr edit <PR_NUMBER> --add-label bug,priority:high

# Add reviewers
gh pr edit <PR_NUMBER> --add-reviewer user1,user2

# Mark as ready for review (convert from draft)
gh pr ready <PR_NUMBER>

# Convert to draft
gh pr edit <PR_NUMBER> --draft
```

### Merge PR

```bash
# Merge when checks pass
gh pr merge <PR_NUMBER>

# Merge with specific strategy
gh pr merge <PR_NUMBER> --merge      # Create merge commit
gh pr merge <PR_NUMBER> --squash     # Squash and merge
gh pr merge <PR_NUMBER> --rebase     # Rebase and merge

# Auto-merge when checks pass
gh pr merge <PR_NUMBER> --auto
```

### Close PR

```bash
gh pr close <PR_NUMBER>

# Close with comment
gh pr close <PR_NUMBER> --comment "Closing because..."
```

## Common Use Cases

### Use Case 1: List All PRs in Repository

```bash
# All open PRs (default)
gh pr list

# All PRs (including closed and merged)
gh pr list --state all

# Show more results
gh pr list --limit 100
```

### Use Case 2: Find My PRs

```bash
# My open PRs
gh pr list --author @me --state open

# All my PRs (including closed)
gh pr list --author @me --state all

# My PRs waiting for review
gh pr list --author @me --search "review:required"
```

### Use Case 3: Find PRs by Specific User

```bash
# PRs by username
gh pr list --author username

# Recent PRs by user (last 7 days)
gh pr list --author username --search "created:>$(date -d '7 days ago' +%Y-%m-%d)"
```

### Use Case 4: Find PRs with Specific Labels

```bash
# Bug fixes
gh pr list --label bug

# High priority items
gh pr list --label "priority:high"

# Multiple labels
gh pr list --label "bug,priority:high"

# PRs without certain labels
gh pr list --search "is:open -label:needs-review"
```

### Use Case 5: Find PRs Waiting for Review

```bash
# All PRs needing review
gh pr list --search "is:open review:required"

# PRs assigned to me for review
gh pr list --search "review-requested:@me"

# PRs I've already reviewed
gh pr list --search "reviewed-by:@me"
```

### Use Case 6: Find Recent/Old PRs

```bash
# PRs from last week
gh pr list --search "created:>$(date -d '7 days ago' +%Y-%m-%d)"

# PRs updated today
gh pr list --search "updated:>$(date -d '1 day ago' +%Y-%m-%d)"

# Stale PRs (not updated in 30 days)
gh pr list --search "updated:<$(date -d '30 days ago' +%Y-%m-%d)"
```

### Use Case 7: Check PR Before Merging

```bash
# Get PR status
gh pr view <PR_NUMBER> --json state,statusCheckRollup,reviews

# Check if all checks passed
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '
  .statusCheckRollup |
  map(select(.conclusion != "SUCCESS")) |
  length == 0
'
```

### Use Case 4: Get Failed Check Details

```bash
# Get all failed checks with details
gh pr view <PR_NUMBER> --json statusCheckRollup --jq '
  .statusCheckRollup[] |
  select(.conclusion == "FAILURE") |
  {
    name: .name,
    detailsUrl: .detailsUrl,
    conclusion: .conclusion
  }
'
```

### Use Case 5: Bulk PR Operations

```bash
# Close all draft PRs by me
gh pr list --author @me --search "is:draft" --json number --jq '.[].number' |
  xargs -I {} gh pr close {}

# Add label to all open PRs
gh pr list --state open --json number --jq '.[].number' |
  xargs -I {} gh pr edit {} --add-label needs-review
```

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `gh: command not found` | gh not installed | Install gh CLI (see Phase 1) |
| `Not authenticated` | No GitHub auth | Run `gh auth login` |
| `Could not resolve to a Repository` | Not in git repo or no remote | Check git remote |
| `GraphQL: Resource not accessible by integration` | Insufficient permissions | Check token scopes with `gh auth status` |
| `Pull request not found` | Invalid PR number | Verify PR number with `gh pr list` |
| `Projects (classic) is being deprecated` | Requesting deprecated fields | **DO NOT request:** `projectCards`, `projectItems` fields |
| `gh pr checks` exits with code 1 | Some checks failed | **This is normal!** Use `gh pr view --json statusCheckRollup` instead |

### Deprecated Fields (DO NOT USE)

GitHub is deprecating classic projects. **Never request these fields:**
- ❌ `projectCards`
- ❌ `projectItems`
- ❌ `projectV2Items` (also being phased out)

**Safe fields to use:**
- ✅ `number`, `title`, `body`, `author`, `state`
- ✅ `baseRefName`, `headRefName`, `labels`, `reviews`
- ✅ `statusCheckRollup`, `reviewDecision`, `mergeable`
- ✅ `createdAt`, `updatedAt`, `files`, `commits`

### Handling Check Status Exit Codes

**Problem:** `gh pr checks` returns exit code 1 when checks fail.

**Solution:** ALWAYS handle the exit code when using `gh pr checks`:

```bash
# ✅ CORRECT: Handle exit code with || true
gh pr checks <PR_NUMBER> || true

# ✅ CORRECT: Capture and handle
if ! gh pr checks <PR_NUMBER> 2>&1; then
    echo "Some checks failed (this is expected behavior)"
fi

# ✅ CORRECT: Capture output for parsing
checks_output=$(gh pr checks <PR_NUMBER> 2>&1 || true)

# ❌ WRONG: Don't use without handling exit code
# gh pr checks <PR_NUMBER>  # This will cause bash tool to report "Error: Exit code 1"
```

**Remember:** Exit code 1 means "checks failed", NOT "command failed". The output is still valid and useful!

### Verify Prerequisites

```bash
# Check all prerequisites
cat << 'EOF'
Checking GitHub CLI setup...

1. gh installed: $(which gh > /dev/null && echo "✓" || echo "✗")
2. Authenticated: $(gh auth status > /dev/null 2>&1 && echo "✓" || echo "✗")
3. In git repo: $(git rev-parse --git-dir > /dev/null 2>&1 && echo "✓" || echo "✗")
4. Has remote: $(git remote -v | grep -q origin && echo "✓" || echo "✗")
EOF
```

## Integration with Other Skills

### From prepare-pull-request

```markdown
1. Invoke `git/gh-client` to check if gh is available
2. If available, use gh commands from this skill
3. Create PR using `gh pr create` patterns from Phase 4
```

### From review-pull-request

```markdown
1. Invoke `git/gh-client` to check availability
2. Use PR search/filter from Phase 2
3. Get PR details and diff from Phase 2
```

### From pr-status

```markdown
1. Invoke `git/gh-client` to check availability
2. Use status check queries from Phase 3
3. Parse and explain check failures
```

## Advanced: GitHub GraphQL API

For complex queries, use GitHub's GraphQL API via gh:

```bash
# Custom GraphQL query
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        title
        state
        commits(last: 1) {
          nodes {
            commit {
              statusCheckRollup {
                contexts(first: 100) {
                  nodes {
                    ... on CheckRun {
                      name
                      conclusion
                      detailsUrl
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
' -f owner=OWNER -f repo=REPO -F number=PR_NUMBER
```

## References

- [gh CLI Manual](https://cli.github.com/manual/)
- [gh pr documentation](https://cli.github.com/manual/gh_pr)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
