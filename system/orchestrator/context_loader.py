from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from system.orchestrator.constants import (
    ADR_PATH,
    ARCHITECTURE_PATH,
    CURRENT_STATE_PATH,
    REPOSITORY_CONVENTIONS_PATH,
    WBS_PATH,
)


@dataclass(frozen=True)
class Context:
    repository_conventions: str
    current_state: str
    architecture: str
    adr: str
    wbs: str


def load_context(base_path: str | Path = ".") -> Context:
    root = Path(base_path)
    return Context(
        repository_conventions=_read(_first_existing(root, REPOSITORY_CONVENTIONS_PATH, Path("basis") / "REPOSITORY_CONVENTIONS.md")),
        current_state=_read(_first_existing(root, CURRENT_STATE_PATH, Path("docs") / "current" / "CURRENT_STATE.md")),
        architecture=_read(_first_existing(root, ARCHITECTURE_PATH, Path("orchestrator") / "ARCHITECTURE.md")),
        adr=_read(_first_existing(root, ADR_PATH, Path("orchestrator") / "ADR-0001.md")),
        wbs=_read(_first_existing(root, WBS_PATH, Path("orchestrator") / "WBS.md")),
    )


def _first_existing(root: Path, primary: Path, fallback: Path) -> Path:
    for candidate in (root / primary, root / fallback):
        if candidate.exists():
            return candidate
    return root / primary


def _read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical document: {path}")
    return path.read_text(encoding="utf-8")
