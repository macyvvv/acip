from system.orchestrator.result import Result
from system.orchestrator.task import Task


def test_result_dataclass_fields() -> None:
    next_task = Task(
        id="ep-005:test",
        artifact="test",
        owner="Codex",
        instruction="do something",
        done_conditions="done",
    )

    result = Result(
        artifacts=["a"],
        files_changed=["b"],
        checkpoint_candidate="checkpoint",
        current_state_candidate="state",
        review_notes=["note"],
        errors=["error"],
        next_task=next_task,
    )

    assert result.artifacts == ["a"]
    assert result.files_changed == ["b"]
    assert result.checkpoint_candidate == "checkpoint"
    assert result.current_state_candidate == "state"
    assert result.review_notes == ["note"]
    assert result.errors == ["error"]
    assert result.next_task == next_task
