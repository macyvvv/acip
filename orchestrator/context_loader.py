from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orchestrator.constants import (
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
        repository_conventions=_read(root / REPOSITORY_CONVENTIONS_PATH),
        current_state=_read(root / CURRENT_STATE_PATH),
        architecture=_read(root / ARCHITECTURE_PATH),
        adr=_read(root / ADR_PATH),
        wbs=_read(root / WBS_PATH),
    )


def _read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical document: {path}")
    return path.read_text(encoding="utf-8")
