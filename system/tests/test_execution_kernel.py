from pathlib import Path

from system.orchestrator.dispatcher import Dispatcher
from system.orchestrator.execution_kernel import ExecutionKernel
from system.orchestrator.result import Result
from system.orchestrator.task import Task
from system.orchestrator.worker import Worker


class EchoWorker(Worker):
    def execute(self, task: Task, context):
        return Result(artifacts=[task.artifact], review_notes=["kernel ok"])


def _write_minimal_repo(root: Path) -> None:
    (root / "basis").mkdir()
    (root / "docs" / "current").mkdir(parents=True)
    (root / "docs" / "ep").mkdir(parents=True)
    (root / "orchestrator").mkdir()
    (root / "scripts").mkdir()
    (root / "specs" / "EP-0112").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "basis" / "REPOSITORY_CONVENTIONS.md").write_text("conventions", encoding="utf-8")
    (root / "orchestrator" / "ARCHITECTURE.md").write_text("arch", encoding="utf-8")
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

M1

---

# Current Phase

EP-0112

---

# Current Objective

Objective

---

# Current Epic

EP-0112

---

# Current Task

Task

---

# Current Next Action

Artifact
artifact

Owner
ChatGPT

Definition of Done
done
""",
        encoding="utf-8",
    )
    (root / "docs" / "current" / "QUEUE_STATE.md").write_text(
        "# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-0111\nnext_ep: EP-0112\n",
        encoding="utf-8",
    )
    (root / "docs" / "current" / "WORKER_STATE.md").write_text(
        "# WORKER_STATE\n\nworker_name: Codex\ncurrent_ep: EP-0111\nqueue_status: READY\n",
        encoding="utf-8",
    )
    (root / "workers").mkdir()
    (root / "workers" / "registry.yaml").write_text(
        """workers:
  Codex:
    capability: [repository_implementation]
    allowed_actions: [implement, validate]
    prohibited_actions: [approve]
    validation_responsibility: [run_repository_validation]
    output_contract: system/orchestrator/output_contract.py
  ChatGPT:
    capability: [architecture_review]
    allowed_actions: [design, review]
    prohibited_actions: [execute_code]
    validation_responsibility: [define_validation_scope]
    output_contract: system/orchestrator/output_contract.py
  Human:
    capability: [approval]
    allowed_actions: [approve]
    prohibited_actions: [implement]
    validation_responsibility: [accept_risk]
    output_contract: system/orchestrator/output_contract.py
  GitHub Actions:
    capability: [ci_execution]
    allowed_actions: [run_workflow]
    prohibited_actions: [edit_code]
    validation_responsibility: [execute_validate_all]
    output_contract: system/orchestrator/output_contract.py
""",
        encoding="utf-8",
    )
    (root / "scripts" / "validate_ep_0112.py").write_text("print('ok')", encoding="utf-8")


def test_execution_kernel_runs_cycle(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    kernel = ExecutionKernel(Dispatcher(workers={"ChatGPT": EchoWorker()}), base_path=tmp_path)

    plan = kernel.plan()
    assignment = kernel.worker_assignment()
    cycle = kernel.run_autonomous_cycle()

    assert plan.next_ep == "EP-0112"
    assert assignment == "Codex"
    assert cycle.success is True
    assert "artifact" in cycle.next_action.lower()
