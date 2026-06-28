from pathlib import Path

from orchestrator.task import Task
from orchestrator.task_decomposer import TaskDecomposer, TaskDecomposerError


def _write_registry(root: Path) -> None:
    (root / "workers").mkdir()
    (root / "workers" / "registry.yaml").write_text(
        """workers:
  Codex:
    capability: [repository_implementation, validation_execution, task_decomposition]
    allowed_actions: [implement, validate]
    prohibited_actions: [approve]
    validation_responsibility: [run_repository_validation]
    output_contract: orchestrator/output_contract.py
  ChatGPT:
    capability: [architecture_review, task_decomposition]
    allowed_actions: [design, review]
    prohibited_actions: [execute_code]
    validation_responsibility: [define_validation_scope]
    output_contract: orchestrator/output_contract.py
  Human:
    capability: [approval]
    allowed_actions: [approve]
    prohibited_actions: [implement]
    validation_responsibility: [accept_risk]
    output_contract: orchestrator/output_contract.py
  GitHub Actions:
    capability: [ci_execution, repository_validation]
    allowed_actions: [run_workflow]
    prohibited_actions: [edit_code]
    validation_responsibility: [execute_validate_all]
    output_contract: orchestrator/output_contract.py
""",
        encoding="utf-8",
    )


def test_decompose_task_deterministic(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    decomposer = TaskDecomposer(tmp_path)
    task = Task(
        id="EP-0115:001",
        artifact="EP-0115",
        owner="ChatGPT",
        instruction="Implement and validate capability routing and task decomposition.",
        done_conditions="done",
    )

    result = decomposer.decompose(task)

    repeat = decomposer.decompose(task)

    assert result == repeat
    assert result.subtasks
    assert result.subtasks[0].worker_candidate in {"Codex", "ChatGPT"}
    assert result.subtasks[0].id.startswith("EP-0115:001:")


def test_decompose_unsupported_capability_fails(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    decomposer = TaskDecomposer(tmp_path)

    try:
        decomposer.decompose("unknown capability only", capability_requirements=("unsupported_capability",))
    except TaskDecomposerError as exc:
        assert "Unsupported capability" in str(exc) or "No capabilities inferred" in str(exc)
    else:
        raise AssertionError("expected failure")
