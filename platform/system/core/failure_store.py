from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_FAILURE_STORE = Path("platform/system/runtime/platform/knowledge/failures.json")


def _failure_store_path(base_path: Path | str | None = None) -> Path:
    if base_path is None:
        return DEFAULT_FAILURE_STORE
    root = Path(base_path)
    return root / "system" / "runtime" / "knowledge" / "failures.json"


def load_failures(base_path: Path | str | None = None) -> list[dict]:
    path = _failure_store_path(base_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def update_retry_count(issue_number: int, failures: list[dict] | None = None) -> int:
    if failures is None:
        failures = load_failures()
    consecutive = 0
    for entry in reversed(failures):
        if entry.get("issue_number") == issue_number:
            consecutive += 1
        else:
            break
    return consecutive + 1


def append_failure(entry: dict, base_path: Path | str | None = None) -> dict:
    path = _failure_store_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    failures = load_failures(base_path)
    retry_count = update_retry_count(int(entry.get("issue_number", 0)), failures)
    payload = {
        "request_id": entry.get("request_id", ""),
        "issue_number": int(entry.get("issue_number", 0)),
        "error_type": entry.get("error_type", "unknown"),
        "model": entry.get("model", ""),
        "timestamp": entry.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "retry_count": retry_count,
        "last_failed_at": entry.get("last_failed_at") or datetime.now(timezone.utc).isoformat(),
    }
    failures.append(payload)
    path.write_text(json.dumps(failures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
