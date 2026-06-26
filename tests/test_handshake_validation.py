from __future__ import annotations

from orchestrator.completion_protocol import CompletionStatus, build_completion_protocol
from orchestrator.handshake_validation import HandshakeValidator
from orchestrator.repository_completion_marker import RepositoryCompletionMarkerWriter


def test_handshake_validation_passes(tmp_path) -> None:
    RepositoryCompletionMarkerWriter(tmp_path).write(
        build_completion_protocol(
            status=CompletionStatus.success,
            pack_id="PACK-0004",
            parent_issue=9,
            ep_id="EP-0160",
            commit_sha="abc1234",
            validation_result="success",
            pytest_result="success",
            worktree_state="clean",
            next_action="Review latest completion marker.",
            requires_human_approval=False,
        )
    )
    result = HandshakeValidator(tmp_path).validate()
    assert result.valid
