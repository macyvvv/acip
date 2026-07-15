from __future__ import annotations

import argparse
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

# ADR-0040's rollback story for a bad unattended merge. Deliberately NOT
# unattended itself: this script prepares the revert (branch, commit, push,
# PR) but never merges it -- a bad auto-merge is exactly the situation that
# calls for a human or an active Claude session looking at the diff before
# anything lands, not another unattended action compounding the first one.


def _run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a revert PR for a bad unattended scheduled-execution merge "
        "(ADR-0040). Never merges the revert itself -- opens a PR for human/session review, "
        "same as every other change in this repo."
    )
    parser.add_argument("merge_commit_sha", help="The SHA of the squash-merge commit on main to revert")
    args = parser.parse_args()

    current_branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False).stdout.strip()
    if current_branch != "main":
        _run(["git", "checkout", "main"])
    _run(["git", "pull", "--ff-only", "origin", "main"])

    branch_name = f"rollback/{args.merge_commit_sha[:12]}"
    _run(["git", "checkout", "-b", branch_name])

    revert = _run(["git", "revert", "--no-edit", "-m", "1", args.merge_commit_sha], check=False)
    if revert.returncode != 0:
        print("revert_failed=true")
        print(revert.stderr.strip())
        _run(["git", "revert", "--abort"], check=False)
        _run(["git", "checkout", "main"], check=False)
        _run(["git", "branch", "-D", branch_name], check=False)
        return 1

    _run(["git", "push", "-u", "origin", branch_name])
    pr = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"Rollback: revert {args.merge_commit_sha[:12]} (ADR-0040 bad auto-merge)",
            "--body",
            f"Reverts {args.merge_commit_sha} -- prepared by rollback_scheduled_merge.py, "
            "never auto-merged. Human/session review required before merging, same as any "
            "other PR in this repo.",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    _run(["git", "checkout", "main"], check=False)
    if pr.returncode != 0:
        print("pr_create_failed=true")
        print(pr.stderr.strip())
        return 1

    print(f"pr_url={pr.stdout.strip()}")
    print("merged=false")
    print("next: review the revert PR and merge it yourself once satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
