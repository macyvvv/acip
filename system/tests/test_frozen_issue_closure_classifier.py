from __future__ import annotations

import json
from pathlib import Path

from system.core.frozen_issue_closure_classifier import build_frozen_issue_closure_plan


def test_completed_frozen_issues_are_close_completed(tmp_path):
    root = tmp_path
    (root / "system" / "runtime" / "roadmap").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "issues" / "completed").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "github").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "roadmap" / "issue_portfolio.json").write_text(
        json.dumps(
            {
                "issues": [
                    {
                        "issue_number": 30,
                        "title": "PRODUCT-0001 Product Launch Checklist",
                        "category": "product_incremental",
                        "current_status": "completed",
                        "priority_bucket": "FROZEN",
                        "execution_fit": "completed",
                        "recommended_reason": "done",
                        "blocking_reason": "",
                        "depends_on": [],
                        "source_of_truth": "completed_marker",
                    },
                    {
                        "issue_number": 25,
                        "title": "PACK-0013 Repository OS v2 Release",
                        "category": "broad_architecture",
                        "current_status": "archived",
                        "priority_bucket": "FROZEN",
                        "execution_fit": "archived",
                        "recommended_reason": "historic",
                        "blocking_reason": "",
                        "depends_on": [],
                        "source_of_truth": "roadmap",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (root / "system" / "runtime" / "issues" / "completed" / "issue_0030.json").write_text(
        json.dumps({"issue_number": 30, "issue_title": "PRODUCT-0001 Product Launch Checklist"}),
        encoding="utf-8",
    )
    (root / "system" / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps([{"number": 30, "title": "PRODUCT-0001 Product Launch Checklist", "state": "open"}]),
        encoding="utf-8",
    )

    plan = build_frozen_issue_closure_plan(root)
    close_30 = next(item for item in plan["issues"] if item["issue_number"] == 30)
    keep_25 = next(item for item in plan["issues"] if item["issue_number"] == 25)
    assert close_30["closure_disposition"] == "close_completed"
    assert close_30["github_action_recommended"] == "close"
    assert close_30["safe_to_apply"] is True
    assert keep_25["closure_disposition"] == "keep_open_broad_architecture"
    assert keep_25["github_action_recommended"] == "keep_open"


def test_plan_is_deterministic(tmp_path):
    root = tmp_path
    (root / "system" / "runtime" / "roadmap").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "issues" / "completed").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "github").mkdir(parents=True, exist_ok=True)
    portfolio = {
        "issues": [
            {
                "issue_number": 31,
                "title": "CONTENT-0001 Content Draft Review",
                "category": "content_incremental",
                "current_status": "completed",
                "priority_bucket": "FROZEN",
                "execution_fit": "completed",
                "recommended_reason": "done",
                "blocking_reason": "",
                "depends_on": [],
                "source_of_truth": "completed_marker",
            }
        ]
    }
    (root / "system" / "runtime" / "roadmap" / "issue_portfolio.json").write_text(json.dumps(portfolio), encoding="utf-8")
    (root / "system" / "runtime" / "issues" / "completed" / "issue_0031.json").write_text(
        json.dumps({"issue_number": 31, "issue_title": "CONTENT-0001 Content Draft Review"}),
        encoding="utf-8",
    )
    (root / "system" / "runtime" / "github" / "open_issues.json").write_text(json.dumps([]), encoding="utf-8")

    first = build_frozen_issue_closure_plan(root)
    second = build_frozen_issue_closure_plan(root)
    assert first == second

