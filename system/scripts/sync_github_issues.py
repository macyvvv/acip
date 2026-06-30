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


def sync_github_issues() -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "open", "--json", "number,title,state"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    if not isinstance(data, list):
        raise ValueError("Invalid GH output")
    print("Fetched issues:", len(data))
    normalized = []
    for issue in data:
        if not isinstance(issue, dict):
            continue
        normalized_issue = dict(issue)
        normalized_issue["state"] = str(normalized_issue.get("state", "open")).strip().lower()
        normalized.append(normalized_issue)
    output_path = _repo_root() / "system" / "runtime" / "github" / "open_issues.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    return normalized


def main() -> None:
    sync_github_issues()


if __name__ == "__main__":
    main()
