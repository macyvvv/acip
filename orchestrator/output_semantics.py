from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


WorkerOutputStatus = Literal["success", "partial_success", "failure", "blocked", "skipped"]


@dataclass(frozen=True)
class WorkerOutputSemantic:
    status: WorkerOutputStatus
    meaning: str
    next_action: str


WORKER_OUTPUT_SEMANTICS: dict[str, WorkerOutputSemantic] = {
    "success": WorkerOutputSemantic(
        status="success",
        meaning="All required work completed and validation passed.",
        next_action="Proceed to review or next repository step.",
    ),
    "partial_success": WorkerOutputSemantic(
        status="partial_success",
        meaning="Some work completed, but one or more required outputs remain incomplete.",
        next_action="Review incomplete outputs and resolve the remaining scope.",
    ),
    "failure": WorkerOutputSemantic(
        status="failure",
        meaning="Required work did not complete or validation failed.",
        next_action="Inspect errors, fix the failure, then rerun validation.",
    ),
    "blocked": WorkerOutputSemantic(
        status="blocked",
        meaning="Execution cannot continue because a dependency, approval, or repository constraint is missing.",
        next_action="Resolve the blocking condition before rerunning execution.",
    ),
    "skipped": WorkerOutputSemantic(
        status="skipped",
        meaning="No execution was performed because the work was not applicable or was intentionally bypassed.",
        next_action="Confirm whether the skipped work should remain skipped or be scheduled later.",
    ),
}


def normalize_worker_output_status(status: str) -> WorkerOutputStatus:
    if status not in WORKER_OUTPUT_SEMANTICS:
        raise ValueError(f"Unsupported worker output status: {status}")
    return status  # type: ignore[return-value]


def worker_output_semantic(status: str) -> WorkerOutputSemantic:
    normalized = normalize_worker_output_status(status)
    return WORKER_OUTPUT_SEMANTICS[normalized]


def determine_worker_output_status(
    *,
    has_subtasks: bool,
    all_subtasks_routed: bool,
    has_errors: bool = False,
    is_blocked: bool = False,
    is_skipped: bool = False,
) -> WorkerOutputStatus:
    if is_skipped:
        return "skipped"
    if is_blocked:
        return "blocked"
    if has_errors:
        return "failure"
    if not has_subtasks or not all_subtasks_routed:
        return "partial_success"
    return "success"
