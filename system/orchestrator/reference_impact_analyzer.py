from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ReferenceImpact:
    path: str
    impact: str


class ReferenceImpactAnalyzer:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def analyze(self) -> tuple[ReferenceImpact, ...]:
        impacts = (
            ReferenceImpact(path='docs/', impact='low'),
            ReferenceImpact(path='system/runtime/', impact='low'),
            ReferenceImpact(path='packs/', impact='low'),
        )
        runtime_dir = self.base_path / 'runtime' / 'root_hygiene'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / 'reference_impact.json').write_text(json.dumps([impact.__dict__ for impact in impacts], indent=2), encoding='utf-8')
        return impacts
