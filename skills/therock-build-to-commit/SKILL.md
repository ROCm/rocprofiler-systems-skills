---
name: therock-build-to-commit
description: Given a TheRock nightly build (URL or run-id), return the rocm-systems pin_sha used in that build
---

# Resolve TheRock Nightly Build to rocm-systems Commit

Resolves a TheRock nightly build to the exact `rocm-systems` commit (`pin_sha`) that was used to produce it, by reading the build's `therock_manifest.json` from S3.

## When to Use

Use this skill when:
- User asks "what rocm-systems commit is in TheRock build X?"
- User provides a TheRock nightly URL (e.g. `https://rocm.nightlies.amd.com/deb/YYYYMMDD-<RUN_ID>/index.html`) or a bare run-id and wants to know what shipped
- User wants the GitHub tree link for the snapshot used by a nightly build
- Another skill needs the `pin_sha` for a build before continuing (e.g. `therock-commit-in-build`)

Unless the user says otherwise, this skill targets the `rocm-systems` submodule.

## Inputs

The user provides **one** of:

| Input form | Example |
|------------|---------|
| Full nightly URL | `https://rocm.nightlies.amd.com/deb/20260302-22561649510/index.html` |
| Index path | `20260302-22561649510` |
| Bare run-id | `22561649510` |

Optional overrides:

| Variable | Default | Notes |
|----------|---------|-------|
| `gpu_family` | `gfx94X-dcgpu` | Folder name under `manifests/` in the artifact bucket |
| `platform` | `linux` | Used in the bucket prefix (`<RUN_ID>-<platform>`) |
| `submodule_name` | `rocm-systems` | Override only if the user explicitly asks |

## Process

### Phase 1: Parse the Run ID

Accept whatever the user pasted and extract the numeric GitHub Actions run id.

```bash
INPUT="$1"
# Strip protocol and path, then split on '-' and take the trailing digits.
# Run ids are >= 10 digits; anchor on that to avoid catching the date.
RUN_ID=$(echo "$INPUT" | grep -oE '[0-9]{10,}' | tail -n1)

if [ -z "$RUN_ID" ]; then
  echo "Could not extract a run id from: $INPUT" >&2
  exit 1
fi
```

Echo the extracted run id back to the user before fetching, so they can confirm.

### Phase 2: Build the Manifest URL

```bash
GPU_FAMILY="${GPU_FAMILY:-gfx94X-dcgpu}"
PLATFORM="${PLATFORM:-linux}"

MANIFEST_URL="https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-${PLATFORM}/manifests/${GPU_FAMILY}/therock_manifest.json"
```

### Phase 3: Fetch the Manifest

```bash
MANIFEST=$(curl -fsSL "$MANIFEST_URL")
```

If `curl` exits non-zero, the build either does not exist or uses different `gpu_family` / `platform` values. Report the URL we tried so the user can adjust the overrides.

### Phase 4: Extract pin_sha for rocm-systems

The manifest is a JSON **object** with this shape:

```json
{
  "the_rock_commit": "75587075f01c8d30d3692386900a3062544e0794",
  "submodules": [
    {
      "submodule_name": "rocm-systems",
      "submodule_path": "rocm-systems",
      "submodule_url": "https://github.com/ROCm/rocm-systems.git",
      "pin_sha": "c7da590396ceef1afaaa1b971f3b3d7d6e3562a9"
    }
  ]
}
```

Note: the submodule entries live under the top-level `submodules` array, not at the root. Always walk `.submodules[]`.

Prefer `jq`:

```bash
SUBMODULE_NAME="${SUBMODULE_NAME:-rocm-systems}"

PIN_SHA=$(echo "$MANIFEST" | jq -r --arg name "$SUBMODULE_NAME" '
  .submodules[] | select(.submodule_name == $name) | .pin_sha
')

THE_ROCK_COMMIT=$(echo "$MANIFEST" | jq -r '.the_rock_commit')
```

Fallback when `jq` is unavailable:

```bash
read -r PIN_SHA THE_ROCK_COMMIT < <(echo "$MANIFEST" | python3 -c '
import json, sys
name = "rocm-systems"
data = json.load(sys.stdin)
pin = ""
for entry in data.get("submodules", []):
    if entry.get("submodule_name") == name:
        pin = entry.get("pin_sha", "")
        break
print(pin, data.get("the_rock_commit", ""))
')
```

If `PIN_SHA` is empty, list every `submodule_name` from the manifest so the user can pick a different one:

```bash
echo "$MANIFEST" | jq -r '.submodules[].submodule_name'
```

### Phase 5: Report

Report back, in this exact shape, so other skills can parse it:

```text
Build:            <RUN_ID>          (gpu_family=<GPU_FAMILY>, platform=<PLATFORM>)
TheRock commit:   <THE_ROCK_COMMIT>
Submodule:        <SUBMODULE_NAME>
pin_sha:          <PIN_SHA>
Repo snapshot:    https://github.com/ROCm/rocm-systems/tree/<PIN_SHA>
GitHub Actions:   https://github.com/ROCm/TheRock/actions/runs/<RUN_ID>
Manifest:         <MANIFEST_URL>
```

## Examples

### Example 1: User pastes the full nightly URL

```bash
INPUT="https://rocm.nightlies.amd.com/deb/20260302-22561649510/index.html"
# RUN_ID -> 22561649510
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/22561649510-linux/manifests/gfx94X-dcgpu/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
# -> c7da590396ceef1afaaa1b971f3b3d7d6e3562a9
```

### Example 2: User gives only the run id

```bash
RUN_ID=22561649510
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/gfx94X-dcgpu/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
```

### Example 3: Different GPU family

```bash
GPU_FAMILY=gfx110X-dgpu
RUN_ID=22561649510
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/${GPU_FAMILY}/therock_manifest.json" \
  | jq -r '.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha'
```

### Example 4: Also surface TheRock's own commit

```bash
RUN_ID=22561649510
curl -fsSL "https://therock-nightly-artifacts.s3.amazonaws.com/${RUN_ID}-linux/manifests/gfx94X-dcgpu/therock_manifest.json" \
  | jq '{the_rock_commit, rocm_systems_pin: (.submodules[] | select(.submodule_name=="rocm-systems") | .pin_sha)}'
# -> {"the_rock_commit":"75587075...","rocm_systems_pin":"c7da5903..."}
```

## Output

This skill produces:

- The `pin_sha` for the requested submodule (default `rocm-systems`) in the requested TheRock nightly build
- The `the_rock_commit` for the build itself (the SHA of TheRock at the time the nightly was produced)
- The GitHub tree URL for the submodule snapshot
- The GitHub Actions run URL for the build
- The manifest URL used (for debugging)

No files are written.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using the date `YYYYMMDD` as the run id | Run ids are the trailing digits after the dash (>= 10 digits); the date is 8 digits |
| Wrong `gpu_family` or `platform` -> 404 from S3 | Try the defaults first (`gfx94X-dcgpu`, `linux`); if 404, ask the user which family/platform they want and retry |
| Confusing `submodule_name` with `submodule_path` | The manifest has both; always filter on `submodule_name` (`rocm-systems`), not the path |
| Truncating `pin_sha` before passing it downstream | Always pass the full 40-char SHA to downstream tools (e.g. `gh api ... compare`) |
| Trusting a stale local mirror | The manifest is the source of truth - re-fetch rather than caching across builds |

## Troubleshooting

### `curl: (22) The requested URL returned error: 403/404`

Cause: the constructed `MANIFEST_URL` does not exist in the bucket for that run id.

Steps:
1. Verify the run id by opening `https://github.com/ROCm/TheRock/actions/runs/<RUN_ID>` in a browser.
2. Confirm `platform` (`linux` vs `windows`) and `gpu_family` (folder names under `manifests/`).
3. Re-run with the overrides:
   ```bash
   PLATFORM=windows GPU_FAMILY=gfx110X-dgpu ./therock-build-to-commit ...
   ```

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
- The same run id may have multiple `gpu_family` folders. Different families build the same `rocm-systems` `pin_sha`, but the file paths differ - so always include `GPU_FAMILY` in the URL.
- Source of this recipe: [Wiki - Helpful Links and Information](https://amd.atlassian.net/wiki/spaces/AGSRCIT/pages/1306934643), *TheRock Nightly Builds* section.
