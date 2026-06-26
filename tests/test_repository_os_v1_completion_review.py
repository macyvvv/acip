from __future__ import annotations

import json
from pathlib import Path


def test_repository_os_v1_completion_review_contains_core_sections() -> None:
    path = Path("docs/current/REPOSITORY_OS_V1_COMPLETION_REVIEW.md")
    text = path.read_text(encoding="utf-8")
    assert "Repository OS v1" in text
    assert "Repository-native planning" in text


def test_repository_os_v1_review_json_is_machine_readable() -> None:
    payload = json.loads(Path("runtime/reviews/repository_os_v1_completion_review.json").read_text(encoding="utf-8"))
    assert payload["repository_os_v1"] is True
    assert "orchestrator/execution_kernel.py" in payload["entry_points"]
    assert "Root layout remains warn-only." in payload["risks"]
