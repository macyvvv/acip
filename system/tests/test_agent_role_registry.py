from __future__ import annotations

from system.core.agent_role_registry import build_agent_role_registry, get_role


def test_seeds_seven_roles(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    assert registry["summary"]["role_count"] == 7
    role_ids = {item["role_id"] for item in registry["roles"]}
    assert role_ids == {
        "market_research",
        "marketing",
        "doc_creation",
        "scenario_writing",
        "image_generation",
        "video_generation",
        "pdca",
    }


def test_role_kind_split_matches_cost_model(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    claude_invocation_roles = {
        item["role_id"] for item in registry["roles"] if item["role_kind"] == "claude_invocation"
    }
    pluggable_provider_roles = {
        item["role_id"] for item in registry["roles"] if item["role_kind"] == "pluggable_provider"
    }
    assert claude_invocation_roles == {"market_research", "marketing", "doc_creation", "scenario_writing", "pdca"}
    assert pluggable_provider_roles == {"image_generation", "video_generation"}


def test_missing_prompt_templates_and_contracts_detected_against_empty_tree(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    assert set(registry["summary"]["missing_prompt_templates"]) == {
        "market_research",
        "marketing",
        "doc_creation",
        "scenario_writing",
        "pdca",
    }
    assert len(registry["summary"]["missing_output_contracts"]) == 7


def test_get_role_returns_none_for_unknown_role(tmp_path):
    assert get_role("not_a_real_role", tmp_path) is None


def test_get_role_returns_record_for_known_role(tmp_path):
    role = get_role("market_research", tmp_path)
    assert role is not None
    assert role.role_kind == "claude_invocation"
    assert role.model_capability == "reasoning"
    assert "WebSearch" in role.allowed_tools
