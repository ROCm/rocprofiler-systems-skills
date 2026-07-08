---
name: therock-build-to-commit
description: Given a TheRock nightly build (URL or run-id), return the rocm-systems pin_sha used in that build
---

# Resolve TheRock Nightly Build to rocm-systems Commit

Resolves a TheRock nightly build to the exact `rocm-systems` commit (`pin_sha`) that was used to produce it, by reading the build's `therock_manifest.json` from S3.

## When to Use

Use this skill when:
- User asks "what rocm-systems commit is in TheRock build X?"
- User provides a TheRock nightly URL (e.g. `https://rocm.nightlies.amd.com/packages-multi-arch/deb/YYYYMMDD-<RUN_ID>/index.html`) or a bare run-id and wants to know what shipped
- User wants the GitHub tree link for the snapshot used by a nightly build
- Another skill needs the `pin_sha` for a build before continuing (e.g. `therock-commit-in-build`)

Unless the user says otherwise, this skill targets the `rocm-systems` submodule.

## Nightly URL Layout (current)

| Artifact | URL pattern |
|----------|-------------|
| **Manifest** (source of truth for `pin_sha`) | `https://therock-nightly-artifacts.s3.amazonaws.com/<RUN_ID>-linux/manifests/therock_manifest.json` |
| **Packages index** (deb repo) | `https://rocm.nightlies.amd.com/packages-multi-arch/deb/<YYYYMMDD>-<RUN_ID>/index.html` |
| **Tarball** | `https://rocm.nightlies.amd.com/tarball-multi-arch/therock-dist-linux-multiarch-<ROCM_PACKAGE_VERSION>.tar.gz` |

`<ROCM_PACKAGE_VERSION>` comes from the manifest field `rocm_package_version` (e.g. `7.14.0a20260624`). The date prefix `<YYYYMMDD>` in the packages URL is the suffix after `a` in that version string (e.g. `20260624`).

**Legacy builds** (before the multi-arch layout) used:
- Packages: `https://rocm.nightlies.amd.com/deb/<YYYYMMDD>-<RUN_ID>/index.html`
- Manifest: `.../manifests/<GPU_FAMILY>/therock_manifest.json` (e.g. `gfx94X-dcgpu`) instead of `.../manifests/therock_manifest.json`

When fetching manifests, try the current path first; fall back to the per-`GPU_FAMILY` path for older runs.

## Inputs

The user provides **one** of:

| Input form | Example |
|------------|---------|
| Full nightly URL (current) | `https://rocm.nightlies.amd.com/packages-multi-arch/deb/20260624-28066115163/index.html` |
| Full nightly URL (legacy) | `https://rocm.nightlies.amd.com/deb/20260302-22561649510/index.html` |
| Index path | `20260624-28066115163` |
| Bare run-id | `28066115163` |

Optional overrides:

| Variable | Default | Notes |
|----------|---------|-------|
| `platform` | `linux` | Bucket prefix segment (`<RUN_ID>-<platform>`) |
| `submodule_name` | `rocm-systems` | Override only if the user explicitly asks |
| `gpu_family` | `gfx94X-dcgpu` | **Legacy only** — used when falling back to old per-family manifest paths |

## Process

### Phase 1: Parse the Run ID

Accept whatever the user pasted and extract the numeric GitHub Actions run id.

```bash
INPUT="$1"
# Run ids are >= 10 digits; anchor on that to avoid catching the 8-digit date.
RUN_ID=$(echo "$INPUT" | grep -oE '[0-9]{10,}' | tail -n1)

if [ -z "$RUN_ID" ]; then
  echo "Could not extract a run id from: $INPUT" >&2
  exit 1
fi
```

Echo the extracted run id back to the user before fetching, so they can confirm.

### Phase 2: Build the Manifest URL

Current layout (try this first):

```bash
PLATFORM="${PLATFORM:-linux}"

MANIFEST_URL="https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-${PLATFORM}/manifests/therock_manifest.json"
```

If that 404s, fall back to the legacy per-GPU-family path:

```bash
GPU_FAMILY="${GPU_FAMILY:-gfx94X-dcgpu}"
LEGACY_MANIFEST_URL="https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-${PLATFORM}/manifests/${GPU_FAMILY}/therock_manifest.json"
```

### Phase 3: Fetch the Manifest

```bash
MANIFEST=$(curl -fsSL "$MANIFEST_URL" || curl -fsSL "$LEGACY_MANIFEST_URL")
```

If both fail, report the URLs tried. Wrong `platform` is the most common cause on current builds.

### Phase 4: Extract pin_sha for rocm-systems

The manifest is a JSON **object** with this shape:

```json
{
  "the_rock_commit": "f1e3fc2311fde45bf3e17b0e3349200be9caa4b4",
  "github_run_id": "28066115163",
  "rocm_package_version": "7.14.0a20260624",
  "rocm_version": "7.14.0",
  "submodules": [
    {
      "submodule_name": "rocm-systems",
      "submodule_path": "rocm-systems",
      "submodule_url": "https://github.com/ROCm/rocm-systems.git",
      "pin_sha": "8b2f7145a33519b7f397b1c3636abddb7823538f"
    }
  ]
}
```

Note: submodule entries live under the top-level `submodules` array, not at the root. Always walk `.submodules[]`.

Prefer `jq`:

```bash
SUBMODULE_NAME="${SUBMODULE_NAME:-rocm-systems}"

PIN_SHA=$(echo "$MANIFEST" | jq -r --arg name "$SUBMODULE_NAME" '
  .submodules[] | select(.submodule_name == $name) | .pin_sha
')

THE_ROCK_COMMIT=$(echo "$MANIFEST" | jq -r '.the_rock_commit')
ROCM_PACKAGE_VERSION=$(echo "$MANIFEST" | jq -r '.rocm_package_version')
```

Fallback when `jq` is unavailable:

```bash
read -r PIN_SHA THE_ROCK_COMMIT ROCM_PACKAGE_VERSION < <(echo "$MANIFEST" | python3 -c '
import json, sys
name = "rocm-systems"
data = json.load(sys.stdin)
pin = ""
for entry in data.get("submodules", []):
    if entry.get("submodule_name") == name:
        pin = entry.get("pin_sha", "")
        break
print(pin, data.get("the_rock_commit", ""), data.get("rocm_package_version", ""))
')
```

If `PIN_SHA` is empty, list every `submodule_name` from the manifest so the user can pick a different one:

```bash
echo "$MANIFEST" | jq -r '.submodules[].submodule_name'
```

### Phase 5: Derive artifact URLs

```bash
# Date prefix from rocm_package_version (7.14.0a20260624 -> 20260624)
DATE_PREFIX="${ROCM_PACKAGE_VERSION##*a}"

if [ -n "$LEGACY" ]; then
  # Pre-migration builds: /deb/ packages layout, no multi-arch tarball.
  PACKAGES_URL="https://rocm.nightlies.amd.com/deb/${DATE_PREFIX}-${RUN_ID}/index.html"
  TARBALL_URL=""
else
  PACKAGES_URL="https://rocm.nightlies.amd.com/packages-multi-arch/deb/${DATE_PREFIX}-${RUN_ID}/index.html"
  TARBALL_URL="https://rocm.nightlies.amd.com/tarball-multi-arch/therock-dist-linux-multiarch-${ROCM_PACKAGE_VERSION}.tar.gz"
fi
```

Set `LEGACY=1` when resolving a pre-migration build (manifest served from the per-GPU-family path, or run found under `ROCm/TheRock`).

### Phase 6: Report

Report back, in this exact shape, so other skills can parse it. `<WORKFLOW_REPO>` is `ROCm/rockrel` for current builds and `ROCm/TheRock` for legacy ones; omit the `Tarball:` line when it is empty (legacy builds).

```text
Build:            <RUN_ID>          (platform=<PLATFORM>)
TheRock commit:   <THE_ROCK_COMMIT>
ROCm package:     <ROCM_PACKAGE_VERSION>
Submodule:        <SUBMODULE_NAME>
pin_sha:          <PIN_SHA>
Repo snapshot:    https://github.com/ROCm/rocm-systems/tree/<PIN_SHA>
GitHub Actions:   https://github.com/<WORKFLOW_REPO>/actions/runs/<RUN_ID>
Manifest:         <MANIFEST_URL>
Packages:         <PACKAGES_URL>
Tarball:          <TARBALL_URL>
```

## Examples

### Example 1: User pastes the current packages URL

```bash
INPUT="https://rocm.nightlies.amd.com/packages-multi-arch/deb/20260624-28066115163/index.html"
# RUN_ID -> 28066115163
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/28066115163-linux/manifests/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
# -> 8b2f7145a33519b7f397b1c3636abddb7823538f
```

### Example 2: User gives only the run id

```bash
RUN_ID=28066115163
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
```

### Example 3: Legacy build (per-GPU-family manifest)

```bash
RUN_ID=22561649510
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/therock_manifest.json" \
  || curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/gfx94X-dcgpu/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
```

### Example 4: Also surface package version and tarball link

```bash
RUN_ID=28066115163
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/therock_manifest.json" \
  | jq '{the_rock_commit, rocm_package_version, rocm_systems_pin: (.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha)}'
```

## Output

This skill produces:

- The `pin_sha` for the requested submodule (default `rocm-systems`) in the requested TheRock nightly build
- The `the_rock_commit` and `rocm_package_version` for the build
- The GitHub tree URL for the submodule snapshot
- The GitHub Actions run URL for the build
- The manifest, packages index, and tarball URLs

No files are written.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using the date `YYYYMMDD` as the run id | Run ids are the trailing digits after the dash (>= 10 digits); the date is 8 digits |
| Using the old `/deb/` packages URL for a new multi-arch build | Current builds use `/packages-multi-arch/deb/`; legacy builds used `/deb/` |
| Wrong `platform` -> 404 from S3 | Try `linux` first (default); use `windows` only for Windows nightlies |
| Confusing `submodule_name` with `submodule_path` | Always filter on `submodule_name` (`rocm-systems`), not the path |
| Truncating `pin_sha` before passing it downstream | Always pass the full 40-char SHA to downstream tools (e.g. `gh api ... compare`) |

## Troubleshooting

### `curl: (22) The requested URL returned error: 403/404`

Cause: the constructed `MANIFEST_URL` does not exist in the bucket for that run id.

Steps:
1. Verify the run id: `https://github.com/ROCm/rockrel/actions/runs/<RUN_ID>` (legacy pre-June-2026 runs: `ROCm/TheRock`)
2. Try the current path: `.../manifests/therock_manifest.json`
3. If that 404s, try the legacy path: `.../manifests/gfx94X-dcgpu/therock_manifest.json`
4. Confirm `platform` (`linux` vs `windows`)

### `PIN_SHA` is empty

Cause: the submodule name does not match (typo, renamed, or not present in this build).

Steps:
1. List every `submodule_name` in the manifest:
   ```bash
   curl -fsSL "$MANIFEST_URL" | jq -r '.submodules[].submodule_name'
   ```
2. Ask the user which one they want; rerun with `SUBMODULE_NAME=<chosen>`.

### `jq: command not found`

Use the `python3` fallback shown in Phase 4. Do not skip JSON parsing in favor of `grep` - the manifest can change shape.

## Integration with Other Skills

| Caller | Why |
|--------|-----|
| `therock-commit-in-build` | Needs the `pin_sha` for the build before checking ancestry of a user-supplied commit |

## Notes

- The manifest is hosted in a public S3 bucket; no auth is required for `curl`.
- Current multi-arch nightlies publish a single manifest at `manifests/therock_manifest.json` (no per-GPU-family subdirectory). The `pin_sha` is the same across architectures.
- Source of this recipe: [Wiki - Helpful Links and Information](https://amd.atlassian.net/wiki/spaces/AGSRCIT/pages/1306934643), *TheRock Nightly Builds* section.
