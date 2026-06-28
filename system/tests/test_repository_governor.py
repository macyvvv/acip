from __future__ import annotations

from pathlib import Path

from system.orchestrator.repository_governor import RepositoryGovernor


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
    (root / "docs" / "current" / "QUEUE_STATE.md").write_text(
        "# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-0108\nnext_ep: EP-0109\n",
        encoding="utf-8",
    )
    (root / "docs" / "current" / "VALIDATION_STATE.md").write_text(
        "# VALIDATION_STATE\n\nlast_validation_status: success\nlast_validation_command: python system/scripts/validate_all.py\nlast_validation_report_json: system/runtime/validation/validation_report.json\nlast_validation_report_md: system/runtime/validation/VALIDATION_REPORT.md\nvalidation_owner: Codex\nrerun_required_when:\n  - any validation step fails\nhuman_rerun_policy: Human reruns validation only when repository outputs changed.\nrelation_to_worker_output_contract: Validation state is a repository-level summary.\n",
        encoding="utf-8",
    )
    (root / "workers").mkdir(exist_ok=True)
    (root / "workers" / "registry.yaml").write_text(
        "workers:\n  Codex:\n    capability: [repository_implementation, validation_execution]\n    allowed_actions: [implement, validate]\n    prohibited_actions: [approve]\n    validation_responsibility: [run_repository_validation]\n    output_contract: system/orchestrator/output_contract.py\n  ChatGPT:\n    capability: [review_package_authoring]\n    allowed_actions: [review]\n    prohibited_actions: [execute_code]\n    validation_responsibility: [define_validation_scope]\n    output_contract: system/orchestrator/output_contract.py\n  Human:\n    capability: [approval]\n    allowed_actions: [approve]\n    prohibited_actions: [implement]\n    validation_responsibility: [approve_validation_scope]\n    output_contract: system/orchestrator/output_contract.py\n  GitHub Actions:\n    capability: [repository_validation]\n    allowed_actions: [run_workflow]\n    prohibited_actions: [edit_code]\n    validation_responsibility: [execute_validate_all]\n    output_contract: system/orchestrator/output_contract.py\n",
        encoding="utf-8",
    )


def test_repository_governor_generates_deterministic_candidates(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    governor = RepositoryGovernor(tmp_path)
    candidates = governor.build_candidates()
    assert candidates == tuple(sorted(candidates, key=lambda item: (-item.priority, item.ep)))


def test_repository_governor_recommendation_has_state(tmp_path: Path) -> None:
    _write_minimal_repo(tmp_path)
    governor = RepositoryGovernor(tmp_path)
    recommendation = governor.recommend()
    assert recommendation.state.next_ep
    assert recommendation.candidates
