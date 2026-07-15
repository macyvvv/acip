from __future__ import annotations

import builtins
import sys
import types
from pathlib import Path

import system.scripts.agent.run_approval_console as launcher


def test_text_mode_flag_emits_summary(capsys) -> None:
    code = launcher.main(["--text"])
    output = capsys.readouterr().out
    assert code == 0
    assert "Approval Console MVP (text-mode fallback)" in output
    assert "source_open_issues=" in output
    assert "current_now_candidate_count=" in output


def test_missing_tkinter_falls_back_without_traceback(monkeypatch, capsys) -> None:
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"tkinter", "_tkinter"} or name.startswith("tkinter."):
            raise ModuleNotFoundError("No module named '_tkinter'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    code = launcher.main([])
    output = capsys.readouterr().out
    assert code == 0
    assert "Tkinter is unavailable in this Python environment" in output
    assert "Traceback" not in output


def test_gui_path_invokes_launch(monkeypatch) -> None:
    calls: list[str] = []
    fake_gui = types.ModuleType("app.tools.approval_console_mvp.gui")

    def fake_launch(repo_root=".") -> None:  # pragma: no cover - simple test double
        calls.append(str(repo_root))

    fake_gui.launch = fake_launch  # type: ignore[attr-defined]
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "app.tools.approval_console_mvp.gui":
            return fake_gui
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    code = launcher.main(["--no-gui"])
    assert code == 0
    assert calls == []

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    code = launcher.main([])
    assert code == 0
    assert calls == ["."] or calls == [str(Path("."))]
