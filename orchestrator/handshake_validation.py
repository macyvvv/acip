from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class HandshakeValidationResult:
    valid: bool
    reason: str


class HandshakeValidationError(ValueError):
    pass


class HandshakeValidator:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def validate(self) -> HandshakeValidationResult:
        payload = json.loads((self.base_path / "runtime" / "handoff" / "latest.json").read_text(encoding="utf-8"))
        required = ["status", "pack_id", "parent_issue", "ep_id", "commit_sha", "validation_result", "pytest_result", "worktree_state", "next_action", "requires_human_approval"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise HandshakeValidationError(f"Missing completion fields: {', '.join(missing)}")
        if payload["status"] not in {"success", "partial_success", "failure", "blocked", "skipped"}:
            raise HandshakeValidationError("Invalid completion status")
        return HandshakeValidationResult(valid=True, reason="completion and review intake are aligned")
