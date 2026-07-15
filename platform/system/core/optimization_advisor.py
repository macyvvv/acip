from __future__ import annotations

import json
from pathlib import Path

from system.core.failure_learning import load_failure_rules
from system.core.kpi_store import load_kpi


DEFAULT_OPTIMIZATION_SUGGESTIONS = Path("platform/system/runtime/platform/knowledge/optimization_suggestions.json")


def _suggestions_path(base_path: Path | str | None = None) -> Path:
    if base_path is None:
        return DEFAULT_OPTIMIZATION_SUGGESTIONS
    root = Path(base_path)
    return root / "system" / "runtime" / "knowledge" / "optimization_suggestions.json"


def analyze_optimization_opportunities(base_path: Path | str | None = None) -> list[dict]:
    kpi = load_kpi(base_path)
    failure_rules = load_failure_rules(base_path)
    suggestions: list[dict] = []
    total_failures = int(kpi.get("failure_count", 0))
    external_capacity = int(kpi.get("failure_breakdown", {}).get("external_capacity", 0))
    if total_failures > 0 and external_capacity / max(total_failures, 1) > 0.5:
        suggestions.append(
            {
                "type": "model_selection",
                "message": "Consider switching to lower-load model",
                "confidence": "medium",
            }
        )

    per_issue_stats = kpi.get("per_issue_stats", {})
    if isinstance(per_issue_stats, dict):
        for issue_number, stats in sorted(per_issue_stats.items(), key=lambda item: int(item[0])):
            runs = int(stats.get("runs", 0))
            failure = int(stats.get("failure", 0))
            failure_rate = failure / runs if runs else 0.0
            if runs > 0 and failure_rate > 0.7:
                suggestions.append(
                    {
                        "type": "issue_prioritization",
                        "issue_number": int(issue_number),
                        "message": "Deprioritize this issue",
                        "confidence": "medium",
                    }
                )

    success_rate = float(kpi.get("success_rate", 0.0))
    if success_rate < 0.5:
        suggestions.append(
            {
                "type": "execution_health",
                "message": "Execution instability detected",
                "confidence": "medium",
            }
        )

    if failure_rules:
        suggestions.append(
            {
                "type": "learning_visibility",
                "message": f"{len(failure_rules)} failure-derived rule(s) active",
                "confidence": "low",
            }
        )
    return suggestions


def write_optimization_suggestions(base_path: Path | str | None = None, suggestions: list[dict] | None = None) -> list[dict]:
    path = _suggestions_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = suggestions if suggestions is not None else analyze_optimization_opportunities(base_path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def analyze_business_agent_optimization_opportunities(base_path: Path | str | None = None) -> list[dict]:
    """Additive, parallel to analyze_optimization_opportunities(): reads only
    business_agent_stats, never touches the repo-dev execution KPI fields. This
    is what the pdca role's prompt reads from for its Check/Act sections."""
    kpi = load_kpi(base_path)
    business_agent_stats = kpi.get("business_agent_stats", {})
    suggestions: list[dict] = []
    if not isinstance(business_agent_stats, dict):
        return suggestions
    for stats_key, stats in sorted(business_agent_stats.items()):
        runs = int(stats.get("runs", 0))
        failure = int(stats.get("failure", 0))
        failure_rate = failure / runs if runs else 0.0
        if runs > 0 and failure_rate > 0.7:
            suggestions.append(
                {
                    "type": "business_role_reliability",
                    "business_role_key": stats_key,
                    "message": "This business/role pairing is failing more often than it succeeds",
                    "confidence": "medium",
                }
            )
        metrics = stats.get("metrics", {})
        if isinstance(metrics, dict):
            for metric_name, metric_entry in metrics.items():
                history = metric_entry.get("history", []) if isinstance(metric_entry, dict) else []
                if len(history) >= 2 and history[-1] < history[-2]:
                    suggestions.append(
                        {
                            "type": "business_metric_decline",
                            "business_role_key": stats_key,
                            "metric": metric_name,
                            "message": f"{metric_name} declined from {history[-2]} to {history[-1]}",
                            "confidence": "low",
                        }
                    )
    return suggestions
