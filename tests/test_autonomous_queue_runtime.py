from __future__ import annotations

from pathlib import Path

from orchestrator.autonomous_queue_runtime import AutonomousQueueRuntime


def test_autonomous_queue_runtime_runs(tmp_path: Path) -> None:
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
                "ep_range: EP-0149..EP-0149",
                "priority: 1",
                "approval_required: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    docs_current = tmp_path / "docs" / "current"
    docs_current.mkdir(parents=True, exist_ok=True)
    docs_current.joinpath("QUEUE_STATE.md").write_text(
        "\n".join(
            [
                "# QUEUE_STATE",
                "",
                "status: READY",
                "active_ep: EP-0149",
                "next_ep: EP-0150",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = AutonomousQueueRuntime(tmp_path).run()
    assert result.next_work_pack_id == "PACK-0002"
