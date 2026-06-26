from __future__ import annotations

from orchestrator.codex_intake import CodexIntake


def test_codex_intake_reads_queue_payload() -> None:
    intake = CodexIntake(".")
    payload = intake.read_next_handoff()
    request = intake.to_execution_request(payload)
    assert payload.pack_id == "PACK-0002"
    assert request.worker_assignment == "Codex"
