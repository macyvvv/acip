import pytest

from system.orchestrator.task import Task
from system.orchestrator.worker import Worker


def test_worker_execute_raises_not_implemented() -> None:
    worker = Worker()
    task = Task(
        id="ep-004:test",
        artifact="test",
        owner="Codex",
        instruction="do something",
        done_conditions="done",
    )

    with pytest.raises(NotImplementedError):
        worker.execute(task, context={})
