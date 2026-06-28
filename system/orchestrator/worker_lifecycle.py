from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.worker_state import WorkerState, read_worker_state


WORKER_LIFECYCLE_STATES = ("Idle", "Reserved", "Running", "Review", "Completed", "Failed")


@dataclass(frozen=True)
class WorkerLifecycleRecord:
    worker_name: str
    previous_state: str
    current_state: str
    current_ep: str
    queue_status: str


class WorkerLifecycleError(ValueError):
    pass


class WorkerLifecycleManager:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def transition(self, state: WorkerState, next_state: str) -> WorkerLifecycleRecord:
        if next_state not in WORKER_LIFECYCLE_STATES:
            raise WorkerLifecycleError(f"Unsupported worker lifecycle state: {next_state}")
        previous_state = self._normalize_queue_status(state.queue_status)
        return WorkerLifecycleRecord(
            worker_name=state.worker_name,
            previous_state=previous_state,
            current_state=next_state,
            current_ep=state.current_ep,
            queue_status=state.queue_status,
        )

    def validate_transition(self, record: WorkerLifecycleRecord) -> None:
        if record.current_state == "Running" and record.previous_state not in {"Reserved", "Idle"}:
            raise WorkerLifecycleError("Running requires Reserved or Idle as the previous state")
        if record.current_state == "Completed" and record.previous_state != "Running":
            raise WorkerLifecycleError("Completed requires Running as the previous state")
        if record.current_state == "Failed" and record.previous_state not in {"Running", "Review"}:
            raise WorkerLifecycleError("Failed requires Running or Review as the previous state")

    def write_runtime_state(self, record: WorkerLifecycleRecord) -> None:
        runtime_dir = self.base_path / "runtime" / "workers"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "worker_name": record.worker_name,
            "previous_state": record.previous_state,
            "current_state": record.current_state,
            "current_ep": record.current_ep,
            "queue_status": record.queue_status,
        }
        (runtime_dir / "worker_lifecycle.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "WORKER_LIFECYCLE.md").write_text(
            "\n".join(
                [
                    "# WORKER_LIFECYCLE",
                    "",
                    f"worker_name: {record.worker_name}",
                    f"previous_state: {record.previous_state}",
                    f"current_state: {record.current_state}",
                    f"current_ep: {record.current_ep}",
                    f"queue_status: {record.queue_status}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def read_current_worker_state(self) -> WorkerState:
        return read_worker_state(self.base_path / "docs" / "current" / "WORKER_STATE.md")

    def _normalize_queue_status(self, queue_status: str) -> str:
        if queue_status == "READY":
            return "Idle"
        if queue_status == "RUNNING":
            return "Running"
        if queue_status == "REVIEW":
            return "Review"
        if queue_status == "DONE":
            return "Completed"
        return "Idle"
