from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from system.core.failure_store import load_failures


DEFAULT_FAILURE_RULES = Path("platform/system/runtime/platform/knowledge/failure_rules.json")
DEFAULT_LEARNING_SUMMARY = Path("platform/system/runtime/platform/knowledge/learning_summary.json")


def _rules_path(base_path: Path | str | None = None) -> Path:
    if base_path is None:
        return DEFAULT_FAILURE_RULES
    root = Path(base_path)
    return root / "system" / "runtime" / "knowledge" / "failure_rules.json"


def load_failure_rules(base_path: Path | str | None = None) -> list[dict]:
    path = _rules_path(base_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def analyze_failure_history(base_path: Path | str | None = None) -> list[dict]:
    failures = load_failures(base_path)
    rules: list[dict] = []
    by_issue: dict[int, list[dict]] = {}
    for entry in failures:
        issue_number = entry.get("issue_number")
        if isinstance(issue_number, int):
            by_issue.setdefault(issue_number, []).append(entry)

    for issue_number, entries in by_issue.items():
        if len(entries) < 3:
            continue
        tail = entries[-3:]
        error_type = tail[-1].get("error_type")
        if error_type and all(entry.get("error_type") == error_type for entry in tail):
            rules.append(
                {
                    "issue_number": issue_number,
                    "error_type": error_type,
                    "action": "temporary_skip",
                    "threshold": 3,
                    "cooldown_seconds": 300,
                    "last_failed_at": tail[-1].get("last_failed_at") or tail[-1].get("timestamp") or "",
                }
            )
    return _deduplicate_rules(rules)


def write_failure_rules(base_path: Path | str | None = None, rules: list[dict] | None = None) -> list[dict]:
    path = _rules_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = rules if rules is not None else analyze_failure_history(base_path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_learning_summary(base_path, payload)
    return payload


def _summary_path(base_path: Path | str | None = None) -> Path:
    if base_path is None:
        return DEFAULT_LEARNING_SUMMARY
    root = Path(base_path)
    return root / "system" / "runtime" / "knowledge" / "learning_summary.json"


def _write_learning_summary(base_path: Path | str | None, rules: list[dict]) -> None:
    failures = load_failures(base_path)
    summary = {
        "total_failures": len(failures),
        "total_rules": len(rules),
        "issues_with_rules": sorted(
            {int(rule.get("issue_number", 0)) for rule in rules if isinstance(rule.get("issue_number"), int)}
        ),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    path = _summary_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _deduplicate_rules(rules: list[dict]) -> list[dict]:
    seen: set[tuple[int, str, str, int]] = set()
    deduped: list[dict] = []
    for rule in rules:
        key = (
            int(rule.get("issue_number", 0)),
            str(rule.get("error_type", "")),
            str(rule.get("action", "")),
            int(rule.get("threshold", 0)),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rule)
    return deduped
