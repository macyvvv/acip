from __future__ import annotations

from orchestrator.root_migration_dry_run import RootMigrationDryRun


def test_root_migration_dry_run_writes_plan(tmp_path) -> None:
    result = RootMigrationDryRun(tmp_path).run()
    assert result.approval_required is True
