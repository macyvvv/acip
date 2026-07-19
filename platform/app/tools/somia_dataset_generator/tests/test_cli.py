from pathlib import Path

from somia_dataset_generator.run import generate, make_plan


def test_plan_command_core_writes_expected_files(tmp_path: Path):
    run_id, run_dir, plan = make_plan("airi", 4, tmp_path)
    assert run_id
    assert len(plan) == 4
    assert (run_dir / "run.json").is_file()
    assert (run_dir / "plan.jsonl").is_file()


def test_generate_dry_run_never_requires_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    run_id = generate("airi", 3, tmp_path, dry_run=True)
    run_dir = tmp_path / run_id
    assert (run_dir / "run.json").is_file()
    assert (run_dir / "plan.jsonl").is_file()
    assert not (run_dir / "generation.jsonl").exists()
