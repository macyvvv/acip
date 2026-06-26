from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class QueueWorkItem:
    queue_path: str
    pack_id: str
    objective: str
    priority: int
    dependencies: tuple[str, ...]
    approval_required: bool


@dataclass(frozen=True)
class NextWorkResolution:
    selected: QueueWorkItem
    candidates: tuple[QueueWorkItem, ...]


class NextWorkResolverError(ValueError):
    pass


class NextWorkResolver:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def resolve(self) -> NextWorkResolution:
        queue_dir = self.base_path / "queue" / "READY"
        if not queue_dir.exists():
            raise FileNotFoundError(f"Queue directory not found: {queue_dir}")
        items = tuple(sorted((self._parse(path) for path in queue_dir.glob("EP-*.md")), key=self._sort_key))
        if not items:
            raise NextWorkResolverError("No queue items available")
        selected = items[0]
        self._write_runtime(selected, items)
        return NextWorkResolution(selected=selected, candidates=items)

    def _parse(self, path: Path) -> QueueWorkItem:
        values = self._parse_key_values(path.read_text(encoding="utf-8"))
        required = ("pack_id", "objective", "status")
        missing = [key for key in required if not values.get(key)]
        if missing:
            raise NextWorkResolverError(f"Missing required queue fields in {path.name}: {', '.join(missing)}")
        priority = int(values.get("priority", "0"))
        dependencies = tuple(
            item.strip()
            for item in values.get("dependencies", "").split(",")
            if item.strip()
        )
        approval_required = values.get("approval_required", "false").lower() == "true"
        return QueueWorkItem(
            queue_path=str(path.relative_to(self.base_path)),
            pack_id=values["pack_id"],
            objective=values["objective"],
            priority=priority,
            dependencies=dependencies,
            approval_required=approval_required,
        )

    def _sort_key(self, item: QueueWorkItem) -> tuple[int, int, int, str]:
        dependency_score = len(item.dependencies)
        approval_score = 1 if item.approval_required else 0
        return (-item.priority, dependency_score, approval_score, item.queue_path)

    def _parse_key_values(self, text: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip()] = value.strip()
        return values

    def _write_runtime(self, selected: QueueWorkItem, candidates: tuple[QueueWorkItem, ...]) -> None:
        runtime_dir = self.base_path / "runtime" / "queue"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "selected": {
                "queue_path": selected.queue_path,
                "pack_id": selected.pack_id,
                "objective": selected.objective,
                "priority": selected.priority,
                "dependencies": list(selected.dependencies),
                "approval_required": selected.approval_required,
            },
            "candidates": [
                {
                    "queue_path": item.queue_path,
                    "pack_id": item.pack_id,
                    "objective": item.objective,
                    "priority": item.priority,
                    "dependencies": list(item.dependencies),
                    "approval_required": item.approval_required,
                }
                for item in candidates
            ],
        }
        (runtime_dir / "next_work.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

