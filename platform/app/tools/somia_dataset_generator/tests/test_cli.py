from pathlib import Path

import pytest

from somia_dataset_generator.cli import main
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


def _run_main(monkeypatch, tmp_path: Path, argv: list[str]):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["somia-dataset", *argv])
    main()


def test_main_dispatches_plan(monkeypatch, tmp_path: Path, capsys):
    _run_main(monkeypatch, tmp_path, ["plan", "--character", "airi", "--count", "3"])
    run_id = capsys.readouterr().out.strip()
    assert (tmp_path / "runs" / run_id / "run.json").is_file()


def test_main_dispatches_plan_with_seed(monkeypatch, tmp_path: Path, capsys):
    _run_main(monkeypatch, tmp_path, ["plan", "--character", "airi", "--count", "3", "--seed", "7"])
    run_id = capsys.readouterr().out.strip()
    assert (tmp_path / "runs" / run_id / "plan.jsonl").is_file()


def test_main_dispatches_generate_dry_run(monkeypatch, tmp_path: Path, capsys):
    _run_main(monkeypatch, tmp_path, ["generate", "--character", "airi", "--count", "2", "--dry-run"])
    run_id = capsys.readouterr().out.strip()
    assert (tmp_path / "runs" / run_id / "plan.jsonl").is_file()
    assert not (tmp_path / "runs" / run_id / "generation.jsonl").exists()


def test_main_dispatches_validate_character(monkeypatch, tmp_path: Path, capsys):
    _run_main(monkeypatch, tmp_path, ["validate", "--character", "airi"])
    assert "valid: airi" in capsys.readouterr().out


def test_main_generate_without_character_or_resume_errors(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["somia-dataset", "generate", "--count", "3"])
    with pytest.raises(SystemExit):
        main()


def test_main_validate_without_character_or_run_id_errors(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["somia-dataset", "validate"])
    with pytest.raises(SystemExit):
        main()


def test_main_module_entrypoint_runs_via_runpy(tmp_path: Path, monkeypatch):
    import runpy
    import sys

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["somia-dataset", "validate", "--character", "airi"])
    runpy.run_module("somia_dataset_generator.__main__", run_name="__main__")
