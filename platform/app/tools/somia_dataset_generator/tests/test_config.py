from pathlib import Path

import pytest

from somia_dataset_generator.config import load_yaml

def test_load_yaml_reads_mapping(tmp_path: Path):
    path = tmp_path / "x.yaml"
    path.write_text("a: 1\nb: 2\n", encoding="utf-8")
    assert load_yaml(path) == {"a": 1, "b": 2}

def test_load_yaml_rejects_non_mapping_root(tmp_path: Path):
    path = tmp_path / "list.yaml"
    path.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_yaml(path)
