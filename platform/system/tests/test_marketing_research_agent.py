from __future__ import annotations

import json
from pathlib import Path

from system.core.marketing_research_agent import (
    generate_research_output,
    load_research_context,
    write_research_artifacts,
)


def _prepare_context(tmp_path: Path) -> None:
    (tmp_path / "system" / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "planning" / "latest.json").write_text(
        json.dumps({"current_objective": "Kabukicho Survival Map MVP"}),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy"}),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "research").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "research" / "opportunities.json").write_text("[]", encoding="utf-8")
    (tmp_path / "system" / "runtime" / "research" / "insights.json").write_text("[]", encoding="utf-8")


def test_marketing_research_agent_is_deterministic(tmp_path: Path) -> None:
    _prepare_context(tmp_path)
    context = load_research_context(tmp_path)
    request = {
        "request_id": "REQ-RESEARCH-0001",
        "topic": "Kabukicho Survival Map MVP / expansion research",
        "target_user": "Visitors",
    }
    output_1 = generate_research_output(request, context)
    output_2 = generate_research_output(request, context)

    assert output_1 == output_2
    assert output_1["request_id"] == "REQ-RESEARCH-0001"
    assert output_1["topic"] == request["topic"]
    assert output_1["facts"]
    assert output_1["assumptions"]
    assert output_1["hypotheses"]
    assert output_1["recommendations"]
    assert output_1["opportunities"]


def test_marketing_research_agent_separates_output_sections(tmp_path: Path) -> None:
    _prepare_context(tmp_path)
    context = load_research_context(tmp_path)
    output = generate_research_output(
        {
            "request_id": "REQ-RESEARCH-0001",
            "topic": "Kabukicho Survival Map MVP / expansion research",
            "target_user": "Visitors",
        },
        context,
    )

    assert all(isinstance(item, str) for item in output["facts"])
    assert all(isinstance(item, str) for item in output["assumptions"])
    assert all(isinstance(item, str) for item in output["hypotheses"])
    assert all(isinstance(item, str) for item in output["recommendations"])
    assert all("opportunity_id" in item for item in output["opportunities"])


def test_marketing_research_agent_writes_canonical_artifacts(tmp_path: Path) -> None:
    _prepare_context(tmp_path)
    context = load_research_context(tmp_path)
    output = generate_research_output(
        {
            "request_id": "REQ-RESEARCH-0001",
            "topic": "Kabukicho Survival Map MVP / expansion research",
            "target_user": "Visitors",
        },
        context,
    )
    paths = write_research_artifacts(tmp_path, output)

    assert paths["latest_json"] == tmp_path / "system" / "runtime" / "research" / "latest.json"
    assert paths["opportunities_json"] == tmp_path / "system" / "runtime" / "research" / "opportunities.json"
    assert paths["insights_json"] == tmp_path / "system" / "runtime" / "research" / "insights.json"
    assert json.loads(paths["latest_json"].read_text(encoding="utf-8"))["request_id"] == "REQ-RESEARCH-0001"
    assert json.loads(paths["opportunities_json"].read_text(encoding="utf-8"))[0]["opportunity_id"] == "OPP-KABUKICHO-001"
    assert json.loads(paths["insights_json"].read_text(encoding="utf-8"))[0].startswith("Higher intent")
