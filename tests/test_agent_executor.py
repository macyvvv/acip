from pathlib import Path

from orchestrator.agent_executor import run_agent_executor
from orchestrator.dispatcher import Dispatcher
from orchestrator.result import Result
from orchestrator.task import Task
from orchestrator.worker import Worker


class EchoWorker(Worker):
    def execute(self, task: Task, context):
        return Result(artifacts=[task.artifact], review_notes=["ok"])


def _write_state(root: Path) -> None:
    (root / "basis").mkdir()
    (root / "docs" / "current").mkdir(parents=True)
    (root / "orchestrator").mkdir()
    (root / "basis" / "REPOSITORY_CONVENTIONS.md").write_text("repo conventions", encoding="utf-8")
    (root / "orchestrator" / "ARCHITECTURE.md").write_text("architecture", encoding="utf-8")
    (root / "orchestrator" / "ADR-0001.md").write_text("adr", encoding="utf-8")
    (root / "orchestrator" / "WBS.md").write_text("wbs", encoding="utf-8")
    (root / "docs" / "current" / "CURRENT_STATE.md").write_text(
        """# CURRENT_STATE

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

Objective

---

# Current Epic

EP-002 Canonical Asset Production

---

# Current Task

Task

---

# Current Next Action

Artifact
CA-0001

Owner
ChatGPT

Definition of Done
Done
        """,
        encoding="utf-8",
    )
    (root / "docs" / "current" / "QUEUE_STATE.md").write_text(
        "# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-0108\nnext_ep: EP-0109\n",
        encoding="utf-8",
    )
    (root / "docs" / "current" / "WORKER_STATE.md").write_text(
        "# WORKER_STATE\n\nworker_name: Codex\ncurrent_ep: EP-0108\nqueue_status: READY\n",
        encoding="utf-8",
    )


def test_run_agent_executor(tmp_path: Path) -> None:
    _write_state(tmp_path)
    dispatcher = Dispatcher(workers={"ChatGPT": EchoWorker()})

    summary = run_agent_executor(dispatcher, base_path=str(tmp_path))

    assert summary.task.artifact == "CA-0001"
    assert summary.review_package.artifacts == ["CA-0001"]
