from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from system.orchestrator.business_agent_execution_adapter import (
    BusinessAgentExecutionAdapter,
    BusinessAgentExecutionError,
)


def _seed_prompt_template(tmp_path: Path) -> None:
    template_path = tmp_path / "system" / "agent_runtime" / "role_prompts" / "market_research.md"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(
        "Role for {business_name}.\nContext: {business_context}\nTask: {task}\n",
        encoding="utf-8",
    )


def test_dry_run_does_not_invoke_subprocess(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(
        business_id="text_syndicate",
        role_id="market_research",
        task_id="task-0001",
        task_description="Research impression-driving niches on note.com",
        dry_run=True,
    )
    assert result.adapter_mode == "dry_run"
    assert result.stdout == "dry-run only"
    assert result.exit_code == 0
    assert result.success is True
    assert result.resolved_model == "claude-sonnet-5"  # market_research.model_capability == "reasoning" -> floor 1
    assert "--tools" in result.agent_cli_command
    assert "--permission-mode" in result.agent_cli_command


def test_market_research_role_resolves_reasoning_capability(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(business_id="text_syndicate", role_id="market_research", task_id="task-0001", dry_run=True)
    # market_research.model_capability == "reasoning" -> floor 1 -> cheapest capable is sonnet, not haiku
    assert result.resolved_model == "claude-sonnet-5"
    assert result.model_capability == "reasoning"


def test_real_execution_without_approval_flag_raises(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    with pytest.raises(BusinessAgentExecutionError):
        adapter.run(business_id="text_syndicate", role_id="market_research", task_id="task-0001", dry_run=False, approval_flag=False)


def test_unknown_business_raises(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    with pytest.raises(BusinessAgentExecutionError):
        adapter.run(business_id="not_a_business", role_id="market_research", task_id="task-0001", dry_run=True)


def test_unknown_role_raises(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    with pytest.raises(BusinessAgentExecutionError):
        adapter.run(business_id="text_syndicate", role_id="not_a_role", task_id="task-0001", dry_run=True)


def test_command_hard_restricts_tools_not_just_prompts(tmp_path: Path) -> None:
    # --allowedTools only skips permission prompts for named tools; it does not
    # cap availability. --tools is the actual hard restriction. This test locks
    # in that distinction after a live pilot run surfaced it was built wrong.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    command = adapter._build_command("prompt text", "claude-sonnet-5", ("Read", "Grep", "Glob", "WebSearch"))
    assert "--tools" in command
    tools_index = command.index("--tools")
    assert command[tools_index + 1] == "Read,Grep,Glob,WebSearch"
    assert "--allowedTools" not in command
    assert "--permission-mode" in command
    permission_index = command.index("--permission-mode")
    assert command[permission_index + 1] == "bypassPermissions"


def test_pluggable_provider_role_not_yet_wired(tmp_path: Path) -> None:
    with pytest.raises(BusinessAgentExecutionError):
        BusinessAgentExecutionAdapter(tmp_path).run(
            business_id="somia", role_id="image_generation", task_id="task-0001", dry_run=True
        )


def test_analytics_role_dry_run_never_calls_provider(tmp_path: Path) -> None:
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(business_id="text_syndicate", role_id="analytics", task_id="task-0001", dry_run=True)
    assert result.adapter_mode == "dry_run"
    assert result.stdout == "dry-run only"
    assert result.success is True


def test_analytics_role_real_run_uses_default_git_activity_provider_safely(tmp_path: Path) -> None:
    # Real execution (adapter dry_run=False) still resolves to the analytics
    # role's own default_provider -- switched 2026-07-15 from "dry_run" to
    # "git_activity" (real, credential-free, safe to run any time) so a real
    # run produces at least some real signal. text_syndicate's content_root
    # (also set 2026-07-15, per this business's own first real PDCA cycle's
    # recommendation) is a real path in this actual repo's git history, so
    # git_activity measures real (if business-agent-generated, not
    # human-authored) commit cadence -- still network-free, still safe,
    # just no longer "nothing to measure."
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(
        business_id="text_syndicate", role_id="analytics", task_id="task-0001", approval_flag=True, dry_run=False
    )
    assert result.adapter_mode == "execute"
    assert result.success is True
    assert "repository-activity proxy" in result.stdout.lower()
    kpi_path = tmp_path / "system" / "runtime" / "knowledge" / "kpi.json"
    assert kpi_path.exists()
    kpi = json.loads(kpi_path.read_text(encoding="utf-8"))
    assert kpi["business_agent_stats"]["text_syndicate:analytics"]["runs"] == 1


def test_artifact_written_to_business_agents_namespace(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(business_id="text_syndicate", role_id="market_research", task_id="task-0001", dry_run=True)
    artifact_path = tmp_path / "system" / "runtime" / "business_agents" / "text_syndicate" / "market_research" / "task-0001" / "latest.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["business_id"] == "text_syndicate"
    assert payload["role_id"] == "market_research"
    # zero collision with the existing repo-dev execution namespace
    assert not (tmp_path / "system" / "runtime" / "local_execution").exists()


def test_exit_zero_session_limit_notice_is_not_success(tmp_path: Path) -> None:
    # ADR-0038's first real Level 3b wake found: `claude -p` can exit 0 while
    # printing only a session/usage-limit notice, no real content -- exit
    # code alone must not be trusted as the success signal.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    fake_completed = subprocess.CompletedProcess(
        args=["claude"], returncode=0, stdout="You've hit your session limit · resets 10:20pm (Asia/Tokyo)\n", stderr=""
    )
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.exit_code == 0
    assert result.success is False
    assert result.failure_reason == "cli_notice:session_limit"


def test_empty_stdout_on_real_run_is_not_success(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    fake_completed = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout="", stderr="")
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is False
    assert result.failure_reason == "empty_stdout"


def test_long_real_content_mentioning_rate_limits_still_succeeds(tmp_path: Path) -> None:
    # The failure-notice check must not false-positive on legitimate,
    # substantial content that happens to discuss rate limits as a topic --
    # bounded by length, not just substring match.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    long_content = "A detailed analysis of API rate limit strategies. " * 20
    assert len(long_content) > 500
    fake_completed = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout=long_content, stderr="")
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is True
    assert result.failure_reason is None


def test_leaked_artifact_header_in_stdout_is_not_success(tmp_path: Path) -> None:
    # Observed live (kabukicho_survival_map/doc_creation/auto-0007,
    # 2026-07-17): a role echoed this adapter's own "# BUSINESS_AGENT_
    # EXECUTION" latest.md template -- for a *different* task_id -- into its
    # generated stdout, almost certainly copied from a past task's latest.md
    # fed back in as prompt context. That artifact was still recorded
    # success=true; exit_code/emptiness checks alone cannot catch this.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    contaminated = (
        "Perfect! Now I have the pattern. Let me draft the document.\n\n"
        "# BUSINESS_AGENT_EXECUTION\n\n"
        "business_id: kabukicho_survival_map\n"
        "role_id: marketing\n"
        "task_id: auto-0009\n"
    )
    fake_completed = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout=contaminated, stderr="")
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is False
    assert result.failure_reason == "artifact_header_leaked_into_stdout"


def test_mismatched_task_id_line_in_stdout_is_not_success(tmp_path: Path) -> None:
    # Same failure shape as above, but without the header marker itself --
    # a bare "task_id: <other>" line leaking in is enough of a signal on
    # its own.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    contaminated = "Some generated content.\ntask_id: some-other-task\nMore content.\n"
    fake_completed = subprocess.CompletedProcess(args=["claude"], returncode=0, stdout=contaminated, stderr="")
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is False
    assert result.failure_reason == "mismatched_task_id_in_stdout:some-other-task"


def test_matching_task_id_line_in_stdout_still_succeeds(tmp_path: Path) -> None:
    # A "task_id: <same id>" line is not contamination -- must not
    # false-positive on legitimate content that happens to mention it.
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    fake_completed = subprocess.CompletedProcess(
        args=["claude"], returncode=0, stdout="Some content.\ntask_id: task-0001\nMore content.\n", stderr=""
    )
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is True
    assert result.failure_reason is None


def test_nonzero_exit_still_fails_regardless_of_stdout(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    fake_completed = subprocess.CompletedProcess(args=["claude"], returncode=1, stdout="ordinary content", stderr="boom")
    with patch.object(BusinessAgentExecutionAdapter, "_run_command", return_value=fake_completed):
        result = adapter.run(
            business_id="text_syndicate", role_id="market_research", task_id="task-0001", approval_flag=True, dry_run=False
        )
    assert result.success is False
    assert result.failure_reason is None  # exit_code alone explains this one


def test_dry_run_never_flagged_as_failure_notice(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(business_id="text_syndicate", role_id="market_research", task_id="task-0001", dry_run=True)
    assert result.success is True
    assert result.failure_reason is None


def test_kpi_updated_on_run(tmp_path: Path) -> None:
    _seed_prompt_template(tmp_path)
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    adapter.run(business_id="text_syndicate", role_id="market_research", task_id="task-0001", dry_run=True)
    kpi_path = tmp_path / "system" / "runtime" / "knowledge" / "kpi.json"
    assert kpi_path.exists()
    kpi = json.loads(kpi_path.read_text(encoding="utf-8"))
    assert kpi["business_agent_stats"]["text_syndicate:market_research"]["runs"] == 1
    # existing repo-dev KPI fields are untouched by this path
    assert kpi["total_runs"] == 0
