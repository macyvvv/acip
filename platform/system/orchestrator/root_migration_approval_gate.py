from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class RootMigrationApprovalDecision:
    approved: bool
    reason: str


class RootMigrationApprovalGate:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def decide(self, approved: bool = False, reason: str = 'Human approval required before root migration execution') -> RootMigrationApprovalDecision:
        runtime_dir = self.base_path / 'runtime' / 'root_hygiene'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / 'root_migration_approval_gate.json').write_text(json.dumps({'approved': approved, 'reason': reason}, indent=2), encoding='utf-8')
        return RootMigrationApprovalDecision(approved=approved, reason=reason)
