from __future__ import annotations

import argparse
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

from app.tools.approval_console_mvp.service import ApprovalConsoleService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the Approval Console MVP.")
    parser.add_argument("--text", action="store_true", help="Force text-mode output.")
    parser.add_argument("--no-gui", action="store_true", help="Disable GUI launch and show text-mode output.")
    return parser


def _print_text_mode(service: ApprovalConsoleService) -> None:
    scopes = service.load_scopes()
    open_issues = ROOT / "system" / "runtime" / "github" / "open_issues.json"
    issue_portfolio = ROOT / "system" / "runtime" / "roadmap" / "issue_portfolio.json"
    frozen_closure_plan = ROOT / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json"
    print("Approval Console MVP (text-mode fallback)")
    print(f"source_open_issues={open_issues}")
    print(f"source_issue_portfolio={issue_portfolio}")
    print(f"source_frozen_closure_plan={frozen_closure_plan}")
    print(
        "source_availability="
        + (
            "available"
            if open_issues.exists() and issue_portfolio.exists() and frozen_closure_plan.exists()
            else "missing"
        )
    )
    print(f"current_now_candidate_count={len(scopes)}")
    target = service._current_execution_target_summary()
    if target:
        print(f"current_execution_target={target}")
        if len(scopes) == 1:
            current = scopes[0]
            print(f"approval_ready={str(current.approval_ready).lower()}")
            print(f"approval_status={current.approval_status}")
    else:
        print(f"zero_candidate_reason={service._zero_candidate_reason() or 'none'}")
    print(service.render_status(scopes[0] if len(scopes) == 1 else None, None))


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
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
    if args.text or args.no_gui:
        _print_text_mode(service)
        return 0
    try:
        from app.tools.approval_console_mvp.gui import launch
    except ModuleNotFoundError as exc:
        if exc.name in {"tkinter", "_tkinter"} or "tkinter" in str(exc).lower():
            print("Tkinter is unavailable in this Python environment; showing text-mode approval console summary instead.")
            _print_text_mode(service)
            return 0
        raise
    launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
