import json
from pathlib import Path
from unittest.mock import patch

import pytest

from somia_dataset_generator.openai_adapter import ImageResult
from somia_dataset_generator.run import generate, read_run_state


class _ScriptedAdapter:
    """A simple fake: pop one outcome per call, in order. "ok" returns a
    tiny real image payload; "fail" raises."""

    def __init__(self, outcomes: list[str], api_key=None):
        self.outcomes = list(outcomes)
        self.calls = 0

    def generate(self, *, prompt: str, model: str, size: str, quality: str, output_format: str):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if outcome == "fail":
            raise RuntimeError("simulated API failure")
        return ImageResult(image_bytes=b"fake-image-bytes", revised_prompt=None)


def _fast_sleep(monkeypatch):
    monkeypatch.setattr("somia_dataset_generator.run.time.sleep", lambda *_: None)


def test_generate_dry_run_is_still_a_no_op(tmp_path: Path):
    run_id = generate("airi", 3, tmp_path, dry_run=True)
    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "planned"
    assert not (tmp_path / run_id / "generation.jsonl").exists()


def test_generate_all_succeed_marks_completed(tmp_path: Path, monkeypatch):
    _fast_sleep(monkeypatch)
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["ok", "ok", "ok"]),
    ):
        run_id = generate("airi", 3, tmp_path)
    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "completed"
    records = [json.loads(line) for line in (tmp_path / run_id / "generation.jsonl").read_text().splitlines()]
    assert all(r["status"] == "generated" for r in records)
    assert len(records) == 3


def test_generate_all_fail_marks_failed(tmp_path: Path, monkeypatch):
    _fast_sleep(monkeypatch)
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["fail"] * (3 * 3)),  # max_attempts_per_slot=3, 3 slots
    ):
        run_id = generate("airi", 3, tmp_path)
    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "failed"
    records = [json.loads(line) for line in (tmp_path / run_id / "generation.jsonl").read_text().splitlines()]
    assert all(r["status"] == "failed" for r in records)


def test_generate_partial_failure_marks_partially_completed(tmp_path: Path, monkeypatch):
    _fast_sleep(monkeypatch)
    # slot 1 ok, slot 2 fails all 3 attempts, slot 3 ok
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["ok", "fail", "fail", "fail", "ok"]),
    ):
        run_id = generate("airi", 3, tmp_path)
    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "partially_completed"
    records = [json.loads(line) for line in (tmp_path / run_id / "generation.jsonl").read_text().splitlines()]
    statuses = {r["slot"]: r["status"] for r in records}
    assert statuses[1] == "generated"
    assert statuses[2] == "failed"
    assert statuses[3] == "generated"


def test_resume_skips_already_generated_slots(tmp_path: Path, monkeypatch):
    _fast_sleep(monkeypatch)
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["ok", "fail", "fail", "fail"]),
    ):
        run_id = generate("airi", 2, tmp_path)
    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "partially_completed"

    # resume: only slot 2 (the failed one) should be retried
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["ok"]),
    ) as _:
        generate(resume_run_id=run_id, run_root=tmp_path)

    state = read_run_state(tmp_path / run_id)
    assert state["status"] == "completed"
    records = [json.loads(line) for line in (tmp_path / run_id / "generation.jsonl").read_text().splitlines()]
    # exactly one row per slot -- the stale failed row for slot 2 must not linger
    assert sorted(r["slot"] for r in records) == [1, 2]
    assert all(r["status"] == "generated" for r in records)


def test_resume_on_completed_run_is_a_no_op(tmp_path: Path, monkeypatch):
    _fast_sleep(monkeypatch)
    with patch(
        "somia_dataset_generator.run.OpenAIImageAdapter",
        lambda api_key=None: _ScriptedAdapter(["ok"]),
    ):
        run_id = generate("airi", 1, tmp_path)
    assert read_run_state(tmp_path / run_id)["status"] == "completed"

    with patch("somia_dataset_generator.run.OpenAIImageAdapter") as mock_adapter_cls:
        result_run_id = generate(resume_run_id=run_id, run_root=tmp_path)
        mock_adapter_cls.assert_not_called()
    assert result_run_id == run_id


def test_resume_requires_existing_run(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        generate(resume_run_id="does-not-exist", run_root=tmp_path)


def test_generate_without_character_or_resume_raises(tmp_path: Path):
    with pytest.raises(ValueError):
        generate(run_root=tmp_path)
