from __future__ import annotations

import json
from pathlib import Path


def test_root_migration_materials_exist() -> None:
    path = Path('runtime/root_hygiene/root_migration_materials.json')
    payload = json.loads(path.read_text(encoding='utf-8'))
    assert 'root_entries' in payload
    assert 'migrations' in payload
    assert 'rollback' in payload
