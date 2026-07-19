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
from .paths import character_spec_path, sampling_policy_path, runtime_config_path
from .planner import create_plan
from .storage import atomic_write_text, read_jsonl, sha256_bytes, write_jsonl

# Run lifecycle: planned -> running -> (completed | failed | partially_completed) -> exported.
# "planned" is the state immediately after make_plan(); dry-run generation never
# leaves it. A real generation attempt moves to "running", then settles into
# exactly one of the three terminal generation states depending on how many
# slots actually produced an image. export_run() (exporter.py) is the only
# thing allowed to move a run to "exported".
TERMINAL_GENERATION_STATUSES = ("completed", "failed", "partially_completed")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_json_path(run_dir: Path) -> Path:
    return run_dir / "run.json"


def read_run_state(run_dir: Path) -> dict:
    path = _run_json_path(run_dir)
    if not path.exists():
        raise FileNotFoundError(f"no run.json in {run_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def mark_exported(run_dir: Path) -> None:
    """The only transition Export is allowed to make on a run's lifecycle
    state -- called by exporter.py after a successful export."""
    _update_run_status(run_dir, "exported")


def _update_run_status(run_dir: Path, status: str, **extra) -> None:
    state = read_run_state(run_dir)
    state.update(extra)
    state["status"] = status
    state["updated_at"] = _now_iso()
    atomic_write_text(_run_json_path(run_dir), json.dumps(state, ensure_ascii=False, indent=2))


def make_plan(character_id: str, count: int, run_root: Path, seed: int | None = None) -> tuple[str, Path, list]:
    character_path = character_spec_path(character_id)
    policy_path = sampling_policy_path(character_id)
    character = validate_character(character_path)
    policy = load_yaml(policy_path)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    plan = create_plan(character, policy, count, seed=seed)
    write_jsonl(run_dir / "plan.jsonl", [x.to_dict() for x in plan])
    atomic_write_text(_run_json_path(run_dir), json.dumps({
        "run_id": run_id,
        "character_id": character_id,
        "requested_count": count,
        "status": "planned",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }, ensure_ascii=False, indent=2))
    return run_id, run_dir, plan


def _generate_pending(run_dir: Path, plan_rows: list[dict], existing_records: list[dict]) -> None:
    completed_slots = {r["slot"] for r in existing_records if r.get("status") == "generated"}
    pending = [row for row in plan_rows if row["slot"] not in completed_slots]
    pending_slots = {row["slot"] for row in pending}
    # Drop stale (e.g. previously-failed) records for slots being retried this
    # pass, so a retried slot gets exactly one row in generation.jsonl instead
    # of an old "failed" row plus a new one.
    records = [r for r in existing_records if r["slot"] not in pending_slots]

    if not pending:
        _update_run_status(run_dir, "completed")
        return

    _update_run_status(run_dir, "running")
    runtime = load_yaml(runtime_config_path())
    adapter = OpenAIImageAdapter(api_key=os.environ.get("OPENAI_API_KEY"))

    for row in pending:
        attempts = 0
        while True:
            attempts += 1
            try:
                result = adapter.generate(
                    prompt=row["prompt"],
                    model=runtime["model"],
                    size=runtime["size"],
                    quality=runtime["quality"],
                    output_format=runtime["output_format"],
                )
                ext = runtime["output_format"]
                image_name = f"{row['slot']:04d}.{ext}"
                image_path = run_dir / "raw" / image_name
                image_path.parent.mkdir(parents=True, exist_ok=True)
                image_path.write_bytes(result.image_bytes)
                records.append({
                    **row,
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
                    records.append({**row, "status": "failed", "attempts": attempts, "error": repr(exc)})
                    write_jsonl(run_dir / "generation.jsonl", records)
                    break
                time.sleep(min(2 ** attempts, 30))

    generated_count = sum(1 for r in records if r.get("status") == "generated")
    failed_count = sum(1 for r in records if r.get("status") == "failed")
    if failed_count == 0:
        final_status = "completed"
    elif generated_count == 0:
        final_status = "failed"
    else:
        final_status = "partially_completed"
    _update_run_status(run_dir, final_status)


def generate(
    character_id: str | None = None,
    count: int | None = None,
    run_root: Path = Path("runs"),
    dry_run: bool = False,
    resume_run_id: str | None = None,
    seed: int | None = None,
) -> str:
    if resume_run_id is not None:
        run_dir = run_root / resume_run_id
        run_state = read_run_state(run_dir)
        if run_state["status"] in ("completed", "exported"):
            return resume_run_id
        run_id = resume_run_id
        plan_rows = read_jsonl(run_dir / "plan.jsonl")
        existing_records = read_jsonl(run_dir / "generation.jsonl")
    else:
        if character_id is None or count is None:
            raise ValueError("character_id and count are required unless resuming an existing run")
        run_id, run_dir, plan = make_plan(character_id, count, run_root, seed=seed)
        plan_rows = [item.to_dict() for item in plan]
        existing_records = []

    if dry_run:
        return run_id

    _generate_pending(run_dir, plan_rows, existing_records)
    return run_id
