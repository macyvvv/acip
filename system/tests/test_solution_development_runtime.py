from __future__ import annotations

from pathlib import Path

from system.orchestrator.solution_development_runtime import SolutionDevelopmentRuntime


def _write_minimal_repo(root: Path) -> None:
    (root / "basis").mkdir(exist_ok=True)
    (root / "basis" / "REPOSITORY_CONVENTIONS.md").write_text("conventions", encoding="utf-8")
    (root / "docs" / "current").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "current" / "CURRENT_STATE.md").write_text(
        "# CURRENT_STATE\n\nArtifact\nCA-0001\n\nOwner\nChatGPT\n\nDefinition of Done\nDone\n",
        encoding="utf-8",
    )
    (root / "orchestrator").mkdir(exist_ok=True)
    (root / "orchestrator" / "ARCHITECTURE.md").write_text("architecture", encoding="utf-8")
    (root / "orchestrator" / "ADR-0001.md").write_text("adr", encoding="utf-8")
    (root / "orchestrator" / "WBS.md").write_text("wbs", encoding="utf-8")
    (root / "workers").mkdir(exist_ok=True)
    (root / "workers" / "registry.yaml").write_text(
        "workers:\n  Codex:\n    capability: [repository_implementation, validation_execution]\n    allowed_actions: [implement, validate]\n    prohibited_actions: [approve, deploy, push_directly_to_main]\n    validation_responsibility: [run_repository_validation, report_validation_results]\n    output_contract: system/orchestrator/output_contract.py\n  ChatGPT:\n    capability: [architecture_review, prompt_generation, review_package_authoring]\n    allowed_actions: [design, review, specify]\n    prohibited_actions: [execute_code, mutate_repository]\n    validation_responsibility: [define_validation_scope, review_validation_results]\n    output_contract: system/orchestrator/output_contract.py\n  Human:\n    capability: [approval, strategy, capital_allocation]\n    allowed_actions: [approve, reject, reprioritize]\n    prohibited_actions: [implementation, automated_execution]\n    validation_responsibility: [approve_validation_scope, accept_risk]\n    output_contract: system/orchestrator/output_contract.py\n  GitHub Actions:\n    capability: [ci_execution, repository_validation]\n    allowed_actions: [run_workflow, collect_logs, publish_artifacts]\n    prohibited_actions: [edit_code, bypass_review]\n    validation_responsibility: [execute_validate_all, persist_validation_artifacts]\n    output_contract: system/orchestrator/output_contract.py\n",
        encoding="utf-8",
    )
    (root / "packs" / "PACK-0001-solution-development").mkdir(parents=True, exist_ok=True)
    (root / "packs" / "registry.yaml").write_text(
        "- pack_id: PACK-0001\n"
        "  name: Solution Development Pack\n"
        "  objective: Build a solution development flow\n"
        "  scope: Development lifecycle\n"
        "  ep_range: [EP-0135, EP-0142]\n"
        "  dependencies: []\n"
        "  done_conditions: [pack defined]\n",
        encoding="utf-8",
    )


def test_solution_development_runtime_runs(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    runtime = SolutionDevelopmentRuntime(tmp_path)
    result = runtime.run("Build a repository-native solution development flow")
    assert result.pack_id == "PACK-0001"
    assert result.next_action == "ready"
