from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import re


@dataclass(frozen=True)
class RuntimeTask:
    task_id: str
    title: str
    objective: str
    source: str
    priority: str
    status: str
    approval_required: bool
    runtime_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "task"


def normalize_task(raw: dict[str, Any], source: str) -> RuntimeTask:
    title = str(raw.get("title") or "Untitled Runtime Task").strip()
    objective = str(raw.get("objective") or title).strip()
    task_id = str(raw.get("task_id") or f"ART-{_slug(title)[:32]}").strip()
    priority = str(raw.get("priority") or "normal").strip()
    return RuntimeTask(
        task_id=task_id,
        title=title,
        objective=objective,
        source=source,
        priority=priority,
        status="normalized",
        approval_required=True,
        runtime_boundary="dry-run only; no external actions",
    )


def load_task(path: Path) -> RuntimeTask:
    if not path.exists():
        raise FileNotFoundError(f"Task input not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_task(raw, path.as_posix())


def write_task(path: Path, task: RuntimeTask) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(task.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
