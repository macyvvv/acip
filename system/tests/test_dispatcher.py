import pytest

from system.orchestrator.dispatcher import Dispatcher, DispatcherError
from system.orchestrator.result import Result
from system.orchestrator.task import Task
from system.orchestrator.worker import Worker


class ResultWorker(Worker):
    def execute(self, task: Task, context):
        return Result(artifacts=[task.artifact])


class NonResultWorker(Worker):
    def execute(self, task: Task, context):
        return {"artifacts": [task.artifact]}


def test_registered_owner_dispatch_succeeds() -> None:
    dispatcher = Dispatcher(workers={"ChatGPT": ResultWorker()})
    task = Task(
        id="ep-005:test",
        artifact="artifact",
        owner="ChatGPT",
        instruction="do",
        done_conditions="done",
    )

    result = dispatcher.dispatch(task, context={})

    assert result.artifacts == ["artifact"]


def test_unregistered_owner_raises() -> None:
    dispatcher = Dispatcher(workers={})
    task = Task(
        id="ep-005:test",
        artifact="artifact",
        owner="ChatGPT",
        instruction="do",
        done_conditions="done",
    )

    with pytest.raises(DispatcherError, match="No worker registered"):
        dispatcher.dispatch(task, context={})


def test_non_result_worker_return_raises() -> None:
    dispatcher = Dispatcher(workers={"ChatGPT": NonResultWorker()})
    task = Task(
        id="ep-005:test",
        artifact="artifact",
        owner="ChatGPT",
        instruction="do",
        done_conditions="done",
    )

    with pytest.raises(DispatcherError, match="non-Result"):
        dispatcher.dispatch(task, context={})
