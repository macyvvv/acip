from __future__ import annotations

from pathlib import Path

from system.orchestrator.implementation_planner import ImplementationPlanner
from system.orchestrator.specification_generator import ImplementationSpecification


def test_implementation_planner_generates_plan(tmp_path: Path) -> None:
    base_path = tmp_path
    (base_path / "solution" / "implementation").mkdir(parents=True)
    (base_path / "workers").mkdir(exist_ok=True)
    (base_path / "workers" / "registry.yaml").write_text(
        "workers:\n  Codex:\n    capability: [repository_implementation, validation_execution]\n    allowed_actions: [implement, validate]\n    prohibited_actions: [approve, deploy, push_directly_to_main]\n    validation_responsibility: [run_repository_validation, report_validation_results]\n    output_contract: system/orchestrator/output_contract.py\n  ChatGPT:\n    capability: [architecture_review, prompt_generation, review_package_authoring]\n    allowed_actions: [design, review, specify]\n    prohibited_actions: [execute_code, mutate_repository]\n    validation_responsibility: [define_validation_scope, review_validation_results]\n    output_contract: system/orchestrator/output_contract.py\n  Human:\n    capability: [approval, strategy, capital_allocation]\n    allowed_actions: [approve, reject, reprioritize]\n    prohibited_actions: [implementation, automated_execution]\n    validation_responsibility: [approve_validation_scope, accept_risk]\n    output_contract: system/orchestrator/output_contract.py\n  GitHub Actions:\n    capability: [ci_execution, repository_validation]\n    allowed_actions: [run_workflow, collect_logs, publish_artifacts]\n    prohibited_actions: [edit_code, bypass_review]\n    validation_responsibility: [execute_validate_all, persist_validation_artifacts]\n    output_contract: system/orchestrator/output_contract.py\n",
        encoding="utf-8",
    )
    specification = ImplementationSpecification(
        spec_id="SPEC-REQ-0001",
        title="Specification for build",
        architecture_option_id="ARCH-REQ-0001",
        implementation_spec="Implement build",
        file_changeset=("a.py",),
        validation=("python system/scripts/validate_all.py",),
        rollback=("Revert a.py",),
        worker_instructions=("Keep the specification deterministic.",),
        specs_reference=("specs/EP-0139",),
    )
    planner = ImplementationPlanner(base_path)
    plan = planner.plan(specification)
    assert plan.worker_candidate == "Codex"
    assert plan.execution_request.worker_assignment == "Codex"
    assert plan.approval_required is False
