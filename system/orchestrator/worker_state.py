from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkerState:
    worker_name: str
    current_ep: str
    queue_status: str


class WorkerStateError(ValueError):
    pass


def read_worker_state(path: str | Path = "docs/current/WORKER_STATE.md") -> WorkerState:
    state_path = Path(path)
    if not state_path.exists():
        raise FileNotFoundError(f"Worker state file not found: {state_path}")
    values = _parse_key_values(state_path.read_text(encoding="utf-8"))
    required = ["worker_name", "current_ep", "queue_status"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise WorkerStateError(f"Missing required worker state fields: {', '.join(missing)}")
    return WorkerState(
        worker_name=values["worker_name"],
        current_ep=values["current_ep"],
        queue_status=values["queue_status"],
    )


def write_worker_state(state: WorkerState, path: str | Path = "docs/current/WORKER_STATE.md") -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "\n".join(
            [
                "# WORKER_STATE",
                "",
                f"worker_name: {state.worker_name}",
                f"current_ep: {state.current_ep}",
                f"queue_status: {state.queue_status}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _parse_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values
