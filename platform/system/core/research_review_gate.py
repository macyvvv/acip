from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReviewDecision:
    draft_id: str
    decision_status: str
    reason: str
    decided_at: str
    decided_by: str


def _runtime_path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "system" / "runtime" / Path(*parts)


def _path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    system_path = root / "system" / "runtime" / Path(*parts)
    legacy_path = root / "runtime" / Path(*parts)
    return system_path if system_path.exists() or not legacy_path.exists() else legacy_path


def build_review_queue(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    path = _path(base_path, "work_planner", "latest.json")
    if not path.exists():
        return []
    plan = json.loads(path.read_text(encoding="utf-8"))
    candidates = plan.get("candidate_items", []) if isinstance(plan, dict) else []
    queue: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("source") != "research_issue_draft_registry":
            continue
        if not bool(candidate.get("ready_for_issue_creation", False)):
            continue
        queue.append(
            {
                "draft_id": candidate.get("draft_id", candidate.get("candidate_id", "")),
                "source_opportunity_id": candidate.get("source_opportunity_id", ""),
                "title": candidate.get("title", ""),
                "objective": candidate.get("objective", ""),
                "source": candidate.get("source", ""),
                "issue_body_draft": candidate.get("issue_body_draft", ""),
            }
        )
    return queue


def load_review_decisions(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    path = _path(base_path, "research", "review_decisions.json")
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def persist_review_queue(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    queue = build_review_queue(base_path)
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "review_queue.json").write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "review_queue.md").write_text(_to_markdown(queue), encoding="utf-8")
    decisions = _merge_pending_decisions(queue, load_review_decisions(base_path))
    (runtime_dir / "review_decisions.json").write_text(json.dumps(decisions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return queue


def approve_review_decision(base_path: Path | str | None, draft_id: str, reason: str, decided_by: str = "repository") -> ReviewDecision:
    return _write_decision(base_path, draft_id, "approved", reason, decided_by)


def reject_review_decision(base_path: Path | str | None, draft_id: str, reason: str, decided_by: str = "repository") -> ReviewDecision:
    return _write_decision(base_path, draft_id, "rejected", reason, decided_by)


def approved_candidates(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    queue = build_review_queue(base_path)
    decisions = load_review_decisions(base_path)
    approved_ids = {entry.get("draft_id") for entry in decisions if entry.get("decision_status") == "approved"}
    return [item for item in queue if item.get("draft_id") in approved_ids]


def _write_decision(base_path: Path | str | None, draft_id: str, status: str, reason: str, decided_by: str) -> ReviewDecision:
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    decisions = load_review_decisions(base_path)
    updated = [entry for entry in decisions if entry.get("draft_id") != draft_id]
    decision = ReviewDecision(
        draft_id=draft_id,
        decision_status=status,
        reason=reason,
        decided_at=datetime.now(timezone.utc).isoformat(),
        decided_by=decided_by,
    )
    updated.append(
        {
            "draft_id": decision.draft_id,
            "decision_status": decision.decision_status,
            "reason": decision.reason,
            "decided_at": decision.decided_at,
            "decided_by": decision.decided_by,
        }
    )
    updated.sort(key=lambda entry: entry["draft_id"])
    (runtime_dir / "review_decisions.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return decision


def _merge_pending_decisions(queue: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = {entry.get("draft_id"): entry for entry in decisions if entry.get("draft_id")}
    merged = []
    for item in queue:
        draft_id = item.get("draft_id", "")
        if draft_id in existing:
            merged.append(existing[draft_id])
        else:
            merged.append(
                {
                    "draft_id": draft_id,
                    "decision_status": "pending",
                    "reason": "",
                    "decided_at": "",
                    "decided_by": "",
                }
            )
    merged.sort(key=lambda entry: entry["draft_id"])
    return merged


def _to_markdown(queue: list[dict[str, Any]]) -> str:
    lines = ["# RESEARCH_REVIEW_QUEUE", ""]
    for item in queue:
        lines.extend(
            [
                f"## {item.get('draft_id', '')}",
                f"- source_opportunity_id: {item.get('source_opportunity_id', '')}",
                f"- title: {item.get('title', '')}",
                f"- source: {item.get('source', '')}",
                f"- objective: {item.get('objective', '')}",
                "",
            ]
        )
    return "\n".join(lines)
