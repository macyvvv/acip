from __future__ import annotations

from pathlib import Path

from system.orchestrator.codex_intake import CodexIntake


def test_codex_intake_reads_queue_payload(tmp_path: Path) -> None:
    ready = tmp_path / "queue" / "READY"
    ready.mkdir(parents=True, exist_ok=True)
    ready.joinpath("EP-0001.md").write_text(
        "\n".join(
            [
                "# sample",
                "",
                "status: READY",
                "pack_id: PACK-0002",
                "objective: Sample",
                "ep_range: EP-0145..EP-0145",
                "",
            ]
        ),
        encoding="utf-8",
    )
    intake = CodexIntake(tmp_path)
    payload = intake.read_next_handoff()
    request = intake.to_execution_request(payload)
    assert payload.pack_id == "PACK-0002"
    assert request.worker_assignment == "Codex"
