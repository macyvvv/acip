from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ChatGPTReviewIntake:
    pack_id: str
    parent_issue: int
    ep_id: str
    commit_sha: str
    validation_result: str
    pytest_result: str
    worktree_state: str
    next_action: str
    requires_human_approval: bool
    review_decision_categories: tuple[str, ...]


class ChatGPTReviewIntakeReader:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def read(self) -> ChatGPTReviewIntake:
        payload = json.loads((self.base_path / "runtime" / "handoff" / "latest.json").read_text(encoding="utf-8"))
        return ChatGPTReviewIntake(
            pack_id=str(payload["pack_id"]),
            parent_issue=int(payload["parent_issue"]),
            ep_id=str(payload["ep_id"]),
            commit_sha=str(payload["commit_sha"]),
            validation_result=str(payload["validation_result"]),
            pytest_result=str(payload["pytest_result"]),
            worktree_state=str(payload["worktree_state"]),
            next_action=str(payload["next_action"]),
            requires_human_approval=bool(payload["requires_human_approval"]),
            review_decision_categories=("accept", "request_changes", "blocked", "requires_human_approval"),
        )
