from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Iterable


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    request_status: str
    request_priority: int
    approval_required: bool
    dependency: tuple[str, ...] = ()
    worker_assignment: str | None = None


class ExecutionRequestBuilder:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def from_governor_candidate(
        self,
        candidate_ep: str,
        *,
        request_priority: int = 0,
        approval_required: bool = False,
        dependency: Iterable[str] = (),
        worker_assignment: str | None = None,
    ) -> ExecutionRequest:
        request_id = f"REQ-{candidate_ep}"
        status = "pending_approval" if approval_required else "ready"
        return ExecutionRequest(
            request_id=request_id,
            request_status=status,
            request_priority=request_priority,
            approval_required=approval_required,
            dependency=tuple(dependency),
            worker_assignment=worker_assignment,
        )

    def write_runtime_request(self, request: ExecutionRequest) -> None:
        runtime_dir = self.base_path / "runtime" / "request"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "request_id": request.request_id,
            "request_status": request.request_status,
            "request_priority": request.request_priority,
            "approval_required": request.approval_required,
            "dependency": list(request.dependency),
            "worker_assignment": request.worker_assignment,
        }
        (runtime_dir / "execution_request.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "EXECUTION_REQUEST.md").write_text(
            "\n".join(
                [
                    "# EXECUTION_REQUEST",
                    "",
                    f"request_id: {request.request_id}",
                    f"request_status: {request.request_status}",
                    f"request_priority: {request.request_priority}",
                    f"approval_required: {str(request.approval_required).lower()}",
                    f"worker_assignment: {request.worker_assignment or 'null'}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
