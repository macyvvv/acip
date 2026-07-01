from __future__ import annotations

import subprocess
from pathlib import Path


def test_install_hooks_installs_pre_push_hook(tmp_path: Path) -> None:
    source_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(["bash", str(source_root / "system" / "scripts" / "git" / "install_hooks.sh")], cwd=source_root, capture_output=True, text=True, check=True)
    hook_path = source_root / ".git" / "hooks" / "pre-push"
    assert hook_path.exists()
    installed = hook_path.read_text(encoding="utf-8")
    assert "prevent_main_push.sh" in installed
    assert "Installed pre-push hook" in result.stdout
