#!/usr/bin/env python3
"""Validate ACIP Phase 0 GitHub foundation.

This script intentionally validates repository governance only.
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
    "README.md",
    "AGENTS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "VERSION",
    ".gitignore",
    ".env.example",
    ".github/ISSUE_TEMPLATE/codex_review.yml",
    ".github/ISSUE_TEMPLATE/design.yml",
    ".github/ISSUE_TEMPLATE/implementation.yml",
    ".github/PULL_REQUEST_TEMPLATE/pull_request_template.md",
    "adr/ADR-0001-gitops-operation.md",
    "adr/ADR-0002-foundation-automation.md",
    "basis/000_project_charter.md",
    "basis/003_authority_matrix.md",
    "basis/004_responsibility_matrix.md",
    "basis/005_measurement_definition.md",
    "basis/006_acceptance_criteria.md",
    "basis/007_automation_scope.md",
    "docs/GITHUB_FOUNDATION_CHECKLIST.md",
]

REQUIRED_DIRS = [
    ".github",
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
    ".github/workflows",
    "adr",
    "basis",
    "docs",
    "scripts",
]

REQUIRED_TEXT = {
    "README.md": [
        "GitHub  = Source of Truth",
        "No change is official until merged into `main`.",
    ],
    "AGENTS.md": [
        "Runtime implementation is not approved.",
        "Never push directly to `main`",
        "Never implement runtime behavior before approval",
        "auto posting",
        "platform API integration in Phase 0",
        "runtime agent implementation in Phase 0",
    ],
    "basis/007_automation_scope.md": [
        "repository governance validation",
        "Runtime agent execution",
        "approval bypass",
    ],
}

PROHIBITED_PATH_PARTS = [
    ".runtime",
    "runtime_agent",
    "auto_post",
    "platform_api",
    "scraper",
]

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


def check_prohibited_paths() -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for part in PROHIBITED_PATH_PARTS:
            if part in relative:
                results.append(
                    CheckResult(
                        name=f"prohibited path: {relative}",
                        ok=False,
                        detail=f"contains {part}",
                    )
                )
    if not results:
        results.append(CheckResult("prohibited paths", True, "none found"))
    return results


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
    results.extend(check_prohibited_paths())
    results.extend(check_prohibited_keywords())
    return results


def main() -> int:
    results = run_checks()
    failed = [result for result in results if not result.ok]

    print("# ACIP Foundation Validation")
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
