from __future__ import annotations

from orchestrator.result import Result
from orchestrator.task import Task
from orchestrator.worker import Worker


class CodexWorker(Worker):
    def execute(self, task: Task, context) -> Result:
        prompt = _build_prompt(task, context)
        return Result(
            artifacts=[task.artifact],
            files_changed=[],
            review_notes=[prompt],
            errors=[],
        )


def _build_prompt(task: Task, context) -> str:
    target_paths = "\n".join(f"- {path}" for path in task.target_paths) or "- None"
    return (
        f"Task ID: {task.id}\n"
        f"Artifact: {task.artifact}\n"
        f"Owner: {task.owner}\n"
        f"Instruction: {task.instruction}\n"
        f"Done Conditions: {task.done_conditions}\n"
        f"Target Paths:\n{target_paths}\n"
        "Validation Commands:\n"
        "- python3 -m pytest -q\n"
        "- git status\n"
        "- git diff --stat\n"
        "- git diff\n"
    )
