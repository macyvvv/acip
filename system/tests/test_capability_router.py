from pathlib import Path

from system.orchestrator.capability_router import CapabilityRouter
from system.orchestrator.planner import PlannerDecision


def _write_registry(root: Path) -> None:
    (root / "workers").mkdir()
    (root / "workers" / "registry.yaml").write_text(
        """workers:
  Codex:
    capability: [repository_implementation, validation_execution]
    allowed_actions: [implement, validate]
    prohibited_actions: [approve, deploy]
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
    capability: [ci_execution, repository_validation]
    allowed_actions: [run_workflow]
    prohibited_actions: [edit_code]
    validation_responsibility: [execute_validate_all]
    output_contract: system/orchestrator/output_contract.py
""",
        encoding="utf-8",
    )


def test_route_worker_deterministic(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    router = CapabilityRouter(tmp_path)
    planner = PlannerDecision(current_ep="EP-0114", next_ep="EP-0114", queue_status="READY", dependency_chain=("EP-0114",))

    route = router.route(
        planner,
        required_capabilities=("repository_implementation", "validation_execution"),
        prohibited_actions=("approve",),
        required_validation_responsibility=("run_repository_validation",),
        execution_boundary=("push_directly_to_main",),
    )

    assert route.worker_name == "Codex"
    assert "Codex" in route.candidates


def test_route_worker_missing_candidate_fails(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    router = CapabilityRouter(tmp_path)
    planner = PlannerDecision(current_ep="EP-0114", next_ep="EP-0114", queue_status="READY", dependency_chain=("EP-0114",))

    try:
        router.route(
            planner,
            required_capabilities=("nonexistent_capability",),
        )
    except Exception as exc:
        assert "No worker matches capabilities" in str(exc)
    else:
        raise AssertionError("expected failure")
