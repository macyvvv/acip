from __future__ import annotations

from pathlib import Path

from orchestrator.autonomous_runtime import AutonomousRuntime
from orchestrator.dispatcher import Dispatcher
from orchestrator.execution_kernel import ExecutionKernel


def test_autonomous_runtime_runs_and_returns_next_action(tmp_path: Path) -> None:
    (tmp_path / "docs" / "current").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "current" / "QUEUE_STATE.md").write_text(
        "# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-0108\nnext_ep: EP-0109\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "current" / "WORKER_STATE.md").write_text(
        "# WORKER_STATE\n\nworker_name: Codex\ncurrent_ep: EP-0108\nqueue_status: READY\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "current" / "CURRENT_STATE.md").write_text(
        "# CURRENT_STATE\n\nCurrent Next Action\n\nArtifact\nCA-0001\n\nOwner\nChatGPT\n\nDefinition of Done\nDone\n",
        encoding="utf-8",
    )
    (tmp_path / "basis").mkdir(exist_ok=True)
    (tmp_path / "basis" / "REPOSITORY_CONVENTIONS.md").write_text("repo conventions", encoding="utf-8")
    (tmp_path / "orchestrator").mkdir(exist_ok=True)
    (tmp_path / "orchestrator" / "ARCHITECTURE.md").write_text("arch", encoding="utf-8")
    (tmp_path / "orchestrator" / "ADR-0001.md").write_text("adr", encoding="utf-8")
    (tmp_path / "orchestrator" / "WBS.md").write_text("wbs", encoding="utf-8")
    (tmp_path / "workers").mkdir(exist_ok=True)
    (tmp_path / "workers" / "registry.yaml").write_text(
        "workers:\n  Codex:\n    capability: [repository_implementation, validation_execution]\n    allowed_actions: [implement, validate]\n    prohibited_actions: [approve, deploy, push_directly_to_main]\n    validation_responsibility: [run_repository_validation, report_validation_results]\n    output_contract: orchestrator/output_contract.py\n  ChatGPT:\n    capability: [architecture_review, prompt_generation, review_package_authoring]\n    allowed_actions: [design, review, specify]\n    prohibited_actions: [execute_code, mutate_repository]\n    validation_responsibility: [define_validation_scope, review_validation_results]\n    output_contract: orchestrator/output_contract.py\n  Human:\n    capability: [approval, strategy, capital_allocation]\n    allowed_actions: [approve, reject, reprioritize]\n    prohibited_actions: [implementation, automated_execution]\n    validation_responsibility: [approve_validation_scope, accept_risk]\n    output_contract: orchestrator/output_contract.py\n  GitHub Actions:\n    capability: [ci_execution, repository_validation]\n    allowed_actions: [run_workflow, collect_logs, publish_artifacts]\n    prohibited_actions: [edit_code, bypass_review]\n    validation_responsibility: [execute_validate_all, persist_validation_artifacts]\n    output_contract: orchestrator/output_contract.py\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "validate_ep_0112.py").write_text("print('ok')", encoding="utf-8")
    runtime = AutonomousRuntime(ExecutionKernel(dispatcher=Dispatcher({}), base_path=tmp_path), tmp_path)
    result = runtime.run()
    assert result.next_action
