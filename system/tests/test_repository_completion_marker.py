from __future__ import annotations

from system.orchestrator.completion_protocol import CompletionStatus, build_completion_protocol
from system.orchestrator.repository_completion_marker import RepositoryCompletionMarkerWriter


def test_repository_completion_marker_writes_latest(tmp_path) -> None:
    writer = RepositoryCompletionMarkerWriter(tmp_path)
    protocol = build_completion_protocol(
        status=CompletionStatus.success,
        pack_id="PACK-0004",
        parent_issue=9,
        ep_id="EP-0157",
        commit_sha="abc1234",
        validation_result="success",
        pytest_result="success",
        worktree_state="clean",
        next_action="Review latest completion marker.",
        requires_human_approval=False,
    )
    marker = writer.write(protocol)
    assert (tmp_path / "runtime" / "handoff" / "latest.json").exists()
    assert marker.latest_path.endswith("latest.json")
