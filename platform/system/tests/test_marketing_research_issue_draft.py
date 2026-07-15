from __future__ import annotations

import json
from pathlib import Path


def test_marketing_research_issue_draft_is_canonical(tmp_path: Path) -> None:
    root = Path(".")
    json_path = root / "system" / "runtime" / "research" / "issue_draft_opp_kabukicho_001.json"
    md_path = root / "system" / "runtime" / "research" / "issue_draft_opp_kabukicho_001.md"

    assert json_path.exists()
    assert md_path.exists()

    draft = json.loads(json_path.read_text(encoding="utf-8"))
    assert draft["opportunity_id"] == "OPP-KABUKICHO-001"
    assert draft["title"].startswith("Kabukicho Survival Map MVP expansion")
    assert "platform/app/products/kabukicho_survival_map_mvp" in draft["dependencies"]
    assert "No GitHub issue is auto-created." in draft["validation_criteria"]
    assert "No automatic issue creation." in draft["implementation_constraints"]
    markdown = md_path.read_text(encoding="utf-8")
    assert "# ISSUE_DRAFT_OPP_KABUKICHO_001" in markdown
    assert "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities" in markdown
