from system.orchestrator.review_package import build_review_package
from system.orchestrator.state import State
from system.orchestrator.task import Task


def test_build_review_package() -> None:
    state = State(
        repository="macyvvv/acip",
        branch="main",
        current_milestone="M1 First Revenue",
        current_phase="EP-002 Canonical Asset Production",
        current_objective="Objective",
        current_epic="EP-002 Canonical Asset Production",
        current_task="Task",
        next_action="Action",
    )
    task = Task(
        id="ep-002:test",
        artifact="CA-0001",
        owner="ChatGPT",
        instruction="Instruction",
        done_conditions="Done",
    )

    package = build_review_package(state, task, artifacts=["a"], validation=["git status"])

    assert package.current_objective == "Objective"
    assert package.task == task
    assert package.artifacts == ["a"]
    assert package.validation == ["git status"]
