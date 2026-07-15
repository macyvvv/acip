from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import importlib
import os

from system.scripts.somia.content_spec import ContentSpec


@dataclass(frozen=True)
class RenderResult:
    provider: str
    model: str
    keyframe_path: str | None
    video_path: str | None
    rendered_at: str
    notes: str
    # Structured list of ways this render deviated from the content spec
    # (e.g. "duration: requested 12s, rendered 10s (vendor cap)",
    # "on_screen_text: not composited, spec text not included"). Kept
    # separate from free-text `notes` so a caller (render_content.py, a
    # future QA pass) can check "did this deviate at all" without parsing
    # prose. Empty list means no known deviation.
    spec_deviations: tuple[str, ...] = ()


class VideoGenerationError(RuntimeError):
    pass


class VideoGenerationProvider(ABC):
    """One adapter per video-generation vendor. Swapping providers should never
    require touching render_content.py or the content spec parser."""

    name: str = "unset"

    @abstractmethod
    def generate(self, spec: ContentSpec, output_dir: Path) -> RenderResult:
        raise NotImplementedError


class DryRunProvider(VideoGenerationProvider):
    """No network calls, no API key. Proves the pipeline end-to-end and is the
    default so this scaffold is runnable before any vendor is chosen."""

    name = "dry_run"

    def generate(self, spec: ContentSpec, output_dir: Path) -> RenderResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        keyframe_path = output_dir / "keyframe.dry_run.txt"
        video_path = output_dir / "video.dry_run.txt"
        keyframe_path.write_text(f"[dry-run keyframe]\nimage_prompt: {spec.image_prompt}\n", encoding="utf-8")
        video_path.write_text(
            "\n".join(
                [
                    "[dry-run video]",
                    f"character: {spec.character}",
                    f"animation_instruction: {spec.animation_instruction}",
                    f"camera_instruction: {spec.camera_instruction}",
                    f"on_screen_text: {spec.on_screen_text}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return RenderResult(
            provider=self.name,
            model="none",
            keyframe_path=str(keyframe_path),
            video_path=str(video_path),
            rendered_at=datetime.now(timezone.utc).isoformat(),
            notes="dry-run: no external API called",
        )


_REGISTRY: dict[str, type[VideoGenerationProvider]] = {
    "dry_run": DryRunProvider,
}

# Vendor adapters that call network APIs live in their own module and are only
# imported when actually selected, so choosing dry_run (the default) never
# pulls in HTTP/vendor-specific code.
_OPTIONAL_PROVIDER_MODULES: dict[str, str] = {
    "pika": "system.scripts.somia.providers_pika",
    "kling": "system.scripts.somia.providers_kling",
    "illustrious_kling": "system.scripts.somia.providers_illustrious_kling",
}


def register_provider(provider_cls: type[VideoGenerationProvider]) -> None:
    """Vendor adapters call this to plug in without editing this file's registry
    literal, e.g. from a platform/system/platform/scripts/somia/providers_pika.py module."""
    _REGISTRY[provider_cls.name] = provider_cls


def get_provider(name: str | None = None) -> VideoGenerationProvider:
    resolved_name = name or os.environ.get("SOMIA_VIDEO_PROVIDER", "dry_run")
    if resolved_name not in _REGISTRY and resolved_name in _OPTIONAL_PROVIDER_MODULES:
        importlib.import_module(_OPTIONAL_PROVIDER_MODULES[resolved_name])
    provider_cls = _REGISTRY.get(resolved_name)
    if provider_cls is None:
        known = ", ".join(sorted(set(_REGISTRY) | set(_OPTIONAL_PROVIDER_MODULES)))
        raise VideoGenerationError(f"Unknown SOMIA_VIDEO_PROVIDER '{resolved_name}'. Known providers: {known}")
    return provider_cls()
