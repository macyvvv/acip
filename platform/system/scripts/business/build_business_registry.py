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

from system.core.business_registry import build_business_registry


def main() -> int:
    runtime_dir = ROOT / "system" / "runtime" / "business"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    registry = build_business_registry(ROOT)
    json_path = runtime_dir / "business_registry.json"
    md_path = runtime_dir / "business_registry.md"
    json_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# BUSINESS_REGISTRY",
        "",
        "## Summary",
        f"- Business count: {registry['summary']['business_count']}",
        f"- Active: {registry['summary']['active_count']}",
        f"- Greenfield: {registry['summary']['greenfield_count']}",
        f"- Dormant: {registry['summary']['dormant_count']}",
        f"- Drifted (active but expected path missing): {registry['summary']['drifted_business_ids'] or 'none'}",
        "",
        "## Businesses",
    ]
    for item in registry["businesses"]:
        lines.append(f"- `{item['business_id']}` ({item['status']}): {item['display_name']}")
        lines.append(f"  - content_root: {item['content_root']} (exists={str(item['content_root_exists']).lower()})")
        lines.append(f"  - product_code_path: {item['product_code_path']} (exists={str(item['product_code_path_exists']).lower()})")
        lines.append(f"  - tracking_issue_numbers: {list(item['tracking_issue_numbers'])}")
        if item["historical_issue_numbers"]:
            lines.append(f"  - historical_issue_numbers: {list(item['historical_issue_numbers'])}")
        lines.append(f"  - notes: {item['notes']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("business registry built")
    print(f"json_path={json_path}")
    print(f"md_path={md_path}")
    print(f"business_count={registry['summary']['business_count']}")
    print(f"drifted_business_ids={registry['summary']['drifted_business_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
