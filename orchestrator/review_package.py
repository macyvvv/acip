from __future__ import annotations

from dataclasses import dataclass

from orchestrator.state import State
from orchestrator.task import Task


@dataclass(frozen=True)
class ReviewPackage:
    current_objective: str
    current_epic: str
    current_task: str
    task: Task
    artifacts: list[str]
    validation: list[str]
    review_checklist: list[str]
    recommended_next_action: str


def build_review_package(state: State, task: Task, artifacts: list[str], validation: list[str]) -> ReviewPackage:
    return ReviewPackage(
        current_objective=state.current_objective,
        current_epic=state.current_epic,
        current_task=state.current_task,
        task=task,
        artifacts=list(artifacts),
        validation=list(validation),
        review_checklist=[
            "Objective matches repository state",
            "Artifacts are limited to requested scope",
            "Validation commands were executed",
            "No unrelated files were changed",
        ],
        recommended_next_action=task.instruction,
    )
