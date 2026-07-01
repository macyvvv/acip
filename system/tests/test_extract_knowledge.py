from __future__ import annotations

from pathlib import Path

from system.scripts.extract_knowledge import extract_knowledge_from_text, update_knowledge_files


def test_extract_knowledge_is_deterministic(tmp_path: Path) -> None:
    text = """
Decision: keep repository native
Idea: add knowledge factory
Task: convert chat logs
Risk: duplication
ADR: canonical knowledge workflow
Parking Lot: later
"""
    first = extract_knowledge_from_text(text)
    second = extract_knowledge_from_text(text)
    assert first == second
    assert first.decisions == ["keep repository native"]
    assert first.ideas == ["add knowledge factory"]
    assert first.tasks == ["convert chat logs"]
    assert first.risks == ["duplication"]
    assert first.adr_candidates == ["canonical knowledge workflow"]
    assert first.parking_lot == ["later"]


def test_update_knowledge_files_writes_expected_paths(tmp_path: Path) -> None:
    extracted = extract_knowledge_from_text(
        "Decision: keep repository native\nIdea: add knowledge factory\nTask: convert chat logs\n"
    )
    outputs = update_knowledge_files(extracted, tmp_path)
    assert outputs["dashboard"] == tmp_path / "knowledge" / "dashboard.md"
    assert outputs["ideas"].exists()
    assert "keep repository native" in (tmp_path / "knowledge" / "decision_log.md").read_text(encoding="utf-8")
