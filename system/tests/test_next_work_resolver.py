from __future__ import annotations

from pathlib import Path

from orchestrator.next_work_resolver import NextWorkResolver


def test_next_work_resolver_selects_highest_priority(tmp_path: Path) -> None:
    ready = tmp_path / "queue" / "READY"
    ready.mkdir(parents=True, exist_ok=True)
    ready.joinpath("EP-1.md").write_text("pack_id: A\nobjective: A\nstatus: READY\npriority: 1\napproval_required: false\n", encoding="utf-8")
    ready.joinpath("EP-2.md").write_text("pack_id: B\nobjective: B\nstatus: READY\npriority: 2\napproval_required: false\n", encoding="utf-8")
    resolution = NextWorkResolver(tmp_path).resolve()
    assert resolution.selected.pack_id == "B"
