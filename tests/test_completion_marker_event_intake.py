from __future__ import annotations

from orchestrator.completion_protocol import CompletionStatus, build_completion_protocol
from orchestrator.repository_completion_marker import RepositoryCompletionMarkerWriter
from orchestrator.completion_marker_event_intake import CompletionMarkerEventIntake


def test_completion_marker_event_intake_reads_latest(tmp_path) -> None:
    RepositoryCompletionMarkerWriter(tmp_path).write(
        build_completion_protocol(
            status=CompletionStatus.success,
            pack_id="PACK-0004",
            parent_issue=9,
            ep_id="EP-0163",
            commit_sha="abc1234",
            validation_result="success",
            pytest_result="success",
            worktree_state="clean",
            next_action="Review latest completion marker.",
            requires_human_approval=False,
        )
    )
    result = CompletionMarkerEventIntake(tmp_path).intake()
    assert result.event.pack_id == "PACK-0004"
    assert result.ready_for_review is True
