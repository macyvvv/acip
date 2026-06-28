from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from system.orchestrator.task import Task


@dataclass
class Worker:
    def execute(self, task: Task, context: Any) -> Any:
        raise NotImplementedError
