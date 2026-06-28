from __future__ import annotations

from system.orchestrator.completion_protocol import CompletionStatus, build_completion_protocol


def test_completion_protocol_builds_payload() -> None:
    protocol = build_completion_protocol(
        status=CompletionStatus.success,
        pack_id="PACK-0004",
        parent_issue=9,
        ep_id="EP-0156",
        commit_sha="abc1234",
        validation_result="success",
        pytest_result="success",
        worktree_state="clean",
        next_action="Review latest completion marker.",
        requires_human_approval=False,
    )
    assert protocol.status is CompletionStatus.success
    assert protocol.pack_id == "PACK-0004"
