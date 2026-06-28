from __future__ import annotations

import json

from system.orchestrator.workflow_dispatch_runtime import WorkflowDispatchRuntime


def test_workflow_dispatch_runtime_runs(tmp_path) -> None:
    (tmp_path / "queue" / "READY").mkdir(parents=True)
    (tmp_path / "queue" / "READY" / "EP-9999-sample.md").write_text("pack_id: PACK-0006\nobjective: Sample\nstatus: READY\n", encoding="utf-8")
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({"event_id":"evt-1","issue_id":14}), encoding="utf-8")
    result = WorkflowDispatchRuntime(tmp_path).run(fixture)
    assert result.decision in {"queue_next_work", "no_work"}
