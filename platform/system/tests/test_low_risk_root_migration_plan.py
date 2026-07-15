from __future__ import annotations

import json
from pathlib import Path


def test_low_risk_root_migration_plan_exists() -> None:
    payload = json.loads(Path('platform/system/runtime/root_hygiene/low_risk_root_migration_plan.json').read_text(encoding='utf-8'))
    assert payload['approval_gate'] == 'required before any file move'
    assert payload['actual_migration_executed'] is False
