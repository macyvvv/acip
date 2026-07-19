"""Validation layer: technical checks + duplicate detection + review record +
coverage validation, run against a completed (or partially completed)
generation run's raw images. Distinct from validation.py, which validates a
character *specification* file, not generated output."""

from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json

from PIL import Image

from .config import load_yaml
from .paths import character_spec_path, runtime_config_path, sampling_policy_path
from .planner import coverage_report, coverage_violations
from .storage import read_jsonl, write_jsonl
from .validation import validate_character


def _parse_size(size: str) -> tuple[int, int]:
    width_str, height_str = size.lower().split("x")
    return int(width_str), int(height_str)


def technical_issues(image_path: Path, runtime: dict) -> list[str]:
    """Returns a list of human-readable technical problems with the image at
    image_path; an empty list means it passed. Never raises -- an unreadable
    file is itself a validation failure, not a crash."""
    if not image_path.exists():
        return [f"missing file: {image_path}"]
    if image_path.stat().st_size == 0:
        return ["zero-byte file"]
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            actual_format = (img.format or "").lower()
            actual_size = img.size
    except Exception as exc:
        return [f"not a readable image: {exc!r}"]

    issues: list[str] = []
    format_aliases = {"jpg": "jpeg"}
    expected_format = runtime["output_format"].lower()
    normalized_expected = format_aliases.get(expected_format, expected_format)
    if actual_format != normalized_expected:
        issues.append(f"format mismatch: expected {expected_format}, got {actual_format}")
    expected_size = _parse_size(runtime["size"])
    if actual_size != expected_size:
        issues.append(f"dimension mismatch: expected {expected_size}, got {actual_size}")
    return issues


def duplicate_groups(records: list[dict]) -> dict[str, list[int]]:
    """Exact-duplicate detection via content hash (sha256, already computed at
    generation time). Returns {sha256: [slot, slot, ...]} for every hash that
    was produced by more than one slot."""
    by_hash: dict[str, list[int]] = defaultdict(list)
    for record in records:
        sha = record.get("sha256")
        if sha:
            by_hash[sha].append(record["slot"])
    return {sha: slots for sha, slots in by_hash.items() if len(slots) > 1}


def validate_run(run_dir: Path) -> dict:
    """Runs the full Validation stage against a run's generated images:
    technical validation, duplicate detection, per-image accept/reject with
    reasons (written to review.jsonl as the audit trail), and coverage
    validation against the character's sampling policy. Returns a summary
    dict; does not raise on validation failures (those are data, not errors)."""
    run_state = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    character_id = run_state["character_id"]
    generation_records = [r for r in read_jsonl(run_dir / "generation.jsonl") if r.get("status") == "generated"]
    runtime = load_yaml(runtime_config_path())

    duplicates = duplicate_groups(generation_records)
    # keep the first occurrence of each duplicate group, flag the rest
    duplicate_slots = {slot for slots in duplicates.values() for slot in slots[1:]}

    review_records = []
    for record in generation_records:
        image_path = run_dir / record["image"]
        issues = technical_issues(image_path, runtime)
        if record["slot"] in duplicate_slots:
            issues = issues + [f"duplicate of an earlier slot (sha256={record['sha256']})"]
        review_records.append({
            "slot": record["slot"],
            "character_id": record.get("character_id"),
            "specification_version": record.get("specification_version"),
            "policy_id": record.get("policy_id"),
            "image": record["image"],
            "sha256": record.get("sha256"),
            "dimensions": record["dimensions"],
            "prompt": record.get("prompt"),
            "accepted": not issues,
            "issues": issues,
        })
    write_jsonl(run_dir / "review.jsonl", review_records)

    accepted_records = [r for r in review_records if r["accepted"]]
    validate_character(character_spec_path(character_id))  # sanity check before scoring coverage
    policy = load_yaml(sampling_policy_path(character_id))
    dimension_names = list(policy["dimensions"])
    coverage = coverage_report(accepted_records, dimension_names)
    violations = coverage_violations(coverage, policy)

    return {
        "run_id": run_state["run_id"],
        "character_id": character_id,
        "accepted": len(accepted_records),
        "rejected": len(review_records) - len(accepted_records),
        "duplicate_groups": duplicates,
        "coverage": coverage,
        "coverage_violations": violations,
    }
