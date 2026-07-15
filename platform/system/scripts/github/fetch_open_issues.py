from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in (current.parent, *current.parents):
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError("Repository root not found")


def fetch_open_issues() -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "open", "--json", "number,title,state"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    if not isinstance(data, list):
        raise ValueError("Invalid GH output")
    normalized: list[dict] = []
    for issue in data:
        if not isinstance(issue, dict):
            continue
        normalized_issue = {
            "number": issue.get("number"),
            "title": issue.get("title"),
            "state": str(issue.get("state", "open")).strip().lower(),
        }
        normalized.append(normalized_issue)
    return normalized


def write_open_issue_mirror(issues: list[dict], repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    output_path = root / "system" / "runtime" / "github" / "open_issues.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = root / "system" / "runtime" / "github" / "open_issues.md"
    md_lines = ["# Open Issues Mirror", ""]
    for issue in issues:
        md_lines.append(f"- #{issue.get('number')}: {issue.get('title')} ({issue.get('state')})")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    issues = fetch_open_issues()
    output_path = write_open_issue_mirror(issues)
    print(f"open_issue_count={len(issues)}")
    print(f"output_path={output_path}")


if __name__ == "__main__":
    main()
