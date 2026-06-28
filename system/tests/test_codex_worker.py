from system.orchestrator.task import Task
from system.orchestrator.workers.codex_worker import CodexWorker


def test_codex_worker_returns_result() -> None:
    worker = CodexWorker()
    task = Task(
        id="ep-006:test",
        artifact="system/orchestrator/workers/codex_worker.py",
        owner="Codex",
        instruction="Generate prompt",
        done_conditions="Prompt contains required fields",
        target_paths=("system/orchestrator/workers/codex_worker.py",),
    )

    result = worker.execute(task, context={})

    assert result.artifacts == ["system/orchestrator/workers/codex_worker.py"]
    assert result.files_changed == []
    assert result.errors == []
    assert len(result.review_notes) == 1


def test_codex_worker_prompt_contains_required_fields() -> None:
    worker = CodexWorker()
    task = Task(
        id="ep-006:test",
        artifact="system/orchestrator/workers/codex_worker.py",
        owner="Codex",
        instruction="Generate prompt",
        done_conditions="Prompt contains required fields",
        target_paths=("system/orchestrator/workers/codex_worker.py", "system/tests/test_codex_worker.py"),
    )

    result = worker.execute(task, context={})
    prompt = result.review_notes[0]

    assert "Artifact: system/orchestrator/workers/codex_worker.py" in prompt
    assert "Owner: Codex" in prompt
    assert "Done Conditions: Prompt contains required fields" in prompt
    assert "- system/orchestrator/workers/codex_worker.py" in prompt
    assert "- system/tests/test_codex_worker.py" in prompt


def test_codex_worker_prompt_contains_validation_commands() -> None:
    worker = CodexWorker()
    task = Task(
        id="ep-006:test",
        artifact="system/orchestrator/workers/codex_worker.py",
        owner="Codex",
        instruction="Generate prompt",
        done_conditions="Prompt contains required fields",
    )

    result = worker.execute(task, context={})
    prompt = result.review_notes[0]

    assert "python3 -m pytest -q" in prompt
    assert "git status" in prompt
    assert "git diff --stat" in prompt
    assert "git diff" in prompt
