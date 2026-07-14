from __future__ import annotations

import json
from pathlib import Path

import pytest

from system.scripts.publishing.finalize_content import (
    FinalizeContentError,
    finalize_content,
    load_finalized_content,
)


def _write_execution_artifact(tmp_path: Path, business_id: str, role_id: str, task_id: str, *, success: bool, stdout: str) -> None:
    path = tmp_path / "system/runtime/business_agents" / business_id / role_id / task_id / "latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"success": success, "stdout": stdout}))


def test_refuses_without_execution_artifact(tmp_path: Path) -> None:
    with pytest.raises(FinalizeContentError):
        finalize_content("text_syndicate", "marketing", "task-0001", "x", "final copy", "macy", tmp_path)


def test_refuses_when_execution_not_successful(tmp_path: Path) -> None:
    _write_execution_artifact(tmp_path, "text_syndicate", "marketing", "task-0001", success=False, stdout="partial draft")
    with pytest.raises(FinalizeContentError):
        finalize_content("text_syndicate", "marketing", "task-0001", "x", "final copy", "macy", tmp_path)


def test_writes_expected_schema(tmp_path: Path) -> None:
    _write_execution_artifact(tmp_path, "text_syndicate", "marketing", "task-0001", success=True, stdout="3 drafts + outline blob")
    path = finalize_content("text_syndicate", "marketing", "task-0001", "x", "the one final tweet", "macy", tmp_path)
    record = json.loads(path.read_text())
    assert record["business_id"] == "text_syndicate"
    assert record["role_id"] == "marketing"
    assert record["task_id"] == "task-0001"
    assert record["platform"] == "x"
    assert record["final_text"] == "the one final tweet"
    assert record["finalized_by"] == "macy"
    assert "source_execution_hash" in record and record["source_execution_hash"]

    loaded = load_finalized_content("text_syndicate", "marketing", "task-0001", "x", tmp_path)
    assert loaded == record


def test_refinalizing_overwrites(tmp_path: Path) -> None:
    _write_execution_artifact(tmp_path, "text_syndicate", "marketing", "task-0001", success=True, stdout="draft blob")
    finalize_content("text_syndicate", "marketing", "task-0001", "x", "first version", "macy", tmp_path)
    finalize_content("text_syndicate", "marketing", "task-0001", "x", "second version", "macy", tmp_path)
    loaded = load_finalized_content("text_syndicate", "marketing", "task-0001", "x", tmp_path)
    assert loaded["final_text"] == "second version"


def test_missing_finalized_content_returns_none(tmp_path: Path) -> None:
    assert load_finalized_content("text_syndicate", "marketing", "task-0001", "x", tmp_path) is None


def test_reply_to_external_id_defaults_to_none(tmp_path: Path) -> None:
    _write_execution_artifact(tmp_path, "text_syndicate", "marketing", "task-0001", success=True, stdout="draft blob")
    path = finalize_content("text_syndicate", "marketing", "task-0001", "x", "standalone post", "macy", tmp_path)
    record = json.loads(path.read_text())
    assert record["reply_to_external_id"] is None


def test_reply_to_external_id_is_stored(tmp_path: Path) -> None:
    _write_execution_artifact(tmp_path, "text_syndicate", "marketing", "task-reply-0001", success=True, stdout="reply candidates blob")
    path = finalize_content(
        "text_syndicate", "marketing", "task-reply-0001", "x", "reply text", "macy", tmp_path,
        reply_to_external_id="1111111111",
    )
    record = json.loads(path.read_text())
    assert record["reply_to_external_id"] == "1111111111"
    loaded = load_finalized_content("text_syndicate", "marketing", "task-reply-0001", "x", tmp_path)
    assert loaded["reply_to_external_id"] == "1111111111"
