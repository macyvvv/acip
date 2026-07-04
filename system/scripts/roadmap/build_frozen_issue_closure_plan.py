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

from system.core.frozen_issue_closure_classifier import build_frozen_issue_closure_plan


def main() -> int:
    root = ROOT
    runtime_dir = root / "system" / "runtime" / "roadmap"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    plan = build_frozen_issue_closure_plan(root)
    json_path = runtime_dir / "frozen_issue_closure_plan.json"
    md_path = runtime_dir / "frozen_issue_closure_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FROZEN_ISSUE_CLOSURE_PLAN",
        "",
        "## Summary",
        f"- Frozen issue count: {plan['summary']['frozen_issue_count']}",
        f"- Close-now count: {plan['summary']['close_now_count']}",
        f"- Keep-open count: {plan['summary']['keep_open_count']}",
        f"- Safe-to-apply count: {plan['summary']['safe_to_apply_count']}",
        "",
        "## Issues",
    ]
    for item in plan["issues"]:
        lines.append(
            f"- Issue #{item['issue_number']}: {item['title']} "
            f"(`{item['closure_disposition']}`, `{item['github_action_recommended']}`, "
            f"safe_to_apply={str(item['safe_to_apply']).lower()})"
        )
        if item["classification_reason"]:
            lines.append(f"  - Reason: {item['classification_reason']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("frozen issue closure plan built")
    print(f"json_path={json_path}")
    print(f"md_path={md_path}")
    print(f"close_now_count={plan['summary']['close_now_count']}")
    print(f"safe_to_apply_count={plan['summary']['safe_to_apply_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
