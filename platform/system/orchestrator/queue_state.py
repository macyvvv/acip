from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QueueState:
    status: str
    active_ep: str
    next_ep: str


class QueueStateError(ValueError):
    pass


def read_queue_state(path: str | Path = "platform/docs/current/QUEUE_STATE.md") -> QueueState:
    state_path = Path(path)
    if not state_path.exists():
        raise FileNotFoundError(f"Queue state file not found: {state_path}")
    values = _parse_key_values(state_path.read_text(encoding="utf-8"))
    required = ["status", "active_ep", "next_ep"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise QueueStateError(f"Missing required queue state fields: {', '.join(missing)}")
    return QueueState(status=values["status"], active_ep=values["active_ep"], next_ep=values["next_ep"])


def write_queue_state(state: QueueState, path: str | Path = "platform/docs/current/QUEUE_STATE.md") -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "\n".join(
            [
                "# QUEUE_STATE",
                "",
                f"status: {state.status}",
                f"active_ep: {state.active_ep}",
                f"next_ep: {state.next_ep}",
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
