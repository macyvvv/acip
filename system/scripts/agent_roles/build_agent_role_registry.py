from __future__ import annotations

import json
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.core.agent_role_registry import build_agent_role_registry


def main() -> int:
    runtime_dir = ROOT / "system" / "runtime" / "agent_roles"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    registry = build_agent_role_registry(ROOT)
    json_path = runtime_dir / "agent_role_registry.json"
    md_path = runtime_dir / "agent_role_registry.md"
    json_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# AGENT_ROLE_REGISTRY",
        "",
        "## Summary",
        f"- Role count: {registry['summary']['role_count']}",
        f"- claude_invocation roles: {registry['summary']['claude_invocation_count']}",
        f"- pluggable_provider roles: {registry['summary']['pluggable_provider_count']}",
        f"- Missing prompt templates: {registry['summary']['missing_prompt_templates'] or 'none'}",
        f"- Missing output contracts: {registry['summary']['missing_output_contracts'] or 'none'}",
        "",
        "## Roles",
    ]
    for item in registry["roles"]:
        lines.append(f"- `{item['role_id']}` ({item['role_kind']}, model_capability={item['model_capability']}): {item['display_name']}")
        if item["prompt_template_path"]:
            lines.append(f"  - prompt_template_path: {item['prompt_template_path']} (exists={str(item['prompt_template_path_exists']).lower()})")
        lines.append(f"  - output_contract_path: {item['output_contract_path']} (exists={str(item['output_contract_path_exists']).lower()})")
        lines.append(f"  - allowed_tools: {list(item['allowed_tools'])}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("agent role registry built")
    print(f"json_path={json_path}")
    print(f"md_path={md_path}")
    print(f"role_count={registry['summary']['role_count']}")
    print(f"missing_prompt_templates={registry['summary']['missing_prompt_templates']}")
    print(f"missing_output_contracts={registry['summary']['missing_output_contracts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
