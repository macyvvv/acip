from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import time
import uuid

from .config import load_yaml
from .validation import validate_character
from .openai_adapter import OpenAIImageAdapter
from .planner import create_plan
from .storage import atomic_write_text, sha256_bytes, write_jsonl

def _paths(character_id: str):
    return (
        Path("specs/characters") / f"{character_id}.yaml",
        Path("specs/sampling") / f"{character_id}_v1.yaml",
    )

def make_plan(character_id: str, count: int, run_root: Path) -> tuple[str, Path, list]:
    character_path, policy_path = _paths(character_id)
    character = validate_character(character_path)
    policy = load_yaml(policy_path)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    plan = create_plan(character, policy, count)
    write_jsonl(run_dir / "plan.jsonl", [x.to_dict() for x in plan])
    atomic_write_text(run_dir / "run.json", json.dumps({
        "run_id": run_id,
        "character_id": character_id,
        "requested_count": count,
        "status": "planned",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2))
    return run_id, run_dir, plan

def generate(character_id: str, count: int, run_root: Path, dry_run: bool = False) -> str:
    run_id, run_dir, plan = make_plan(character_id, count, run_root)
    if dry_run:
        return run_id
    runtime = load_yaml("config/runtime.yaml")
    adapter = OpenAIImageAdapter(api_key=os.environ.get("OPENAI_API_KEY"))
    records = []
    for item in plan:
        attempts = 0
        while True:
            attempts += 1
            try:
                result = adapter.generate(
                    prompt=item.prompt,
                    model=runtime["model"],
                    size=runtime["size"],
                    quality=runtime["quality"],
                    output_format=runtime["output_format"],
                )
                ext = runtime["output_format"]
                image_name = f"{item.slot:04d}.{ext}"
                image_path = run_dir / "raw" / image_name
                image_path.parent.mkdir(parents=True, exist_ok=True)
                image_path.write_bytes(result.image_bytes)
                records.append({
                    **item.to_dict(),
                    "status": "generated",
                    "attempts": attempts,
                    "image": str(image_path.relative_to(run_dir)),
                    "sha256": sha256_bytes(result.image_bytes),
                    "revised_prompt": result.revised_prompt,
                })
                write_jsonl(run_dir / "generation.jsonl", records)
                break
            except Exception as exc:
                if attempts >= runtime["max_attempts_per_slot"]:
                    records.append({**item.to_dict(), "status": "failed", "attempts": attempts, "error": repr(exc)})
                    write_jsonl(run_dir / "generation.jsonl", records)
                    raise
                time.sleep(min(2 ** attempts, 30))
    return run_id
