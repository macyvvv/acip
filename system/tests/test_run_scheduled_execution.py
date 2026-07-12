from __future__ import annotations

import fcntl
import json
from pathlib import Path

from system.core.business_agent_handoff import write_business_agent_handoff
from system.core.business_agent_task_queue import add_task
from system.core.scheduled_execution_control import pause_scheduled_execution
from system.scripts.business_agent import run_scheduled_execution as scheduler


def _write_pre_approval_policy(tmp_path: Path, business_id: str, role_id: str, **overrides) -> None:
    entry = {
        "policy_id": f"PREAPP-{business_id}-{role_id}",
        "business_id": business_id,
        "role_id": role_id,
        "enabled": True,
        "max_auto_approvals_per_day": 10,
        "max_auto_approvals_per_week": 50,
        "authored_by": "macy",
        "authored_at": "2026-07-12T00:00:00+00:00",
        "reason": "pilot",
    }
    entry.update(overrides)
    path = tmp_path / "system" / "runtime" / "agent_handoff" / "auto_approval_policy.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(path.read_text()) if path.exists() else {"version": 1, "policies": []}
    existing["policies"] = [p for p in existing["policies"] if not (p["business_id"] == business_id and p["role_id"] == role_id)]
    existing["policies"].append(entry)
    path.write_text(json.dumps(existing))


def _seed_candidate(tmp_path: Path, business_id: str, role_id: str, task_id: str, **policy_overrides) -> None:
    write_business_agent_handoff(business_id, role_id, task_id, "desc", tmp_path)
    add_task(business_id, role_id, task_id, "title", tmp_path)
    _write_pre_approval_policy(tmp_path, business_id, role_id, **policy_overrides)


def _init_git_repo(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("seed\n")
    _write_gitignore(tmp_path)
    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=tmp_path, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=tmp_path, check=True)


def _write_gitignore(tmp_path: Path) -> None:
    # Mirrors the real repo's .gitignore for the two things run_scheduled_
    # execution.py itself creates (system/core/file_lock.py's lock file,
    # the scheduler's own audit dir) -- without this, a synthetic test
    # repo has no .gitignore at all, so the runner's own lock file would
    # show up as untracked and spuriously trip the pre-flight dirty check.
    (tmp_path / ".gitignore").write_text("system/runtime/**/*.lock\nsystem/runtime/scheduler/audit/\n")


def _commit_everything(tmp_path: Path, message: str = "seed pre-existing candidate state") -> None:
    # Real production state: a candidate sitting in queue.json is already
    # committed history (Level 1 writes it, a human/session PRs it in) --
    # this must never itself register as "dirty" before a wake starts.
    import subprocess

    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=tmp_path, check=True)


def _fake_successful_run(calls: list[dict]):
    class FakeOutcome:
        success = True
        artifact_path = "irrelevant/for/this/test/latest.json"
        exit_code = 0

    def fake_run(self, *, business_id, role_id, task_id, task_description="", approval_flag=False, dry_run=True):
        calls.append({"business_id": business_id, "role_id": role_id, "task_id": task_id})
        return FakeOutcome()

    return fake_run


# --- find_scheduled_candidates: pure selection logic, no execution -------

def test_no_candidates_when_queue_empty(tmp_path: Path) -> None:
    assert scheduler.find_scheduled_candidates(tmp_path) == []


def test_candidate_without_policy_is_skipped(tmp_path: Path) -> None:
    write_business_agent_handoff("somia", "scenario_writing", "task-0001", "desc", tmp_path)
    add_task("somia", "scenario_writing", "task-0001", "title", tmp_path)
    # deliberately no policy written -- somia has none yet in production either
    assert scheduler.find_scheduled_candidates(tmp_path) == []


def test_pluggable_provider_role_never_selected_even_with_a_policy_entry(tmp_path: Path) -> None:
    # get_execution_pre_approval_policy re-validates role_kind against the
    # live registry and raises for image_generation/video_generation -- the
    # pre-filter must swallow that as "not eligible," not propagate it.
    _seed_candidate(tmp_path, "somia", "image_generation", "task-0001")
    assert scheduler.find_scheduled_candidates(tmp_path) == []


def test_one_task_id_per_business_role_pair_oldest_first(tmp_path: Path) -> None:
    write_business_agent_handoff("kabukicho_survival_map", "marketing", "auto-0004", "desc", tmp_path)
    add_task("kabukicho_survival_map", "marketing", "auto-0004", "title", tmp_path)
    write_business_agent_handoff("kabukicho_survival_map", "marketing", "auto-0005", "desc", tmp_path)
    add_task("kabukicho_survival_map", "marketing", "auto-0005", "title", tmp_path)
    _write_pre_approval_policy(tmp_path, "kabukicho_survival_map", "marketing")

    candidates = scheduler.find_scheduled_candidates(tmp_path)
    assert len(candidates) == 1
    assert candidates[0].task_id == "auto-0004"  # queue.json is append-ordered -- first entry is oldest


def test_capped_at_max_per_wake(tmp_path: Path) -> None:
    for i in range(scheduler.MAX_TASK_EXECUTIONS_PER_WAKE + 3):
        business_id = f"biz-{i}"
        write_business_agent_handoff(business_id, "market_research", "task-0001", "desc", tmp_path)
        add_task(business_id, "market_research", "task-0001", "title", tmp_path)
        _write_pre_approval_policy(tmp_path, business_id, "market_research")

    candidates = scheduler.find_scheduled_candidates(tmp_path)
    assert len(candidates) == scheduler.MAX_TASK_EXECUTIONS_PER_WAKE


# --- run_scheduled_execution: kill switch, execution, failure handling ---

def test_kill_switch_blocks_the_whole_wake(tmp_path: Path, monkeypatch) -> None:
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    pause_scheduled_execution("investigating", "macy", tmp_path)

    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert summary.kill_switch_engaged is True
    assert summary.candidates_considered == 0
    assert summary.executed == []
    assert calls == []


def test_happy_path_executes_and_lands_via_pr(tmp_path: Path, monkeypatch) -> None:
    _init_git_repo(tmp_path)
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    _commit_everything(tmp_path)

    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))

    land_calls: list[tuple] = []

    def fake_land(base_path, run_key, executed):
        land_calls.append((base_path, run_key, executed))
        return "https://github.com/example/pr/1", None

    monkeypatch.setattr(scheduler, "_land_via_pr", fake_land)

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert len(calls) == 1
    assert len(summary.executed) == 1
    assert summary.executed[0]["execution_result_status"] == "success"
    assert summary.pr_url == "https://github.com/example/pr/1"
    assert len(land_calls) == 1  # landing only attempted because something actually executed
    assert Path(summary.audit_path).exists()
    latest = json.loads((tmp_path / "system/runtime/scheduler/audit/latest.json").read_text())
    assert latest["pr_url"] == "https://github.com/example/pr/1"


def test_no_candidates_never_attempts_to_land(tmp_path: Path, monkeypatch) -> None:
    _init_git_repo(tmp_path)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("_land_via_pr must never be called when nothing executed")

    monkeypatch.setattr(scheduler, "_land_via_pr", fail_if_called)

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert summary.executed == []
    assert summary.pr_url is None


def test_one_scope_adapter_failure_does_not_abort_the_wake(tmp_path: Path, monkeypatch) -> None:
    # ApprovedAutonomousExecution._run_business_agent already catches an
    # adapter exception internally and returns a normal "failure" result
    # rather than propagating (confirmed by this test) -- the runner's own
    # loop must still move on to the next scope regardless.
    _init_git_repo(tmp_path)
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    _seed_candidate(tmp_path, "kabukicho_survival_map", "market_research", "task-0001")
    _commit_everything(tmp_path)

    def flaky_run(self, *, business_id, role_id, task_id, task_description="", approval_flag=False, dry_run=True):
        if business_id == "text_syndicate":
            raise RuntimeError("simulated adapter crash")

        class FakeOutcome:
            success = True
            artifact_path = "irrelevant/latest.json"
            exit_code = 0

        return FakeOutcome()

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", flaky_run)
    monkeypatch.setattr(scheduler, "_land_via_pr", lambda base_path, run_key, executed: (None, "test_skip"))

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert len(summary.executed) == 2  # both scopes were attempted despite the first raising
    statuses = {item["business_id"]: item["execution_result_status"] for item in summary.executed}
    assert statuses["text_syndicate"] == "failure"
    assert statuses["kabukicho_survival_map"] == "success"


def test_one_scope_unexpected_exception_above_the_adapter_does_not_abort_the_wake(tmp_path: Path, monkeypatch) -> None:
    # A deeper backstop than the test above: something raising BEFORE it
    # ever reaches ApprovedAutonomousExecution's own internal try/except
    # (e.g. a bug in a layer that isn't already exception-safe) must still
    # be caught by the runner's own loop, not just re-tested coverage of
    # the same inner catch.
    _init_git_repo(tmp_path)
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    _seed_candidate(tmp_path, "kabukicho_survival_map", "market_research", "task-0001")
    _commit_everything(tmp_path)

    real_run = scheduler.ApprovedAutonomousExecution.run

    def flaky_top_level_run(self, *, business_id=None, role_id=None, task_id=None):
        if business_id == "text_syndicate":
            raise RuntimeError("simulated failure above the adapter's own try/except")
        return real_run(self, business_id=business_id, role_id=role_id, task_id=task_id)

    monkeypatch.setattr(scheduler.ApprovedAutonomousExecution, "run", flaky_top_level_run)
    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))
    monkeypatch.setattr(scheduler, "_land_via_pr", lambda base_path, run_key, executed: (None, "test_skip"))

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert len(summary.executed) == 2
    statuses = {item["business_id"]: item["execution_result_status"] for item in summary.executed}
    assert statuses["text_syndicate"] == "runner_exception"
    assert statuses["kabukicho_survival_map"] == "success"
    assert calls == [{"business_id": "kabukicho_survival_map", "role_id": "market_research", "task_id": "task-0001"}]


def test_overlapping_wake_is_skipped_not_double_run(tmp_path: Path, monkeypatch) -> None:
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))

    lock_path = tmp_path / "system" / "runtime" / "scheduler" / "scheduler.lock"
    lock_file_path = Path(str(lock_path) + ".lock")
    lock_file_path.parent.mkdir(parents=True, exist_ok=True)
    held_file = open(lock_file_path, "w")
    try:
        fcntl.flock(held_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # simulate a previous wake still running
        summary = scheduler.run_scheduled_execution(tmp_path)
        assert summary.skipped_overlap is True
        assert summary.executed == []
        assert calls == []  # never even attempted -- the previous (simulated) wake owns this work
    finally:
        fcntl.flock(held_file, fcntl.LOCK_UN)
        held_file.close()


# --- pre-flight dirty-tree guard: checked BEFORE execution, not after ----
# (a real bug: an earlier version checked this only inside _land_via_pr,
# which runs AFTER the wake's own candidates already executed and wrote
# runtime-state files -- so it self-triggered on every real wake with any
# output at all. Confirmed live against production data before the fix.)

def test_dirty_tree_before_the_wake_starts_skips_the_whole_wake_not_just_landing(tmp_path: Path, monkeypatch) -> None:
    # A human's own in-progress, uncommitted work already sitting in the
    # tree BEFORE the wake starts -- must refuse to execute anything at
    # all, not just refuse to land afterward.
    _init_git_repo(tmp_path)
    (tmp_path / "unrelated_in_progress_work.txt").write_text("do not touch me\n")
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")

    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))

    def fail_if_called(*args, **kwargs):
        raise AssertionError("_land_via_pr must never be reached when the tree was already dirty")

    monkeypatch.setattr(scheduler, "_land_via_pr", fail_if_called)

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert summary.executed == []
    assert summary.candidates_considered == 0
    assert summary.pr_skip_reason == "working_tree_dirty_skip_wake"
    assert calls == []  # never even attempted
    assert (tmp_path / "unrelated_in_progress_work.txt").read_text() == "do not touch me\n"


def test_clean_tree_before_the_wake_lets_execution_and_landing_proceed(tmp_path: Path, monkeypatch) -> None:
    # The wake's own output legitimately dirties the tree -- that must
    # never be mistaken for a reason to skip landing.
    _init_git_repo(tmp_path)
    _seed_candidate(tmp_path, "text_syndicate", "market_research", "task-0001")
    _commit_everything(tmp_path)

    calls: list[dict] = []
    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", _fake_successful_run(calls))

    land_calls: list[tuple] = []

    def fake_land(base_path, run_key, executed):
        land_calls.append((base_path, run_key, executed))
        return "https://github.com/example/pr/2", None

    monkeypatch.setattr(scheduler, "_land_via_pr", fake_land)

    summary = scheduler.run_scheduled_execution(tmp_path)
    assert len(calls) == 1
    assert summary.candidates_considered == 1
    assert len(land_calls) == 1
    assert summary.pr_url == "https://github.com/example/pr/2"


# --- _land_via_pr: the only function allowed to shell out to git/gh ------
# (reached only once _run_wake has already confirmed the tree was clean
# before execution -- so by this point, whatever is dirty is exclusively
# this wake's own known-good output; there is nothing left to re-guard.)

def test_land_via_pr_commits_only_the_known_runtime_paths(tmp_path: Path, monkeypatch) -> None:
    import subprocess

    bare_origin = tmp_path / "bare_origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare_origin)], check=True)

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    subprocess.run(["git", "remote", "add", "origin", str(bare_origin)], cwd=repo, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo, check=True)

    (repo / "system" / "runtime" / "business_agent_tasks").mkdir(parents=True)
    (repo / "system" / "runtime" / "business_agent_tasks" / "queue.json").write_text('{"fake": "queue update"}')
    # A file outside the known runtime paths must never be swept in, even
    # if present and modified -- only the explicit allowlist is `git add`ed.
    (repo / "README.md").write_text("modified, not a runtime path\n")

    real_subprocess_run = subprocess.run  # scheduler.subprocess IS this same module object --
    # patching its .run would also intercept _run_git's own internal calls,
    # so the fake must dispatch by command name, not replace wholesale.

    def dispatching_run(cmd, *args, **kwargs):
        if cmd[0] == "gh":
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="https://github.com/example/pr/3\n", stderr="")
        return real_subprocess_run(cmd, *args, **kwargs)

    monkeypatch.setattr(scheduler.subprocess, "run", dispatching_run)

    pr_url, reason = scheduler._land_via_pr(repo, "20260712T000000Z", [])

    assert pr_url == "https://github.com/example/pr/3"
    assert reason is None
    # The commit landed on the scheduler's own branch (never main, never
    # merged) -- check that branch specifically, not whatever HEAD is now.
    log = subprocess.run(
        ["git", "log", "--name-only", "-1", "scheduler/run-20260712T000000Z"], cwd=repo, capture_output=True, text=True
    ).stdout
    assert "queue.json" in log
    assert "README.md" not in log
    # _land_via_pr returns to main afterward; README.md's modification must
    # still be present and uncommitted there -- never touched by landing.
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert branch == "main"
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout
    assert "README.md" in status  # still sitting there, uncommitted
