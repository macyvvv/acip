from system.orchestrator.execution_record import build_worker_execution_record
from system.orchestrator.queue_state import QueueState
from system.orchestrator.result import Result
from system.orchestrator.task import Task
from system.orchestrator.worker_state import WorkerState


def test_build_worker_execution_record() -> None:
    task = Task(
        id="EP-0106:1",
        artifact="system/orchestrator/queue_transition.py",
        owner="Codex",
        instruction="implement",
        done_conditions="tests pass",
    )
    result = Result(
        artifacts=["system/orchestrator/queue_transition.py"],
        files_changed=["system/orchestrator/queue_transition.py"],
        review_notes=["ok"],
    )
    record = build_worker_execution_record(
        task,
        result,
        QueueState(status="RUNNING", active_ep="EP-0106", next_ep="EP-0107"),
        WorkerState(worker_name="Codex", current_ep="EP-0106", queue_status="RUNNING"),
    )

    assert record.task_id == "EP-0106:1"
    assert record.worker_name == "Codex"
    assert record.queue_status == "RUNNING"
    assert record.files_changed == ["system/orchestrator/queue_transition.py"]
    assert record.next_task_id is None
