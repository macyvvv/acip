from __future__ import annotations

import json
from pathlib import Path

from system.scripts.validate_repository_os_v2_release import main as validate_release


def test_repository_os_v2_release_projection(tmp_path: Path) -> None:
    release_dir = tmp_path / "runtime" / "releases"
    release_dir.mkdir(parents=True)
    release_dir.joinpath("repository_os_v2.json").write_text(
        json.dumps({"status": "frozen", "release_id": "REPOSITORY_OS_V2"}),
        encoding="utf-8",
    )
    release_dir.joinpath("repository_os_v2.md").write_text("# REPOSITORY_OS_V2\n", encoding="utf-8")
    assert release_dir.joinpath("repository_os_v2.json").exists()
    assert release_dir.joinpath("repository_os_v2.md").exists()
