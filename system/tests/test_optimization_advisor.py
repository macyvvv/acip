from __future__ import annotations

import json
from pathlib import Path

from system.core.kpi_store import update_kpi
from system.core.optimization_advisor import analyze_optimization_opportunities, write_optimization_suggestions


def test_high_external_capacity_generates_suggestion(tmp_path: Path) -> None:
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    update_kpi(True, tmp_path, issue_number=33)
    update_kpi(False, tmp_path, issue_number=34, error_type="usage_limit")
    suggestions = analyze_optimization_opportunities(tmp_path)

    assert any(suggestion["type"] == "model_selection" for suggestion in suggestions)


def test_low_success_rate_generates_suggestion(tmp_path: Path) -> None:
    update_kpi(False, tmp_path, issue_number=32, error_type="unknown")
    suggestions = analyze_optimization_opportunities(tmp_path)

    assert any(suggestion["type"] == "execution_health" for suggestion in suggestions)


def test_no_pattern_returns_empty_output(tmp_path: Path) -> None:
    update_kpi(True, tmp_path, issue_number=32)
    update_kpi(True, tmp_path, issue_number=33)
    suggestions = analyze_optimization_opportunities(tmp_path)

    assert suggestions == []


def test_suggestions_are_written(tmp_path: Path) -> None:
    update_kpi(False, tmp_path, issue_number=32, error_type="unknown")
    suggestions = write_optimization_suggestions(tmp_path)
    path = tmp_path / "system" / "runtime" / "knowledge" / "optimization_suggestions.json"
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == suggestions
