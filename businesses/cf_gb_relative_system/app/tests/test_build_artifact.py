from __future__ import annotations

import json
import tarfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_artifact import build_release_artifact


def test_build_release_artifact_contains_expected_files(tmp_path: Path) -> None:
    archive_path, manifest_path = build_release_artifact(tmp_path)

    assert archive_path.exists()
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_name"] == archive_path.name
    assert manifest["included_files"] == ["README.md", "pyproject.toml", "requirements.lock"]

    with tarfile.open(archive_path, "r:gz") as tar:
        assert sorted(tar.getnames()) == ["README.md", "pyproject.toml", "requirements.lock"]
