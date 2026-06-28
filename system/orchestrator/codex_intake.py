from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib

from orchestrator.execution_request import ExecutionRequest


@dataclass(frozen=True)
class HandoffPayload:
    queue_path: str
    pack_id: str
    objective: str
    ep_range: tuple[str, str]
    status: str


class CodexIntakeError(ValueError):
    pass


class CodexIntake:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def read_next_handoff(self) -> HandoffPayload:
        queue_dir = self.base_path / "queue" / "READY"
        if not queue_dir.exists():
            raise FileNotFoundError(f"Queue directory not found: {queue_dir}")
        candidates = sorted(queue_dir.glob("EP-*.md"))
        if not candidates:
            raise CodexIntakeError("No ready handoff payload found")
        return self._parse_payload(candidates[0])

    def to_execution_request(self, payload: HandoffPayload) -> ExecutionRequest:
        request_id = self._stable_request_id(payload.queue_path)
        return ExecutionRequest(
            request_id=request_id,
            request_status="ready",
            request_priority=self._priority_from_ep_range(payload.ep_range),
            approval_required=False,
            dependency=(payload.queue_path,),
            worker_assignment="Codex",
        )

    def _parse_payload(self, path: Path) -> HandoffPayload:
        values = self._parse_key_values(path.read_text(encoding="utf-8"))
        required = ("pack_id", "objective", "status", "ep_range")
        missing = [key for key in required if not values.get(key)]
        if missing:
            raise CodexIntakeError(f"Missing required handoff fields: {', '.join(missing)}")
        ep_range = tuple(part.strip() for part in values["ep_range"].split("..", 1))
        if len(ep_range) != 2 or not ep_range[0] or not ep_range[1]:
            raise CodexIntakeError("Invalid ep_range in handoff payload")
        return HandoffPayload(
            queue_path=str(path.relative_to(self.base_path)),
            pack_id=values["pack_id"],
            objective=values["objective"],
            ep_range=(ep_range[0], ep_range[1]),
            status=values["status"],
        )

    def _parse_key_values(self, text: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip()] = value.strip()
        return values

    def _stable_request_id(self, queue_path: str) -> str:
        digest = hashlib.sha1(queue_path.encode("utf-8")).hexdigest()[:8].upper()
        return f"REQ-{digest}"

    def _priority_from_ep_range(self, ep_range: tuple[str, str]) -> int:
        return 100 if ep_range[0] <= ep_range[1] else 0

