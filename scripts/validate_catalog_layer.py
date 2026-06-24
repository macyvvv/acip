#!/usr/bin/env python3
"""Validate ACIP Catalog Layer controls.

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
    "basis/023_catalog_policy.md",
    "basis/024_tag_policy.md",
    "basis/025_searchability_policy.md",
    "basis/026_autonomy_first_policy.md",
    "adr/ADR-0008-catalog-and-search-governance.md",
    "adr/ADR-0009-autonomy-first-operating-boundary.md",
    "registry/KNOWLEDGE_INDEX.md",
    "registry/CONTENT_INDEX.md",
    "registry/MEDIA_INDEX.md",
    "registry/OPERATIONAL_INDEX.md",
    "registry/DEPRECATED_INDEX.md",
    "catalog/CATEGORY_TAXONOMY.md",
    "catalog/TAG_STANDARD.md",
    "catalog/NAMING_STANDARD.md",
    "catalog/SEARCH_GUIDELINE.md",
    "catalog/RELATIONSHIP_MODEL.md",
    "docs/CATALOG_ENTRY_TEMPLATE.md",
    "docs/KNOWLEDGE_CARD_TEMPLATE.md",
    "docs/SEARCH_METADATA_TEMPLATE.md",
    "docs/CATALOG_LAYER_CHECKLIST.md",
    "wbs/WBS-0006-catalog-layer.md",
    ".github/ISSUE_TEMPLATE/catalog_update.yml",
    ".github/workflows/catalog-layer-check.yml",
]

REQUIRED_DIRS = [
    "catalog",
    "registry",
]

REQUIRED_TEXT = {
    "basis/023_catalog_policy.md": [
        "Catalog Layer",
        "Human must not be assigned work that can be performed",
        "Runtime implementation remains out of scope",
    ],
    "basis/024_tag_policy.md": [
        "lowercase kebab-case",
        "Automation Bias",
        "Repository overrides conversation.",
    ],
    "basis/025_searchability_policy.md": [
        "Searchability is a first-class requirement",
        "Chat memory is not a search substitute",
        "Human should not manually search",
    ],
    "basis/026_autonomy_first_policy.md": [
        "Mission",
        "Approval",
        "Emergency Stop",
        "If a task can be safely performed",
    ],
    "adr/ADR-0008-catalog-and-search-governance.md": [
        "Catalog and Search Governance",
        "Human should not perform catalog hygiene",
        "runtime implementation remains out of scope",
    ],
    "adr/ADR-0009-autonomy-first-operating-boundary.md": [
        "Autonomy First Operating Boundary",
        "Human responsibilities are limited",
        "Runtime implementation remains out of scope",
    ],
    "catalog/RELATIONSHIP_MODEL.md": [
        "derived_from",
        "supersedes",
        "contradicts",
    ],
    "wbs/WBS-0006-catalog-layer.md": [
        "Current Objective",
        "Canonical Asset Production",
        "Routine catalog hygiene",
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

    print("# ACIP Catalog Layer Validation")
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
