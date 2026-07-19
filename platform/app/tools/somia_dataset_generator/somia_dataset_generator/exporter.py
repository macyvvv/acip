from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil

from .config import load_yaml
from .paths import runtime_config_path
from .run import mark_exported, read_run_state
from .storage import atomic_write_text, read_jsonl


def _prompt_sha256(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def export_run(run_dir: Path) -> Path:
    """Export stage: ships only images the Validation stage accepted. Requires
    review.jsonl to already exist (produced by `validate --run-id`) -- Export
    is not allowed to make its own accept/reject judgment, only to act on
    Validation's."""
    review_path = run_dir / "review.jsonl"
    if not review_path.exists():
        raise FileNotFoundError(
            f"{review_path} not found -- run `validate --run-id <run_id>` before export "
            "(export only ships images the Validation stage has accepted)"
        )
    run_state = read_run_state(run_dir)
    runtime = load_yaml(runtime_config_path())
    runtime_config_version = runtime.get("schema_version")

    out = run_dir / "export"
    images_dir = out / "images"
    captions_dir = out / "captions"
    metadata_dir = out / "metadata"
    for directory in (images_dir, captions_dir, metadata_dir):
        directory.mkdir(parents=True, exist_ok=True)

    review_rows = read_jsonl(review_path)
    accepted_rows = [row for row in review_rows if row["accepted"]]

    manifest_entries = []
    for row in accepted_rows:
        src = run_dir / row["image"]
        dst = images_dir / src.name
        shutil.copy2(src, dst)

        caption = ", ".join([row["character_id"], *row["dimensions"].values()])
        (captions_dir / f"{src.stem}.txt").write_text(caption, encoding="utf-8")

        prompt = row.get("prompt") or ""
        entry = {
            "slot": row["slot"],
            "run_id": run_state["run_id"],
            "character_id": row["character_id"],
            "specification_version": row.get("specification_version"),
            "runtime_config_version": runtime_config_version,
            "policy_id": row.get("policy_id"),
            "dimensions": row["dimensions"],
            "prompt_sha256": _prompt_sha256(prompt),
            "image_sha256": row["sha256"],
            "export_image": str(dst.relative_to(out)),
        }
        (metadata_dir / f"{src.stem}.json").write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest_entries.append(entry)

    atomic_write_text(out / "manifest.json", json.dumps(manifest_entries, ensure_ascii=False, indent=2))

    report = {
        "run_id": run_state["run_id"],
        "character_id": run_state["character_id"],
        "reviewed": len(review_rows),
        "accepted": len(accepted_rows),
        "rejected": len(review_rows) - len(accepted_rows),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_text(out / "report.json", json.dumps(report, ensure_ascii=False, indent=2))

    mark_exported(run_dir)
    return out
