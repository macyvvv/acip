from __future__ import annotations

import json
from pathlib import Path

from system.core.issue_creation_draft_bridge import build_issue_creation_drafts, persist_issue_creation_drafts


def _prepare(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "approved_issue_drafts.json").write_text(
        json.dumps(
            [
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-001",
                    "source_opportunity_id": "OPP-KABUKICHO-001",
                    "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                    "issue_body_draft": "body",
                    "target_product_scope": "app/products/kabukicho_survival_map_mvp",
                    "dependencies": ["system/runtime/research/request_kabukicho_expansion.json"],
                    "validation_readiness": "ready",
                    "source": "research_issue_draft_registry",
                    "approved_from_review_gate": True,
                },
                {
                    "draft_id": "DRAFT-OPP-KABUKICHO-002",
                    "source_opportunity_id": "OPP-KABUKICHO-002",
                    "title": "Rejected draft",
                    "issue_body_draft": "body",
                    "target_product_scope": "app/products/kabukicho_survival_map_mvp",
                    "dependencies": [],
                    "validation_readiness": "ready",
                    "source": "research_issue_draft_registry",
                    "approved_from_review_gate": False,
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def test_approved_entry_appears_in_issue_creation_drafts(tmp_path: Path) -> None:
    _prepare(tmp_path)
    drafts = build_issue_creation_drafts(tmp_path)

    assert len(drafts) == 1
    assert drafts[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert drafts[0]["ready_for_manual_github_issue_creation"] is True
    assert (tmp_path / "system" / "runtime" / "research" / "issue_creation_drafts.json").exists()
    assert (tmp_path / "system" / "runtime" / "research" / "issue_creation_drafts.md").exists()


def test_non_approved_entries_do_not_appear(tmp_path: Path) -> None:
    _prepare(tmp_path)
    (tmp_path / "system" / "runtime" / "research" / "approved_issue_drafts.json").write_text("[]\n", encoding="utf-8")
    assert build_issue_creation_drafts(tmp_path) == []


def test_issue_creation_output_is_deterministic(tmp_path: Path) -> None:
    _prepare(tmp_path)
    first = persist_issue_creation_drafts(tmp_path)
    second = persist_issue_creation_drafts(tmp_path)
    assert first == second
    json_path = tmp_path / "system" / "runtime" / "research" / "issue_creation_drafts.json"
    md_path = tmp_path / "system" / "runtime" / "research" / "issue_creation_drafts.md"
    assert json_path.exists()
    assert md_path.exists()
    assert json_path.read_text(encoding="utf-8") == json_path.read_text(encoding="utf-8")
    assert md_path.read_text(encoding="utf-8") == md_path.read_text(encoding="utf-8")


def test_source_attribution_is_preserved(tmp_path: Path) -> None:
    _prepare(tmp_path)
    drafts = build_issue_creation_drafts(tmp_path)
    assert drafts[0]["source"] == "research_issue_draft_registry"
