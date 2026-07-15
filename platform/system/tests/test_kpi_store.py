from __future__ import annotations

import json
from pathlib import Path

from system.core.kpi_store import compute_success_rate, load_kpi, update_business_agent_kpi, update_kpi


def test_initialize_file(tmp_path: Path) -> None:
    kpi = load_kpi(tmp_path)
    assert kpi == {
        "total_runs": 0,
        "success_count": 0,
        "failure_count": 0,
        "success_rate": 0.0,
        "failure_breakdown": {
            "external_capacity": 0,
            "usage_limit": 0,
            "model_unsupported": 0,
            "unknown": 0,
        },
        "per_issue_stats": {},
        "business_agent_stats": {},
        "last_updated": "",
    }


def test_success_update(tmp_path: Path) -> None:
    kpi = update_kpi(True, tmp_path, issue_number=32)
    assert kpi["total_runs"] == 1
    assert kpi["success_count"] == 1
    assert kpi["failure_count"] == 0
    assert kpi["success_rate"] == 1.0
    assert kpi["per_issue_stats"]["32"] == {"runs": 1, "success": 1, "failure": 0}
    assert (tmp_path / "system" / "runtime" / "knowledge" / "kpi.json").exists()


def test_failure_update(tmp_path: Path) -> None:
    update_kpi(True, tmp_path, issue_number=32)
    kpi = update_kpi(False, tmp_path, issue_number=32, error_type="usage_limit")
    assert kpi["total_runs"] == 2
    assert kpi["success_count"] == 1
    assert kpi["failure_count"] == 1
    assert kpi["success_rate"] == 0.5
    assert kpi["failure_breakdown"]["usage_limit"] == 1
    assert kpi["per_issue_stats"]["32"] == {"runs": 2, "success": 1, "failure": 1}


def test_success_rate_helper() -> None:
    assert compute_success_rate(0, 0) == 0.0
    assert compute_success_rate(4, 3) == 0.75


def test_business_agent_kpi_is_additive_and_isolated(tmp_path: Path) -> None:
    update_kpi(True, tmp_path, issue_number=32)
    kpi = update_business_agent_kpi("text_syndicate", "market_research", True, tmp_path, metrics={"impressions": 100.0})
    assert kpi["total_runs"] == 1
    assert kpi["per_issue_stats"]["32"] == {"runs": 1, "success": 1, "failure": 0}
    assert kpi["business_agent_stats"]["text_syndicate:market_research"]["runs"] == 1
    assert kpi["business_agent_stats"]["text_syndicate:market_research"]["success"] == 1
    assert kpi["business_agent_stats"]["text_syndicate:market_research"]["metrics"]["impressions"]["latest"] == 100.0


def test_business_agent_kpi_tracks_metric_history(tmp_path: Path) -> None:
    update_business_agent_kpi("text_syndicate", "market_research", True, tmp_path, metrics={"impressions": 100.0})
    kpi = update_business_agent_kpi("text_syndicate", "market_research", True, tmp_path, metrics={"impressions": 150.0})
    metric = kpi["business_agent_stats"]["text_syndicate:market_research"]["metrics"]["impressions"]
    assert metric["latest"] == 150.0
    assert metric["history"] == [100.0, 150.0]
