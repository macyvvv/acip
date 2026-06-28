#!/usr/bin/env python3
"""Move deprecated SelfTest skeleton files to archive so they stop colliding with canonical files.

This script performs repository file moves only. It does not delete historical reasoning.
"""

from __future__ import annotations

from pathlib import Path
import shutil

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ARCHIVE = ROOT / "archive" / "selftest_skeleton"

DEPRECATED_PATHS = [
    "README_SELFTEST_PACK.md",
    "README_REPOSITORY_SELFTEST_PACK.md",
    "adr/ADR-0016-repository-self-test.md",
    "wbs/WBS-0011-repository-selftest.md",
    "basis/53_repository_health_policy.md",
    "basis/54_dead_asset_policy.md",
    "basis/55_drift_detection_policy.md",
    "basis/56_boundary_validation_policy.md",
    "basis/57_continuous_governance_policy.md",
    "basis/58_link_integrity_policy.md",
    "basis/59_orphan_detection_policy.md",
    "basis/60_duplicate_detection_policy.md",
    "basis/61_validator_policy.md",
    "basis/62_selftest_policy.md",
]

def main() -> int:
    moved = []
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for rel in DEPRECATED_PATHS:
        src = ROOT / rel
        if not src.exists():
            continue
        dst = ARCHIVE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved.append((rel, dst.relative_to(ROOT).as_posix()))
    print("# SelfTest Skeleton Cleanup")
    for src, dst in moved:
        print(f"moved: {src} -> {dst}")
    print(f"moved_count={len(moved)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
