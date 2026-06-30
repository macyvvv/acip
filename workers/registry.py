from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal envs
    yaml = None


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
    raw_text = registry_path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(raw_text) or {}
    else:
        data = _parse_registry_yaml(raw_text)
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


def _parse_registry_yaml(raw_text: str) -> dict[str, Any]:
    """Parse the narrow registry YAML shape without external dependencies."""
    workers: dict[str, dict[str, list[str] | str]] = {}
    current_worker: str | None = None
    current_key: str | None = None

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "workers:":
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 2 and stripped.endswith(":"):
            current_worker = stripped[:-1]
            workers[current_worker] = {}
            current_key = None
            continue
        if indent == 4 and stripped.endswith(":"):
            if current_worker is None:
                raise WorkerRegistryError("Invalid registry structure")
            current_key = stripped[:-1]
            workers[current_worker][current_key] = []
            continue
        if indent == 6 and stripped.startswith("- "):
            if current_worker is None or current_key is None:
                raise WorkerRegistryError("Invalid registry list entry")
            workers[current_worker][current_key].append(stripped[2:])  # type: ignore[union-attr]
            continue
        if indent == 4 and ":" in stripped:
            if current_worker is None:
                raise WorkerRegistryError("Invalid registry scalar entry")
            key, value = stripped.split(":", 1)
            workers[current_worker][key.strip()] = value.strip()
            current_key = None
            continue
        raise WorkerRegistryError(f"Unsupported registry line: {line!r}")

    return {"workers": workers}


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
