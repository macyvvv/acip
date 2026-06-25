from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ROOT_ALLOWLIST = {
    "README.md",
    "AGENTS.md",
    "VERSION",
    "CHANGELOG.md",
    "ROADMAP.md",
    "PROJECT.md",
    ".gitignore",
    ".github",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "basis",
    "adr",
    "wbs",
    "docs",
    "specs",
    "contracts",
    "scripts",
    "orchestrator",
    "workers",
    "runtime",
    "graph",
    "tests",
    "archive",
    ".env.example",
    "selftest.yml",
}


def validate_repository_layout(report_only: bool = True) -> list[str]:
    violations = []
    for path in ROOT.iterdir():
        if path.name.startswith(".git"):
            continue
        if path.name not in ROOT_ALLOWLIST:
            violations.append(path.name)
    if report_only:
        return sorted(violations)
    if violations:
        raise ValueError(f"Root allowlist violations: {', '.join(sorted(violations))}")
    return []
