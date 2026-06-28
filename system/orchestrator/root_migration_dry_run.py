from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.reference_impact_analyzer import ReferenceImpactAnalyzer
from system.orchestrator.root_inventory import RootInventory
from system.orchestrator.target_layout_contract import TargetLayoutContract


@dataclass(frozen=True)
class RootMigrationDryRunResult:
    inventory_count: int
    impacted_paths: tuple[str, ...]
    approval_required: bool


class RootMigrationDryRun:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self) -> RootMigrationDryRunResult:
        inventory = RootInventory(self.base_path).classify()
        impacts = ReferenceImpactAnalyzer(self.base_path).analyze()
        contract = TargetLayoutContract(root_allowlist=("README.md", "AGENTS.md", "docs/", "packs/", "queue/", "system/runtime/", "system/scripts/", "specs/", "system/orchestrator/", "system/tests/", "contracts/"), migration_policy='dry-run only until approved')
        runtime_dir = self.base_path / 'runtime' / 'root_hygiene'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            'inventory_count': len(inventory),
            'impacted_paths': [impact.path for impact in impacts],
            'approval_required': True,
            'root_allowlist': list(contract.root_allowlist),
        }
        (runtime_dir / 'root_migration_dry_run.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
        return RootMigrationDryRunResult(inventory_count=len(inventory), impacted_paths=tuple(impact.path for impact in impacts), approval_required=True)
