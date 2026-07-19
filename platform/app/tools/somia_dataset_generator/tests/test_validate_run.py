import json
from pathlib import Path

from PIL import Image

from somia_dataset_generator.validate_run import duplicate_groups, technical_issues, validate_run

RUNTIME = {"output_format": "png", "size": "64x96"}


def _make_image(path: Path, size: tuple[int, int] = (64, 96), fmt: str = "PNG") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color="white").save(path, format=fmt)


def test_technical_issues_missing_file(tmp_path: Path):
    issues = technical_issues(tmp_path / "nope.png", RUNTIME)
    assert issues == [f"missing file: {tmp_path / 'nope.png'}"]


def test_technical_issues_zero_byte_file(tmp_path: Path):
    path = tmp_path / "empty.png"
    path.write_bytes(b"")
    assert technical_issues(path, RUNTIME) == ["zero-byte file"]


def test_technical_issues_not_an_image(tmp_path: Path):
    path = tmp_path / "fake.png"
    path.write_bytes(b"this is not png data")
    issues = technical_issues(path, RUNTIME)
    assert len(issues) == 1
    assert "not a readable image" in issues[0]


def test_technical_issues_dimension_mismatch(tmp_path: Path):
    path = tmp_path / "wrong_size.png"
    _make_image(path, size=(32, 32))
    issues = technical_issues(path, RUNTIME)
    assert any("dimension mismatch" in issue for issue in issues)


def test_technical_issues_format_mismatch(tmp_path: Path):
    path = tmp_path / "wrong_format.png"
    _make_image(path, size=(64, 96), fmt="BMP")
    issues = technical_issues(path, RUNTIME)
    assert any("format mismatch" in issue for issue in issues)


def test_technical_issues_pass(tmp_path: Path):
    path = tmp_path / "good.png"
    _make_image(path)
    assert technical_issues(path, RUNTIME) == []


def test_duplicate_groups_flags_repeated_hashes():
    records = [
        {"slot": 1, "sha256": "aaa"},
        {"slot": 2, "sha256": "bbb"},
        {"slot": 3, "sha256": "aaa"},
    ]
    groups = duplicate_groups(records)
    assert groups == {"aaa": [1, 3]}


def test_duplicate_groups_no_duplicates():
    records = [{"slot": 1, "sha256": "aaa"}, {"slot": 2, "sha256": "bbb"}]
    assert duplicate_groups(records) == {}


def test_validate_run_end_to_end(tmp_path: Path):
    run_dir = tmp_path / "run1"
    (run_dir / "raw").mkdir(parents=True)

    run_state = {
        "run_id": "run1",
        "character_id": "airi",
        "requested_count": 3,
        "status": "completed",
    }
    (run_dir / "run.json").write_text(json.dumps(run_state), encoding="utf-8")

    _make_image(run_dir / "raw" / "0001.png", size=(1024, 1536))
    _make_image(run_dir / "raw" / "0002.png", size=(1024, 1536))
    # 0003 is a duplicate of 0001's content -- same hash on purpose
    (run_dir / "raw" / "0003.png").write_bytes((run_dir / "raw" / "0001.png").read_bytes())

    generation_records = [
        {
            "slot": 1, "character_id": "airi", "dimensions": {"framing": "close_up"},
            "prompt": "p", "status": "generated", "image": "raw/0001.png", "sha256": "hash-a",
        },
        {
            "slot": 2, "character_id": "airi", "dimensions": {"framing": "upper_body"},
            "prompt": "p", "status": "generated", "image": "raw/0002.png", "sha256": "hash-b",
        },
        {
            "slot": 3, "character_id": "airi", "dimensions": {"framing": "close_up"},
            "prompt": "p", "status": "generated", "image": "raw/0003.png", "sha256": "hash-a",
        },
    ]
    (run_dir / "generation.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in generation_records), encoding="utf-8"
    )

    report = validate_run(run_dir)

    assert report["accepted"] == 2
    assert report["rejected"] == 1
    assert report["duplicate_groups"] == {"hash-a": [1, 3]}
    assert (run_dir / "review.jsonl").is_file()

    review_rows = [json.loads(line) for line in (run_dir / "review.jsonl").read_text().splitlines()]
    rejected = [r for r in review_rows if not r["accepted"]]
    assert rejected[0]["slot"] == 3
    assert any("duplicate" in issue for issue in rejected[0]["issues"])
