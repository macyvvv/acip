from __future__ import annotations

from system.scripts.github.fetch_open_issues import fetch_open_issues, write_open_issue_mirror


def sync_github_issues() -> list[dict]:
    issues = fetch_open_issues()
    print("Fetched issues:", len(issues))
    write_open_issue_mirror(issues)
    return issues


def main() -> None:
    sync_github_issues()


if __name__ == "__main__":
    main()
