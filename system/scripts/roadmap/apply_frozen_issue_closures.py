from __future__ import annotations

import argparse
import json
import subprocess
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


def _load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _close_issue(issue_number: int, state_reason: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", "issue", "close", str(issue_number), "--reason", state_reason],
        capture_output=True,
        text=True,
        check=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply controlled frozen issue closures.")
    parser.add_argument("--apply", action="store_true", help="Actually close eligible issues on GitHub.")
    args = parser.parse_args(argv)

    root = ROOT
    plan_path = root / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json"
    if not plan_path.exists():
        print(f"missing closure plan: {plan_path}")
        return 1
    plan = _load_plan(plan_path)

    closed: list[int] = []
    close_ready: list[int] = []
    deferred: list[int] = []
    for item in plan.get("issues", []):
        issue_number = item["issue_number"]
        eligible = item.get("github_action_recommended") == "close" and bool(item.get("safe_to_apply"))
        if not eligible:
            deferred.append(issue_number)
            continue
        close_ready.append(issue_number)
        if not args.apply:
            continue
        result = _close_issue(issue_number, item.get("state_reason_if_closed") or "completed")
        if result.returncode != 0:
            print(f"failed to close issue #{issue_number}")
            print(result.stderr.strip())
            return result.returncode
        closed.append(issue_number)

    print(f"dry_run={str(not args.apply).lower()}")
    print(f"close_ready_count={len(close_ready)}")
    print(f"closed_count={len(closed)}")
    print(f"deferred_count={len(deferred)}")
    if close_ready:
        print("close_ready_issues=" + ",".join(str(number) for number in close_ready))
    if closed:
        print("closed_issues=" + ",".join(str(number) for number in closed))
    if deferred:
        print("deferred_issues=" + ",".join(str(number) for number in deferred))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
