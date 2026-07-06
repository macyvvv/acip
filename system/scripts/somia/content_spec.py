from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class ContentSpec:
    content_id: str
    character: str
    image_prompt: str
    animation_instruction: str
    camera_instruction: str
    on_screen_text: str
    audio_notes: str


class ContentSpecError(ValueError):
    pass


def _section(markdown: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)", markdown, re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def _first_backtick_line(markdown: str) -> str:
    match = re.search(r"`([^`]+)`", markdown)
    return match.group(1) if match else ""


def load_content_spec(content_dir: str | Path) -> ContentSpec:
    content_dir = Path(content_dir)
    prompt_path = content_dir / "prompt.md"
    script_path = content_dir / "script.md"
    metadata_path = content_dir / "metadata.json"
    missing = [p.name for p in (prompt_path, script_path, metadata_path) if not p.exists()]
    if missing:
        raise ContentSpecError(f"Missing content files in {content_dir}: {', '.join(missing)}")

    prompt_text = prompt_path.read_text(encoding="utf-8")
    script_text = script_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    character = str(metadata.get("character") or _section(script_text, "Character"))
    if not character:
        raise ContentSpecError(f"Could not determine character for {content_dir}")

    return ContentSpec(
        content_id=content_dir.name,
        character=character,
        image_prompt=_section(prompt_text, "Image Prompt (KV)"),
        animation_instruction=_section(prompt_text, "Animation Instruction"),
        camera_instruction=_section(prompt_text, "Camera Instruction"),
        on_screen_text=_first_backtick_line(_section(script_text, "Text")),
        audio_notes=_section(script_text, "Audio"),
    )
