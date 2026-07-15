from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    # Prefer the outermost git root in case a nested .git directory exists.
    git_matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists():
            git_matches.append(candidate)
    if git_matches:
        return git_matches[-1]
    for candidate in current.parents:
        if (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ROOT_ALLOWLIST = {
    "platform",
    "businesses",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "VERSION",
    ".claude",
    ".gitignore",
    ".env",
    ".env.example",
    ".github",
    "requirements-dev.txt",
    "netlify.toml",
    "selftest.yml",
}

TRANSITION_COMPAT_SYMLINKS = {
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
    "scratch",
    "scripts",
    "specs",
    "system",
    "wbs",
    "web",
}

LOCAL_IGNORED = {
    ".DS_Store",
    ".pytest_cache",
    ".venv",
}


def validate_repository_layout(report_only: bool = True) -> list[str]:
    violations = []
    for path in ROOT.iterdir():
        if path.name.startswith(".git"):
            continue
        if path.name in LOCAL_IGNORED:
            continue
        if path.is_symlink() and path.name in TRANSITION_COMPAT_SYMLINKS:
            continue
        if path.name not in ROOT_ALLOWLIST:
            violations.append(path.name)
    if report_only:
        return sorted(violations)
    if violations:
        raise ValueError(f"Root allowlist violations: {', '.join(sorted(violations))}")
    return []
