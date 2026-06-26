from __future__ import annotations

from orchestrator.chatgpt_review_intake import ChatGPTReviewIntake
from orchestrator.issue_synchronizer import IssueSynchronizer


def test_issue_synchronizer_builds_comment(tmp_path) -> None:
    synchronizer = IssueSynchronizer(tmp_path)
    payload = synchronizer.build_comment(
        ChatGPTReviewIntake(
            pack_id="PACK-0004",
            parent_issue=9,
            ep_id="EP-0159",
            commit_sha="abc1234",
            validation_result="success",
            pytest_result="success",
            worktree_state="clean",
            next_action="Review latest completion marker.",
            requires_human_approval=False,
            review_decision_categories=("accept", "request_changes", "blocked", "requires_human_approval"),
        )
    )
    assert payload.issue_number == 9
    assert "commit_sha: abc1234" in payload.comment_body
