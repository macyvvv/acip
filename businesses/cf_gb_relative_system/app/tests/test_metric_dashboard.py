from __future__ import annotations

import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
BUSINESS_ROOT = APP_ROOT.parent
REPO_ROOT = BUSINESS_ROOT.parents[1]
sys.path.insert(0, str(APP_ROOT))
sys.path.insert(0, str(REPO_ROOT / "platform"))

from metric_dashboard import build_metric_dashboard


def _dataset(*, observations: list[dict[str, object]], numerator: float, denominator: float, late_revision_count: int) -> dict[str, object]:
    return {
        "dataset_id": "metric_demo",
        "study_id": "study_revenue_lift_001",
        "metric_name": "ctr",
        "metric_value": 0.0 if denominator == 0 else numerator / denominator,
        "numerator": numerator,
        "denominator": denominator,
        "late_revision_count": late_revision_count,
        "observations": observations,
    }


def test_metric_dashboard_flags_missing_metric_data() -> None:
    dashboard = build_metric_dashboard(
        _dataset(observations=[], numerator=0.0, denominator=0.0, late_revision_count=0),
        now="2026-07-16T12:00:00Z",
    )
    assert dashboard["confidence_interval"] is None
    assert any(alert["code"] == "missing_observations" for alert in dashboard["alerts"])


def test_metric_dashboard_flags_stale_metric() -> None:
    dashboard = build_metric_dashboard(
        _dataset(
            observations=[{"observed_at": "2026-07-14T00:00:00Z"}],
            numerator=9.0,
            denominator=50.0,
            late_revision_count=1,
        ),
        now="2026-07-16T12:00:00Z",
        freshness_sla_hours=24,
    )
    assert any(alert["code"] == "stale_metric" for alert in dashboard["alerts"])


def test_metric_dashboard_shows_estimate_ci_and_revision_count() -> None:
    dashboard = build_metric_dashboard(
        _dataset(
            observations=[
                {"observed_at": "2026-07-16T00:00:00Z"},
                {"observed_at": "2026-07-16T03:00:00Z"},
            ],
            numerator=9.0,
            denominator=50.0,
            late_revision_count=2,
        ),
        now="2026-07-16T12:00:00Z",
    )
    assert dashboard["metric_value"] == 0.18
    assert dashboard["confidence_interval"]["level"] == 0.95
    assert dashboard["confidence_interval"]["lower"] < dashboard["metric_value"] < dashboard["confidence_interval"]["upper"]
    assert dashboard["late_revision_count"] == 2
    assert dashboard["summary_cards"][2]["value"] == 2
