from __future__ import annotations

import json
from pathlib import Path

from system.core.research_candidate_source import research_issue_draft_candidates


def test_ready_registry_entry_becomes_candidate(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_registry.json").write_text(
        json.dumps([
            {
                "draft_id": "DRAFT-OPP-KABUKICHO-001",
                "source_opportunity_id": "OPP-KABUKICHO-001",
                "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "status": "draft",
                "ready_for_issue_creation": True,
                "target_product_scope": "app/products/kabukicho_survival_map_mvp",
                "dependencies": ["app/products/kabukicho_survival_map_mvp"],
                "validation_readiness": "ready",
                "created_from": "system/runtime/research/issue_draft_opp_kabukicho_001.json",
            }
        ]),
        encoding="utf-8",
    )
    (research_dir / "issue_draft_opp_kabukicho_001.json").write_text(
        json.dumps({
            "opportunity_id": "OPP-KABUKICHO-001",
            "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
            "objective": "Convert research findings into an incremental implementation issue for the Kabukicho Survival Map MVP.",
            "facts": ["Repository-native research artifacts are deterministic."],
            "assumptions": ["Night-time visitors need fast, local decision support."],
            "recommendations": ["Interview local visitors and repeat workers."],
            "dependencies": ["app/products/kabukicho_survival_map_mvp"],
            "implementation_constraints": ["Incremental only."],
        }),
        encoding="utf-8",
    )

    candidates = research_issue_draft_candidates(tmp_path)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["candidate_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert candidate["source"] == "research_issue_draft_registry"
    assert candidate["approval_required"] is False
    assert candidate["dependencies"] == ["app/products/kabukicho_survival_map_mvp"]
    assert candidate["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert candidate["source_opportunity_id"] == "OPP-KABUKICHO-001"
    assert candidate["ready_for_issue_creation"] is True
    assert candidate["issue_body_draft"].startswith("# Kabukicho Survival Map MVP expansion")


def test_non_ready_entry_is_excluded(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_registry.json").write_text(
        json.dumps([
            {
                "draft_id": "DRAFT-OPP-KABUKICHO-001",
                "source_opportunity_id": "OPP-KABUKICHO-001",
                "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "status": "draft",
                "ready_for_issue_creation": False,
                "target_product_scope": "app/products/kabukicho_survival_map_mvp",
                "dependencies": [],
                "validation_readiness": "blocked",
                "created_from": "system/runtime/research/issue_draft_opp_kabukicho_001.json",
            }
        ]),
        encoding="utf-8",
    )

    assert research_issue_draft_candidates(tmp_path) == []
