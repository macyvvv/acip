from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _queue_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "business_agent_tasks" / "queue.json"


def load_queue(base_path: str | Path = ".") -> list[dict[str, Any]]:
    path = _queue_path(base_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _write_queue(queue: list[dict[str, Any]], base_path: str | Path = ".") -> None:
    path = _queue_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_task(
    business_id: str,
    role_id: str,
    task_id: str,
    title: str,
    base_path: str | Path = ".",
    *,
    source: str = "manual",
) -> list[dict[str, Any]]:
    queue = load_queue(base_path)
    existing = next(
        (item for item in queue if item.get("business_id") == business_id and item.get("role_id") == role_id and item.get("task_id") == task_id),
        None,
    )
    if existing is not None:
        return queue
    queue.append(
        {
            "business_id": business_id,
            "role_id": role_id,
            "task_id": task_id,
            "title": title,
            "status": "candidate",
            "source": source,
        }
    )
    _write_queue(queue, base_path)
    return queue


def mark_task_status(
    business_id: str,
    role_id: str,
    task_id: str,
    status: str,
    base_path: str | Path = ".",
) -> list[dict[str, Any]]:
    queue = load_queue(base_path)
    for item in queue:
        if item.get("business_id") == business_id and item.get("role_id") == role_id and item.get("task_id") == task_id:
            item["status"] = status
    _write_queue(queue, base_path)
    return queue
