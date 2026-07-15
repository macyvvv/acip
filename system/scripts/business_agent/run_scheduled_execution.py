from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.core.approved_autonomous_execution import ApprovedAutonomousExecution
from system.core.business_agent_task_queue import list_candidate_tasks
from system.core.execution_pre_approval_policy import (
    ExecutionPreApprovalPolicyError,
    get_execution_pre_approval_policy,
)
from system.core.file_lock import FileLockTimeout, locked
from system.core.scheduled_execution_control import is_scheduled_execution_paused
from system.core.scheduled_merge_circuit import record_merge_gate_failure, record_merge_gate_success
from system.core.scheduled_merge_control import is_scheduled_merge_paused

# ADR-0038. See docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md's Level 3b
# section for the full spec this implements: a kill switch, an actual
# notification (not just git-tracked state), a rollback plan, and a cost
# guard. Scope is generation-only roles (claude_invocation/data_fetch) --
# get_execution_pre_approval_policy() re-validates role_kind/allowed_tools
# against the LIVE registry on every call, so a pluggable_provider role or a
# role with a mutating tool can never be picked up here, structurally, the
# same way Level 3a already guarantees this for interactive/session-triggered
# runs. Posting/publishing (Level 3c) and any deploy action are untouched.
#
# ADR-0040 (Level 3d) extends this with an unattended-merge capability,
# gated separately (see _attempt_auto_merge below) -- generation (3b) and
# merge (3d) are two distinct trust decisions with two distinct kill
# switches, not one capability under a single letter.

MAX_TASK_EXECUTIONS_PER_WAKE = 5

# Once auto-merge exists, a malformed identifier reaching a filesystem path
# with zero human eyes on the diff is a real path-traversal-shaped risk that
# used to be caught by PR review. Validated before a wake even attempts
# execution, not just before merge.
_SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# Bounded poll for GitHub's real CI status before an unattended merge --
# never block/retry indefinitely; a timeout is treated the same as
# CI-not-green (leave the PR open for human/session review).
_CI_POLL_TIMEOUT_SECONDS = 300
_CI_POLL_INTERVAL_SECONDS = 15

# A launchd/cron-invoked process inherits none of an interactive shell's
# exported env vars. business_agent_execution_adapter.py's
# DEFAULT_CLI_TIMEOUT_SECONDS=60 is too short for real generation work (this
# already caused a live failure: text_syndicate/market_research/task-0003-
# finance-saas-niche timed out at the 60s default before this fix existed).
# setdefault, not assignment, so an operator's own explicit env var (e.g. for
# a manual dry-run) is never silently overridden.
os.environ.setdefault("CLAUDE_EXECUTION_TIMEOUT_SECONDS", "240")

_TRACKED_RUNTIME_PATHS = [
    "system/runtime/agent_execution",
    "system/runtime/agent_handoff/scopes",
    "system/runtime/agent_handoff/pre_approval_state",
    "system/runtime/business_agents",
    "system/runtime/business_agent_tasks/queue.json",
    "system/runtime/knowledge/kpi.json",
]


@dataclass(frozen=True)
class ScheduledCandidate:
    business_id: str
    role_id: str
    task_id: str
    policy_id: str


@dataclass(frozen=True)
class ScheduledExecutionSummary:
    started_at: str
    finished_at: str
    kill_switch_engaged: bool
    skipped_overlap: bool
    candidates_considered: int
    executed: list[dict[str, Any]]
    pr_url: str | None
    pr_skip_reason: str | None
    audit_path: str
    merge_attempted: bool = False
    merge_result: str | None = None
    merge_skip_reason: str | None = None


def _is_safe_identifier(value: str) -> bool:
    return bool(value) and bool(_SAFE_IDENTIFIER_RE.match(value))


def find_scheduled_candidates(base_path: str | Path = ".") -> list[ScheduledCandidate]:
    """Advisory pre-filter only -- adds zero new authorization surface. The
    one real authorization decision still lives entirely inside
    ApprovedAutonomousExecution.run() / _try_policy_pre_approval, called
    below with the exact (business_id, role_id, task_id) a human could pass
    manually via run_approved_autonomous_execution.py. Deliberately reuses
    get_execution_pre_approval_policy() itself -- the SAME function the real
    check calls -- rather than a second, independently-maintained
    role_kind/allowed_tools check, so this pre-filter can never silently
    drift from what's actually authoritative."""
    selected: list[ScheduledCandidate] = []
    seen_pairs: set[tuple[str, str]] = set()
    for item in list_candidate_tasks(base_path):
        business_id = str(item.get("business_id") or "")
        role_id = str(item.get("role_id") or "")
        task_id = str(item.get("task_id") or "")
        if not (_is_safe_identifier(business_id) and _is_safe_identifier(role_id) and _is_safe_identifier(task_id)):
            continue
        pair = (business_id, role_id)
        if pair in seen_pairs:
            continue
        try:
            policy = get_execution_pre_approval_policy(business_id, role_id, base_path)
        except ExecutionPreApprovalPolicyError:
            continue
        if policy is None:
            continue
        seen_pairs.add(pair)
        selected.append(ScheduledCandidate(business_id, role_id, task_id, policy.policy_id))
        if len(selected) >= MAX_TASK_EXECUTIONS_PER_WAKE:
            break
    return selected


def run_scheduled_execution(base_path: str | Path = ".") -> ScheduledExecutionSummary:
    started_at = _now()
    base_path = Path(base_path)

    if is_scheduled_execution_paused(base_path):
        finished_at = _now()
        audit_path = _write_audit(started_at, finished_at, True, False, 0, [], base_path)
        return ScheduledExecutionSummary(started_at, finished_at, True, False, 0, [], None, "kill_switch_paused", str(audit_path))

    lock_path = base_path / "system" / "runtime" / "scheduler" / "scheduler.lock"
    try:
        with locked(lock_path, timeout_seconds=2.0):
            return _run_wake(base_path, started_at)
    except FileLockTimeout:
        finished_at = _now()
        audit_path = _write_audit(started_at, finished_at, False, True, 0, [], base_path)
        return ScheduledExecutionSummary(started_at, finished_at, False, True, 0, [], None, "previous_wake_still_running", str(audit_path))


def _run_wake(base_path: Path, started_at: str) -> ScheduledExecutionSummary:
    # Checked BEFORE any candidate executes, not after -- executing legitimately
    # dirties the tree with the wake's own output, so checking cleanliness only
    # protects against PRE-EXISTING unrelated dirty state (a human's own
    # in-progress work on the same clone), not the wake's own changes. A
    # check placed after execution would spuriously fire on every real wake.
    if not _working_tree_is_clean(base_path):
        finished_at = _now()
        audit_path = _write_audit(started_at, finished_at, False, False, 0, [], base_path, pr_skip_reason="working_tree_dirty_skip_wake")
        return ScheduledExecutionSummary(started_at, finished_at, False, False, 0, [], None, "working_tree_dirty_skip_wake", str(audit_path))

    candidates = find_scheduled_candidates(base_path)
    executed: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            result = ApprovedAutonomousExecution(base_path).run(
                business_id=candidate.business_id,
                role_id=candidate.role_id,
                task_id=candidate.task_id,
            )
            executed.append(
                {
                    "business_id": candidate.business_id,
                    "role_id": candidate.role_id,
                    "task_id": candidate.task_id,
                    "policy_id": candidate.policy_id,
                    "execution_triggered": result.execution_triggered,
                    "execution_result_status": result.execution_result_status,
                    "authorization_source": result.authorization_source,
                    "stopped_reason": result.stopped_reason,
                }
            )
        except Exception as exc:  # a single scope's unexpected failure must never abort the wake
            executed.append(
                {
                    "business_id": candidate.business_id,
                    "role_id": candidate.role_id,
                    "task_id": candidate.task_id,
                    "policy_id": candidate.policy_id,
                    "execution_triggered": False,
                    "execution_result_status": "runner_exception",
                    "authorization_source": "policy_pre_approval",
                    "stopped_reason": str(exc),
                }
            )
            continue

    finished_at = _now()
    run_key = started_at.replace(":", "").replace("-", "").replace("+", "").replace(".", "")
    triggered = [item for item in executed if item["execution_triggered"]]
    pr_url: str | None = None
    pr_skip_reason: str | None = None
    merge_attempted = False
    merge_result: str | None = None
    merge_skip_reason: str | None = None
    if triggered:
        landing = _land_via_pr(base_path, run_key, executed)
        pr_url, pr_skip_reason, merge_attempted, merge_result, merge_skip_reason = landing
    audit_path = _write_audit(
        started_at,
        finished_at,
        False,
        False,
        len(candidates),
        executed,
        base_path,
        pr_url=pr_url,
        pr_skip_reason=pr_skip_reason,
        merge_attempted=merge_attempted,
        merge_result=merge_result,
        merge_skip_reason=merge_skip_reason,
    )
    return ScheduledExecutionSummary(
        started_at,
        finished_at,
        False,
        False,
        len(candidates),
        executed,
        pr_url,
        pr_skip_reason,
        str(audit_path),
        merge_attempted=merge_attempted,
        merge_result=merge_result,
        merge_skip_reason=merge_skip_reason,
    )


# --- Git/GitHub landing -----------------------------------------------------
# The ONLY functions in this module that shell out to git/gh. Everything
# above (candidate selection, execution) never touches git. Deliberately
# conservative: _run_wake already refused to execute anything at all unless
# the tree was clean *before* the wake started, so by the time this is
# called, whatever is dirty is exclusively this wake's own known-good
# output (protected end-to-end by the whole-invocation lock) -- there is
# nothing left here to re-guard against a human's in-progress work with.

def _run_git(args: list[str], base_path: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=base_path, capture_output=True, text=True, check=check)


def _working_tree_is_clean(base_path: Path) -> bool:
    result = _run_git(["status", "--porcelain"], base_path, check=False)
    return result.returncode == 0 and result.stdout.strip() == ""


def _land_via_pr(
    base_path: Path, run_key: str, executed: list[dict[str, Any]]
) -> tuple[str | None, str | None, bool, str | None, str | None]:
    """Returns (pr_url, pr_skip_reason, merge_attempted, merge_result, merge_skip_reason)."""
    current_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], base_path, check=False).stdout.strip()
    if current_branch != "main":
        if _run_git(["checkout", "main"], base_path, check=False).returncode != 0:
            return None, "checkout_main_failed", False, None, None
    if _run_git(["pull", "--ff-only", "origin", "main"], base_path, check=False).returncode != 0:
        return None, "pull_main_failed", False, None, None

    # Recorded now, BEFORE the wake's own commits/branch exist -- this is the
    # base every downstream merge-gate check (ADR-0040) compares against to
    # detect a concurrent landing (another wake/clone/session merging first)
    # while this one was still executing.
    base_sha = _run_git(["rev-parse", "origin/main"], base_path, check=False).stdout.strip()

    branch_name = f"scheduler/run-{run_key}"
    if _run_git(["checkout", "-b", branch_name], base_path, check=False).returncode != 0:
        _run_git(["checkout", "main"], base_path, check=False)
        return None, "create_branch_failed", False, None, None

    for rel_path in _TRACKED_RUNTIME_PATHS:
        if (base_path / rel_path).exists():
            _run_git(["add", rel_path], base_path, check=False)

    if _working_tree_is_clean(base_path):
        _run_git(["checkout", "main"], base_path, check=False)
        _run_git(["branch", "-D", branch_name], base_path, check=False)
        return None, "nothing_to_commit", False, None, None

    commit_result = _run_git(["commit", "-m", _commit_message(executed)], base_path, check=False)
    if commit_result.returncode != 0:
        _run_git(["checkout", "main"], base_path, check=False)
        _run_git(["branch", "-D", branch_name], base_path, check=False)
        return None, "commit_failed", False, None, None

    if _run_git(["push", "-u", "origin", branch_name], base_path, check=False).returncode != 0:
        _run_git(["checkout", "main"], base_path, check=False)
        return None, "push_failed", False, None, None

    pr_result = subprocess.run(
        ["gh", "pr", "create", "--title", f"Scheduled execution: {branch_name}", "--body", _pr_body(executed)],
        cwd=base_path,
        capture_output=True,
        text=True,
    )
    if pr_result.returncode != 0:
        _run_git(["checkout", "main"], base_path, check=False)
        return None, f"pr_create_failed:{pr_result.stderr.strip()[:200]}", False, None, None
    pr_url = pr_result.stdout.strip()

    merge_attempted, merge_result, merge_skip_reason = _attempt_auto_merge(base_path, pr_url, branch_name, base_sha, executed)

    _run_git(["checkout", "main"], base_path, check=False)
    return pr_url, None, merge_attempted, merge_result, merge_skip_reason


# --- ADR-0040: unattended merge ---------------------------------------------
# A separate trust decision from generation (ADR-0038), gated by its own
# kill switch (scheduled_merge_control.py) and its own circuit breaker
# (scheduled_merge_circuit.py). Every gate below must pass; the first one
# that fails aborts the merge (PR stays open for human/session review, same
# as this repo's behavior before this capability existed) and counts toward
# the circuit breaker -- except is_scheduled_merge_paused itself, which is
# an intentional pause, not a failure.

def _attempt_auto_merge(
    base_path: Path, pr_url: str, branch_name: str, base_sha: str, executed: list[dict[str, Any]]
) -> tuple[bool, str | None, str | None]:
    if is_scheduled_merge_paused(base_path):
        return False, None, "merge_paused"

    if not all(item["execution_triggered"] and item["execution_result_status"] == "success" for item in executed):
        return False, None, "partial_failure_in_wake"

    ok, reason = _diff_within_allowlist(base_path, branch_name)
    if not ok:
        record_merge_gate_failure(reason, base_path)
        return True, "not_merged", reason

    ok, reason = _run_local_validation(base_path)
    if not ok:
        record_merge_gate_failure(reason, base_path)
        return True, "not_merged", reason

    # Re-checked immediately before merging, not just at wake-start -- a wake
    # can take minutes (up to MAX_TASK_EXECUTIONS_PER_WAKE * the CLI timeout),
    # long enough for a concurrent wake (another clone, another session) to
    # land first. The local whole-invocation file lock only protects this one
    # process/clone; this check is the cross-process-safe backstop, verified
    # against GitHub's own state, not a local file.
    current_main = _run_git(["rev-parse", "origin/main"], base_path, check=False).stdout.strip()
    _run_git(["fetch", "origin", "main"], base_path, check=False)
    latest_main = _run_git(["rev-parse", "origin/main"], base_path, check=False).stdout.strip()
    if latest_main and latest_main != base_sha:
        record_merge_gate_failure("stale_base_abort", base_path)
        return True, "not_merged", "stale_base_abort"
    del current_main  # only fetched to force a real network round-trip above

    ok, reason = _poll_ci_green(base_path, pr_url)
    if not ok:
        record_merge_gate_failure(reason, base_path)
        return True, "not_merged", reason

    merge_result = subprocess.run(
        ["gh", "pr", "merge", pr_url, "--squash", "--delete-branch"],
        cwd=base_path,
        capture_output=True,
        text=True,
    )
    if merge_result.returncode != 0:
        record_merge_gate_failure("merge_command_failed", base_path)
        return True, "not_merged", f"merge_command_failed:{merge_result.stderr.strip()[:200]}"

    record_merge_gate_success(base_path)
    return True, "merged", None


def _diff_within_allowlist(base_path: Path, branch_name: str) -> tuple[bool, str]:
    result = _run_git(["diff", "--name-only", f"main...{branch_name}"], base_path, check=False)
    if result.returncode != 0:
        return False, "allowlist_diff_check_failed"
    changed = [line for line in result.stdout.splitlines() if line.strip()]
    for path in changed:
        if not any(path == allowed or path.startswith(allowed + "/") for allowed in _TRACKED_RUNTIME_PATHS):
            return False, f"diff_outside_allowlist:{path}"
    return True, ""


def _run_local_validation(base_path: Path) -> tuple[bool, str]:
    pytest_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=base_path, capture_output=True, text=True
    )
    if pytest_result.returncode != 0:
        return False, "local_pytest_failed"
    validate_result = subprocess.run(
        [sys.executable, "system/scripts/validate_all.py"], cwd=base_path, capture_output=True, text=True
    )
    if validate_result.returncode != 0:
        return False, "local_validate_all_failed"
    return True, ""


def _poll_ci_green(base_path: Path, pr_url: str) -> tuple[bool, str]:
    deadline = time.monotonic() + _CI_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["gh", "pr", "checks", pr_url, "--json", "state"],
            cwd=base_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                checks = json.loads(result.stdout)
            except json.JSONDecodeError:
                checks = []
            states = [str(c.get("state", "")).upper() for c in checks if isinstance(c, dict)]
            if states and all(state in {"SUCCESS", "SKIPPED", "NEUTRAL"} for state in states):
                return True, ""
            if any(state in {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT"} for state in states):
                return False, "ci_failed"
        time.sleep(_CI_POLL_INTERVAL_SECONDS)
    return False, "ci_check_timeout"


def _commit_message(executed: list[dict[str, Any]]) -> str:
    lines = ["Scheduled execution (Level 3b, unattended)", ""]
    for item in executed:
        lines.append(f"- {item['business_id']}/{item['role_id']}/{item['task_id']}: {item['execution_result_status']}")
    lines += ["", "May be auto-merged per ADR-0040's gate; if not, opened for human/session review like every other PR in this repo."]
    return "\n".join(lines)


def _pr_body(executed: list[dict[str, Any]]) -> str:
    lines = ["## Scheduled execution run", "", "Ran unattended via Level 3b (ADR-0038). May be auto-merged per ADR-0040's gate.", "", "| scope | outcome | authorization |", "|---|---|---|"]
    for item in executed:
        lines.append(f"| {item['business_id']}/{item['role_id']}/{item['task_id']} | {item['execution_result_status']} | {item['authorization_source']} |")
    return "\n".join(lines)


# --- Audit trail (local only, gitignored -- see .gitignore) ----------------

def _write_audit(
    started_at: str,
    finished_at: str,
    kill_switch_engaged: bool,
    skipped_overlap: bool,
    candidates_considered: int,
    executed: list[dict[str, Any]],
    base_path: Path,
    *,
    pr_url: str | None = None,
    pr_skip_reason: str | None = None,
    merge_attempted: bool = False,
    merge_result: str | None = None,
    merge_skip_reason: str | None = None,
) -> Path:
    audit_dir = base_path / "system" / "runtime" / "scheduler" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "started_at": started_at,
        "finished_at": finished_at,
        "kill_switch_engaged": kill_switch_engaged,
        "skipped_overlap": skipped_overlap,
        "candidates_considered": candidates_considered,
        "executed": executed,
        "pr_url": pr_url,
        "pr_skip_reason": pr_skip_reason,
        "merge_attempted": merge_attempted,
        "merge_result": merge_result,
        "merge_skip_reason": merge_skip_reason,
    }
    run_key = started_at.replace(":", "").replace("-", "").replace("+", "").replace(".", "")
    run_path = audit_dir / f"{run_key}.json"
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    run_path.write_text(text, encoding="utf-8")
    (audit_dir / f"{run_key}.md").write_text(_markdown(payload), encoding="utf-8")
    (audit_dir / "latest.json").write_text(text, encoding="utf-8")
    (audit_dir / "latest.md").write_text(_markdown(payload), encoding="utf-8")
    return run_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# SCHEDULED_EXECUTION_RUN",
        "",
        f"started_at: {payload['started_at']}",
        f"finished_at: {payload['finished_at']}",
        f"kill_switch_engaged: {str(payload['kill_switch_engaged']).lower()}",
        f"skipped_overlap: {str(payload['skipped_overlap']).lower()}",
        f"candidates_considered: {payload['candidates_considered']}",
        f"pr_url: {payload.get('pr_url') or ''}",
        f"pr_skip_reason: {payload.get('pr_skip_reason') or ''}",
        f"merge_attempted: {str(payload.get('merge_attempted')).lower()}",
        f"merge_result: {payload.get('merge_result') or ''}",
        f"merge_skip_reason: {payload.get('merge_skip_reason') or ''}",
        "",
        "## executed",
    ]
    for item in payload["executed"]:
        lines.append(
            f"- {item['business_id']}/{item['role_id']}/{item['task_id']}: "
            f"{item['execution_result_status']} (authorization={item['authorization_source']})"
        )
    lines.append("")
    return "\n".join(lines)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    argparse.ArgumentParser(description="Run one Level 3b scheduled-execution wake against all eligible candidate tasks.").parse_args()
    summary = run_scheduled_execution(ROOT)
    print(f"kill_switch_engaged={str(summary.kill_switch_engaged).lower()}")
    print(f"skipped_overlap={str(summary.skipped_overlap).lower()}")
    print(f"candidates_considered={summary.candidates_considered}")
    print(f"executed={len(summary.executed)}")
    print(f"pr_url={summary.pr_url or ''}")
    print(f"pr_skip_reason={summary.pr_skip_reason or ''}")
    print(f"merge_attempted={str(summary.merge_attempted).lower()}")
    print(f"merge_result={summary.merge_result or ''}")
    print(f"merge_skip_reason={summary.merge_skip_reason or ''}")
    print(f"audit_path={summary.audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
