"""Unit tests for the pure, I/O-free helpers in find_first_build.py.

Run with: python3 -m pytest test_find_first_build.py

Only the helpers that do no network / gh / filesystem work are covered here;
the walk itself (fetch_manifest, is_ancestor, resolve_commit, main) needs
GitHub and S3 and is exercised manually against live runs.
"""

from __future__ import annotations

import pytest

import find_first_build as ffb


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("7.14.0a20260624", "20260624"),
        ("7.14.0", None),  # no 'a' date suffix
        ("7.14.0a2026062", None),  # suffix too short
        ("7.14.0a2026062x", None),  # suffix not all digits
        ("", None),
        (None, None),
    ],
)
def test_date_prefix_from_package_version(version, expected):
    assert ffb.date_prefix_from_package_version(version) == expected


def test_manifest_candidate_urls_order():
    urls = ffb.manifest_candidate_urls(123, "gfx94X-dcgpu")
    assert urls == [
        f"{ffb.S3_BASE}/123-linux/manifests/therock_manifest.json",
        f"{ffb.S3_BASE}/123-linux/manifests/gfx94X-dcgpu/therock_manifest.json",
    ]


def test_packages_index_url_current():
    assert ffb.packages_index_url(123, "20260624") == (
        f"{ffb.NIGHTLIES_BASE}/packages-multi-arch/deb/20260624-123/index.html"
    )


def test_packages_index_url_legacy():
    assert ffb.packages_index_url(123, "20260624", legacy=True) == (
        f"{ffb.NIGHTLIES_BASE}/deb/20260624-123/index.html"
    )


def test_packages_index_url_no_date():
    assert ffb.packages_index_url(123, None) is None
    assert ffb.packages_index_url(123, None, legacy=True) is None


def test_tarball_url_current():
    assert ffb.tarball_url("7.14.0a20260624") == (
        f"{ffb.NIGHTLIES_BASE}/tarball-multi-arch/"
        "therock-dist-linux-multiarch-7.14.0a20260624.tar.gz"
    )


def test_tarball_url_legacy_is_none():
    # Pre-migration builds had no multi-arch tarball at a predictable path.
    assert ffb.tarball_url("7.14.0a20260624", legacy=True) is None


def test_tarball_url_no_version():
    assert ffb.tarball_url(None) is None
    assert ffb.tarball_url("") is None


def _found_result(**overrides):
    b = {
        "run_id": 28066115163,
        "created_at": "2026-06-24T00:17:13Z",
        "the_rock_commit": "f1e3fc23",
        "pin_sha": "8b2f7145",
        "ahead_by": 3,
        "behind_by": 0,
        "snapshot_url": "https://github.com/ROCm/rocm-systems/tree/8b2f7145",
        "run_url": "https://github.com/ROCm/rockrel/actions/runs/28066115163",
        "compare_url": "https://github.com/ROCm/rocm-systems/compare/d22352b...8b2f7145",
        "manifest_url": "https://s3/manifests/therock_manifest.json",
        "packages_url": "https://n/packages-multi-arch/deb/20260624-28066115163/index.html",
        "tarball_url": "https://n/tarball-multi-arch/x.tar.gz",
    }
    b.update(overrides)
    return {"found": True, "commit": "d22352b", "repo": "ROCm/rocm-systems", "first_build": b}


def test_format_human_is_bullet_list():
    out = ffb.format_human(_found_result())
    body = [line for line in out.splitlines() if line.startswith("  ")]
    assert all(line.startswith("  - ") for line in body)
    assert "  - run_id: 28066115163 (created 2026-06-24T00:17:13Z)" in out
    assert "  - pin_sha: 8b2f7145 (3 commits ahead)" in out


def test_format_human_intro_line():
    b = _found_result()["first_build"]
    b["rocm_package_version"] = "7.14.0a20260624"
    out = ffb.format_human(
        {"found": True, "commit": "b697dfca1234", "repo": "ROCm/rocm-systems",
         "first_build": b}
    )
    assert out.splitlines()[0] == "Commit b697dfca first shipped in the 2026-06-24 nightly."


def test_format_human_intro_falls_back_to_created_at():
    out = ffb.format_human(_found_result(rocm_package_version=None))
    assert out.splitlines()[0] == "Commit d22352b first shipped in the 2026-06-24 nightly."


def test_format_human_singular_commit_ahead():
    out = ffb.format_human(_found_result(ahead_by=1))
    assert "(1 commit ahead)" in out


def test_format_human_omits_empty_tarball():
    out = ffb.format_human(_found_result(tarball_url=None))
    assert "Tarball:" not in out
    assert "Packages (deb):" in out


def test_pin_sha_for():
    manifest = {
        "submodules": [
            {"submodule_name": "other", "pin_sha": "aaa"},
            {"submodule_name": "rocm-systems", "pin_sha": "bbb"},
        ]
    }
    assert ffb.pin_sha_for(manifest, "rocm-systems") == "bbb"
    assert ffb.pin_sha_for(manifest, "missing") is None
    assert ffb.pin_sha_for({}, "rocm-systems") is None
