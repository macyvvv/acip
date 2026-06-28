from __future__ import annotations

import json

from orchestrator.event_runtime_dry_run import EventRuntimeDryRun
from orchestrator.completion_protocol import CompletionStatus, build_completion_protocol
from orchestrator.repository_completion_marker import RepositoryCompletionMarkerWriter


def test_event_runtime_dry_run_produces_output(tmp_path) -> None:
    (tmp_path / "queue" / "READY").mkdir(parents=True)
    (tmp_path / "queue" / "READY" / "EP-9999-sample.md").write_text("pack_id: PACK-0005\nobjective: Sample\nstatus: READY\n", encoding="utf-8")
    RepositoryCompletionMarkerWriter(tmp_path).write(
        build_completion_protocol(
            status=CompletionStatus.success,
            pack_id="PACK-0004",
            parent_issue=9,
            ep_id="EP-0165",
            commit_sha="abc1234",
            validation_result="success",
            pytest_result="success",
            worktree_state="clean",
            next_action="Review latest completion marker.",
            requires_human_approval=False,
        )
    )
    fixture = tmp_path / "issue_event.json"
    fixture.write_text(json.dumps({
        "event_id": "evt-issue-1",
        "issue_id": 14,
        "pack_id": "PACK-0005",
        "ep_id": "EP-0165",
        "actor": "Codex",
        "timestamp": "2026-06-26T00:00:00Z",
        "action": "issue_event",
        "risk_level": "low",
        "approval_required": False,
        "state": "open",
    }), encoding="utf-8")
    result = EventRuntimeDryRun(tmp_path).run_issue_fixture(fixture)
    assert result.approved is True
    assert (tmp_path / "runtime" / "event_runtime" / "dry_run.json").exists()
