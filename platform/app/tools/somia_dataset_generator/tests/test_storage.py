from pathlib import Path

from somia_dataset_generator.storage import atomic_write_text, read_jsonl, sha256_bytes, write_jsonl

def test_sha256_is_stable():
    assert sha256_bytes(b"somia") == sha256_bytes(b"somia")

def test_sha256_differs_for_different_content():
    assert sha256_bytes(b"a") != sha256_bytes(b"b")

def test_write_and_read_jsonl_roundtrip(tmp_path: Path):
    path = tmp_path / "rows.jsonl"
    rows = [{"a": 1}, {"a": 2}]
    write_jsonl(path, rows)
    assert read_jsonl(path) == rows

def test_read_jsonl_missing_file_returns_empty_list(tmp_path: Path):
    assert read_jsonl(tmp_path / "does_not_exist.jsonl") == []

def test_atomic_write_text_creates_parent_dirs(tmp_path: Path):
    path = tmp_path / "nested" / "dir" / "file.txt"
    atomic_write_text(path, "hello")
    assert path.read_text(encoding="utf-8") == "hello"
