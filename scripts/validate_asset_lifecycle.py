#!/usr/bin/env python3
"""Validate ACIP Canonical Asset lifecycle control.

This script validates repository governance only.
It must not perform runtime actions, external API calls, scraping, posting, or mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


REQUIRED_FILES = [
    "basis/011_asset_lifecycle.md",
    "basis/012_asset_repository_conventions.md",
    "adr/ADR-0004-asset-lifecycle-control.md",
    "docs/ASSET_LIFECYCLE_CHECKLIST.md",
    "docs/ASSET_STATUS_MODEL.md",
    "docs/ASSET_INDEX_TEMPLATE.md",
    "docs/ASSET_CHANGELOG_TEMPLATE.md",
    "wbs/WBS-0002-asset-lifecycle-control.md",
    ".github/ISSUE_TEMPLATE/asset_lifecycle.yml",
    ".github/workflows/asset-lifecycle-check.yml",
]

REQUIRED_TEXT = {
    "basis/011_asset_lifecycle.md": [
        "Intake → Draft → Review → Approved → Canonical → Reuse → Revision → Deprecated",
        "Repository overrides conversation.",
        "approval bypass is prohibited",
    ],
    "basis/012_asset_repository_conventions.md": [
        "assets/",
        "asset_id",
        "Derived outputs must reference source asset id.",
    ],
    "adr/ADR-0004-asset-lifecycle-control.md": [
        "Asset Lifecycle Control",
        "Proposed",
        "runtime implementation remains out of scope",
    ],
    "docs/ASSET_STATUS_MODEL.md": [
        "intake",
        "canonical",
        "deprecated",
    ],
    "wbs/WBS-0002-asset-lifecycle-control.md": [
        "Current Objective",
        "Canonical Asset Production",
        "runtime implementation",
    ],
}

PROHIBITED_KEYWORDS = [
    "auto_post(",
    "publish_to_platform(",
    "run_runtime_agent(",
    "scrape_platform(",
]

SCAN_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".txt"}


def exists_file(path: str) -> CheckResult:
    target = ROOT / path
    return CheckResult(
        name=f"required file: {path}",
        ok=target.is_file(),
        detail="exists" if target.is_file() else "missing",
    )


def contains_required_text(path: str, anchors: list[str]) -> list[CheckResult]:
    target = ROOT / path
    if not target.is_file():
        return [CheckResult(f"required text: {path}", False, "file missing")]
    text = target.read_text(encoding="utf-8")
    return [
        CheckResult(
            name=f"required text in {path}: {anchor}",
            ok=anchor in text,
            detail="found" if anchor in text else "missing",
        )
        for anchor in anchors
    ]


def check_prohibited_keywords() -> list[CheckResult]:
    failures: list[CheckResult] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for keyword in PROHIBITED_KEYWORDS:
            if keyword in text:
                failures.append(
                    CheckResult(
                        name=f"prohibited keyword in {relative}",
                        ok=False,
                        detail=keyword,
                    )
                )
    if not failures:
        failures.append(CheckResult("prohibited keywords", True, "none found"))
    return failures


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.extend(exists_file(path) for path in REQUIRED_FILES)
    for path, anchors in REQUIRED_TEXT.items():
        results.extend(contains_required_text(path, anchors))
    results.extend(check_prohibited_keywords())
    return results


def main() -> int:
    results = run_checks()
    failed = [result for result in results if not result.ok]

    print("# ACIP Asset Lifecycle Validation")
    print()
    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        print(f"[{mark}] {result.name} - {result.detail}")

    if failed:
        print()
        print(f"Validation failed: {len(failed)} issue(s).")
        return 1

    print()
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
