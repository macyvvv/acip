from __future__ import annotations

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

from app.tools.approval_console_mvp.gui import launch
from app.tools.approval_console_mvp.service import ApprovalConsoleService


def main() -> int:
    required_sources = [
        ROOT / "system" / "runtime" / "github" / "open_issues.json",
        ROOT / "system" / "runtime" / "roadmap" / "issue_portfolio.json",
        ROOT / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_sources if not path.exists()]
    if missing:
        print("Missing approval console sources:", ", ".join(missing))
        return 1
    service = ApprovalConsoleService(ROOT)
    scopes = service.load_scopes()
    print("Approval Console MVP startup")
    print(f"source_open_issues={ROOT / 'system' / 'runtime' / 'github' / 'open_issues.json'}")
    print(f"source_issue_portfolio={ROOT / 'system' / 'runtime' / 'roadmap' / 'issue_portfolio.json'}")
    print(f"source_frozen_closure_plan={ROOT / 'system' / 'runtime' / 'roadmap' / 'frozen_issue_closure_plan.json'}")
    print(f"candidate_count={len(scopes)}")
    launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
