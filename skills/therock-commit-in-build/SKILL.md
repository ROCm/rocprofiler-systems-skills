---
name: therock-commit-in-build
description: Check whether a given rocm-systems commit is included in a specific TheRock nightly build
---

# Check if a rocm-systems Commit is in a TheRock Nightly Build

Answers the question *"Is my rocm-systems commit XYZ included in TheRock build X?"* by resolving the build to its `rocm-systems` `pin_sha` and asking GitHub whether the user's commit is an ancestor of that pin.

## When to Use

Use this skill when:
- User asks "is commit `<sha>` in TheRock build `<X>`?"
- User wants to know whether a recent fix has shipped in a nightly
- User shares both a nightly URL/run-id and a commit hash
- Another skill needs a yes/no answer about commit inclusion (not just the `pin_sha`)

Unless the user says otherwise, this skill targets the `rocm-systems` repository (`ROCm/rocm-systems`).

Run URLs for current nightlies are on [`ROCm/rockrel`](https://github.com/ROCm/rockrel/actions/workflows/multi_arch_release.yml); legacy pre-June-2026 runs are on `ROCm/TheRock`. See [therock-build-to-commit](../therock-build-to-commit/SKILL.md) for manifest and packages URL patterns.

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Commit SHA | yes | Full 40-char SHA recommended; minimum 7 chars; must be a commit on `ROCm/rocm-systems` (or reachable from a tag/branch there) |
| Build URL or run-id | yes | Current: `packages-multi-arch/deb/...` URL, index path, or bare run-id. Legacy `/deb/...` URLs still parse. |
| `platform` | no | Default `linux` (forwarded to manifest fetch) |

## Prerequisites

- `gh` CLI installed and authenticated against `github.com` (see `git-gh-client` skill for setup).
- Network access to `github.com` for the compare API.
- The user's commit must exist on `ROCm/rocm-systems` (not only in a private fork).

Verify quickly:

```bash
gh auth status
gh api repos/ROCm/rocm-systems/commits/<COMMIT_SHA> --jq '.sha' >/dev/null && echo "commit visible"
```

## Process

### Phase 1: Resolve the Build to a pin_sha

Invoke `therock-build-to-commit` with the user's build URL/run-id (and any `platform` overrides). Capture the reported `pin_sha`.

Do not re-implement the manifest fetch here - delegate to keep behavior consistent.

```bash
# Pseudocode: capture pin_sha emitted by therock-build-to-commit
PIN_SHA=<from therock-build-to-commit>
```

If `therock-build-to-commit` fails to produce a `pin_sha`, surface its error verbatim and stop. Do not guess.

### Phase 2: Ancestry Check via GitHub Compare

Ask GitHub whether `COMMIT_SHA` is an ancestor of `PIN_SHA` by comparing them:

```bash
COMMIT_SHA="$1"
STATUS=$(gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" --jq '.status')
```

Interpret `.status`:

| Status | Meaning | Verdict |
|--------|---------|---------|
| `identical` | `COMMIT_SHA == PIN_SHA` | **Included** (it IS the build's pin) |
| `ahead` | `PIN_SHA` is ahead of `COMMIT_SHA` -> `COMMIT_SHA` is an ancestor of `PIN_SHA` | **Included** |
| `behind` | `PIN_SHA` is behind `COMMIT_SHA` -> commit was made after the build's pin | **Not included** |
| `diverged` | The two commits share history but neither is an ancestor of the other | **Not included** |

The `gh api ... compare` call also returns counts that are useful to surface:

```bash
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" \
  --jq '{status, ahead_by, behind_by, total_commits}'
```

### Phase 3: Report

Report back in this exact shape:

```text
Commit:           <COMMIT_SHA>
Build:            <RUN_ID>  (pin_sha=<PIN_SHA>)
Status:           <STATUS>   (ahead_by=<N>, behind_by=<M>)
Verdict:          <Included | Not included>
Reason:           <one-line explanation derived from Status row above>
Compare URL:      https://github.com/ROCm/rocm-systems/compare/<COMMIT_SHA>...<PIN_SHA>
Build snapshot:   https://github.com/ROCm/rocm-systems/tree/<PIN_SHA>
```

## Examples

### Example 1: Included (commit is an ancestor of pin)

```bash
COMMIT_SHA=abc1234abc1234abc1234abc1234abc1234abcd
RUN_ID=22561649510
PIN_SHA=$(./therock-build-to-commit "$RUN_ID")     # via the helper skill
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" --jq '.status'
# -> "ahead"
# Verdict: Included
```

### Example 2: Exact match

```bash
COMMIT_SHA=c7da590396ceef1afaaa1b971f3b3d7d6e3562a9
PIN_SHA=c7da590396ceef1afaaa1b971f3b3d7d6e3562a9
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" --jq '.status'
# -> "identical"
# Verdict: Included (this commit IS the build's pin)
```

### Example 3: Not included (commit landed after the build)

```bash
COMMIT_SHA=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
RUN_ID=22561649510
PIN_SHA=$(./therock-build-to-commit "$RUN_ID")
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" --jq '.status'
# -> "behind"
# Verdict: Not included (the commit is newer than pin_sha; wait for the next nightly that pins past it)
```

### Example 4: Diverged (commit lives on a branch the pin never reached)

```bash
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" --jq '.status'
# -> "diverged"
# Verdict: Not included (commit is on a side branch never merged before pin_sha)
```

## Output

This skill produces:

- A clear yes/no verdict on inclusion
- The `pin_sha` for the build, the GitHub `compare` status, and `ahead_by`/`behind_by` counts
- Links to the GitHub compare view and the repo snapshot at `pin_sha`

No files are written.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Equating "commit on a branch" with "commit in build" | Only commits reachable from `pin_sha` are in the build. A merged-but-pinned-later commit is **not** in earlier builds |
| Using a fork's SHA that upstream cannot resolve | The compare API runs against `ROCm/rocm-systems`; the SHA must be visible there. If the user has only a fork, ask them to push to upstream or share an upstream-resolvable SHA |
| Abbreviating the SHA below 7 chars | GitHub may refuse or resolve ambiguously; require at least 7 chars and prefer the full 40 |
| Skipping the helper and hand-coding S3 lookups | Always delegate to `therock-build-to-commit` so URL parsing and manifest handling stay in one place |
| Treating exit code != 0 from `gh api` as "not included" | A non-zero exit can also mean the SHA is unknown to GitHub. Read stderr; do not silently report "Not included" on lookup failure |

## Troubleshooting

### `gh: HTTP 404: Not Found` from the compare endpoint

Cause: at least one of `COMMIT_SHA` or `PIN_SHA` is not visible on `ROCm/rocm-systems`.

Steps:
1. Verify each SHA individually:
   ```bash
   gh api repos/ROCm/rocm-systems/commits/<SHA> --jq '.sha'
   ```
2. If `COMMIT_SHA` is missing, ask the user where it lives (fork? unmerged branch?).
3. If `PIN_SHA` is missing, the manifest may be stale or referencing an unreachable commit - report this to the user; do not guess inclusion.

### `STATUS` is `null` or unexpected

GitHub occasionally returns extra states for very large diffs. Fall back to inspecting `ahead_by` and `behind_by` directly:

```bash
gh api "repos/ROCm/rocm-systems/compare/${COMMIT_SHA}...${PIN_SHA}" \
  --jq '{status, ahead_by, behind_by}'
```

If `behind_by == 0`, the commit is an ancestor (included). If `behind_by > 0` and `ahead_by == 0`, it's strictly newer than the pin (not included).

### `gh api` returns auth errors

Run `gh auth login` (see the `git-gh-client` skill for the full flow). The compare endpoint is public for public repos but `gh` still requires auth to make requests.

## Integration with Other Skills

| Relationship | Skill | Why |
|--------------|-------|-----|
| Calls | `therock-build-to-commit` | To resolve the build to a `pin_sha` |
| Calls | `git-gh-client` | For `gh` availability checks and auth |
| Called by (typical) | Ad-hoc user questions like "did fix XYZ ship in last night's build?" | |

## Notes

- The compare API is the simplest reliable ancestry check that does not require a local clone of `rocm-systems`. If a local clone is available, `git merge-base --is-ancestor <commit> <pin_sha>` is an offline equivalent (exit code 0 -> included).
- Source of this recipe: [Wiki - Helpful Links and Information](https://amd.atlassian.net/wiki/spaces/AGSRCIT/pages/1306934643), *TheRock Nightly Builds* section.
