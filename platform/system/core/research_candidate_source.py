from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _runtime_path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "system" / "runtime" / Path(*parts)


def load_issue_draft_registry(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    path = _runtime_path(base_path, "research", "issue_draft_registry.json")
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def research_issue_draft_candidates(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for entry in load_issue_draft_registry(base_path):
        if not bool(entry.get("ready_for_issue_creation", False)):
            continue
        draft_draft = _load_issue_draft(base_path, str(entry.get("draft_id", "")))
        if not draft_draft:
            continue
        candidates.append(
            {
                "candidate_id": entry.get("draft_id", ""),
                "title": draft_draft.get("title", ""),
                "proposed_pack_or_ep": "RESEARCH-DRAFT",
                "objective": draft_draft.get("objective", ""),
                "rationale": draft_draft.get("facts", [""])[0] if draft_draft.get("facts") else "",
                "draft_id": entry.get("draft_id", ""),
                "source_opportunity_id": entry.get("source_opportunity_id", ""),
                "ready_for_issue_creation": bool(entry.get("ready_for_issue_creation", False)),
                "mission_contribution": 4,
                "management_cost_reduction": 4,
                "risk_reduction": 4,
                "strategic_value": 4,
                "operational_value": 4,
                "learning_value": 4,
                "dependencies": list(draft_draft.get("dependencies", [])),
                "blocked_by": [],
                "approval_required": False,
                "recommended_action": "create_issue",
                "issue_body_draft": _issue_body_draft(draft_draft),
                "source": "research_issue_draft_registry",
            }
        )
    return candidates


def _load_issue_draft(base_path: Path | str | None, draft_id: str) -> dict[str, Any]:
    if draft_id == "DRAFT-OPP-KABUKICHO-001":
        path = _runtime_path(base_path, "research", "issue_draft_opp_kabukicho_001.json")
    else:
        return {}
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _issue_body_draft(draft: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {draft.get('title', '')}",
            "",
            f"Objective: {draft.get('objective', '')}",
            "",
            "## Facts",
            *[f"- {item}" for item in draft.get("facts", [])],
            "",
            "## Assumptions",
            *[f"- {item}" for item in draft.get("assumptions", [])],
            "",
            "## Recommendations",
            *[f"- {item}" for item in draft.get("implementation_constraints", [])],
            "",
        ]
    )
