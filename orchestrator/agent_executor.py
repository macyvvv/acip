from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from orchestrator.context_loader import load_context
from orchestrator.dispatcher import Dispatcher
from orchestrator.queue import state_to_task
from orchestrator.review_package import ReviewPackage, build_review_package
from orchestrator.state import State, read_state
from orchestrator.task import Task


@dataclass(frozen=True)
class AgentExecutionSummary:
    state: State
    task: Task
    review_package: ReviewPackage
    execution_notes: list[str]


def run_agent_executor(dispatcher: Dispatcher, base_path: str = ".") -> AgentExecutionSummary:
    root = Path(base_path)
    context = load_context(root)
    state = read_state(root / "docs/current/CURRENT_STATE.md")
    task = state_to_task(state)
    result = dispatcher.dispatch(task, context)
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
    execution_notes = [
        f"Current Objective: {state.current_objective}",
        f"Current EP: {state.current_epic}",
        f"Current Task: {state.current_task}",
    ]
    return AgentExecutionSummary(
        state=state,
        task=task,
        review_package=review_package,
        execution_notes=execution_notes,
    )
