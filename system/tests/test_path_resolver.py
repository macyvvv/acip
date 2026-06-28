from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from system.core.path_resolver import get_repo_root


ROOT = get_repo_root()


def test_get_repo_root_returns_repository_root() -> None:
    assert get_repo_root() == ROOT


def test_validate_script_runs_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "system" / "scripts" / "validate_ep_0100.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_validate_script_runs_from_arbitrary_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "system" / "scripts" / "validate_ep_0100.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
