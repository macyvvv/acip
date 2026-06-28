from __future__ import annotations

from system.orchestrator.root_migration_approval_gate import RootMigrationApprovalGate


def test_root_migration_approval_gate_blocks_by_default(tmp_path) -> None:
    decision = RootMigrationApprovalGate(tmp_path).decide()
    assert decision.approved is False
