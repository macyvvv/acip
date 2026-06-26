from __future__ import annotations

import json

from orchestrator.event_runtime_cli import run_cli


def test_event_runtime_cli_returns_path(tmp_path) -> None:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"event_id":"evt-1","issue_id":14}), encoding="utf-8")
    (tmp_path / "queue" / "READY").mkdir(parents=True)
    (tmp_path / "queue" / "READY" / "EP-9999-sample.md").write_text("pack_id: PACK-0006\nobjective: Sample\nstatus: READY\n", encoding="utf-8")
    path = run_cli(fixture, tmp_path)
    assert path.endswith("dry_run.json")
