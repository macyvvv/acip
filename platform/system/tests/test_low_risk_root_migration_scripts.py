from __future__ import annotations

from pathlib import Path


def test_low_risk_root_migration_scripts_exist() -> None:
    execute = Path('platform/system/scripts/root_hygiene/execute_low_risk_root_migration.sh').read_text(encoding='utf-8')
    rollback = Path('platform/system/scripts/root_hygiene/rollback_low_risk_root_migration.sh').read_text(encoding='utf-8')
    assert 'APPROVAL_FLAG=true' in execute
    assert 'DRY_RUN' in execute
    assert 'mv %q %q' in rollback
    assert 'medium-risk' not in execute
    assert 'high-risk' not in execute
