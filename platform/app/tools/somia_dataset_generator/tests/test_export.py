import json
from pathlib import Path

import pytest

from somia_dataset_generator.exporter import export_run
from somia_dataset_generator.run import read_run_state


def _setup_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run1"
    (run_dir / "raw").mkdir(parents=True)
    (run_dir / "raw" / "0001.png").write_bytes(b"fake-png-bytes-1")
    (run_dir / "raw" / "0002.png").write_bytes(b"fake-png-bytes-2")

    run_state = {"run_id": "run1", "character_id": "airi", "requested_count": 2, "status": "completed"}
    (run_dir / "run.json").write_text(json.dumps(run_state), encoding="utf-8")

    review_rows = [
        {
            "slot": 1, "character_id": "airi", "specification_version": "1.1", "policy_id": "airi_v1",
            "image": "raw/0001.png", "sha256": "hash-1", "dimensions": {"framing": "close_up"},
            "prompt": "prompt one", "accepted": True, "issues": [],
        },
        {
            "slot": 2, "character_id": "airi", "specification_version": "1.1", "policy_id": "airi_v1",
            "image": "raw/0002.png", "sha256": "hash-2", "dimensions": {"framing": "upper_body"},
            "prompt": "prompt two", "accepted": False, "issues": ["dimension mismatch"],
        },
    ]
    (run_dir / "review.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in review_rows), encoding="utf-8"
    )
    return run_dir


def test_export_requires_review(tmp_path: Path):
    run_dir = tmp_path / "run_no_review"
    run_dir.mkdir()
    (run_dir / "run.json").write_text(json.dumps({"run_id": "run_no_review", "character_id": "airi"}))
    with pytest.raises(FileNotFoundError):
        export_run(run_dir)


def test_export_ships_only_accepted_images(tmp_path: Path):
    run_dir = _setup_run(tmp_path)
    out = export_run(run_dir)

    assert (out / "images" / "0001.png").is_file()
    assert not (out / "images" / "0002.png").exists()
    assert (out / "captions" / "0001.txt").read_text() == "airi, close_up"
    assert (out / "metadata" / "0001.json").is_file()
    assert not (out / "metadata" / "0002.json").exists()


def test_export_manifest_has_required_fields(tmp_path: Path):
    run_dir = _setup_run(tmp_path)
    out = export_run(run_dir)
    manifest = json.loads((out / "manifest.json").read_text())
    assert len(manifest) == 1
    entry = manifest[0]
    for field in (
        "run_id", "character_id", "specification_version", "runtime_config_version",
        "policy_id", "prompt_sha256", "image_sha256", "dimensions", "export_image",
    ):
        assert field in entry, f"missing manifest field: {field}"
    assert entry["run_id"] == "run1"
    assert entry["image_sha256"] == "hash-1"


def test_export_report_summarizes_accept_reject(tmp_path: Path):
    run_dir = _setup_run(tmp_path)
    out = export_run(run_dir)
    report = json.loads((out / "report.json").read_text())
    assert report["reviewed"] == 2
    assert report["accepted"] == 1
    assert report["rejected"] == 1
    assert "exported_at" in report


def test_export_marks_run_as_exported(tmp_path: Path):
    run_dir = _setup_run(tmp_path)
    export_run(run_dir)
    assert read_run_state(run_dir)["status"] == "exported"
