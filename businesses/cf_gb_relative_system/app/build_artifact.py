from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent


def build_release_artifact(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / "cf-gb-relative-system-app.tar.gz"
    manifest_path = output_dir / "cf-gb-relative-system-app.manifest.json"
    included = ["README.md", "pyproject.toml", "requirements.lock"]
    with tarfile.open(archive_path, "w:gz") as tar:
      for relative in included:
        tar.add(APP_ROOT / relative, arcname=relative)
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    manifest = {
        "artifact_name": archive_path.name,
        "sha256": digest,
        "included_files": included,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return archive_path, manifest_path


if __name__ == "__main__":
    build_release_artifact(APP_ROOT / "dist")
