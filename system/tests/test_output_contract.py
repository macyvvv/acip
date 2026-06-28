from orchestrator.output_contract import (
    ValidationResult,
    WorktreeState,
    build_output_contract,
)


def test_build_output_contract() -> None:
    contract = build_output_contract(
        task_id="EP-0107:1",
        validation_results=[ValidationResult(command="python -m pytest -q", exit_code=0)],
        commit_sha="abc123",
        worktree_state=WorktreeState(clean=True, changed_files=[]),
        next_action="Review",
        rerun_validation_conditions=["non-zero exit code"],
    )

    assert contract.task_id == "EP-0107:1"
    assert contract.commit_sha == "abc123"
    assert contract.worktree_state.clean is True
    assert contract.rerun_validation_conditions == ["non-zero exit code"]
