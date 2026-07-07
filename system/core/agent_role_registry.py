from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


@dataclass(frozen=True)
class AgentRoleRecord:
    role_id: str
    display_name: str
    role_kind: str
    prompt_template_path: str | None
    provider_registry_module: str | None
    default_provider: str | None
    output_contract_path: str
    artifact_root_template: str
    allowed_tools: tuple[str, ...]
    model_capability: str
    prompt_template_path_exists: bool
    output_contract_path_exists: bool


_ARTIFACT_ROOT_TEMPLATE = "system/runtime/business_agents/{business_id}/{role_id}/{task_id}/"

_SEED_ROLES: tuple[dict[str, Any], ...] = (
    {
        "role_id": "market_research",
        "display_name": "Market Research",
        "role_kind": "claude_invocation",
        "prompt_template_path": "system/agent_runtime/role_prompts/market_research.md",
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/MARKET_RESEARCH_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob", "WebSearch"),
        "model_capability": "reasoning",
    },
    {
        "role_id": "marketing",
        "display_name": "Marketing",
        "role_kind": "claude_invocation",
        "prompt_template_path": "system/agent_runtime/role_prompts/marketing.md",
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/MARKETING_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob", "WebSearch"),
        "model_capability": "reasoning",
    },
    {
        "role_id": "doc_creation",
        "display_name": "Document Creation",
        "role_kind": "claude_invocation",
        "prompt_template_path": "system/agent_runtime/role_prompts/doc_creation.md",
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/DOC_CREATION_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob"),
        "model_capability": "cost_optimized",
    },
    {
        "role_id": "scenario_writing",
        "display_name": "Scenario Writing",
        "role_kind": "claude_invocation",
        "prompt_template_path": "system/agent_runtime/role_prompts/scenario_writing.md",
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/SCENARIO_WRITING_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob"),
        "model_capability": "reasoning",
    },
    {
        "role_id": "image_generation",
        "display_name": "Image Generation",
        "role_kind": "pluggable_provider",
        "prompt_template_path": None,
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/IMAGE_GENERATION_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob"),
        "model_capability": "cost_optimized",
    },
    {
        "role_id": "video_generation",
        "display_name": "Video Generation",
        "role_kind": "pluggable_provider",
        "prompt_template_path": None,
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/VIDEO_GENERATION_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob"),
        "model_capability": "cost_optimized",
    },
    {
        "role_id": "pdca",
        "display_name": "PDCA",
        "role_kind": "claude_invocation",
        "prompt_template_path": "system/agent_runtime/role_prompts/pdca.md",
        "provider_registry_module": None,
        "default_provider": None,
        "output_contract_path": "contracts/roles/PDCA_OUTPUT_CONTRACT.md",
        "allowed_tools": ("Read", "Grep", "Glob"),
        "model_capability": "reasoning",
    },
)


def _path_exists(root: Path, relative: str | None) -> bool:
    if relative is None:
        return False
    return (root / relative).exists()


def build_agent_role_registry(base_path: Path | None = None) -> dict[str, Any]:
    root = Path(base_path) if base_path is not None else get_repo_root()
    records: list[AgentRoleRecord] = []
    for seed in _SEED_ROLES:
        prompt_template_path_exists = _path_exists(root, seed["prompt_template_path"])
        output_contract_path_exists = _path_exists(root, seed["output_contract_path"])
        records.append(
            AgentRoleRecord(
                role_id=seed["role_id"],
                display_name=seed["display_name"],
                role_kind=seed["role_kind"],
                prompt_template_path=seed["prompt_template_path"],
                provider_registry_module=seed["provider_registry_module"],
                default_provider=seed["default_provider"],
                output_contract_path=seed["output_contract_path"],
                artifact_root_template=_ARTIFACT_ROOT_TEMPLATE,
                allowed_tools=tuple(seed["allowed_tools"]),
                model_capability=seed["model_capability"],
                prompt_template_path_exists=prompt_template_path_exists,
                output_contract_path_exists=output_contract_path_exists,
            )
        )

    missing_prompt_templates = [
        record.role_id
        for record in records
        if record.role_kind == "claude_invocation" and not record.prompt_template_path_exists
    ]
    missing_output_contracts = [record.role_id for record in records if not record.output_contract_path_exists]

    registry = {
        "source_artifacts": [
            "system/core/agent_role_registry.py",
        ],
        "summary": {
            "role_count": len(records),
            "claude_invocation_count": sum(1 for item in records if item.role_kind == "claude_invocation"),
            "pluggable_provider_count": sum(1 for item in records if item.role_kind == "pluggable_provider"),
            "missing_prompt_templates": missing_prompt_templates,
            "missing_output_contracts": missing_output_contracts,
        },
        "roles": [asdict(item) for item in records],
    }
    return registry


def get_role(role_id: str, base_path: Path | None = None) -> AgentRoleRecord | None:
    registry = build_agent_role_registry(base_path)
    for item in registry["roles"]:
        if item["role_id"] == role_id:
            return AgentRoleRecord(**item)
    return None
