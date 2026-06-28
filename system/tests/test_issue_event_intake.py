from __future__ import annotations

import json

from orchestrator.issue_event_intake import IssueEventIntake


def test_issue_event_intake_reads_fixture(tmp_path) -> None:
    fixture = tmp_path / "issue_event.json"
    fixture.write_text(
        json.dumps(
            {
                "event_id": "evt-issue-1",
                "issue_id": 14,
                "pack_id": "PACK-0005",
                "ep_id": "EP-0162",
                "actor": "Codex",
                "timestamp": "2026-06-26T00:00:00Z",
                "action": "issue_event",
                "risk_level": "low",
                "approval_required": False,
                "state": "open",
            }
        ),
        encoding="utf-8",
    )
    result = IssueEventIntake(tmp_path).intake(fixture)
    assert result.event.issue_id == 14
    assert result.eligible_for_resolution is True
