from __future__ import annotations

from pathlib import Path


REQUIRED_REPOSITORY_FILES = [
    "VERSION",
    "graph/repository_graph.json",
    "graph/agent_context_pack.json",
    "system/orchestrator/execution_plan.json",
]


def find_repository_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists() or (candidate / "VERSION").exists():
            return candidate
    raise FileNotFoundError("Could not locate repository root. Run inside the ACIP repository.")


def assert_required_files(root: Path) -> None:
    missing = [rel for rel in REQUIRED_REPOSITORY_FILES if not (root / rel).exists()]
    if missing:
        raise FileNotFoundError("Missing required repository files: " + ", ".join(missing))
