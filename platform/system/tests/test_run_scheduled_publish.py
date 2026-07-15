from __future__ import annotations

import json
from pathlib import Path

from system.core.business_agent_automation_control import pause_automation
from system.core.publishing_control import pause_publishing
from system.scripts.publishing.finalize_content import finalize_content
from system.scripts.publishing.run_scheduled_publish import (
    evaluate_candidate,
    find_publish_candidates,
    run_scheduled_publish,
    PublishCandidate,
)


def _seed_policy(tmp_path: Path, **overrides) -> None:
    entry = {
        "policy_id": "PUBPOLICY-TEXT_SYNDICATE-X-0001",
        "business_id": "text_syndicate",
        "platform": "x",
        "enabled": True,
        "provider": "dry_run",
        "allowed_source_roles": ["marketing", "doc_creation"],
        "max_posts_per_day": 3,
        "max_posts_per_week": 10,
        "require_disclosure_tag_for_affiliate_content": False,
        "authored_by": "macy",
        "authored_at": "2026-07-10T00:00:00+00:00",
        "reason": "pilot",
    }
    entry.update(overrides)
    path = tmp_path / "platform/system/runtime/publishing/policy.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "policies": [entry]}))


def _seed_execution(tmp_path: Path, business_id: str, role_id: str, task_id: str, stdout: str, *, success: bool = True) -> None:
    path = tmp_path / "platform/system/runtime/business_agents" / business_id / role_id / task_id / "latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"success": success, "stdout": stdout}))


def _seed_eligible(tmp_path: Path, task_id: str = "task-0001", final_text: str = "the one final tweet", **policy_overrides) -> None:
    _seed_execution(tmp_path, "text_syndicate", "marketing", task_id, "3 drafts + outline blob")
    finalize_content("text_syndicate", "marketing", task_id, "x", final_text, "macy", tmp_path)
    _seed_policy(tmp_path, **policy_overrides)


def test_no_candidates_when_nothing_finalized(tmp_path: Path) -> None:
    assert find_publish_candidates(tmp_path) == []
    summary = run_scheduled_publish(tmp_path)
    assert summary.candidates_considered == 0
    assert summary.published == []


def test_full_dry_run_end_to_end(tmp_path: Path) -> None:
    _seed_eligible(tmp_path)
    summary = run_scheduled_publish(tmp_path)
    assert len(summary.published) == 1
    assert summary.published[0]["business_id"] == "text_syndicate"
    assert summary.published[0]["provider"] == "dry_run"
    assert summary.blocked == []
    assert Path(summary.audit_path).exists()
    latest = json.loads((tmp_path / "platform/system/runtime/publishing/audit/latest.json").read_text())
    assert len(latest["published"]) == 1


def test_negative_no_finalized_content_never_published(tmp_path: Path) -> None:
    # Approved-and-executed, and a fully enabled policy exists -- but nothing
    # was ever finalize_content.py'd. Execution approval + policy alone must
    # never be sufficient.
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0001", "3 drafts + outline blob")
    _seed_policy(tmp_path)
    assert find_publish_candidates(tmp_path) == []
    summary = run_scheduled_publish(tmp_path)
    assert summary.published == []


def test_no_policy_blocks(tmp_path: Path) -> None:
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0001", "blob")
    finalize_content("text_syndicate", "marketing", "task-0001", "x", "final text", "macy", tmp_path)
    # no policy.json written at all
    decision = evaluate_candidate(PublishCandidate("text_syndicate", "marketing", "task-0001", "x"), tmp_path)
    assert decision.eligible is False
    assert decision.reason == "no_enabled_policy"


def test_role_not_allowed(tmp_path: Path) -> None:
    _seed_eligible(tmp_path, allowed_source_roles=["doc_creation"])
    decision = evaluate_candidate(PublishCandidate("text_syndicate", "marketing", "task-0001", "x"), tmp_path)
    assert decision.eligible is False
    assert decision.reason == "role_not_allowed"


def test_cap_enforcement(tmp_path: Path) -> None:
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0001", "blob 1")
    finalize_content("text_syndicate", "marketing", "task-0001", "x", "final 1", "macy", tmp_path)
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0002", "blob 2")
    finalize_content("text_syndicate", "marketing", "task-0002", "x", "final 2", "macy", tmp_path)
    _seed_policy(tmp_path, max_posts_per_day=1, max_posts_per_week=1)

    summary = run_scheduled_publish(tmp_path)
    assert len(summary.published) == 1
    assert len(summary.blocked) == 1
    assert summary.blocked[0]["reason"] == "cap_exceeded"


def test_idempotency_running_twice_never_double_publishes(tmp_path: Path) -> None:
    _seed_eligible(tmp_path)
    first = run_scheduled_publish(tmp_path)
    second = run_scheduled_publish(tmp_path)
    assert len(first.published) == 1
    assert len(second.published) == 0
    assert second.blocked[0]["reason"] == "already_published"


def test_publishing_kill_switch_blocks(tmp_path: Path) -> None:
    _seed_eligible(tmp_path)
    pause_publishing("investigating", "macy", tmp_path)
    summary = run_scheduled_publish(tmp_path)
    assert summary.kill_switch_engaged is True
    assert summary.published == []
    assert summary.blocked[0]["reason"] == "kill_switch_paused"


def test_automation_kill_switch_also_blocks_publishing(tmp_path: Path) -> None:
    _seed_eligible(tmp_path)
    pause_automation("investigating an unrelated chain", "macy", tmp_path)
    summary = run_scheduled_publish(tmp_path)
    assert summary.kill_switch_engaged is True
    assert summary.published == []
    assert summary.blocked[0]["reason"] == "kill_switch_paused"


def test_execution_content_changed_since_finalization_blocks(tmp_path: Path) -> None:
    _seed_eligible(tmp_path)
    # Scope reused/content regenerated after finalization -- the hash must no longer match.
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0001", "a completely different draft now")
    decision = evaluate_candidate(PublishCandidate("text_syndicate", "marketing", "task-0001", "x"), tmp_path)
    assert decision.eligible is False
    assert decision.reason == "execution_content_changed_since_finalization"


def test_disclosure_tag_required_and_missing_blocks(tmp_path: Path) -> None:
    _seed_eligible(tmp_path, final_text="check out this great product, link in bio", require_disclosure_tag_for_affiliate_content=True)
    decision = evaluate_candidate(PublishCandidate("text_syndicate", "marketing", "task-0001", "x"), tmp_path)
    assert decision.eligible is False
    assert decision.reason == "missing_disclosure_tag"


def test_disclosure_tag_present_publishes(tmp_path: Path) -> None:
    _seed_eligible(
        tmp_path,
        final_text="check out this product (PR: affiliate link, アフィリエイト)",
        require_disclosure_tag_for_affiliate_content=True,
    )
    summary = run_scheduled_publish(tmp_path)
    assert len(summary.published) == 1


def test_disclosure_check_runs_against_final_text_not_outline(tmp_path: Path) -> None:
    # An outline that mentions "disclosure" as an instruction, without the
    # actual marker in the final text, must still block.
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-0001", "outline: place a disclosure block here")
    finalize_content(
        "text_syndicate", "marketing", "task-0001", "x",
        "no marker in this specific final string at all", "macy", tmp_path,
    )
    _seed_policy(tmp_path, require_disclosure_tag_for_affiliate_content=True)
    decision = evaluate_candidate(PublishCandidate("text_syndicate", "marketing", "task-0001", "x"), tmp_path)
    assert decision.eligible is False
    assert decision.reason == "missing_disclosure_tag"


def test_cross_scope_isolation_cap(tmp_path: Path) -> None:
    _seed_eligible(tmp_path, task_id="task-0001", max_posts_per_day=1)
    # A second business/platform combo, unrelated, with its own cap.
    _seed_execution(tmp_path, "kabukicho_survival_map", "doc_creation", "task-0001", "blob")
    finalize_content("kabukicho_survival_map", "doc_creation", "task-0001", "threads", "final threads copy", "macy", tmp_path)
    path = tmp_path / "platform/system/runtime/publishing/policy.json"
    policies = json.loads(path.read_text())
    policies["policies"].append(
        {
            "policy_id": "PUBPOLICY-KABUKICHO-THREADS-0001",
            "business_id": "kabukicho_survival_map",
            "platform": "threads",
            "enabled": True,
            "provider": "dry_run",
            "allowed_source_roles": ["marketing", "doc_creation"],
            "max_posts_per_day": 1,
            "max_posts_per_week": 5,
            "require_disclosure_tag_for_affiliate_content": False,
            "authored_by": "macy",
            "authored_at": "2026-07-10T00:00:00+00:00",
            "reason": "pilot",
        }
    )
    path.write_text(json.dumps(policies))

    summary = run_scheduled_publish(tmp_path)
    assert len(summary.published) == 2
    published_businesses = {item["business_id"] for item in summary.published}
    assert published_businesses == {"text_syndicate", "kabukicho_survival_map"}


def test_reply_to_external_id_is_passed_through_to_provider(tmp_path: Path, monkeypatch) -> None:
    _seed_execution(tmp_path, "text_syndicate", "marketing", "task-reply-0001", "reply candidates blob")
    finalize_content(
        "text_syndicate", "marketing", "task-reply-0001", "x", "reply text", "macy", tmp_path,
        reply_to_external_id="42",
    )
    _seed_policy(tmp_path)

    received = {}

    class _SpyProvider:
        name = "dry_run"

        def publish(self, platform, final_text, business_id, *, in_reply_to=None):
            from system.scripts.publishing.providers import PublishResult
            from datetime import datetime, timezone

            received["in_reply_to"] = in_reply_to
            return PublishResult(
                provider=self.name, platform=platform, business_id=business_id,
                external_post_id="1", published_at=datetime.now(timezone.utc).isoformat(), notes="spy",
            )

    import system.scripts.publishing.run_scheduled_publish as run_module

    monkeypatch.setattr(run_module, "get_provider", lambda name=None: _SpyProvider())

    summary = run_scheduled_publish(tmp_path)
    assert len(summary.published) == 1
    assert received["in_reply_to"] == "42"
