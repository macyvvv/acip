from __future__ import annotations

import json
from pathlib import Path

from system.core.research_review_gate import approve_review_decision, build_review_queue, persist_review_queue, reject_review_decision, approved_candidates


def _prepare(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(
        json.dumps({
            "candidate_items": [
                {
                    "candidate_id": "DRAFT-OPP-KABUKICHO-001",
                    "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                    "source": "research_issue_draft_registry",
                    "objective": "Convert research findings into an incremental implementation issue for the Kabukicho Survival Map MVP.",
                    "rationale": "Repository-native research artifacts are deterministic.",
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "source_opportunity_id": "OPP-KABUKICHO-001",
                    "ready_for_issue_creation": True,
                    "issue_body_draft": "body",
                },
                {
                    "candidate_id": "WP-0194",
                    "title": "EP-0194 Work Planner Contract",
                    "source": "planner_native",
                    "objective": "Define the work planner contract.",
                    "rationale": "establish boundary",
                    "draft_id": None,
                    "source_opportunity_id": None,
                    "ready_for_issue_creation": False,
                    "issue_body_draft": "body",
                },
            ]
        }),
        encoding="utf-8",
    )


def test_review_queue_contains_only_research_candidates(tmp_path: Path) -> None:
    _prepare(tmp_path)
    queue = build_review_queue(tmp_path)
    assert len(queue) == 1
    assert queue[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert queue[0]["source"] == "research_issue_draft_registry"


def test_review_queue_persists_pending_by_default(tmp_path: Path) -> None:
    _prepare(tmp_path)
    queue = persist_review_queue(tmp_path)
    decisions = json.loads((tmp_path / "system" / "runtime" / "research" / "review_decisions.json").read_text(encoding="utf-8"))
    assert queue[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert decisions[0]["decision_status"] == "pending"


def test_review_decisions_are_persisted_deterministically(tmp_path: Path) -> None:
    _prepare(tmp_path)
    approve_review_decision(tmp_path, "DRAFT-OPP-KABUKICHO-001", "approved for implementation")
    reject_review_decision(tmp_path, "DRAFT-OPP-KABUKICHO-002", "out of scope")
    decisions = json.loads((tmp_path / "system" / "runtime" / "research" / "review_decisions.json").read_text(encoding="utf-8"))
    assert decisions[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert decisions[0]["decision_status"] == "approved"
    assert decisions[1]["decision_status"] == "rejected"


def test_approved_candidates_are_visible(tmp_path: Path) -> None:
    _prepare(tmp_path)
    persist_review_queue(tmp_path)
    approve_review_decision(tmp_path, "DRAFT-OPP-KABUKICHO-001", "approved for implementation")
    assert approved_candidates(tmp_path)[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
