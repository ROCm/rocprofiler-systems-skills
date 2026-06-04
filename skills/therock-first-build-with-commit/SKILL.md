---
name: therock-first-build-with-commit
description: Find the first TheRock nightly build that includes a given rocm-systems commit
---

# Find the First TheRock Nightly Build to Include a Commit

Walks scheduled runs of the `Release portable Linux packages` workflow (the one that actually publishes nightly manifests to S3) on `ROCm/TheRock` in chronological order, starting at (or just before) the commit's date, and reports the first build whose `rocm-systems` `pin_sha` is an ancestor of (or equal to) the user's commit.

Backed by an executable helper script: [find_first_build.py](find_first_build.py).

## When to Use

Use this skill when:
- User asks "what is the first nightly build to include commit `<sha>`?"
- User asks "has my fix shipped yet, and if so where can I grab it?"
- Bisecting which nightly first contained a regression
- Verifying a PR landed in a downstream consumer (a TheRock-based image, package, or wheel)

Unless the user says otherwise, this skill targets the `rocm-systems` submodule on `ROCm/rocm-systems`.

## Inputs

| Flag | Required | Default | Notes |
|------|----------|---------|-------|
| `--commit SHA` | yes | - | Full 40-char SHA preferred (>= 7 chars); must be visible on `--repo` |
| `--repo OWNER/REPO` | no | `ROCm/rocm-systems` | The repo that hosts the commit |
| `--submodule NAME` | no | `rocm-systems` | Submodule name in `therock_manifest.json` |
| `--gpu-family FAMILY` | no | `gfx94X-dcgpu` | Manifest folder name; `pin_sha` is identical across families, so any one is fine |
| `--platform {linux,windows}` | no | `linux` | Bucket prefix segment |
| `--workflow ID` | no | `161312296` | TheRock's `Release portable Linux packages` workflow id (the one that publishes nightly manifests). `CI Nightly` (id `171171403`) does *not* publish to the canonical S3 path. |
| `--since YYYY-MM-DD` | no | commit date minus 1 day | Lower bound for the run listing |
| `--max-runs N` | no | `90` | Caps the linear walk (Actions retention is ~90 days) |
| `--json` | no | off | Emit final result as JSON on stdout (per-iteration progress still goes to stderr) |

## Prerequisites

- `gh` CLI installed and authenticated against `github.com` (see [skills/git-gh-client/SKILL.md](../git-gh-client/SKILL.md) for setup).
- `python3 >= 3.8` (standard library only; no `pip install` needed).
- Outbound HTTPS to `github.com` and `therock-nightly-artifacts.s3.amazonaws.com`.

Quick sanity check:

```bash
gh auth status
python3 --version
```

## Process

The skill is a thin wrapper around the bundled script. The agent's job is to:

1. Confirm prerequisites.
2. Determine the SKILL directory (the folder containing this `SKILL.md`); call it `SKILL_DIR`. Typically `~/.claude/skills/therock-first-build-with-commit/`.
3. Invoke the script with the user's commit:

   ```bash
   python3 "$SKILL_DIR/find_first_build.py" --commit <SHA>
   ```

4. Stream the per-iteration progress (stderr) to the user as it runs. When done, present the final result (stdout) verbatim.
5. If the user wants to pipe the result into other tooling, add `--json`:

   ```bash
   python3 "$SKILL_DIR/find_first_build.py" --commit <SHA> --json
   ```

### Resolving non-SHA inputs

If the user provides a PR URL/number instead of a SHA, resolve it first:

```bash
gh api repos/ROCm/rocm-systems/pulls/<PR_NUMBER> \
  --jq '{merged, merge_commit_sha, head_sha, base_ref: .base.ref}'
```

Use `merge_commit_sha` (the commit that landed on the base branch) - **not** `head_sha` (the tip of the PR branch before merge). Then pass `merge_commit_sha` to `--commit`.

## Examples

### Example 1: Commit landed today, find the next nightly

```bash
SKILL_DIR=~/.claude/skills/therock-first-build-with-commit
python3 "$SKILL_DIR/find_first_build.py" \
  --commit 570dcd3205005305b32b50996be1d7154d399c4a
```

Sample stderr (progress):

```text
Resolving commit 570dcd3205005305b32b50996be1d7154d399c4a on ROCm/rocm-systems...
  full sha: 570dcd3205005305b32b50996be1d7154d399c4a
  committed: 2026-05-28T16:08:55+00:00
Listing scheduled runs of workflow 161312296 since 2026-05-27 (max 90)...
Inspecting 8 runs in chronological order.
[  1/8] run=26552616764 created=2026-05-28T03:21:11Z pin=ed975342 status=behind    ahead_by=0 behind_by=212
[  2/8] run=26615892682 created=2026-05-29T03:19:41Z pin=4a30df8d status=behind    ahead_by=0 behind_by=75
[  3/8] run=26673017729 created=2026-05-30T03:16:41Z pin=cb656124 status=behind    ahead_by=0 behind_by=7
[  4/8] run=26701995708 created=2026-05-31T03:19:59Z pin=cb656124 status=behind    ahead_by=0 behind_by=7
[  5/8] run=26733368587 created=2026-06-01T03:21:50Z pin=cb656124 status=behind    ahead_by=0 behind_by=7
[  6/8] run=26796279962 created=2026-06-02T03:21:38Z pin=b8c378ef status=ahead     ahead_by=52 behind_by=0  FOUND
```

Sample stdout (final result):

```text
First nightly build to include 570dcd3205005305b32b50996be1d7154d399c4a:
  run_id:           26796279962
  created_at:       2026-06-02T03:21:38Z
  the_rock_commit:  412f3070ee240a2bd4df70b04d699c6cad7d3b09
  pin_sha:          b8c378ef2c7220a68122d13b81dab5addd61e016
  Repo snapshot:    https://github.com/ROCm/rocm-systems/tree/b8c378ef2c7220a68122d13b81dab5addd61e016
  GitHub Actions:   https://github.com/ROCm/TheRock/actions/runs/26796279962
  Compare:          https://github.com/ROCm/rocm-systems/compare/570dcd32...b8c378ef  (full URL below)
  Compare (full):   https://github.com/ROCm/rocm-systems/compare/570dcd3205005305b32b50996be1d7154d399c4a...b8c378ef2c7220a68122d13b81dab5addd61e016
  Manifest:         https://therock-nightly-artifacts.s3.amazonaws.com/26796279962-linux/manifests/gfx94X-dcgpu/therock_manifest.json
```

### Example 2: Commit hasn't shipped yet

```bash
python3 "$SKILL_DIR/find_first_build.py" --commit <fresh_sha>
```

Final stdout:

```text
No nightly build in the inspected window contains <fresh_sha>.
  Inspected runs: 1 (since 2026-06-03)
  The commit may still ship in a later nightly; rerun later or widen --max-runs / --since.
```

Exit code is `5` (no match). Suggest the user rerun in a day, or widen the window if their commit is older.

### Example 3: Old commit - widen the search window

```bash
python3 "$SKILL_DIR/find_first_build.py" \
  --commit <old_sha> \
  --since 2026-03-01 \
  --max-runs 90
```

### Example 4: JSON output for piping

```bash
python3 "$SKILL_DIR/find_first_build.py" --commit <sha> --json \
  | jq '.first_build.run_id // empty'
```

### Example 5: PR -> first build (compose with `gh`)

```bash
PR=6445
COMMIT=$(gh api repos/ROCm/rocm-systems/pulls/$PR --jq .merge_commit_sha)
python3 "$SKILL_DIR/find_first_build.py" --commit "$COMMIT"
```

## Output

This skill produces:

- Per-iteration progress on stderr (one line per nightly run, with status and ahead/behind counts).
- Final result on stdout - either a human-readable block (default) or a JSON object (`--json`).
- Exit codes: `0` found, `3` invalid input, `4` upstream/network failure, `5` exhausted window without finding. (`5` rather than `2` so callers can distinguish "no match" from Python's argparse default of `2`.)

No files are written.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Passing a PR number instead of a SHA | Resolve via `gh api repos/.../pulls/<N> --jq .merge_commit_sha` first |
| Passing the PR's `head_sha` instead of `merge_commit_sha` | The head SHA may not exist on the base branch (especially after squash); always use `merge_commit_sha` |
| Setting `--since` *after* the commit's committer date | The walk would skip the very window where the fix could appear; if unsure, omit `--since` and let the default handle it |
| Assuming `pin_sha` varies by GPU family | It does not - the script always queries one family because all families pin the same `rocm-systems` SHA |
| Treating exit code `5` as a script failure | Exit code `5` means "no nightly in the window contains the commit yet" - rerun later or widen `--max-runs` / `--since`. (Note: argparse uses exit `2` for CLI errors like missing `--commit`, so `5` lets callers distinguish "no match" from "bad invocation".) |
| Reading from stdout while the script is still running | Per-iteration progress goes to stderr; redirect appropriately (`2>progress.log` or just observe both) |

## Troubleshooting

### Many `manifest=missing (skipped)` lines

Cause: not every workflow run publishes artifacts. Failed, cancelled, or in-progress runs typically have no manifest. The script skips them and continues.

If *all* runs are skipped, the more likely cause is wrong `--platform` or `--gpu-family`. Verify against one known-good build first using [therock-build-to-commit](../therock-build-to-commit/SKILL.md):

```bash
curl -fsSL https://therock-nightly-artifacts.s3.amazonaws.com/<RUN_ID>-linux/manifests/gfx94X-dcgpu/therock_manifest.json | head -c 200
```

### `gh` rate-limit errors

Cause: anonymous rate limit hit, or token scope too narrow.

Steps:
1. Confirm a personal token is configured: `gh auth status`.
2. For ephemeral environments, export `GH_TOKEN=<your_pat>` before invoking the script.
3. Reduce `--max-runs` to limit API calls.

### `error: could not resolve commit <sha> on ROCm/rocm-systems`

Cause: the SHA is on a private fork or not pushed to upstream.

Steps:
1. Verify visibility: `gh api repos/ROCm/rocm-systems/commits/<sha> --jq .sha`.
2. If the SHA is fork-only, ask the user to push to upstream or rebase the work onto an upstream-visible base.

### Script reports `status=null`

Cause: GitHub returns extra states for very large diffs.

The script logs `ahead_by`/`behind_by` either way. Use that as the source of truth: `behind_by == 0` -> commit is an ancestor (included).

## Integration with Other Skills

| Relationship | Skill | Why |
|--------------|-------|-----|
| Calls | [git-gh-client](../git-gh-client/SKILL.md) | For `gh` availability and authentication setup |
| Sibling | [therock-build-to-commit](../therock-build-to-commit/SKILL.md) | Reverse direction: given a build, what's the pinned commit? |
| Sibling | [therock-commit-in-build](../therock-commit-in-build/SKILL.md) | Single-build spot check (you already know which build to look at) |

Decision matrix:

| User asks... | Use |
|--------------|-----|
| "What commit is in build X?" | `therock-build-to-commit` |
| "Is commit Y in build X?" | `therock-commit-in-build` |
| "What's the first build containing commit Y?" | this skill |

## Notes

- This is the first skill in this repository to ship an executable helper script. The rationale: this lookup has multiple knobs (`--commit`, `--repo`, `--submodule`, `--gpu-family`, `--platform`, `--workflow`, `--since`, `--max-runs`, `--json`), needs structured per-iteration progress, and is most useful when reusable from a shell prompt or CI - not just from inside an agent session.
- Standard library only; no `pip install` required.
- Bounded by GitHub Actions' default 90-day retention - older commits may not be locatable via this method even if they did ship.
- Source recipe: [Wiki - Helpful Links and Information](https://amd.atlassian.net/wiki/spaces/AGSRCIT/pages/1306934643), *TheRock Nightly Builds* section.
