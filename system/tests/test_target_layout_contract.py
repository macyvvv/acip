from __future__ import annotations

from orchestrator.target_layout_contract import TargetLayoutContract


def test_target_layout_contract_exists() -> None:
    contract = TargetLayoutContract(root_allowlist=('docs/',), migration_policy='dry-run only')
    assert 'docs/' in contract.root_allowlist
