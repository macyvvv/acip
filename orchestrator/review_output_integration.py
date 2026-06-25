from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from orchestrator.capability_router import CapabilityRoute
from orchestrator.task_decomposer import TaskDecompositionResult, DecomposedSubtask


@dataclass(frozen=True)
class ReviewSummary:
    status: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewOutputIntegrationResult:
    decomposition_result: TaskDecompositionResult
    routing_result: CapabilityRoute
    review_summary: ReviewSummary
    worker_output: dict[str, object] = field(default_factory=dict)


def build_review_output_integration(
    decomposition_result: TaskDecompositionResult,
    routing_result: CapabilityRoute,
    review_notes: Iterable[str] | None = None,
) -> ReviewOutputIntegrationResult:
    notes = tuple(review_notes or ())
    status = "success"
    if not decomposition_result.subtasks:
        status = "failure"
    elif any(subtask.worker_candidate != routing_result.worker_name for subtask in decomposition_result.subtasks):
        status = "partial_success"
    worker_output = {
        "task_id": decomposition_result.source,
        "objective": decomposition_result.objective,
        "subtasks": [
            {
                "id": subtask.id,
                "title": subtask.title,
                "required_capability": subtask.required_capability,
                "worker_candidate": subtask.worker_candidate,
                "worker_candidates": list(subtask.worker_candidates),
            }
            for subtask in decomposition_result.subtasks
        ],
        "routing": {
            "worker_name": routing_result.worker_name,
            "candidates": list(routing_result.candidates),
            "reason": routing_result.reason,
        },
        "review_summary": {
            "status": status,
            "notes": list(notes),
        },
    }
    return ReviewOutputIntegrationResult(
        decomposition_result=decomposition_result,
        routing_result=routing_result,
        review_summary=ReviewSummary(status=status, notes=notes),
        worker_output=worker_output,
    )
