from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
from typing import Any

from system.orchestrator.capability_router import CapabilityRoute, CapabilityRouter
from system.orchestrator.task import Task


@dataclass(frozen=True)
class DecomposedSubtask:
    id: str
    title: str
    required_capability: str
    worker_candidate: str
    worker_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaskDecompositionResult:
    source: str
    objective: str
    subtasks: tuple[DecomposedSubtask, ...] = ()


class TaskDecomposerError(ValueError):
    pass


class TaskDecomposer:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def decompose(self, task: Task | str, capability_requirements: tuple[str, ...] | None = None) -> TaskDecompositionResult:
        objective = task.instruction if isinstance(task, Task) else str(task)
        source = task.id if isinstance(task, Task) else "objective"
        required_capabilities = capability_requirements or self._infer_capabilities(objective)
        if not required_capabilities:
            required_capabilities = ("repository_implementation",)
        if not required_capabilities:
            raise TaskDecomposerError("No capabilities inferred for decomposition")

        router = CapabilityRouter(self.base_path)
        subtasks = []
        for index, capability in enumerate(required_capabilities, start=1):
            try:
                route = router.route(
                    planner=self._planner_proxy(objective),
                    required_capabilities=(capability,),
                    prohibited_actions=("approve", "deploy"),
                    required_validation_responsibility=("run_repository_validation",),
                    execution_boundary=("push_directly_to_main",),
                )
            except Exception as exc:
                raise TaskDecomposerError(f"Unsupported capability: {capability}") from exc
            if not route.worker_name:
                raise TaskDecomposerError(f"Unsupported capability: {capability}")
            subtasks.append(
                DecomposedSubtask(
                    id=self._stable_subtask_id(source, capability, index),
                    title=f"{capability.replace('_', ' ').title()} subtask",
                    required_capability=capability,
                    worker_candidate=route.worker_name,
                    worker_candidates=route.candidates,
                )
            )
        if len(subtasks) != len(required_capabilities):
            raise TaskDecomposerError("Failed to decompose all capabilities")
        return TaskDecompositionResult(source=source, objective=objective, subtasks=tuple(subtasks))

    def _infer_capabilities(self, objective: str) -> tuple[str, ...]:
        text = objective.lower()
        matches: list[str] = []
        mapping = [
            ("validate", "validation_execution"),
            ("test", "validation_execution"),
            ("refactor", "repository_implementation"),
            ("implement", "repository_implementation"),
            ("route", "capability_routing"),
            ("kernel", "execution_kernel"),
            ("registry", "worker_registry"),
            ("decompose", "task_decomposition"),
        ]
        for keyword, capability in mapping:
            if keyword in text and capability not in matches:
                matches.append(capability)
        return tuple(matches)

    def _stable_subtask_id(self, source: str, capability: str, index: int) -> str:
        digest = hashlib.sha1(f"{source}:{capability}:{index}".encode("utf-8")).hexdigest()[:8]
        return f"{source}:{index:02d}:{digest}"

    def _planner_proxy(self, objective: str):
        return type("PlannerProxy", (), {"next_ep": objective})()
