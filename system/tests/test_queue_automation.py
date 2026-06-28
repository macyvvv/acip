from __future__ import annotations

from pathlib import Path

from system.orchestrator.queue_automation import QueueAutomation


def test_queue_automation_advances_state(tmp_path: Path) -> None:
    docs_current = tmp_path / "docs" / "current"
    docs_current.mkdir(parents=True, exist_ok=True)
    docs_current.joinpath("QUEUE_STATE.md").write_text(
        "\n".join(
            [
                "# QUEUE_STATE",
                "",
                "status: READY",
                "active_ep: EP-0145",
                "next_ep: EP-0146",
                "",
            ]
        ),
        encoding="utf-8",
    )
    automation = QueueAutomation(tmp_path)
    result = automation.advance()
    assert result.previous.status == "READY"
    assert result.current.status == "RUNNING"
