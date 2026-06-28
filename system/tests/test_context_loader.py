from pathlib import Path

from orchestrator.context_loader import load_context


def test_load_context_reads_canonical_documents(tmp_path: Path) -> None:
    (tmp_path / "basis").mkdir()
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "orchestrator").mkdir()

    (tmp_path / "basis" / "REPOSITORY_CONVENTIONS.md").write_text("repo conventions", encoding="utf-8")
    (tmp_path / "docs" / "current" / "CURRENT_STATE.md").write_text("current state", encoding="utf-8")
    (tmp_path / "orchestrator" / "ARCHITECTURE.md").write_text("architecture", encoding="utf-8")
    (tmp_path / "orchestrator" / "ADR-0001.md").write_text("adr", encoding="utf-8")
    (tmp_path / "orchestrator" / "WBS.md").write_text("wbs", encoding="utf-8")

    context = load_context(tmp_path)

    assert context.repository_conventions == "repo conventions"
    assert context.current_state == "current state"
    assert context.architecture == "architecture"
    assert context.adr == "adr"
    assert context.wbs == "wbs"
