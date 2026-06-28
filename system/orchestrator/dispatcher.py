from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from system.orchestrator.result import Result
from system.orchestrator.task import Task
from system.orchestrator.worker import Worker


class DispatcherError(ValueError):
    pass


@dataclass
class Dispatcher:
    workers: dict[str, Worker]

    def dispatch(self, task: Task, context: Any) -> Result:
        worker = self.workers.get(task.owner)
        if worker is None:
            raise DispatcherError(f"No worker registered for owner: {task.owner}")

        result = worker.execute(task, context)
        if not isinstance(result, Result):
            raise DispatcherError(
                f"Worker returned non-Result for owner: {task.owner}"
            )

        return result
