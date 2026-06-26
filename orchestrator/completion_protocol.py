from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompletionStatus(str, Enum):
    success = "success"
    partial_success = "partial_success"
    failure = "failure"
    blocked = "blocked"
    skipped = "skipped"


@dataclass(frozen=True)
class CompletionProtocol:
    status: CompletionStatus
    pack_id: str
    parent_issue: int
    ep_id: str
    commit_sha: str
    validation_result: str
    pytest_result: str
    worktree_state: str
    next_action: str
    requires_human_approval: bool


def build_completion_protocol(**kwargs) -> CompletionProtocol:
    return CompletionProtocol(**kwargs)
