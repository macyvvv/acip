from __future__ import annotations

from system.core.agent_role_registry import build_agent_role_registry, get_role


def test_seeds_eight_roles(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    assert registry["summary"]["role_count"] == 8
    role_ids = {item["role_id"] for item in registry["roles"]}
    assert role_ids == {
        "market_research",
        "marketing",
        "doc_creation",
        "scenario_writing",
        "image_generation",
        "video_generation",
        "analytics",
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
    data_fetch_roles = {item["role_id"] for item in registry["roles"] if item["role_kind"] == "data_fetch"}
    assert claude_invocation_roles == {"market_research", "marketing", "doc_creation", "scenario_writing", "pdca"}
    assert pluggable_provider_roles == {"image_generation", "video_generation"}
    assert data_fetch_roles == {"analytics"}


def test_missing_prompt_templates_and_contracts_detected_against_empty_tree(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    assert set(registry["summary"]["missing_prompt_templates"]) == {
        "market_research",
        "marketing",
        "doc_creation",
        "scenario_writing",
        "pdca",
    }
    assert len(registry["summary"]["missing_output_contracts"]) == 8


def test_get_role_returns_none_for_unknown_role(tmp_path):
    assert get_role("not_a_real_role", tmp_path) is None


def test_get_role_returns_record_for_known_role(tmp_path):
    role = get_role("market_research", tmp_path)
    assert role is not None
    assert role.role_kind == "claude_invocation"
    assert role.model_capability == "reasoning"
    assert "WebSearch" in role.allowed_tools


def test_next_roles_seed_chain(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    next_roles_by_id = {item["role_id"]: item["next_roles"] for item in registry["roles"]}
    assert next_roles_by_id["market_research"] == ("marketing",)
    assert next_roles_by_id["marketing"] == ("doc_creation",)
    assert next_roles_by_id["analytics"] == ("pdca",)
    # terminal for Level 1 -- no auto-chain beyond these
    assert next_roles_by_id["doc_creation"] == ()
    assert next_roles_by_id["pdca"] == ()


def test_next_roles_drift_check_detects_unknown_reference(tmp_path, monkeypatch):
    import system.core.agent_role_registry as registry_module

    bad_seeds = tuple(
        {**seed, "next_roles": ("not_a_real_role",)} if seed["role_id"] == "market_research" else seed
        for seed in registry_module._SEED_ROLES
    )
    monkeypatch.setattr(registry_module, "_SEED_ROLES", bad_seeds)
    registry = registry_module.build_agent_role_registry(tmp_path)
    assert "market_research->not_a_real_role" in registry["summary"]["unknown_next_role_references"]


def test_next_roles_no_unknown_references_by_default(tmp_path):
    registry = build_agent_role_registry(tmp_path)
    assert registry["summary"]["unknown_next_role_references"] == []
