from __future__ import annotations

import json
from pathlib import Path

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


def test_analytics_role_real_run_uses_default_dry_run_provider_safely(tmp_path: Path) -> None:
    # Real execution (adapter dry_run=False) still resolves to the analytics
    # role's own default_provider, which is itself "dry_run" until a real
    # platform provider is registered -- so this stays network-free too.
    adapter = BusinessAgentExecutionAdapter(tmp_path)
    result = adapter.run(
        business_id="text_syndicate", role_id="analytics", task_id="task-0001", approval_flag=True, dry_run=False
    )
    assert result.adapter_mode == "execute"
    assert result.success is True
    assert "dry-run" in result.stdout.lower()
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
