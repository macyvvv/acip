from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from system.core.statistics_engine import wilson_confidence_interval


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_metric_dashboard(
    metric_dataset: dict[str, Any],
    *,
    now: str,
    freshness_sla_hours: int = 24,
) -> dict[str, Any]:
    observations = metric_dataset.get("observations", [])
    revision_count = int(metric_dataset.get("late_revision_count", 0))
    alerts: list[dict[str, str]] = []
    if not observations:
        alerts.append({"severity": "critical", "code": "missing_observations", "message": "No validated observations"})
        last_observed_at = None
    else:
        last_observed_at = max(item["observed_at"] for item in observations)
    if last_observed_at is not None:
        age = _parse_timestamp(now) - _parse_timestamp(last_observed_at)
        if age > timedelta(hours=freshness_sla_hours):
            alerts.append(
                {
                    "severity": "warning",
                    "code": "stale_metric",
                    "message": f"Latest observation is older than {freshness_sla_hours}h",
                }
            )
    denominator = int(round(float(metric_dataset.get("denominator", 0.0))))
    numerator = int(round(float(metric_dataset.get("numerator", 0.0))))
    if denominator > 0:
        interval = wilson_confidence_interval(numerator, denominator, confidence_level=0.95)
        ci = {"level": interval.level, "lower": interval.lower, "upper": interval.upper}
    else:
        ci = None
    return {
        "dataset_id": metric_dataset["dataset_id"],
        "metric_name": metric_dataset["metric_name"],
        "metric_value": metric_dataset["metric_value"],
        "confidence_interval": ci,
        "late_revision_count": revision_count,
        "last_observed_at": last_observed_at,
        "alerts": alerts,
        "summary_cards": [
            {"id": "estimate", "label": "Estimate", "value": metric_dataset["metric_value"]},
            {"id": "sample_size", "label": "Sample Size", "value": denominator},
            {"id": "revisions", "label": "Late Revisions", "value": revision_count},
        ],
    }
