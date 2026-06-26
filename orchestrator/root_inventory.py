from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RootInventoryEntry:
    path: str
    kind: str
    classification: str


class RootInventory:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def classify(self) -> tuple[RootInventoryEntry, ...]:
        entries: list[RootInventoryEntry] = []
        for path in sorted(self.base_path.iterdir(), key=lambda item: item.name):
            if path.name.startswith('.') and path.name not in {'.github', '.gitignore'}:
                continue
            if path.name in {'README.md', 'AGENTS.md', 'docs', 'packs', 'queue', 'runtime', 'scripts', 'specs', 'orchestrator', 'tests', 'contracts'}:
                classification = 'allowed'
            elif path.is_dir():
                classification = 'review'
            else:
                classification = 'review'
            entries.append(RootInventoryEntry(path=path.name, kind='dir' if path.is_dir() else 'file', classification=classification))
        return tuple(entries)
