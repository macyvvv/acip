from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            matches.append(candidate)
    if matches:
        return matches[-1]
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ROOT_ALLOWLIST = {
    "platform",
    "businesses",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "VERSION",
    ".gitignore",
    ".github",
    ".env.example",
    "requirements-dev.txt",
    "selftest.yml",
    "netlify.toml",
    # Transitional compatibility links maintained at root.
    ".system",
    "adr",
    "app",
    "archive",
    "baseline",
    "basis",
    "context",
    "contracts",
    "docs",
    "inbox",
    "knowledge",
    "packs",
    "releases",
    "scripts",
    "somia",
    "specs",
    "system",
    "wbs",
    "web",
}


def validate_repository_layout(report_only: bool = True) -> list[str]:
    violations = []
    for path in ROOT.iterdir():
        if path.name.startswith("."):
            continue
        if path.name not in ROOT_ALLOWLIST:
            violations.append(path.name)
    if report_only:
        return sorted(violations)
    if violations:
        raise ValueError(f"Root allowlist violations: {', '.join(sorted(violations))}")
    return []
