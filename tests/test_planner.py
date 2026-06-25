from pathlib import Path

import pytest

from orchestrator.planner import PlannerError, plan_and_persist_queue_state, plan_next_ep
from orchestrator.queue_state import QueueState
from orchestrator.worker_state import WorkerState


def test_plan_next_ep_advances_from_repository_state() -> None:
    decision = plan_next_ep(
        QueueState(status="READY", active_ep="EP-0108", next_ep="EP-0109"),
        WorkerState(worker_name="Codex", current_ep="EP-0108", queue_status="READY"),
    )

    assert decision.current_ep == "EP-0108"
    assert decision.next_ep == "EP-0109"
    assert decision.dependency_chain[-1] == "EP-0109"


def test_plan_and_persist_queue_state(tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs" / "current").mkdir(parents=True)
    (root / "docs" / "current" / "QUEUE_STATE.md").write_text(
        "# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-0108\nnext_ep: EP-0109\n",
        encoding="utf-8",
    )
    (root / "docs" / "current" / "WORKER_STATE.md").write_text(
        "# WORKER_STATE\n\nworker_name: Codex\ncurrent_ep: EP-0108\nqueue_status: READY\n",
        encoding="utf-8",
    )

    decision = plan_and_persist_queue_state(root)

    assert decision.next_ep == "EP-0109"
    persisted = (root / "docs" / "current" / "QUEUE_STATE.md").read_text(encoding="utf-8")
    assert "active_ep: EP-0108" in persisted
    assert "next_ep: EP-0109" in persisted


@pytest.mark.parametrize(
    "status",
    ["UNKNOWN", ""],
)
def test_plan_next_ep_rejects_invalid_status(status: str) -> None:
    with pytest.raises(PlannerError, match="Invalid queue status"):
        plan_next_ep(
            QueueState(status=status, active_ep="EP-0108", next_ep="EP-0109"),
            WorkerState(worker_name="Codex", current_ep="EP-0108", queue_status="READY"),
        )
