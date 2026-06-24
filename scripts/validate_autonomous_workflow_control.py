#!/usr/bin/env python3
"""Validate ACIP Autonomous Workflow Control.

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
    "basis/037_autonomous_workflow_policy.md",
    "basis/038_runbook_policy.md",
    "basis/039_control_plane_policy.md",
    "basis/040_failure_recovery_policy.md",
    "basis/041_status_reporting_policy.md",
    "adr/ADR-0012-autonomous-workflow-control-plane.md",
    "runbooks/RB-0001-mission-to-issue.md",
    "runbooks/RB-0002-issue-to-wbs.md",
    "runbooks/RB-0003-wbs-to-codex-instruction.md",
    "runbooks/RB-0004-pr-review-prep.md",
    "runbooks/RB-0005-validation-failure-recovery.md",
    "runbooks/RB-0006-emergency-stop.md",
    "control/MISSION_INTAKE.md",
    "control/TASK_QUEUE.md",
    "control/REVIEW_QUEUE.md",
    "control/RETRY_QUEUE.md",
    "control/ESCALATION_QUEUE.md",
    "control/PARKING_LOT.md",
    "control/DECISION_LOG.md",
    "control/STATUS_REPORT_TEMPLATE.md",
    "docs/AUTONOMOUS_WORKFLOW_CHECKLIST.md",
    "docs/CODEX_AUTONOMOUS_EXECUTION_PROMPT.md",
    "wbs/WBS-0008-autonomous-workflow-control.md",
    ".github/ISSUE_TEMPLATE/autonomous_workflow.yml",
    ".github/workflows/autonomous-workflow-control-check.yml",
]

REQUIRED_DIRS = ["runbooks", "control"]

REQUIRED_TEXT = {
    "basis/037_autonomous_workflow_policy.md": [
        "Human handles only",
        "approval bypass",
        "Repository overrides conversation.",
    ],
    "basis/038_runbook_policy.md": [
        "Human Boundary",
        "failure modes",
        "done condition",
    ],
    "basis/039_control_plane_policy.md": [
        "Mission Intake",
        "Task Queue",
        "Runtime implementation remains out of scope.",
    ],
    "basis/040_failure_recovery_policy.md": [
        "failed validation",
        "Retry only when failure cause is known.",
        "Do not bypass approval.",
    ],
    "basis/041_status_reporting_policy.md": [
        "decision-ready summaries",
        "Human Decision Required",
        "routine investigation",
    ],
    "adr/ADR-0012-autonomous-workflow-control-plane.md": [
        "Autonomous Workflow Control Plane",
        "Mission",
        "runtime implementation remains out of scope",
    ],
    "docs/CODEX_AUTONOMOUS_EXECUTION_PROMPT.md": [
        "Keep Human out of routine execution.",
        "Run validation.",
        "approval bypass",
    ],
    "wbs/WBS-0008-autonomous-workflow-control.md": [
        "Current Objective",
        "Agent OS Foundation",
        "Human is responsible only for Mission, Approval, and Emergency Stop",
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
                failures.append(CheckResult(f"prohibited keyword in {relative}", False, keyword))
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

    print("# ACIP Autonomous Workflow Control Validation")
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
