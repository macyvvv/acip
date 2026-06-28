from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.chatgpt_review_intake import ChatGPTReviewIntake


@dataclass(frozen=True)
class IssueCommentPayload:
    issue_number: int
    comment_body: str
    comment_json_path: str


class IssueSynchronizer:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build_comment(self, intake: ChatGPTReviewIntake) -> IssueCommentPayload:
        body = "\n".join(
            [
                f"PACK: {intake.pack_id}",
                f"EP: {intake.ep_id}",
                f"commit_sha: {intake.commit_sha}",
                f"validation_result: {intake.validation_result}",
                f"pytest_result: {intake.pytest_result}",
                f"worktree_state: {intake.worktree_state}",
                f"next_action: {intake.next_action}",
                f"requires_human_approval: {str(intake.requires_human_approval).lower()}",
            ]
        )
        runtime_dir = self.base_path / "runtime" / "handoff" / "completion"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {"issue_number": intake.parent_issue, "comment_body": body}
        comment_json_path = runtime_dir / "issue_comment.json"
        comment_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (runtime_dir / "issue_comment.md").write_text(body + "\n", encoding="utf-8")
        return IssueCommentPayload(issue_number=intake.parent_issue, comment_body=body, comment_json_path=str(comment_json_path))
