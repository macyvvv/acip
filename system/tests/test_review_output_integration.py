from __future__ import annotations

from system.orchestrator.capability_router import CapabilityRoute
from system.orchestrator.review_output_integration import build_review_output_integration
from system.orchestrator.task_decomposer import DecomposedSubtask, TaskDecompositionResult


def test_review_output_integration_builds_worker_output() -> None:
    decomposition = TaskDecompositionResult(
        source="EP-0119",
        objective="Integrate review output",
        subtasks=(
            DecomposedSubtask(
                id="EP-0119:01:deadbeef",
                title="Review integration",
                required_capability="review_output",
                worker_candidate="Codex",
                worker_candidates=("Codex",),
            ),
        ),
    )
    routing = CapabilityRoute(worker_name="Codex", reason="selected", candidates=("Codex",))
    result = build_review_output_integration(decomposition, routing, review_notes=("ok",))

    assert result.review_summary.status == "success"
    assert result.worker_output["routing"]["worker_name"] == "Codex"
    assert result.worker_output["subtasks"][0]["id"] == "EP-0119:01:deadbeef"


def test_review_output_integration_marks_partial_success() -> None:
    decomposition = TaskDecompositionResult(
        source="EP-0119",
        objective="Integrate review output",
        subtasks=(
            DecomposedSubtask(
                id="EP-0119:01:deadbeef",
                title="Review integration",
                required_capability="review_output",
                worker_candidate="Human",
                worker_candidates=("Human",),
            ),
        ),
    )
    routing = CapabilityRoute(worker_name="Codex", reason="selected", candidates=("Codex",))
    result = build_review_output_integration(decomposition, routing)

    assert result.review_summary.status == "partial_success"
