#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT_FOR_BOOTSTRAP = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT_FOR_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_BOOTSTRAP))

from system.core.dotenv import load_dotenv
from system.core.path_resolver import get_repo_root
from system.scripts.somia.content_spec import load_content_spec
from system.scripts.somia.providers import VideoGenerationError, get_provider


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a somia/CONTENT/<id> spec into a video via a pluggable provider.")
    parser.add_argument("--content-id", required=True, help="e.g. 0001")
    parser.add_argument("--provider", default=None, help="Overrides SOMIA_VIDEO_PROVIDER env var. Defaults to dry_run.")
    return parser


def render(content_id: str, *, provider_name: str | None = None, root: Path | None = None) -> dict:
    root = root or get_repo_root()
    content_dir = root / "somia" / "CONTENT" / content_id
    spec = load_content_spec(content_dir)
    provider = get_provider(provider_name)
    result = provider.generate(spec, content_dir)

    def _relative(path: str | None) -> str | None:
        if not path:
            return path
        try:
            return str(Path(path).resolve().relative_to(root))
        except ValueError:
            return path

    metadata_path = content_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["render"] = {
        "provider": result.provider,
        "model": result.model,
        "keyframe_path": _relative(result.keyframe_path),
        "video_path": _relative(result.video_path),
        "rendered_at": result.rendered_at,
        "notes": result.notes,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata["render"]


def main() -> int:
    load_dotenv(get_repo_root() / ".env")
    args = _build_parser().parse_args()
    try:
        render_record = render(args.content_id, provider_name=args.provider)
    except VideoGenerationError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"Rendered {args.content_id} via {render_record['provider']}")
    print(f"keyframe: {render_record['keyframe_path']}")
    print(f"video: {render_record['video_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
