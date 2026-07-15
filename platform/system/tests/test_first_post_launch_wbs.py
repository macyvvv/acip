from __future__ import annotations

import json
from pathlib import Path


def test_first_post_launch_wbs_payload_exists() -> None:
    payload = json.loads(Path('platform/system/runtime/planning/first_post_launch_wbs.json').read_text(encoding='utf-8'))
    assert payload['first_post_objective']
    assert payload['done_condition']


def test_background_system_image_payload_exists() -> None:
    payload = json.loads(Path('platform/system/runtime/planning/background_system_image.json').read_text(encoding='utf-8'))
    assert 'Planning State' in payload['components']
    assert payload['repository_os_dependency'] is True
