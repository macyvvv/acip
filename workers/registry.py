from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class WorkerRegistryEntry:
    name: str
    capability: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    validation_responsibility: tuple[str, ...]
    output_contract: str


@dataclass(frozen=True)
class WorkerRegistry:
    workers: dict[str, WorkerRegistryEntry] = field(default_factory=dict)

    def get(self, worker_name: str) -> WorkerRegistryEntry:
        if worker_name not in self.workers:
            raise WorkerRegistryError(f"Unknown worker: {worker_name}")
        return self.workers[worker_name]

    def has(self, worker_name: str) -> bool:
        return worker_name in self.workers


class WorkerRegistryError(ValueError):
    pass


def load_worker_registry(path: str | Path = "workers/registry.yaml") -> WorkerRegistry:
    registry_path = Path(path)
    if not registry_path.exists():
        raise FileNotFoundError(f"Worker registry file not found: {registry_path}")
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    workers = data.get("workers", {})
    entries: dict[str, WorkerRegistryEntry] = {}
    for name, entry in workers.items():
        entries[name] = WorkerRegistryEntry(
            name=name,
            capability=tuple(entry.get("capability", [])),
            allowed_actions=tuple(entry.get("allowed_actions", [])),
            prohibited_actions=tuple(entry.get("prohibited_actions", [])),
            validation_responsibility=tuple(entry.get("validation_responsibility", [])),
            output_contract=str(entry.get("output_contract", "")),
        )
    _validate_registry(entries)
    return WorkerRegistry(workers=entries)


def _validate_registry(entries: dict[str, WorkerRegistryEntry]) -> None:
    required = {"Codex", "ChatGPT", "Human", "GitHub Actions"}
    missing = sorted(required - set(entries))
    if missing:
        raise WorkerRegistryError(f"Missing required workers: {', '.join(missing)}")
    for name, entry in entries.items():
        if not entry.capability:
            raise WorkerRegistryError(f"Missing capability for worker: {name}")
        if not entry.allowed_actions:
            raise WorkerRegistryError(f"Missing allowed_actions for worker: {name}")
        if not entry.prohibited_actions:
            raise WorkerRegistryError(f"Missing prohibited_actions for worker: {name}")
        if not entry.validation_responsibility:
            raise WorkerRegistryError(f"Missing validation_responsibility for worker: {name}")
        if not entry.output_contract:
            raise WorkerRegistryError(f"Missing output_contract for worker: {name}")
