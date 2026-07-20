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
from .planner import (
    coverage_report,
    coverage_violations,
    pairwise_coverage_report,
    pairwise_coverage_violations,
)
from .storage import read_jsonl, write_jsonl
from .validation import validate_character

DEFAULT_NEAR_DUPLICATE_HAMMING_THRESHOLD = 5
DHASH_SIZE = 8


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


def _dhash(image_path: Path, hash_size: int = DHASH_SIZE) -> int:
    """Difference hash: shrink to (hash_size+1) x hash_size grayscale, bit i
    is 1 if pixel i is brighter than its right neighbor in the same row.
    Cheap, dependency-free (Pillow only) perceptual hash -- stable across
    recompression/minor crop/color-shift noise that a byte-exact sha256
    comparison (duplicate_groups) can't catch, which is exactly the gap
    between "identical file" and "the model rendered the same pose twice"."""
    with Image.open(image_path) as img:
        small = img.convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)
        pixels = list(small.getdata())
    bits = 0
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            bits = (bits << 1) | (1 if pixels[row_start + col] > pixels[row_start + col + 1] else 0)
    return bits


def near_duplicate_groups(
    run_dir: Path,
    records: list[dict],
    threshold: int = DEFAULT_NEAR_DUPLICATE_HAMMING_THRESHOLD,
    hash_size: int = DHASH_SIZE,
) -> dict[int, list[int]]:
    """Near-duplicate detection via dHash + Hamming distance over the given
    records (callers pass only the subset not already flagged as an exact
    duplicate). Returns {lowest_slot: [other_slot, ...]} for each cluster of
    perceptually-similar images; each slot appears in at most one group
    (first match wins, scanned in slot order) -- clusters are for reporting
    only and don't need to be a maximal clique."""
    hashes: dict[int, int] = {}
    for record in records:
        image_path = run_dir / record["image"]
        if not image_path.exists():
            continue
        try:
            hashes[record["slot"]] = _dhash(image_path, hash_size)
        except Exception:
            continue

    slots_sorted = sorted(hashes)
    grouped: dict[int, list[int]] = {}
    assigned: set[int] = set()
    for i, slot_a in enumerate(slots_sorted):
        if slot_a in assigned:
            continue
        group = []
        for slot_b in slots_sorted[i + 1 :]:
            if slot_b in assigned:
                continue
            distance = bin(hashes[slot_a] ^ hashes[slot_b]).count("1")
            if distance <= threshold:
                group.append(slot_b)
                assigned.add(slot_b)
        if group:
            grouped[slot_a] = group
            assigned.add(slot_a)
    return grouped


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

    # Near-duplicate detection only scans records not already flagged as an
    # exact duplicate -- no point perceptually re-comparing images we've
    # already decided are byte-identical.
    near_duplicate_candidates = [r for r in generation_records if r["slot"] not in duplicate_slots]
    near_duplicates = near_duplicate_groups(run_dir, near_duplicate_candidates)
    near_duplicate_slots = {slot for slots in near_duplicates.values() for slot in slots}

    review_records = []
    for record in generation_records:
        image_path = run_dir / record["image"]
        issues = technical_issues(image_path, runtime)
        if record["slot"] in duplicate_slots:
            issues = issues + [f"duplicate of an earlier slot (sha256={record['sha256']})"]
        elif record["slot"] in near_duplicate_slots:
            issues = issues + ["near-duplicate of an earlier slot (perceptual hash match)"]
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
    pairwise_coverage = pairwise_coverage_report(accepted_records, dimension_names)
    pairwise_violations = pairwise_coverage_violations(pairwise_coverage, policy)

    return {
        "run_id": run_state["run_id"],
        "character_id": character_id,
        "accepted": len(accepted_records),
        "rejected": len(review_records) - len(accepted_records),
        "duplicate_groups": duplicates,
        "near_duplicate_groups": near_duplicates,
        "coverage": coverage,
        "coverage_violations": violations,
        "pairwise_coverage": pairwise_coverage,
        "pairwise_coverage_violations": pairwise_violations,
    }
