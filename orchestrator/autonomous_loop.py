from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orchestrator.context_loader import Context, load_context
from orchestrator.dispatcher import Dispatcher
from orchestrator.execution_record import WorkerExecutionRecord, build_worker_execution_record
from orchestrator.output_contract import CodexOutputContract, WorktreeState, build_output_contract
from orchestrator.planner import PlannerDecision, plan_and_persist_queue_state
from orchestrator.queue import state_to_task
from orchestrator.queue_state import QueueState, read_queue_state, write_queue_state
from orchestrator.queue_transition import QueueTransitionResult, advance_queue_state
from orchestrator.review_package import ReviewPackage, build_review_package
from orchestrator.state import State, read_state
from orchestrator.worker_state import WorkerState, read_worker_state


@dataclass(frozen=True)
class AutonomousExecutionSummary:
    state: State
    queue_state: QueueState
    worker_state: WorkerState
    planner: PlannerDecision
    task_id: str
    transition: QueueTransitionResult
    execution_record: WorkerExecutionRecord
    output_contract: CodexOutputContract
    review_package: ReviewPackage
    context: Context


def run_autonomous_execution_loop(dispatcher: Dispatcher, base_path: str | Path = ".") -> AutonomousExecutionSummary:
    root = Path(base_path)
    context = load_context(root)
    planner = plan_and_persist_queue_state(root)
    state = read_state(root / "docs/current/CURRENT_STATE.md")
    queue_state = read_queue_state(root / "docs/current/QUEUE_STATE.md")
    worker_state = read_worker_state(root / "docs/current/WORKER_STATE.md")
    task = state_to_task(state)
    result = dispatcher.dispatch(task, context)

    next_queue_state, transition = advance_queue_state(queue_state)
    write_queue_state(next_queue_state, root / "docs/current/QUEUE_STATE.md")

    execution_record = build_worker_execution_record(task, result, queue_state, worker_state)
    output_contract = build_output_contract(
        task_id=task.id,
        validation_results=[],
        commit_sha=None,
        worktree_state=WorktreeState(clean=not bool(result.files_changed), changed_files=list(result.files_changed)),
        next_action=task.instruction,
        rerun_validation_conditions=["validation failed", "worktree has unexpected changes"],
    )
    review_package = build_review_package(
        state=state,
        task=task,
        artifacts=result.artifacts,
        validation=[
            "python3 -m pytest -q",
            "git status",
            "git diff --stat",
            "git diff",
        ],
    )
    return AutonomousExecutionSummary(
        state=state,
        queue_state=next_queue_state,
        worker_state=worker_state,
        planner=planner,
        task_id=task.id,
        transition=transition,
        execution_record=execution_record,
        output_contract=output_contract,
        review_package=review_package,
        context=context,
    )
