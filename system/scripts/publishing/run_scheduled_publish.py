from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.core.business_agent_automation_control import is_automation_paused
from system.core.publishing_control import is_publishing_paused
from system.core.publishing_policy import get_publishing_policy
from system.core.publishing_state import (
    PublishingStateError,
    counts_for_today,
    counts_for_week,
    is_already_published,
    record_publish,
)
from system.scripts.publishing.finalize_content import load_finalized_content
from system.scripts.publishing.providers import PublishError, get_provider

# Simple heuristic, not a legal guarantee: checks for a literal disclosure
# marker inside the actual final_text that will post, not an outline
# describing where a disclosure should go elsewhere in a longer draft. Word-
# boundary matched (not bare substring) so short/generic markers like "PR"
# don't false-positive inside ordinary words such as "product" or "print".
_DISCLOSURE_MARKER_PATTERN = re.compile(
    r"(アフィリエイト|広告|\bPR\b|\bsponsored\b|\baffiliate\b)", re.IGNORECASE
)


def _has_disclosure_marker(text: str) -> bool:
    return bool(_DISCLOSURE_MARKER_PATTERN.search(text))


@dataclass(frozen=True)
class PublishCandidate:
    business_id: str
    role_id: str
    task_id: str
    platform: str


@dataclass(frozen=True)
class PublishDecision:
    candidate: PublishCandidate
    eligible: bool
    reason: str


@dataclass(frozen=True)
class PublishRunSummary:
    started_at: str
    finished_at: str
    kill_switch_engaged: bool
    candidates_considered: int
    published: list[dict[str, Any]]
    blocked: list[dict[str, Any]]
    audit_path: str


def find_publish_candidates(base_path: str | Path = ".") -> list[PublishCandidate]:
    """The finalized-content artifacts under system/runtime/publishing/finalized/
    ARE the candidate list -- not a scan of the task queue. Execution approval
    alone never makes a task a candidate; only an explicit, human-authored
    finalize_content.py call does."""
    finalized_root = Path(base_path) / "system/runtime/publishing/finalized"
    if not finalized_root.exists():
        return []
    candidates = []
    for path in sorted(finalized_root.glob("*/*/*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        candidates.append(
            PublishCandidate(
                business_id=str(record["business_id"]),
                role_id=str(record["role_id"]),
                task_id=str(record["task_id"]),
                platform=str(record["platform"]),
            )
        )
    return candidates


def _execution_artifact(business_id: str, role_id: str, task_id: str, base_path: str | Path) -> dict[str, Any] | None:
    path = Path(base_path) / "system/runtime/business_agents" / business_id / role_id / task_id / "latest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_candidate(candidate: PublishCandidate, base_path: str | Path = ".") -> PublishDecision:
    if is_publishing_paused(base_path) or is_automation_paused(base_path):
        return PublishDecision(candidate, False, "kill_switch_paused")

    finalized = load_finalized_content(candidate.business_id, candidate.role_id, candidate.task_id, candidate.platform, base_path)
    if finalized is None:
        return PublishDecision(candidate, False, "no_finalized_content")

    policy = get_publishing_policy(candidate.business_id, candidate.platform, base_path)
    if policy is None:
        return PublishDecision(candidate, False, "no_enabled_policy")
    if candidate.role_id not in policy.allowed_source_roles:
        return PublishDecision(candidate, False, "role_not_allowed")

    if is_already_published(candidate.business_id, candidate.platform, candidate.role_id, candidate.task_id, base_path):
        return PublishDecision(candidate, False, "already_published")

    if counts_for_today(candidate.business_id, candidate.platform, base_path) >= policy.max_posts_per_day:
        return PublishDecision(candidate, False, "cap_exceeded")
    if policy.max_posts_per_week is not None and counts_for_week(candidate.business_id, candidate.platform, base_path) >= policy.max_posts_per_week:
        return PublishDecision(candidate, False, "cap_exceeded")

    artifact = _execution_artifact(candidate.business_id, candidate.role_id, candidate.task_id, base_path)
    if artifact is None or not artifact.get("success"):
        return PublishDecision(candidate, False, "execution_not_successful")
    current_hash = hashlib.sha256(str(artifact.get("stdout") or "").encode("utf-8")).hexdigest()
    if current_hash != finalized.get("source_execution_hash"):
        return PublishDecision(candidate, False, "execution_content_changed_since_finalization")

    if policy.require_disclosure_tag_for_affiliate_content:
        final_text = str(finalized.get("final_text") or "")
        if not _has_disclosure_marker(final_text):
            return PublishDecision(candidate, False, "missing_disclosure_tag")

    return PublishDecision(candidate, True, "eligible")


def run_scheduled_publish(base_path: str | Path = ".") -> PublishRunSummary:
    started_at = datetime.now(timezone.utc).isoformat()
    kill_switch_engaged = is_publishing_paused(base_path) or is_automation_paused(base_path)
    candidates = find_publish_candidates(base_path)

    published: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for candidate in candidates:
        decision = evaluate_candidate(candidate, base_path)
        if not decision.eligible:
            blocked.append({**asdict(candidate), "reason": decision.reason})
            continue

        finalized = load_finalized_content(candidate.business_id, candidate.role_id, candidate.task_id, candidate.platform, base_path)
        policy = get_publishing_policy(candidate.business_id, candidate.platform, base_path)
        try:
            provider = get_provider(policy.provider)
            result = provider.publish(
                candidate.platform,
                str(finalized["final_text"]),
                candidate.business_id,
                in_reply_to=finalized.get("reply_to_external_id"),
            )
            record_publish(
                candidate.business_id,
                candidate.role_id,
                candidate.task_id,
                candidate.platform,
                result.provider,
                result.external_post_id,
                base_path,
            )
        except (PublishError, PublishingStateError) as exc:
            blocked.append({**asdict(candidate), "reason": f"publish_failed: {exc}"})
            continue
        published.append({**asdict(candidate), "provider": result.provider, "external_post_id": result.external_post_id})

    finished_at = datetime.now(timezone.utc).isoformat()
    audit_path = _write_audit(
        started_at=started_at,
        finished_at=finished_at,
        kill_switch_engaged=kill_switch_engaged,
        candidates_considered=len(candidates),
        published=published,
        blocked=blocked,
        base_path=base_path,
    )
    return PublishRunSummary(
        started_at=started_at,
        finished_at=finished_at,
        kill_switch_engaged=kill_switch_engaged,
        candidates_considered=len(candidates),
        published=published,
        blocked=blocked,
        audit_path=str(audit_path),
    )


def _write_audit(
    *,
    started_at: str,
    finished_at: str,
    kill_switch_engaged: bool,
    candidates_considered: int,
    published: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
    base_path: str | Path,
) -> Path:
    audit_dir = Path(base_path) / "system/runtime/publishing/audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "started_at": started_at,
        "finished_at": finished_at,
        "kill_switch_engaged": kill_switch_engaged,
        "candidates_considered": candidates_considered,
        "published": published,
        "blocked": blocked,
    }
    run_key = started_at.replace(":", "").replace("-", "").replace("+", "").replace(".", "")
    run_path = audit_dir / f"{run_key}.json"
    run_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (audit_dir / f"{run_key}.md").write_text(_markdown(payload), encoding="utf-8")
    (audit_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (audit_dir / "latest.md").write_text(_markdown(payload), encoding="utf-8")
    return run_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PUBLISHING_RUN",
        "",
        f"started_at: {payload['started_at']}",
        f"finished_at: {payload['finished_at']}",
        f"kill_switch_engaged: {str(payload['kill_switch_engaged']).lower()}",
        f"candidates_considered: {payload['candidates_considered']}",
        "",
        "## published",
    ]
    for item in payload["published"]:
        lines.append(f"- {item['business_id']}/{item['role_id']}/{item['task_id']} -> {item['platform']} (provider={item['provider']})")
    lines.append("")
    lines.append("## blocked")
    for item in payload["blocked"]:
        lines.append(f"- {item['business_id']}/{item['role_id']}/{item['task_id']} -> {item['platform']}: {item['reason']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    argparse.ArgumentParser(description="Run the publishing scheduler once against all finalized content candidates.").parse_args()
    summary = run_scheduled_publish(ROOT)
    print(f"kill_switch_engaged={str(summary.kill_switch_engaged).lower()}")
    print(f"candidates_considered={summary.candidates_considered}")
    print(f"published={len(summary.published)}")
    print(f"blocked={len(summary.blocked)}")
    print(f"audit_path={summary.audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
