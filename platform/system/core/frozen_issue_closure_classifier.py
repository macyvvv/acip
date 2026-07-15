from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


@dataclass(frozen=True)
class FrozenIssueClosureRecord:
    issue_number: int
    title: str
    current_bucket: str
    closure_disposition: str
    github_action_recommended: str
    state_reason_if_closed: str
    classification_reason: str
    evidence_source: str
    safe_to_apply: bool


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _completed_issue_numbers(root: Path) -> set[int]:
    completed_dir = root / "system" / "runtime" / "issues" / "completed"
    numbers: set[int] = set()
    if not completed_dir.exists():
        return numbers
    for path in completed_dir.glob("issue_*.json"):
        try:
            payload = _load_json(path)
        except Exception:
            continue
        issue_number = payload.get("issue_number")
        if isinstance(issue_number, int):
            numbers.add(issue_number)
    return numbers


def _open_issue_numbers(root: Path) -> set[int]:
    open_issues_path = root / "system" / "runtime" / "github" / "open_issues.json"
    if not open_issues_path.exists():
        return set()
    try:
        payload = _load_json(open_issues_path)
    except Exception:
        return set()
    numbers: set[int] = set()
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict) and isinstance(item.get("number"), int):
                numbers.add(item["number"])
    return numbers


def _disposition_for_issue(item: dict[str, Any]) -> tuple[str, str, str, str, str]:
    issue_number = item["issue_number"]
    title = item["title"]
    category = item["category"]
    current_status = item["current_status"]
    evidence_source = item.get("title_source", "roadmap")

    if current_status == "completed":
        return (
            "close_completed",
            "close",
            "completed",
            "completed repository evidence exists",
            evidence_source,
        )

    if current_status == "archived":
        if category == "governance/operator":
            return (
                "keep_open_governance_backlog",
                "keep_open",
                "",
                "governance and operator backlog remains visible but open",
                evidence_source,
            )
        if category == "broad_architecture":
            return (
                "keep_open_broad_architecture",
                "keep_open",
                "",
                "broad architecture work remains open unless explicitly marked not planned",
                evidence_source,
            )
        if category == "infra_foundation":
            return (
                "keep_open_dependency_waiting",
                "keep_open",
                "",
                "infrastructure item remains open as a dependency or support layer",
                evidence_source,
            )
        if category == "product_incremental":
            return (
                "keep_open_parked",
                "keep_open",
                "",
                "product work is parked from the active baseline",
                evidence_source,
            )
        return (
            "keep_open_parked",
            "keep_open",
            "",
            "archived item remains visible but not active",
            evidence_source,
        )

    return (
        "keep_open_parked",
        "keep_open",
        "",
        "non-terminal portfolio item remains visible for later review",
        evidence_source,
    )


def build_frozen_issue_closure_plan(base_path: Path | None = None) -> dict[str, Any]:
    root = Path(base_path) if base_path is not None else get_repo_root()
    roadmap_path = root / "system" / "runtime" / "roadmap" / "issue_portfolio.json"
    roadmap = _load_json(roadmap_path)
    issues = roadmap.get("issues", [])
    completed_numbers = _completed_issue_numbers(root)
    open_numbers = _open_issue_numbers(root)

    records: list[FrozenIssueClosureRecord] = []
    for item in issues:
        if item.get("priority_bucket") != "FROZEN":
            continue
        closure_disposition, github_action_recommended, state_reason_if_closed, classification_reason, evidence_source = _disposition_for_issue(item)
        issue_number = item["issue_number"]
        title = item["title"]
        if closure_disposition == "close_completed":
            safe_to_apply = issue_number in open_numbers
            if issue_number in completed_numbers:
                evidence_source = "platform/system/runtime/issues/completed/"
        else:
            safe_to_apply = False
        records.append(
            FrozenIssueClosureRecord(
                issue_number=issue_number,
                title=title,
                current_bucket="FROZEN",
                closure_disposition=closure_disposition,
                github_action_recommended=github_action_recommended,
                state_reason_if_closed=state_reason_if_closed,
                classification_reason=classification_reason,
                evidence_source=evidence_source,
                safe_to_apply=safe_to_apply,
            )
        )

    records.sort(key=lambda item: item.issue_number)
    plan = {
        "generated_at": "deterministic",
        "source_artifacts": [
            "platform/docs/current/ISSUE_PORTFOLIO_ROADMAP.md",
            "platform/docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md",
            "platform/docs/current/ISSUE_OPERATOR_QUICKSTART.md",
            "platform/system/runtime/roadmap/issue_portfolio.json",
            "platform/system/runtime/issues/completed/",
            "platform/system/runtime/github/open_issues.json",
        ],
        "summary": {
            "frozen_issue_count": len(records),
            "close_now_count": sum(1 for item in records if item.github_action_recommended == "close"),
            "keep_open_count": sum(1 for item in records if item.github_action_recommended == "keep_open"),
            "safe_to_apply_count": sum(1 for item in records if item.safe_to_apply),
        },
        "issues": [asdict(item) for item in records],
    }
    return plan

