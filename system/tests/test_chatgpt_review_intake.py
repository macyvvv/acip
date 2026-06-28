from __future__ import annotations

from system.orchestrator.chatgpt_review_intake import ChatGPTReviewIntakeReader
from system.orchestrator.completion_protocol import CompletionStatus, build_completion_protocol
from system.orchestrator.repository_completion_marker import RepositoryCompletionMarkerWriter


def test_chatgpt_review_intake_reads_latest_marker(tmp_path) -> None:
    writer = RepositoryCompletionMarkerWriter(tmp_path)
    writer.write(
        build_completion_protocol(
            status=CompletionStatus.success,
            pack_id="PACK-0004",
            parent_issue=9,
            ep_id="EP-0158",
            commit_sha="abc1234",
            validation_result="success",
            pytest_result="success",
            worktree_state="clean",
            next_action="Review latest completion marker.",
            requires_human_approval=False,
        )
    )
    intake = ChatGPTReviewIntakeReader(tmp_path).read()
    assert intake.pack_id == "PACK-0004"
    assert "accept" in intake.review_decision_categories
