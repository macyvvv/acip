import json
import subprocess
import sys
from pathlib import Path


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "somia_dataset_generator", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_plan_subcommand(tmp_path: Path):
    result = _run("plan", "--character", "airi", "--count", "4", "--runs", "runs", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    run_id = result.stdout.strip()
    assert (tmp_path / "runs" / run_id / "run.json").is_file()
    assert (tmp_path / "runs" / run_id / "plan.jsonl").is_file()


def test_generate_dry_run_subcommand(tmp_path: Path):
    result = _run(
        "generate", "--character", "airi", "--count", "3", "--dry-run", "--runs", "runs", cwd=tmp_path
    )
    assert result.returncode == 0, result.stderr
    run_id = result.stdout.strip()
    assert (tmp_path / "runs" / run_id / "plan.jsonl").is_file()
    assert not (tmp_path / "runs" / run_id / "generation.jsonl").exists()


def test_generate_without_character_or_resume_errors(tmp_path: Path):
    result = _run("generate", "--count", "3", cwd=tmp_path)
    assert result.returncode != 0
    assert "requires --character and --count" in result.stderr


def test_validate_character_subcommand(tmp_path: Path):
    result = _run("validate", "--character", "airi", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "valid: airi" in result.stdout


def test_validate_without_character_or_run_id_errors(tmp_path: Path):
    result = _run("validate", cwd=tmp_path)
    assert result.returncode != 0
    assert "requires --character or --run-id" in result.stderr


def test_validate_run_id_and_export_subcommands(tmp_path: Path):
    plan_result = _run("plan", "--character", "airi", "--count", "2", "--runs", "runs", cwd=tmp_path)
    run_id = plan_result.stdout.strip()
    run_dir = tmp_path / "runs" / run_id

    # simulate a completed generation (no real API call in this test)
    plan_rows = [json.loads(line) for line in (run_dir / "plan.jsonl").read_text().splitlines()]
    (run_dir / "raw").mkdir()
    generation_records = []
    for row in plan_rows:
        image_path = run_dir / "raw" / f"{row['slot']:04d}.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\nnot-a-real-png-but-nonzero")
        generation_records.append({
            **row, "status": "generated", "attempts": 1,
            "image": str(image_path.relative_to(run_dir)), "sha256": f"hash-{row['slot']}", "revised_prompt": None,
        })
    (run_dir / "generation.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in generation_records), encoding="utf-8"
    )
    run_state = json.loads((run_dir / "run.json").read_text())
    run_state["status"] = "completed"
    (run_dir / "run.json").write_text(json.dumps(run_state), encoding="utf-8")

    validate_result = _run("validate", "--run-id", run_id, "--runs", "runs", cwd=tmp_path)
    assert validate_result.returncode == 0, validate_result.stderr
    assert f"run {run_id}" in validate_result.stdout
    assert (run_dir / "review.jsonl").is_file()

    export_result = _run("export", "--run-id", run_id, "--runs", "runs", cwd=tmp_path)
    assert export_result.returncode == 0, export_result.stderr
    out_dir = tmp_path / Path(export_result.stdout.strip())
    assert out_dir.is_dir()
    assert (out_dir / "manifest.json").is_file()
    assert (out_dir / "report.json").is_file()
