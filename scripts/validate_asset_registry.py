#!/usr/bin/env python3
"""Validate ACIP Asset Registry and traceability controls.

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
    "basis/013_asset_registry_policy.md",
    "basis/014_asset_traceability_policy.md",
    "adr/ADR-0005-asset-registry-traceability.md",
    "docs/ASSET_REGISTRY_CHECKLIST.md",
    "docs/ASSET_REGISTRY_TEMPLATE.md",
    "docs/ASSET_TRACEABILITY_MAP_TEMPLATE.md",
    "registry/ASSET_REGISTRY.md",
    "wbs/WBS-0003-asset-registry-traceability.md",
    ".github/ISSUE_TEMPLATE/asset_registry.yml",
    ".github/workflows/asset-registry-check.yml",
]

REQUIRED_DIRS = [
    "registry",
]

REQUIRED_TEXT = {
    "basis/013_asset_registry_policy.md": [
        "Asset Registry",
        "asset_id",
        "Repository overrides conversation.",
        "ROI connection",
    ],
    "basis/014_asset_traceability_policy.md": [
        "Source Context",
        "Canonical Asset",
        "Derived outputs must reference source asset id.",
        "approval bypass",
    ],
    "adr/ADR-0005-asset-registry-traceability.md": [
        "Asset Registry and Traceability",
        "Proposed",
        "runtime implementation remains out of scope",
    ],
    "registry/ASSET_REGISTRY.md": [
        "asset_id",
        "source_path",
        "quality_gate_status",
        "Repository overrides conversation.",
    ],
    "wbs/WBS-0003-asset-registry-traceability.md": [
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


def exists_dir(path: str) -> CheckResult:
    target = ROOT / path
    return CheckResult(
        name=f"required dir: {path}",
        ok=target.is_dir(),
        detail="exists" if target.is_dir() else "missing",
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
    results.extend(exists_dir(path) for path in REQUIRED_DIRS)
    for path, anchors in REQUIRED_TEXT.items():
        results.extend(contains_required_text(path, anchors))
    results.extend(check_prohibited_keywords())
    return results


def main() -> int:
    results = run_checks()
    failed = [result for result in results if not result.ok]

    print("# ACIP Asset Registry Validation")
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
