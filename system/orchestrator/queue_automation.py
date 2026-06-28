from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.queue_state import QueueState, read_queue_state, write_queue_state


QUEUE_STATES = ("READY", "RUNNING", "REVIEW", "DONE")


@dataclass(frozen=True)
class QueueAutomationResult:
    previous: QueueState
    current: QueueState
    transition: str


class QueueAutomationError(ValueError):
    pass


class QueueAutomation:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def advance(self) -> QueueAutomationResult:
        current = read_queue_state(self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        next_state = self._next_state(current)
        write_queue_state(next_state, self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        self._write_runtime_state(current, next_state)
        return QueueAutomationResult(
            previous=current,
            current=next_state,
            transition=f"{current.status}->{next_state.status}",
        )

    def _next_state(self, state: QueueState) -> QueueState:
        if state.status not in QUEUE_STATES:
            raise QueueAutomationError(f"Unsupported queue state: {state.status}")
        index = QUEUE_STATES.index(state.status)
        if index == len(QUEUE_STATES) - 1:
            return state
        return QueueState(status=QUEUE_STATES[index + 1], active_ep=state.active_ep, next_ep=state.next_ep)

    def _write_runtime_state(self, previous: QueueState, current: QueueState) -> None:
        runtime_dir = self.base_path / "runtime" / "queue"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "previous": {"status": previous.status, "active_ep": previous.active_ep, "next_ep": previous.next_ep},
            "current": {"status": current.status, "active_ep": current.active_ep, "next_ep": current.next_ep},
            "transition": f"{previous.status}->{current.status}",
        }
        (runtime_dir / "queue_state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

