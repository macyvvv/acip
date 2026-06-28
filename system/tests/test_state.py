from pathlib import Path

import pytest

from orchestrator.state import StateParseError, read_state


def test_read_state_parses_current_state(tmp_path: Path) -> None:
    state_file = tmp_path / "CURRENT_STATE.md"
    state_file.write_text(
        """# CURRENT_STATE

Version: v1.0

Status: Canonical

---

# Repository

GitHub Account
demo

Repository
acip

Branch
main

---

# Current Milestone

M1 First Revenue

---

# Current Phase

EP-002 Canonical Asset Production

---

# Current Objective

QuestionをCanonical Assetへ変換する。

---

# Current Epic

EP-002 Canonical Asset Production

Status
Doing

---

# Current Task

Canonical Asset CA-0001〜CA-0020を
Publish Ready品質へ引き上げる。

---

# Current Next Action

Artifact
CA-0001〜CA-0020 Publish Ready

Owner
ChatGPT

Definition of Done
・20件がPublish品質
・Evidence追加済み
・CTA統一
・HumanがGo/No-Goのみ判断可能
""",
        encoding="utf-8",
    )

    state = read_state(state_file)

    assert state.repository == "demo/acip"
    assert state.branch == "main"
    assert state.current_milestone == "M1 First Revenue"
    assert state.current_phase == "EP-002 Canonical Asset Production"
    assert state.current_objective == "QuestionをCanonical Assetへ変換する。"
    assert state.current_epic == "EP-002 Canonical Asset Production"
    assert state.current_task == "Canonical Asset CA-0001〜CA-0020を\nPublish Ready品質へ引き上げる。"
    assert "Artifact" in state.next_action


def test_read_state_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        read_state("does-not-exist.md")


def test_read_state_missing_fields_raises(tmp_path: Path) -> None:
    state_file = tmp_path / "CURRENT_STATE.md"
    state_file.write_text(
        """# CURRENT_STATE

# Repository

GitHub Account
demo

Repository
acip
""",
        encoding="utf-8",
    )

    with pytest.raises(StateParseError, match="Missing required state fields"):
        read_state(state_file)
