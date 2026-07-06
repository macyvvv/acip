from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ROOT_ALLOWLIST = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
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
