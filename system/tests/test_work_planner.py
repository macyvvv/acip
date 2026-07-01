from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.work_planner import WorkPlanner


def test_work_planner_builds_candidates(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission": "Build an AI Native Company.", "current_phase": "GitHub Foundation", "current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"approval_required": False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_constitution").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_constitution" / "constitution.json").write_text(json.dumps({"status": "stable"}), encoding="utf-8")
    planner = WorkPlanner(tmp_path)
    plan = planner.build()
    assert plan.candidate_items[0].candidate_id == "WP-0194"
    assert plan.candidate_items[-1].approval_required is False
    planner.write(plan)
    assert (tmp_path / "runtime" / "work_planner" / "latest.json").exists()


def test_work_planner_surfaces_research_candidate(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission": "Build an AI Native Company.", "current_phase": "GitHub Foundation", "current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"approval_required": False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_constitution").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_constitution" / "constitution.json").write_text(json.dumps({"status": "stable"}), encoding="utf-8")
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

    planner = WorkPlanner(tmp_path)
    plan = planner.build()
    planner.write(plan)

    payload = json.loads((tmp_path / "runtime" / "work_planner" / "latest.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "runtime" / "work_planner" / "latest.md").read_text(encoding="utf-8")

    research_candidates = [candidate for candidate in payload["candidate_items"] if candidate["source"] == "research_issue_draft_registry"]
    assert research_candidates
    assert research_candidates[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert research_candidates[0]["source_opportunity_id"] == "OPP-KABUKICHO-001"
    assert research_candidates[0]["ready_for_issue_creation"] is True
    assert "research_issue_draft_registry" in markdown
    assert "DRAFT-OPP-KABUKICHO-001" in markdown
    assert "source_opportunity_id" in markdown
