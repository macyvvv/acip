#!/usr/bin/env python3
"""Validate ACIP Canonical Asset Production closure controls.

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
    "basis/008_canonical_asset_definition.md",
    "basis/009_asset_production_policy.md",
    "basis/010_quality_gate.md",
    "basis/011_asset_lifecycle.md",
    "basis/012_asset_repository_conventions.md",
    "basis/013_asset_registry_policy.md",
    "basis/014_asset_traceability_policy.md",
    "basis/015_asset_intake_policy.md",
    "basis/016_asset_production_workflow.md",
    "basis/017_asset_review_cadence.md",
    "basis/018_asset_output_policy.md",
    "basis/019_asset_quality_policy.md",
    "basis/020_asset_roi_policy.md",
    "basis/021_asset_risk_policy.md",
    "basis/022_asset_completion_policy.md",
    "adr/ADR-0007-asset-quality-roi-risk-closure.md",
    "docs/ASSET_QUALITY_SCORECARD.md",
    "docs/ASSET_ROI_CANVAS.md",
    "docs/ASSET_RISK_REVIEW.md",
    "docs/CANONICAL_ASSET_PRODUCTION_CLOSURE_CHECKLIST.md",
    "docs/HUMAN_APPROVAL_RECORD_TEMPLATE.md",
    "wbs/WBS-0005-canonical-asset-production-closure.md",
    ".github/ISSUE_TEMPLATE/asset_quality_review.yml",
    ".github/ISSUE_TEMPLATE/canonical_asset_closure.yml",
    ".github/workflows/canonical-asset-production-closure-check.yml",
]

REQUIRED_TEXT = {
    "basis/019_asset_quality_policy.md": [
        "Objective Fit",
        "ROI Link",
        "Quality Gate must be completed before Human Approval.",
    ],
    "basis/020_asset_roi_policy.md": [
        "Revenue is the final KGI.",
        "Operational Value",
        "measurement window",
    ],
    "basis/021_asset_risk_policy.md": [
        "Risk notes must travel with derived outputs.",
        "Approval bypass is prohibited.",
        "Runtime implementation remains out of scope.",
    ],
    "basis/022_asset_completion_policy.md": [
        "Canonical Asset Production is complete only when",
        "Repository overrides conversation.",
        "Human approves closure",
    ],
    "adr/ADR-0007-asset-quality-roi-risk-closure.md": [
        "Asset Quality, ROI, Risk, and Closure Control",
        "Proposed",
        "runtime implementation remains out of scope",
    ],
    "docs/CANONICAL_ASSET_PRODUCTION_CLOSURE_CHECKLIST.md": [
        "Canonical Asset Production can be closed",
        "Human approves closure",
        "Runtime remains out of scope",
    ],
    "wbs/WBS-0005-canonical-asset-production-closure.md": [
        "Current Objective",
        "Canonical Asset Production",
        "Runtime implementation remains out of scope",
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

    print("# ACIP Canonical Asset Production Closure Validation")
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
