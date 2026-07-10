from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from system.core.file_lock import locked


DEFAULT_KPI_STORE = Path("system/runtime/knowledge/kpi.json")


def _kpi_path(base_path: Path | str | None = None) -> Path:
    if base_path is None:
        return DEFAULT_KPI_STORE
    root = Path(base_path)
    return root / "system" / "runtime" / "knowledge" / "kpi.json"


def _default_kpi() -> dict:
    return {
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


def load_kpi(base_path: Path | str | None = None) -> dict:
    path = _kpi_path(base_path)
    if not path.exists():
        return _default_kpi()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return _default_kpi()
    payload = _default_kpi()
    for key in ("total_runs", "success_count", "failure_count", "success_rate", "last_updated"):
        payload[key] = data.get(key, payload[key])
    failure_breakdown = data.get("failure_breakdown", {})
    if isinstance(failure_breakdown, dict):
        payload["failure_breakdown"].update(
            {key: int(failure_breakdown.get(key, payload["failure_breakdown"][key])) for key in payload["failure_breakdown"]}
        )
    per_issue_stats = data.get("per_issue_stats", {})
    if isinstance(per_issue_stats, dict):
        for issue_number, stats in per_issue_stats.items():
            if not isinstance(stats, dict):
                continue
            payload["per_issue_stats"][str(issue_number)] = {
                "runs": int(stats.get("runs", 0)),
                "success": int(stats.get("success", 0)),
                "failure": int(stats.get("failure", 0)),
            }
    business_agent_stats = data.get("business_agent_stats", {})
    if isinstance(business_agent_stats, dict):
        for key, stats in business_agent_stats.items():
            if not isinstance(stats, dict):
                continue
            metrics = stats.get("metrics", {})
            payload["business_agent_stats"][str(key)] = {
                "runs": int(stats.get("runs", 0)),
                "success": int(stats.get("success", 0)),
                "failure": int(stats.get("failure", 0)),
                "metrics": metrics if isinstance(metrics, dict) else {},
            }
    return payload


def compute_success_rate(total_runs: int, success_count: int) -> float:
    if total_runs <= 0:
        return 0.0
    return round(success_count / total_runs, 4)


def update_kpi(
    success: bool,
    base_path: Path | str | None = None,
    *,
    issue_number: int | None = None,
    error_type: str = "unknown",
) -> dict:
    path = _kpi_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked(path):
        kpi = load_kpi(base_path)
        kpi["total_runs"] = int(kpi.get("total_runs", 0)) + 1
        if success:
            kpi["success_count"] = int(kpi.get("success_count", 0)) + 1
        else:
            kpi["failure_count"] = int(kpi.get("failure_count", 0)) + 1
            breakdown = kpi.setdefault("failure_breakdown", _default_kpi()["failure_breakdown"])
            if error_type not in breakdown:
                error_type = "unknown"
            breakdown[error_type] = int(breakdown.get(error_type, 0)) + 1
        if issue_number is not None:
            issue_key = str(issue_number)
            stats = kpi.setdefault("per_issue_stats", {})
            issue_stats = stats.setdefault(issue_key, {"runs": 0, "success": 0, "failure": 0})
            issue_stats["runs"] = int(issue_stats.get("runs", 0)) + 1
            if success:
                issue_stats["success"] = int(issue_stats.get("success", 0)) + 1
            else:
                issue_stats["failure"] = int(issue_stats.get("failure", 0)) + 1
        kpi["success_rate"] = compute_success_rate(int(kpi["total_runs"]), int(kpi["success_count"]))
        kpi["last_updated"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(kpi, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return kpi


def update_business_agent_kpi(
    business_id: str,
    role_id: str,
    success: bool,
    base_path: Path | str | None = None,
    *,
    metrics: dict[str, float] | None = None,
) -> dict:
    """Additive, parallel to update_kpi(): never touches total_runs/success_count/
    failure_count/per_issue_stats, so the existing repo-dev KPI stream is untouched."""
    path = _kpi_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked(path):
        kpi = load_kpi(base_path)
        stats_key = f"{business_id}:{role_id}"
        business_agent_stats = kpi.setdefault("business_agent_stats", {})
        stats = business_agent_stats.setdefault(stats_key, {"runs": 0, "success": 0, "failure": 0, "metrics": {}})
        stats["runs"] = int(stats.get("runs", 0)) + 1
        if success:
            stats["success"] = int(stats.get("success", 0)) + 1
        else:
            stats["failure"] = int(stats.get("failure", 0)) + 1
        if metrics:
            metric_bag = stats.setdefault("metrics", {})
            for name, value in metrics.items():
                entry = metric_bag.setdefault(name, {"latest": value, "history": [], "unit": ""})
                entry["latest"] = value
                entry.setdefault("history", []).append(value)
        kpi["last_updated"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(kpi, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return kpi
