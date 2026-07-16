from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from system.core.measurement_transforms import (
    InvalidMeasurementRecordError,
    build_metric_dataset,
    validate_raw_event,
    validate_raw_observation,
)


def _study() -> dict[str, object]:
    return {
        "schema_version": "study:v1",
        "study_id": "study_revenue_lift_001",
        "question": "Will automated relative-business cards improve affiliate clickthrough rate?",
        "population": "Eligible page sessions on GB relative pages",
        "frame": {
            "description": "Tracked sessions in July 2026",
            "coverage_limitations": ["Bot-filtered traffic excluded"],
        },
        "unit": "session",
        "estimand": {"kind": "proportion", "target": "clickthrough conversion rate"},
        "primary_metric": {
            "name": "ctr",
            "formula": "affiliate_clicks / eligible_sessions",
            "window": "2026-07-01/2026-07-31",
            "timezone": "UTC",
        },
        "precision": {"kind": "ci_half_width", "value": 0.02},
        "stopping": {"rule": "fixed_n", "decision_boundary": "complete at n >= 1200"},
        "sample_size_method": {
            "library": "statistics_engine",
            "version": "v1",
            "inputs": {"baseline_rate": 0.12, "target_half_width": 0.02},
        },
        "missingness": "Late events after 24h cutoff excluded and counted.",
        "analysis_code_version": "analysis:abcdef0",
    }


def _raw_event(event_id: str, dedup_key: str, received_at: str) -> dict[str, object]:
    return {
        "received_at": received_at,
        "source_artifact": f"businesses/cf_gb_relative_system/artifacts/E-009B/{event_id}.json",
        "event": {
            "schema_version": "event:v1",
            "event_name": "affiliate_click",
            "event_version": "v1",
            "event_id": event_id,
            "occurred_at": "2026-07-16T00:00:00Z",
            "identity": {
                "dedup_key": dedup_key,
                "session_id": "sess-001",
                "actor_id": "user-001",
            },
            "properties": {"affiliate_clicks": 1, "eligible_sessions": 1},
        },
    }


def _raw_observation(observation_id: str, affiliate_clicks: int, eligible_sessions: int, received_at: str) -> dict[str, object]:
    return {
        "received_at": received_at,
        "source_artifact": f"businesses/cf_gb_relative_system/artifacts/E-009B/{observation_id}.json",
        "observation": {
            "schema_version": "observation:v1",
            "observation_id": observation_id,
            "study_id": "study_revenue_lift_001",
            "entity_id": f"page:{observation_id}",
            "observed_at": "2026-07-16T00:00:00Z",
            "source": {"channel": "event_log", "record_locator": f"locator:{observation_id}"},
            "measures": {
                "affiliate_clicks": affiliate_clicks,
                "eligible_sessions": eligible_sessions,
            },
            "quality_flags": [],
        },
    }


def test_observation_transform_rejects_missing_source_artifact() -> None:
    raw = _raw_observation("obs_ctr_001", 3, 20, "2026-07-16T00:01:00Z")
    raw["source_artifact"] = ""
    try:
        validate_raw_observation(raw)
    except InvalidMeasurementRecordError as exc:
        assert "source_artifact" in str(exc)
    else:
        raise AssertionError("missing source_artifact should fail closed")


def test_event_transform_deduplicates_identity_to_latest_revision() -> None:
    study = _study()
    dataset = build_metric_dataset(
        study,
        raw_events=[
            _raw_event("evt_affiliate_0001", "sess-001:affiliate_click", "2026-07-16T00:02:00Z"),
            _raw_event("evt_affiliate_0002", "sess-001:affiliate_click", "2026-07-16T00:03:00Z"),
        ],
        raw_observations=[_raw_observation("obs_ctr_001", 3, 20, "2026-07-16T00:01:00Z")],
        replay_seed="seed-a",
    )
    assert dataset["validated_event_count"] == 1
    assert dataset["late_revision_count"] == 1
    history = dataset["event_revision_history"]["affiliate_click|v1|sess-001:affiliate_click"]
    assert len(history) == 2
    assert history[-1]["event_id"] == "evt_affiliate_0002"


def test_metric_transform_seeded_replay_is_identical_under_reordering() -> None:
    study = _study()
    raw_events = [
        _raw_event("evt_affiliate_0001", "sess-001:affiliate_click", "2026-07-16T00:02:00Z"),
        _raw_event("evt_affiliate_0003", "sess-002:affiliate_click", "2026-07-16T00:04:00Z"),
    ]
    raw_observations = [
        _raw_observation("obs_ctr_001", 3, 20, "2026-07-16T00:01:00Z"),
        _raw_observation("obs_ctr_002", 5, 30, "2026-07-16T00:05:00Z"),
    ]
    shuffled_events = list(raw_events)
    shuffled_observations = list(raw_observations)
    random.Random(42).shuffle(shuffled_events)
    random.Random(24).shuffle(shuffled_observations)
    first = build_metric_dataset(study, raw_events, raw_observations, replay_seed="seed-a")
    second = build_metric_dataset(study, shuffled_events, shuffled_observations, replay_seed="seed-a")
    assert first == second


def test_metric_transform_retains_late_observation_revision() -> None:
    study = _study()
    dataset = build_metric_dataset(
        study,
        raw_events=[],
        raw_observations=[
            _raw_observation("obs_ctr_001", 3, 20, "2026-07-16T00:01:00Z"),
            _raw_observation("obs_ctr_001", 4, 20, "2026-07-16T00:06:00Z"),
            _raw_observation("obs_ctr_002", 5, 30, "2026-07-16T00:05:00Z"),
        ],
        replay_seed="seed-b",
    )
    assert dataset["validated_observation_count"] == 2
    assert dataset["late_revision_count"] == 1
    assert dataset["numerator"] == 9.0
    assert dataset["denominator"] == 50.0
    assert abs(dataset["metric_value"] - 0.18) < 1e-12
    history = dataset["observation_revision_history"]["obs_ctr_001"]
    assert len(history) == 2
    assert history[0]["measures"]["affiliate_clicks"] == 3
    assert history[-1]["measures"]["affiliate_clicks"] == 4
