from __future__ import annotations

import json
from pathlib import Path

from system.core.research_issue_draft import build_issue_draft_registry, intake_issue_draft, write_issue_draft_registry


def test_issue_draft_registry_registers_kabukicho_draft(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_opp_kabukicho_001.json").write_text(
        json.dumps({
            "opportunity_id": "OPP-KABUKICHO-001",
            "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
            "dependencies": ["app/products/kabukicho_survival_map_mvp"],
        }),
        encoding="utf-8",
    )

    registry = build_issue_draft_registry(tmp_path)

    assert registry[0]["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert registry[0]["source_opportunity_id"] == "OPP-KABUKICHO-001"
    assert registry[0]["ready_for_issue_creation"] is False
    assert registry[0]["target_product_scope"] == "app/products/kabukicho_survival_map_mvp"


def test_issue_draft_registry_writes_artifacts(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_opp_kabukicho_001.json").write_text(
        json.dumps({
            "opportunity_id": "OPP-KABUKICHO-001",
            "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
            "dependencies": ["app/products/kabukicho_survival_map_mvp"],
        }),
        encoding="utf-8",
    )

    registry = write_issue_draft_registry(tmp_path)

    assert (research_dir / "issue_draft_registry.json").exists()
    assert (research_dir / "issue_draft_registry.md").exists()
    assert registry[0]["created_from"].endswith("issue_draft_opp_kabukicho_001.json")


def test_issue_draft_intake_returns_canonical_entry(tmp_path: Path) -> None:
    research_dir = tmp_path / "system" / "runtime" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "issue_draft_opp_kabukicho_001.json").write_text(
        json.dumps({
            "opportunity_id": "OPP-KABUKICHO-001",
            "title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
            "dependencies": ["app/products/kabukicho_survival_map_mvp"],
        }),
        encoding="utf-8",
    )

    entry = intake_issue_draft(tmp_path)

    assert entry["draft_id"] == "DRAFT-OPP-KABUKICHO-001"
    assert entry["source_opportunity_id"] == "OPP-KABUKICHO-001"
    assert entry["ready_for_issue_creation"] is False
