from __future__ import annotations

from dataclasses import dataclass, field

from system.orchestrator.queue_state import QueueState
from system.orchestrator.result import Result
from system.orchestrator.task import Task
from system.orchestrator.worker_state import WorkerState


@dataclass(frozen=True)
class WorkerExecutionRecord:
    task_id: str
    worker_name: str
    queue_status: str
    artifacts: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    checkpoint_candidate: str | None = None
    current_state_candidate: str | None = None
    review_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    next_task_id: str | None = None


def build_worker_execution_record(
    task: Task,
    result: Result,
    queue_state: QueueState,
    worker_state: WorkerState,
) -> WorkerExecutionRecord:
    return WorkerExecutionRecord(
        task_id=task.id,
        worker_name=worker_state.worker_name,
        queue_status=queue_state.status,
        artifacts=list(result.artifacts),
        files_changed=list(result.files_changed),
        checkpoint_candidate=result.checkpoint_candidate,
        current_state_candidate=result.current_state_candidate,
        review_notes=list(result.review_notes),
        errors=list(result.errors),
        next_task_id=result.next_task.id if result.next_task else None,
    )
