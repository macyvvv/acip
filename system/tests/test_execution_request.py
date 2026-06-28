from __future__ import annotations

from orchestrator.execution_request import ExecutionRequestBuilder


def test_execution_request_builder_creates_ready_request() -> None:
    builder = ExecutionRequestBuilder(".")
    request = builder.from_governor_candidate("EP-0130", request_priority=10, approval_required=False)
    assert request.request_id == "REQ-EP-0130"
    assert request.request_status == "ready"
