from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from system.orchestrator.capability_router import CapabilityRoute
from system.orchestrator.output_semantics import determine_worker_output_status, worker_output_semantic
from system.orchestrator.task_decomposer import TaskDecompositionResult, DecomposedSubtask


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
    *,
    has_errors: bool = False,
    is_blocked: bool = False,
    is_skipped: bool = False,
) -> ReviewOutputIntegrationResult:
    notes = tuple(review_notes or ())
    status = determine_worker_output_status(
        has_subtasks=bool(decomposition_result.subtasks),
        all_subtasks_routed=all(
            subtask.worker_candidate == routing_result.worker_name for subtask in decomposition_result.subtasks
        ),
        has_errors=has_errors,
        is_blocked=is_blocked,
        is_skipped=is_skipped,
    )
    semantic = worker_output_semantic(status)
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
            "meaning": semantic.meaning,
            "next_action": semantic.next_action,
        },
    }
    return ReviewOutputIntegrationResult(
        decomposition_result=decomposition_result,
        routing_result=routing_result,
        review_summary=ReviewSummary(status=status, notes=notes),
        worker_output=worker_output,
    )
