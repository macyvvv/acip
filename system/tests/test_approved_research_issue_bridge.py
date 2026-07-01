from __future__ import annotations

import json
from pathlib import Path

from system.core.approved_research_issue_bridge import build_approved_issue_drafts, persist_approved_issue_drafts


def _prepare(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_registry.json").write_text(
        json.dumps(
            [
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "source_opportunity_id": "OPP-KABUKICHO-001",
                    "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                    "status": "draft",
                    "ready_for_issue_creation": True,
                    "target_product_scope": "app/products/kabukicho_survival_map_mvp",
                    "dependencies": ["system/runtime/research/request_kabukicho_expansion.json"],
                    "validation_readiness": "ready",
                    "created_from": "system/runtime/research/issue_draft_opp_kabukicho_001.json",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    (research_dir / "issue_draft_opp_kabukicho_001.json").write_text(
        json.dumps(
            {
                "opportunity_id": "OPP-KABUKICHO-001",
                "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "objective": "Convert research findings into an incremental implementation issue for the Kabukicho Survival Map MVP.",
                "facts": ["fact 1"],
                "assumptions": ["assumption 1"],
                "implementation_constraints": ["constraint 1"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_approved_entry_appears_in_approved_issue_drafts(tmp_path: Path) -> None:
    _prepare(tmp_path)
    (tmp_path / "system" / "runtime" / "research" / "review_decisions.json").write_text(
        json.dumps(
            [
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "decision_status": "approved",
                    "reason": "ready",
                    "decided_at": "2026-01-01T00:00:00Z",
                    "decided_by": "repository",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    drafts = build_approved_issue_drafts(tmp_path)

    assert len(drafts) == 1
    assert drafts[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert drafts[0]["approved_from_review_gate"] is True


def test_pending_and_rejected_entries_are_excluded(tmp_path: Path) -> None:
    _prepare(tmp_path)
    (tmp_path / "system" / "runtime" / "research" / "review_decisions.json").write_text(
        json.dumps(
            [
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "decision_status": "pending",
                    "reason": "",
                    "decided_at": "",
                    "decided_by": "",
                },
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-002",
                    "decision_status": "rejected",
                    "reason": "no",
                    "decided_at": "2026-01-01T00:00:00Z",
                    "decided_by": "repository",
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    drafts = build_approved_issue_drafts(tmp_path)

    assert drafts == []


def test_approved_output_is_deterministic(tmp_path: Path) -> None:
    _prepare(tmp_path)
    decisions_path = tmp_path / "system" / "runtime" / "research" / "review_decisions.json"
    decisions_path.write_text(
        json.dumps(
            [
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "decision_status": "approved",
                    "reason": "ready",
                    "decided_at": "2026-01-01T00:00:00Z",
                    "decided_by": "repository",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    first = persist_approved_issue_drafts(tmp_path)
    second = persist_approved_issue_drafts(tmp_path)

    assert first == second
    assert (tmp_path / "system" / "runtime" / "research" / "approved_issue_drafts.json").exists()
    assert (tmp_path / "system" / "runtime" / "research" / "approved_issue_drafts.md").exists()
