from orchestrator.task import Task


def test_task_is_immutable() -> None:
    task = Task(
        id="ep-002:CA-0001",
        artifact="CA-0001",
        owner="ChatGPT",
        instruction="Artifact\nCA-0001",
        done_conditions="20件がPublish品質",
        target_paths=("knowledge/draft/CA-0001.md",),
    )

    assert task.artifact == "CA-0001"
    assert task.target_paths == ("knowledge/draft/CA-0001.md",)

