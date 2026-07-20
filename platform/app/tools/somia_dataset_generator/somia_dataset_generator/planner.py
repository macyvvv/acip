from itertools import combinations
import random

from .models import PlanItem
from .prompt_builder import build_prompt


def _apportion(values: dict[str, int], count: int) -> dict[str, int]:
    """Largest-remainder (Hamilton) apportionment: allocate `count` slots
    across buckets proportional to their policy weights, guaranteeing the
    allocation sums to exactly `count` regardless of the weights' own total
    (so a small ad-hoc --count, e.g. for a CI smoke test, still works, while
    a production-sized --count still gets genuinely proportional stratified
    coverage rather than naive round-robin cycling)."""
    total_weight = sum(values.values())
    if total_weight <= 0:
        raise ValueError("sampling dimension cannot be empty")
    if any(weight < 0 for weight in values.values()):
        raise ValueError("sampling weight/count must be non-negative")
    exact = {name: weight * count / total_weight for name, weight in values.items()}
    allocation = {name: int(share) for name, share in exact.items()}
    remainder = count - sum(allocation.values())
    remainders_desc = sorted(values, key=lambda name: exact[name] - allocation[name], reverse=True)
    for name in remainders_desc[:remainder]:
        allocation[name] += 1
    return allocation


def _stratified_streams(dims: dict[str, dict[str, int]], count: int, seed: int) -> dict[str, list[str]]:
    """One shuffled, proportionally-apportioned stream per dimension, built
    with a seeded RNG so the same (policy, count, seed) always reproduces the
    same plan, while different dimensions don't share an identical shuffle
    pattern (each gets its own sub-seed)."""
    streams: dict[str, list[str]] = {}
    for name, values in dims.items():
        allocation = _apportion(values, count)
        expanded = [bucket for bucket, n in allocation.items() for _ in range(n)]
        rng = random.Random(f"{seed}:{name}")
        rng.shuffle(expanded)
        streams[name] = expanded
    return streams


def coverage_report(records: list[dict], dimension_names: list[str]) -> dict[str, dict[str, int]]:
    """Tally per-dimension bucket counts from a list of dict-like records
    (plan items or accepted generation records). Used both as a planning-time
    sanity check and, post-validation, as the real accepted-coverage report."""
    report: dict[str, dict[str, int]] = {name: {} for name in dimension_names}
    for record in records:
        dimensions = record["dimensions"]
        for name in dimension_names:
            bucket = dimensions.get(name)
            if bucket is None:
                continue
            report[name][bucket] = report[name].get(bucket, 0) + 1
    return report


def coverage_violations(coverage: dict[str, dict[str, int]], policy: dict) -> list[str]:
    """Returns human-readable violation messages for any bucket whose accepted
    count is below the policy's constraints.minimum_per_bucket. Empty list
    means coverage is satisfied. Callers decide when this check applies (e.g.
    a small ad-hoc/smoke-test count is expected to violate it)."""
    minimum = policy.get("constraints", {}).get("minimum_per_bucket", 0)
    if minimum <= 0:
        return []
    violations: list[str] = []
    for dimension_name, buckets in policy["dimensions"].items():
        counted = coverage.get(dimension_name, {})
        for bucket_name in buckets:
            actual = counted.get(bucket_name, 0)
            if actual < minimum:
                violations.append(
                    f"{dimension_name}.{bucket_name}: {actual} accepted, minimum {minimum} required"
                )
    return violations


def pairwise_coverage_report(records: list[dict], dimension_names: list[str]) -> dict[str, dict[str, int]]:
    """Tally counts for every (bucket_a, bucket_b) combination across each
    unordered pair of dimensions. A marginal per-dimension report can hide a
    real gap -- e.g. profile_left always paired with full_body and never
    with close_up, even though both buckets individually meet their minimum
    -- so this is a finer-grained check on top of coverage_report(), not a
    replacement for it."""
    report: dict[str, dict[str, int]] = {}
    for dim_a, dim_b in combinations(dimension_names, 2):
        pair_key = f"{dim_a}*{dim_b}"
        counts: dict[str, int] = {}
        for record in records:
            dimensions = record["dimensions"]
            bucket_a = dimensions.get(dim_a)
            bucket_b = dimensions.get(dim_b)
            if bucket_a is None or bucket_b is None:
                continue
            combo_key = f"{bucket_a}*{bucket_b}"
            counts[combo_key] = counts.get(combo_key, 0) + 1
        report[pair_key] = counts
    return report


def pairwise_coverage_violations(pairwise_coverage: dict[str, dict[str, int]], policy: dict) -> list[str]:
    """Returns human-readable violation messages for any (bucket_a, bucket_b)
    combination whose accepted count is below
    constraints.minimum_per_pair_bucket. Disabled (returns []) unless the
    policy sets a positive threshold -- opt-in the same way
    minimum_per_bucket is, since a full pairwise grid can be large relative
    to a small/smoke-test count."""
    minimum = policy.get("constraints", {}).get("minimum_per_pair_bucket", 0)
    if minimum <= 0:
        return []
    violations: list[str] = []
    dims = policy["dimensions"]
    for dim_a, dim_b in combinations(dims, 2):
        pair_key = f"{dim_a}*{dim_b}"
        counted = pairwise_coverage.get(pair_key, {})
        for bucket_a in dims[dim_a]:
            for bucket_b in dims[dim_b]:
                combo_key = f"{bucket_a}*{bucket_b}"
                actual = counted.get(combo_key, 0)
                if actual < minimum:
                    violations.append(
                        f"{pair_key}: {combo_key} = {actual} accepted, minimum {minimum} required"
                    )
    return violations


def create_plan(character: dict, policy: dict, count: int, seed: int | None = None) -> list[PlanItem]:
    if count <= 0:
        raise ValueError("count must be positive")
    dims = policy["dimensions"]
    resolved_seed = seed if seed is not None else policy.get("seed", 0)
    streams = _stratified_streams(dims, count, resolved_seed)
    items: list[PlanItem] = []
    for slot in range(count):
        selected = {name: streams[name][slot] for name in dims}
        items.append(PlanItem(
            slot=slot + 1,
            character_id=character["character_id"],
            dimensions=selected,
            prompt=build_prompt(character, selected),
            specification_version=character["schema_version"],
            policy_id=policy["policy_id"],
        ))
    return items
