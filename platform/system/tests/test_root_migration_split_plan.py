from __future__ import annotations

import json
from pathlib import Path


def test_root_migration_split_plan_exists() -> None:
    payload = json.loads(Path('platform/system/runtime/root_hygiene/root_migration_split_plan.json').read_text(encoding='utf-8'))
    assert payload['ep_0178_state'] == 'split_required'
    assert 'low_risk' in payload
    assert 'medium_risk' in payload
    assert 'high_risk' in payload
