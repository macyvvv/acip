from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime, timezone


@dataclass(frozen=True)
class ExecutionSession:
    session_id: str
    session_status: str
    started_at: str
    finished_at: str | None = None


class ExecutionSessionManager:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def start(self, session_id: str) -> ExecutionSession:
        return ExecutionSession(session_id=session_id, session_status="running", started_at=self._now())

    def finish(self, session: ExecutionSession, status: str) -> ExecutionSession:
        return ExecutionSession(
            session_id=session.session_id,
            session_status=status,
            started_at=session.started_at,
            finished_at=self._now(),
        )

    def write_session(self, session: ExecutionSession) -> None:
        runtime_dir = self.base_path / "runtime" / "session"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": session.session_id,
            "session_status": session.session_status,
            "started_at": session.started_at,
            "finished_at": session.finished_at,
        }
        (runtime_dir / "execution_session.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "EXECUTION_SESSION.md").write_text(
            "\n".join(
                [
                    "# EXECUTION_SESSION",
                    "",
                    f"session_id: {session.session_id}",
                    f"session_status: {session.session_status}",
                    f"started_at: {session.started_at}",
                    f"finished_at: {session.finished_at or 'null'}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
