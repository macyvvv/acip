from __future__ import annotations

import json
from pathlib import Path

from system.scripts.dataops.verify_sourced_facts import extract_figures, verify_sourced_facts


def _write_artifact(base_path: Path, business_id: str, role_id: str, task_id: str, stdout: str) -> None:
    artifact_dir = base_path / "platform/system/runtime/business_agents" / business_id / role_id / task_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "latest.json").write_text(json.dumps({"stdout": stdout}), encoding="utf-8")


def test_extract_figures_finds_currency_and_percentages() -> None:
    text = "Priced at $20/month, saves 70% of the time, or ¥1,500 in Japan."
    figures = extract_figures(text)
    assert "$20" in figures
    assert "70%" in figures
    assert "¥1,500" in figures


def test_no_figures_in_draft_returns_empty(tmp_path: Path) -> None:
    _write_artifact(tmp_path, "text_syndicate", "doc_creation", "task-0001", "A draft with no numbers at all.")
    assert verify_sourced_facts("text_syndicate", "doc_creation", "task-0001", tmp_path) == []


def test_figure_present_in_market_research_is_not_flagged(tmp_path: Path) -> None:
    _write_artifact(
        tmp_path, "text_syndicate", "market_research", "task-0001", "Perplexity Pro costs $20/month per the vendor site."
    )
    _write_artifact(tmp_path, "text_syndicate", "doc_creation", "task-0002", "Perplexity Pro is priced at $20/month.")
    assert verify_sourced_facts("text_syndicate", "doc_creation", "task-0002", tmp_path) == []


def test_fabricated_figure_with_no_research_precedent_is_flagged(tmp_path: Path) -> None:
    # Mirrors the real incident this check exists for: doc_creation stated
    # a materially wrong Perplexity Pro price with zero research backing.
    _write_artifact(
        tmp_path, "text_syndicate", "market_research", "task-0001", "GetResponse pays 40-60% recurring commission."
    )
    _write_artifact(tmp_path, "text_syndicate", "doc_creation", "task-0002", "Perplexity Pro costs just ¥20/月.")
    unsourced = verify_sourced_facts("text_syndicate", "doc_creation", "task-0002", tmp_path)
    assert "¥20" in unsourced


def test_no_market_research_directory_flags_every_figure(tmp_path: Path) -> None:
    _write_artifact(tmp_path, "text_syndicate", "doc_creation", "task-0001", "Costs $9.99/month.")
    unsourced = verify_sourced_facts("text_syndicate", "doc_creation", "task-0001", tmp_path)
    assert "$9.99" in unsourced


def test_different_business_research_does_not_source_another_businesss_draft(tmp_path: Path) -> None:
    _write_artifact(tmp_path, "kabukicho_survival_map", "market_research", "task-0001", "Locker fee is ¥500/day.")
    _write_artifact(tmp_path, "text_syndicate", "doc_creation", "task-0001", "Costs ¥500/day.")
    unsourced = verify_sourced_facts("text_syndicate", "doc_creation", "task-0001", tmp_path)
    assert "¥500" in unsourced
