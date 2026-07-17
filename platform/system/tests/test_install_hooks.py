from __future__ import annotations

import subprocess
from pathlib import Path


def test_install_hooks_installs_pre_push_hook(tmp_path: Path) -> None:
    # parents[2] from platform/system/tests/ is platform/, not the repo
    # root -- install_hooks.sh resolves its own target via BASH_SOURCE
    # (always the true repo root, regardless of cwd), so this test's
    # expected hook_path must match that, not a cwd-relative guess. Using
    # platform/ here previously matched a stray, untracked platform/.git/
    # directory that this same mismatch had already created locally,
    # which is why it passed there but failed on a clean CI checkout
    # (see ADR-0042).
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(["bash", str(repo_root / "platform" / "system" / "scripts" / "git" / "install_hooks.sh")], cwd=repo_root, capture_output=True, text=True, check=True)
    hook_path = repo_root / ".git" / "hooks" / "pre-push"
    assert hook_path.exists()
    installed = hook_path.read_text(encoding="utf-8")
    assert "prevent_main_push.sh" in installed
    assert "Installed pre-push hook" in result.stdout
