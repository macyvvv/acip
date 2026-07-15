from __future__ import annotations

from pathlib import Path

from system.core.knowledge_candidate_source import build_knowledge_candidates, persist_knowledge_candidates


def _prepare_knowledge(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    root.mkdir(parents=True)
    (root / "decisions.md").write_text("# DECISIONS\n\n- decision: keep repository native\n", encoding="utf-8")
    (root / "ideas.md").write_text("# IDEAS\n\n- idea: knowledge factory\n- idea: knowledge factory\n", encoding="utf-8")
    (root / "tasks.md").write_text("# TASKS\n\n- task: extract knowledge\n", encoding="utf-8")
    (root / "risks.md").write_text("# RISKS\n\n- risk: duplication\n", encoding="utf-8")
    (root / "adrs.md").write_text("# ADRS\n\n- adr: canonical pipeline\n", encoding="utf-8")
    (root / "parking_lot.md").write_text("# PARKING_LOT\n\n- later: revise glossary\n", encoding="utf-8")


def test_empty_knowledge_assets_are_safe(tmp_path: Path) -> None:
    assert build_knowledge_candidates(tmp_path) == []


def test_knowledge_candidates_are_deterministic_and_deduplicated(tmp_path: Path) -> None:
    _prepare_knowledge(tmp_path)
    first = build_knowledge_candidates(tmp_path)
    second = build_knowledge_candidates(tmp_path)
    assert first == second
    assert len([candidate for candidate in first if candidate["source_asset"] == "ideas.md"]) == 1


def test_knowledge_candidates_preserve_source_and_usability(tmp_path: Path) -> None:
    _prepare_knowledge(tmp_path)
    candidates = build_knowledge_candidates(tmp_path)
    sources = {candidate["source_asset"] for candidate in candidates}
    usability = {candidate["usable_by"] for candidate in candidates}
    assert {"decisions.md", "ideas.md", "tasks.md", "risks.md", "adrs.md", "parking_lot.md"} <= sources
    assert {"planner", "research", "both"} <= usability


def test_knowledge_candidate_artifacts_are_written(tmp_path: Path) -> None:
    _prepare_knowledge(tmp_path)
    candidates = persist_knowledge_candidates(tmp_path)
    runtime_dir = tmp_path / "system" / "runtime" / "knowledge"
    assert (runtime_dir / "knowledge_candidates.json").exists()
    assert (runtime_dir / "knowledge_candidates.md").exists()
    assert candidates[0]["candidate_id"].startswith("KC-")
