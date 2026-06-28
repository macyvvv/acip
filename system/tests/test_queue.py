from pathlib import Path

import pytest

from system.orchestrator.queue import state_to_task
from system.orchestrator.state import read_state
from system.orchestrator.task import TaskValidationError


def _write_state(path: Path, next_action: str) -> Path:
    path.write_text(
        f"""# CURRENT_STATE

Version: v1.0

Status: Canonical

---

# Repository

GitHub Account
macyvvv

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

{next_action}
""",
        encoding="utf-8",
    )
    return path


def test_state_to_task_succeeds(tmp_path: Path) -> None:
    state_file = _write_state(
        tmp_path / "CURRENT_STATE.md",
        """Artifact
CA-0001〜CA-0020 Publish Ready

Owner
ChatGPT

Definition of Done
・20件がPublish品質
・Evidence追加済み
・CTA統一
・HumanがGo/No-Goのみ判断可能
""",
    )

    task = state_to_task(read_state(state_file))

    assert task.artifact == "CA-0001〜CA-0020 Publish Ready"
    assert task.owner == "ChatGPT"
    assert "Evidence追加済み" in task.done_conditions


@pytest.mark.parametrize(
    "next_action, message",
    [
        (
            """Owner
ChatGPT

Definition of Done
・20件がPublish品質
""",
            "Artifact",
        ),
        (
            """Artifact
CA-0001〜CA-0020 Publish Ready

Definition of Done
・20件がPublish品質
""",
            "Owner",
        ),
        (
            """Artifact
CA-0001〜CA-0020 Publish Ready

Owner
ChatGPT
""",
            "Done Conditions",
        ),
    ],
)
def test_state_to_task_validation_errors(tmp_path: Path, next_action: str, message: str) -> None:
    state_file = _write_state(tmp_path / "CURRENT_STATE.md", next_action)

    with pytest.raises(TaskValidationError, match=message):
        state_to_task(read_state(state_file))
