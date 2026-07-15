from __future__ import annotations

import subprocess
from pathlib import Path


def test_prevent_main_push_blocks_main_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "git" / "prevent_main_push.sh"
    result = subprocess.run(["bash", str(script)], cwd=repo, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Blocked: direct push to main is prohibited" in result.stderr


def test_prevent_main_push_allows_feature_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "feature/test"], cwd=repo, check=True, capture_output=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "git" / "prevent_main_push.sh"
    result = subprocess.run(["bash", str(script)], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Push allowed from branch: feature/test" in result.stdout
