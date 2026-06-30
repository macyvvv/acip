from __future__ import annotations

from pathlib import Path

from system.core.kpi_store import load_kpi, update_kpi


def test_failure_type_increments_correctly(tmp_path: Path) -> None:
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    kpi = load_kpi(tmp_path)

    assert kpi["failure_breakdown"]["external_capacity"] == 2
    assert kpi["failure_breakdown"]["usage_limit"] == 0


def test_per_issue_stats_tracked_correctly(tmp_path: Path) -> None:
    update_kpi(True, tmp_path, issue_number=32)
    update_kpi(False, tmp_path, issue_number=32, error_type="usage_limit")
    update_kpi(False, tmp_path, issue_number=33, error_type="unknown")
    kpi = load_kpi(tmp_path)

    assert kpi["per_issue_stats"]["32"] == {"runs": 2, "success": 1, "failure": 1}
    assert kpi["per_issue_stats"]["33"] == {"runs": 1, "success": 0, "failure": 1}


def test_success_rate_remains_correct(tmp_path: Path) -> None:
    update_kpi(True, tmp_path, issue_number=32)
    update_kpi(False, tmp_path, issue_number=32, error_type="usage_limit")
    update_kpi(True, tmp_path, issue_number=33)
    kpi = load_kpi(tmp_path)

    assert kpi["total_runs"] == 3
    assert kpi["success_count"] == 2
    assert kpi["failure_count"] == 1
    assert kpi["success_rate"] == 0.6667
