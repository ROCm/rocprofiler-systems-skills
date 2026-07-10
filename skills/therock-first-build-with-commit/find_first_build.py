#!/usr/bin/env python3
"""Find the first TheRock nightly build that includes a given rocm-systems commit.

Walks scheduled runs of the ``Multi-Arch Release`` workflow on ``ROCm/rockrel``
(the workflow that currently publishes nightly manifests to S3) in chronological
order starting at (or just before) the commit's committer date, fetches each
run's ``therock_manifest.json``, and uses the GitHub compare API to determine
whether the commit is an ancestor of the manifest's ``pin_sha``. Stops on the
first match.

Legacy nightlies (before mid-June 2026) used ``Release portable Linux packages``
on ``ROCm/TheRock`` (workflow id ``161312296``, now deleted). Pass ``--legacy``
to walk those runs instead of the current ``ROCm/rockrel`` workflow.

Exit codes:
  0  - found
  3  - invalid input (commit not visible on the target repo, etc.)
  4  - upstream failure (gh not authenticated, network error, etc.)
  5  - exhausted the search window without finding the commit
       (chosen over 2 to avoid colliding with argparse's exit-on-error code)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_REPO = "ROCm/rocm-systems"
DEFAULT_SUBMODULE = "rocm-systems"
DEFAULT_GPU_FAMILY = "gfx94X-dcgpu"  # legacy per-family manifest layout only
PLATFORM = "linux"  # nightlies only publish Linux artifacts to the canonical S3 path
DEFAULT_WORKFLOW_ID = 265449761  # Multi-Arch Release (nightly) on ROCm/rockrel
DEFAULT_WORKFLOW_REPO = "ROCm/rockrel"
LEGACY_WORKFLOW_ID = (
    161312296  # Release portable Linux packages on ROCm/TheRock (deleted)
)
LEGACY_WORKFLOW_REPO = "ROCm/TheRock"
DEFAULT_MAX_RUNS = 90
S3_BASE = "https://therock-nightly-artifacts.s3.amazonaws.com"
NIGHTLIES_BASE = "https://rocm.nightlies.amd.com"

EXIT_FOUND = 0
EXIT_INVALID_INPUT = 3
EXIT_UPSTREAM = 4
EXIT_EXHAUSTED = 5


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def die(code: int, msg: str) -> None:
    log(f"error: {msg}")
    sys.exit(code)


def run_gh(*args: str, fatal: bool = True) -> str | None:
    """Run ``gh`` and return stdout, or None on failure when ``fatal=False``."""
    if shutil.which("gh") is None:
        die(
            EXIT_UPSTREAM,
            "gh CLI not found on PATH; install from https://cli.github.com/",
        )
    try:
        proc = subprocess.run(["gh", *args], check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        if fatal:
            die(EXIT_UPSTREAM, f"gh {' '.join(args)} failed: {stderr or exc}")
        log(f"warn: gh {' '.join(args)} failed: {stderr or exc}")
        return None
    return proc.stdout


def gh_json(*api_args: str, fatal: bool = True) -> Any:
    out = run_gh("api", *api_args, fatal=fatal)
    if out is None:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        if fatal:
            die(EXIT_UPSTREAM, f"gh api {' '.join(api_args)} returned non-JSON: {exc}")
        log(f"warn: gh api {' '.join(api_args)} returned non-JSON: {exc}")
        return None


def resolve_commit(repo: str, ref: str) -> tuple[str, dt.datetime]:
    """Return (full_sha, committer_datetime_utc) for a commit on ``repo``."""
    data = gh_json(f"repos/{repo}/commits/{ref}", fatal=False)
    if data is None:
        die(
            EXIT_INVALID_INPUT,
            f"could not resolve commit {ref!r} on {repo} (not visible upstream?)",
        )
    full_sha = data.get("sha")
    date_str = ((data.get("commit") or {}).get("committer") or {}).get("date")
    if not full_sha or not date_str:
        die(EXIT_INVALID_INPUT, f"could not resolve commit {ref!r} on {repo}")
    when = dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=dt.timezone.utc
    )
    return full_sha, when


def list_nightly_runs(
    workflow_repo: str, workflow_id: int, since_iso: str, max_runs: int
) -> list[dict[str, Any]]:
    """Return scheduled nightly runs at/after ``since_iso``, oldest first.

    Filters ``event=schedule`` so manual re-runs and PR-triggered runs (which
    don't publish nightly artifacts to the canonical S3 path) are excluded.
    """
    query = urllib.parse.urlencode(
        {"per_page": 100, "event": "schedule", "created": f">={since_iso}"}
    )
    raw = run_gh(
        "api",
        "--paginate",
        f"repos/{workflow_repo}/actions/workflows/{workflow_id}/runs?{query}",
        "--jq",
        ".workflow_runs[] | {id, created_at, status, conclusion, head_branch, html_url}",
    )
    if raw is None:
        return []
    runs: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    runs.sort(key=lambda r: r.get("created_at", ""))
    return runs[:max_runs]


def manifest_candidate_urls(run_id: int, gpu_family: str) -> list[str]:
    """Return manifest URLs to try, current layout first then legacy per-GPU-family."""
    base = f"{S3_BASE}/{run_id}-{PLATFORM}/manifests"
    return [
        f"{base}/therock_manifest.json",
        f"{base}/{gpu_family}/therock_manifest.json",
    ]


def _fetch_manifest_url(url: str) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code not in (403, 404):
            log(f"warn: HTTP {exc.code} fetching {url}: {exc.reason}")
        return None
    except urllib.error.URLError as exc:
        log(f"warn: network error fetching {url}: {exc.reason}")
        return None
    except (json.JSONDecodeError, ValueError) as exc:
        log(f"warn: invalid JSON manifest at {url}: {exc}")
        return None


def fetch_manifest(
    run_id: int, gpu_family: str
) -> tuple[str, dict[str, Any] | None]:
    urls = manifest_candidate_urls(run_id, gpu_family)
    last_url = urls[0]
    for url in urls:
        last_url = url
        manifest = _fetch_manifest_url(url)
        if manifest is not None:
            return url, manifest
    return last_url, None


def date_prefix_from_package_version(version: str | None) -> str | None:
    """Extract YYYYMMDD from ``rocm_package_version`` like ``7.14.0a20260624``."""
    if not version:
        return None
    suffix = version.rsplit("a", 1)[-1]
    if len(suffix) == 8 and suffix.isdigit():
        return suffix
    return None


def packages_index_url(
    run_id: int, date_prefix: str | None, legacy: bool = False
) -> str | None:
    if not date_prefix:
        return None
    segment = "deb" if legacy else "packages-multi-arch/deb"
    return f"{NIGHTLIES_BASE}/{segment}/{date_prefix}-{run_id}/index.html"


def tarball_url(rocm_package_version: str | None, legacy: bool = False) -> str | None:
    # Pre-migration nightlies had no multi-arch tarball at a predictable path.
    if not rocm_package_version or legacy:
        return None
    return (
        f"{NIGHTLIES_BASE}/tarball-multi-arch/"
        f"therock-dist-linux-multiarch-{rocm_package_version}.tar.gz"
    )


def pin_sha_for(manifest: dict[str, Any], submodule: str) -> str | None:
    for entry in manifest.get("submodules", []):
        if entry.get("submodule_name") == submodule:
            return entry.get("pin_sha")
    return None


def is_ancestor(repo: str, commit: str, pin: str) -> tuple[bool, dict[str, Any] | None]:
    """Return ``(commit_is_in_pin, raw_compare_data)``.

    Soft-fails (returns ``(False, None)``) if ``gh api compare`` errors, so a
    single unresolvable ``pin_sha`` (e.g. force-pushed branch) does not abort
    the whole walk.
    """
    data = gh_json(f"repos/{repo}/compare/{commit}...{pin}", fatal=False)
    if data is None:
        return False, None
    status = data.get("status")
    if status in ("identical", "ahead"):
        return True, data
    # GitHub can return status=null for very large diffs; fall back to the
    # ancestry counts. behind_by == 0 means commit is reachable from pin.
    if (
        status is None
        and data.get("behind_by") == 0
        and data.get("ahead_by") is not None
    ):
        return True, data
    return False, data


def parse_since(value: str) -> str:
    """Validate a --since YYYY-MM-DD string and normalize to ISO date."""
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="find_first_build.py",
        description=(
            "Find the first TheRock nightly build that includes a given "
            "rocm-systems commit."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--commit",
        required=True,
        help="Commit SHA to look for (full 40-char SHA preferred).",
    )
    p.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help="GitHub repo that hosts the commit (OWNER/REPO).",
    )
    p.add_argument(
        "--submodule",
        default=DEFAULT_SUBMODULE,
        help="Submodule name in therock_manifest.json to extract pin_sha from.",
    )
    p.add_argument(
        "--gpu-family",
        default=DEFAULT_GPU_FAMILY,
        help=(
            "Legacy manifest folder name for older builds that published "
            "per-GPU-family manifests under manifests/<family>/."
        ),
    )
    p.add_argument(
        "--legacy",
        action="store_true",
        help=(
            "Walk legacy TheRock nightlies (ROCm/TheRock workflow 161312296) "
            "instead of current ROCm/rockrel Multi-Arch Release (265449761). "
            "Use for commits first shipped before the mid-June 2026 migration."
        ),
    )
    p.add_argument(
        "--workflow-repo",
        default=None,
        help=(
            "GitHub repo hosting the nightly workflow (OWNER/REPO). "
            "Default: ROCm/rockrel (or ROCm/TheRock with --legacy)."
        ),
    )
    p.add_argument(
        "--workflow",
        type=int,
        default=None,
        help=(
            "Workflow id to enumerate scheduled runs from. "
            "Default: 265449761 on ROCm/rockrel (or 161312296 with --legacy)."
        ),
    )
    p.add_argument(
        "--since",
        type=parse_since,
        default=None,
        help="Lower bound (YYYY-MM-DD); default = commit committer date minus 1 day.",
    )
    p.add_argument(
        "--max-runs",
        type=int,
        default=DEFAULT_MAX_RUNS,
        help="Maximum number of nightly runs to inspect after --since.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit the final result as JSON on stdout instead of human text.",
    )
    return p


def format_human(result: dict[str, Any]) -> str:
    if not result["found"]:
        lines = [
            f"No nightly build in the inspected window contains {result['commit']}.",
            f"  Inspected runs: {result['inspected_runs']} (since {result['since']})",
            "  The commit may still ship in a later nightly; rerun later or"
            " widen --max-runs / --since.",
        ]
        return "\n".join(lines)

    b = result["first_build"]
    pin = b["pin_sha"]

    ahead_by = b.get("ahead_by")
    if ahead_by == 1:
        pin_note = " (1 commit ahead)"
    elif ahead_by:
        pin_note = f" ({ahead_by} commits ahead)"
    else:
        pin_note = ""

    date_prefix = date_prefix_from_package_version(b.get("rocm_package_version"))
    if date_prefix:
        nightly_date = f"{date_prefix[:4]}-{date_prefix[4:6]}-{date_prefix[6:]}"
    else:
        nightly_date = b["created_at"][:10]

    lines = [
        f"Commit {result['commit'][:8]} first shipped in the {nightly_date} nightly.",
        "",
        f"First nightly build to include {result['commit']}:",
        f"  - run_id: {b['run_id']} (created {b['created_at']})",
        f"  - pin_sha: {pin}{pin_note}",
        f"  - the_rock_commit: {b['the_rock_commit']}",
        f"  - Repo snapshot: {b['snapshot_url']}",
        f"  - GitHub Actions: {b['run_url']}",
        f"  - Compare: {b['compare_url']}",
        f"  - Manifest: {b['manifest_url']}",
    ]
    if b.get("packages_url"):
        lines.append(f"  - Packages (deb): {b['packages_url']}")
    if b.get("tarball_url"):
        lines.append(f"  - Tarball: {b['tarball_url']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.legacy:
        workflow_repo = LEGACY_WORKFLOW_REPO
        workflow_id = LEGACY_WORKFLOW_ID
    else:
        workflow_repo = DEFAULT_WORKFLOW_REPO
        workflow_id = DEFAULT_WORKFLOW_ID
    if args.workflow_repo is not None:
        workflow_repo = args.workflow_repo
    if args.workflow is not None:
        workflow_id = args.workflow

    # Legacy TheRock builds used the /deb/ packages layout and had no multi-arch
    # tarball; detect from the resolved repo so --workflow-repo also counts.
    is_legacy = workflow_repo == LEGACY_WORKFLOW_REPO

    log(f"Resolving commit {args.commit} on {args.repo}...")
    full_sha, committer_when = resolve_commit(args.repo, args.commit)
    log(f"  full sha: {full_sha}")
    log(f"  committed: {committer_when.isoformat()}")

    if args.since is None:
        since_date = (committer_when.date() - dt.timedelta(days=1)).isoformat()
    else:
        since_date = args.since
    log(
        f"Listing scheduled runs of {workflow_repo} workflow {workflow_id}"
        f" since {since_date} (max {args.max_runs})..."
    )

    runs = list_nightly_runs(workflow_repo, workflow_id, since_date, args.max_runs)
    if not runs:
        log("No nightly runs found in the window.")
        result = {
            "found": False,
            "commit": full_sha,
            "repo": args.repo,
            "since": since_date,
            "workflow_repo": workflow_repo,
            "workflow_id": workflow_id,
            "inspected_runs": 0,
            "inspected": [],
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_human(result))
        return EXIT_EXHAUSTED

    log(f"Inspecting {len(runs)} runs in chronological order.")
    inspected: list[dict[str, Any]] = []
    total = len(runs)
    for idx, run in enumerate(runs, start=1):
        run_id = run["id"]
        created = run["created_at"]
        manifest_url, manifest = fetch_manifest(run_id, args.gpu_family)
        if manifest is None:
            log(
                f"[{idx:>3}/{total}] run={run_id} created={created}"
                f" manifest=missing (skipped)"
            )
            inspected.append(
                {
                    "run_id": run_id,
                    "created_at": created,
                    "pin_sha": None,
                    "status": "no-manifest",
                }
            )
            continue

        pin = pin_sha_for(manifest, args.submodule)
        if not pin:
            log(
                f"[{idx:>3}/{total}] run={run_id} created={created}"
                f" submodule={args.submodule} not in manifest (skipped)"
            )
            inspected.append(
                {
                    "run_id": run_id,
                    "created_at": created,
                    "pin_sha": None,
                    "status": "no-submodule",
                }
            )
            continue

        included, cmp_data = is_ancestor(args.repo, full_sha, pin)
        if cmp_data is None:
            log(
                f"[{idx:>3}/{total}] run={run_id} created={created}"
                f" pin={pin[:8]} compare=error (skipped)"
            )
            inspected.append(
                {
                    "run_id": run_id,
                    "created_at": created,
                    "pin_sha": pin,
                    "status": "compare-error",
                }
            )
            continue

        status = cmp_data.get("status")
        ahead_by = cmp_data.get("ahead_by")
        behind_by = cmp_data.get("behind_by")
        log(
            f"[{idx:>3}/{total}] run={run_id} created={created}"
            f" pin={pin[:8]} status={status or 'null':<9}"
            f" ahead_by={ahead_by} behind_by={behind_by}"
            f"{'  FOUND' if included else ''}"
        )

        inspected.append(
            {
                "run_id": run_id,
                "created_at": created,
                "pin_sha": pin,
                "status": status,
                "ahead_by": ahead_by,
                "behind_by": behind_by,
            }
        )

        if included:
            the_rock_commit = manifest.get("the_rock_commit")
            rocm_package_version = manifest.get("rocm_package_version")
            date_prefix = date_prefix_from_package_version(rocm_package_version)
            result = {
                "found": True,
                "commit": full_sha,
                "repo": args.repo,
                "since": since_date,
                "workflow_repo": workflow_repo,
                "workflow_id": workflow_id,
                "inspected_runs": idx,
                "first_build": {
                    "run_id": run_id,
                    "created_at": created,
                    "the_rock_commit": the_rock_commit,
                    "rocm_package_version": rocm_package_version,
                    "pin_sha": pin,
                    "compare_status": status,
                    "ahead_by": ahead_by,
                    "behind_by": behind_by,
                    "compare_url": (
                        f"https://github.com/{args.repo}/compare/{full_sha}...{pin}"
                    ),
                    "snapshot_url": f"https://github.com/{args.repo}/tree/{pin}",
                    "run_url": run.get(
                        "html_url",
                        f"https://github.com/{workflow_repo}/actions/runs/{run_id}",
                    ),
                    "manifest_url": manifest_url,
                    "packages_url": packages_index_url(
                        run_id, date_prefix, legacy=is_legacy
                    ),
                    "tarball_url": tarball_url(
                        rocm_package_version, legacy=is_legacy
                    ),
                },
                "inspected": inspected,
            }
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_human(result))
            return EXIT_FOUND

    result = {
        "found": False,
        "commit": full_sha,
        "repo": args.repo,
        "since": since_date,
        "workflow_repo": workflow_repo,
        "workflow_id": workflow_id,
        "inspected_runs": len(inspected),
        "inspected": inspected,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    return EXIT_EXHAUSTED


if __name__ == "__main__":
    sys.exit(main())
