from __future__ import annotations

import json
from pathlib import Path

import pytest

from system.scripts.somia.content_spec import ContentSpecError, load_content_spec
from system.scripts.somia.providers import DryRunProvider, VideoGenerationError, get_provider
from system.scripts.somia.render_content import render


def _write_content_dir(base: Path) -> Path:
    content_dir = base / "somia" / "CONTENT" / "0001"
    content_dir.mkdir(parents=True)
    (content_dir / "prompt.md").write_text(
        "\n".join(
            [
                "# Prompt 0001",
                "",
                "## Image Prompt (KV)",
                "",
                "Airi, cool blue palette, dim corridor.",
                "",
                "## Animation Instruction",
                "",
                "Minimal motion, single gaze shift.",
                "",
                "## Camera Instruction",
                "",
                "Extreme close-up, slow zoom out.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (content_dir / "script.md").write_text(
        "\n".join(
            [
                "# Script 0001",
                "",
                "## Character",
                "",
                "Airi",
                "",
                "## Audio",
                "",
                "- Base: soft ambient bed",
                "",
                "## Text",
                "",
                "`You noticed too late that she was already there.`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (content_dir / "metadata.json").write_text(
        json.dumps({"character": "Airi", "variation_type": "audio_intensity", "hypothesis": "test"}),
        encoding="utf-8",
    )
    return content_dir


def test_load_content_spec_parses_sections(tmp_path: Path) -> None:
    content_dir = _write_content_dir(tmp_path)
    spec = load_content_spec(content_dir)
    assert spec.character == "Airi"
    assert "cool blue palette" in spec.image_prompt
    assert "gaze shift" in spec.animation_instruction
    assert "zoom out" in spec.camera_instruction
    assert spec.on_screen_text == "You noticed too late that she was already there."


def test_load_content_spec_missing_file_raises(tmp_path: Path) -> None:
    content_dir = tmp_path / "somia" / "CONTENT" / "0002"
    content_dir.mkdir(parents=True)
    with pytest.raises(ContentSpecError):
        load_content_spec(content_dir)


def test_dry_run_provider_writes_placeholder_outputs(tmp_path: Path) -> None:
    content_dir = _write_content_dir(tmp_path)
    spec = load_content_spec(content_dir)
    provider = DryRunProvider()
    result = provider.generate(spec, content_dir)
    assert Path(result.keyframe_path).exists()
    assert Path(result.video_path).exists()
    assert result.provider == "dry_run"


def test_get_provider_defaults_to_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOMIA_VIDEO_PROVIDER", raising=False)
    provider = get_provider()
    assert isinstance(provider, DryRunProvider)


def test_get_provider_rejects_unknown_name() -> None:
    with pytest.raises(VideoGenerationError):
        get_provider("runway")


def test_render_updates_metadata_with_render_record(tmp_path: Path) -> None:
    _write_content_dir(tmp_path)
    render_record = render("0001", provider_name="dry_run", root=tmp_path)
    metadata = json.loads((tmp_path / "somia" / "CONTENT" / "0001" / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["render"] == render_record
    assert metadata["hypothesis"] == "test"
    assert metadata["render"]["provider"] == "dry_run"
    # Paths are stored repo-relative so committing metadata.json doesn't churn per machine.
    assert render_record["video_path"] == "somia/CONTENT/0001/video.dry_run.txt"
    assert render_record["keyframe_path"] == "somia/CONTENT/0001/keyframe.dry_run.txt"
