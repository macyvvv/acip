from __future__ import annotations

import json
from pathlib import Path

from system.scripts.roadmap.apply_frozen_issue_closures import main


def test_dry_run_produces_no_github_mutation(tmp_path, monkeypatch):
    root = tmp_path
    (root / "system" / "runtime" / "roadmap").mkdir(parents=True, exist_ok=True)
    plan = {
        "issues": [
            {
                "issue_number": 31,
                "title": "CONTENT-0001 Content Draft Review",
                "current_bucket": "FROZEN",
                "closure_disposition": "close_completed",
                "github_action_recommended": "close",
                "state_reason_if_closed": "completed",
                "classification_reason": "completed repository evidence exists",
                "evidence_source": "system/runtime/issues/completed/",
                "safe_to_apply": True,
            },
            {
                "issue_number": 25,
                "title": "PACK-0013 Repository OS v2 Release",
                "current_bucket": "FROZEN",
                "closure_disposition": "keep_open_broad_architecture",
                "github_action_recommended": "keep_open",
                "state_reason_if_closed": "",
                "classification_reason": "broad architecture work remains open unless explicitly marked not planned",
                "evidence_source": "roadmap",
                "safe_to_apply": False,
            },
        ]
    }
    plan_path = root / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    monkeypatch.setattr("system.scripts.roadmap.apply_frozen_issue_closures.ROOT", root)

    called = []
    monkeypatch.setattr("system.scripts.roadmap.apply_frozen_issue_closures.subprocess.run", lambda *args, **kwargs: called.append(args) or type("R", (), {"returncode": 0, "stderr": "", "stdout": ""})())
    rc = main([])
    assert rc == 0
    assert called == []


def test_apply_mode_closes_only_safe_plan_items(tmp_path, monkeypatch):
    root = tmp_path
    (root / "system" / "runtime" / "roadmap").mkdir(parents=True, exist_ok=True)
    plan = {
        "issues": [
            {
                "issue_number": 31,
                "title": "CONTENT-0001 Content Draft Review",
                "current_bucket": "FROZEN",
                "closure_disposition": "close_completed",
                "github_action_recommended": "close",
                "state_reason_if_closed": "completed",
                "classification_reason": "completed repository evidence exists",
                "evidence_source": "system/runtime/issues/completed/",
                "safe_to_apply": True,
            },
            {
                "issue_number": 25,
                "title": "PACK-0013 Repository OS v2 Release",
                "current_bucket": "FROZEN",
                "closure_disposition": "keep_open_broad_architecture",
                "github_action_recommended": "keep_open",
                "state_reason_if_closed": "",
                "classification_reason": "broad architecture work remains open unless explicitly marked not planned",
                "evidence_source": "roadmap",
                "safe_to_apply": False,
            },
        ]
    }
    plan_path = root / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    monkeypatch.setattr("system.scripts.roadmap.apply_frozen_issue_closures.ROOT", root)

    calls = []
    def fake_run(cmd, capture_output, text, check):  # noqa: ANN001
        calls.append(cmd)
        return type("R", (), {"returncode": 0, "stderr": "", "stdout": ""})()
    monkeypatch.setattr("system.scripts.roadmap.apply_frozen_issue_closures.subprocess.run", fake_run)

    rc = main(["--apply"])
    assert rc == 0
    assert calls == [["gh", "issue", "close", "31", "--reason", "completed"]]
