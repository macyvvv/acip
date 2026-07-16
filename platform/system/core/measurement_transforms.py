from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any

from system.core.statistics_engine import validate_study_config


class InvalidMeasurementRecordError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedEventRecord:
    event_name: str
    event_version: str
    event_id: str
    occurred_at: str
    dedup_key: str
    actor_id: str | None
    session_id: str | None
    properties: dict[str, Any]
    received_at: str
    source_artifact: str


@dataclass(frozen=True)
class ValidatedObservationRecord:
    observation_id: str
    study_id: str
    entity_id: str
    observed_at: str
    source_channel: str
    record_locator: str
    measures: dict[str, Any]
    quality_flags: tuple[str, ...]
    received_at: str
    source_artifact: str


def _parse_timestamp(value: str, field_name: str) -> str:
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).isoformat()
    except ValueError as exc:
        raise InvalidMeasurementRecordError(f"{field_name} must be ISO-8601: {value}") from exc


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidMeasurementRecordError(f"{name} must be an object")
    return value


def _validate_raw_wrapper(raw: dict[str, Any], record_key: str) -> tuple[dict[str, Any], str, str]:
    record = _require_mapping(record_key, raw.get(record_key))
    received_at = _parse_timestamp(str(raw.get("received_at", "")), "received_at")
    source_artifact = str(raw.get("source_artifact", "")).strip()
    if not source_artifact:
        raise InvalidMeasurementRecordError("source_artifact is required")
    return record, received_at, source_artifact


def validate_raw_event(raw: dict[str, Any]) -> ValidatedEventRecord:
    record, received_at, source_artifact = _validate_raw_wrapper(raw, "event")
    if record.get("schema_version") != "event:v1":
        raise InvalidMeasurementRecordError("event schema_version must be event:v1")
    identity = _require_mapping("event.identity", record.get("identity"))
    properties = _require_mapping("event.properties", record.get("properties"))
    return ValidatedEventRecord(
        event_name=str(record.get("event_name", "")),
        event_version=str(record.get("event_version", "")),
        event_id=str(record.get("event_id", "")),
        occurred_at=_parse_timestamp(str(record.get("occurred_at", "")), "event.occurred_at"),
        dedup_key=str(identity.get("dedup_key", "")),
        actor_id=identity.get("actor_id"),
        session_id=identity.get("session_id"),
        properties=properties,
        received_at=received_at,
        source_artifact=source_artifact,
    )


def validate_raw_observation(raw: dict[str, Any]) -> ValidatedObservationRecord:
    record, received_at, source_artifact = _validate_raw_wrapper(raw, "observation")
    if record.get("schema_version") != "observation:v1":
        raise InvalidMeasurementRecordError("observation schema_version must be observation:v1")
    source = _require_mapping("observation.source", record.get("source"))
    measures = _require_mapping("observation.measures", record.get("measures"))
    quality_flags = tuple(sorted(str(flag) for flag in record.get("quality_flags", ())))
    return ValidatedObservationRecord(
        observation_id=str(record.get("observation_id", "")),
        study_id=str(record.get("study_id", "")),
        entity_id=str(record.get("entity_id", "")),
        observed_at=_parse_timestamp(str(record.get("observed_at", "")), "observation.observed_at"),
        source_channel=str(source.get("channel", "")),
        record_locator=str(source.get("record_locator", "")),
        measures=measures,
        quality_flags=quality_flags,
        received_at=received_at,
        source_artifact=source_artifact,
    )


def _event_identity(record: ValidatedEventRecord) -> str:
    return f"{record.event_name}|{record.event_version}|{record.dedup_key}"


def _pick_latest_revision(records: list[Any], *, id_getter: Any) -> tuple[list[Any], dict[str, list[dict[str, Any]]], int]:
    grouped: dict[str, list[Any]] = {}
    for record in records:
        grouped.setdefault(id_getter(record), []).append(record)
    latest: list[Any] = []
    revision_history: dict[str, list[dict[str, Any]]] = {}
    late_revision_count = 0
    for record_id, revisions in sorted(grouped.items()):
        ordered = sorted(
            revisions,
            key=lambda item: (
                getattr(item, "received_at"),
                getattr(item, "observed_at", None) or getattr(item, "occurred_at"),
                getattr(item, "source_artifact"),
            ),
        )
        latest.append(ordered[-1])
        revision_history[record_id] = [item.__dict__ for item in ordered]
        if len(ordered) > 1:
            late_revision_count += len(ordered) - 1
    return latest, revision_history, late_revision_count


def _coerce_metric_number(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        return float(value)
    raise InvalidMeasurementRecordError(f"metric value is not numeric: {value!r}")


def build_metric_dataset(
    study: dict[str, Any],
    raw_events: list[dict[str, Any]],
    raw_observations: list[dict[str, Any]],
    *,
    replay_seed: str,
) -> dict[str, Any]:
    validate_study_config(study)
    validated_events = [validate_raw_event(item) for item in raw_events]
    validated_observations = [validate_raw_observation(item) for item in raw_observations]
    active_events, event_revision_history, event_late_revisions = _pick_latest_revision(
        validated_events,
        id_getter=_event_identity,
    )
    active_observations, observation_revision_history, observation_late_revisions = _pick_latest_revision(
        validated_observations,
        id_getter=lambda item: item.observation_id,
    )
    metric_name = str(study["primary_metric"]["name"])
    numerator = 0.0
    denominator = 0.0
    for observation in active_observations:
        numerator += _coerce_metric_number(observation.measures.get("affiliate_clicks", 0))
        denominator += _coerce_metric_number(observation.measures.get("eligible_sessions", 0))
    metric_value = 0.0 if denominator == 0 else numerator / denominator
    ordered_observations = [
        {
            "observation_id": item.observation_id,
            "study_id": item.study_id,
            "entity_id": item.entity_id,
            "observed_at": item.observed_at,
            "source_channel": item.source_channel,
            "record_locator": item.record_locator,
            "measures": dict(sorted(item.measures.items())),
            "quality_flags": list(item.quality_flags),
            "received_at": item.received_at,
            "source_artifact": item.source_artifact,
        }
        for item in sorted(active_observations, key=lambda row: (row.observed_at, row.observation_id))
    ]
    ordered_events = [
        {
            "event_name": item.event_name,
            "event_version": item.event_version,
            "event_id": item.event_id,
            "occurred_at": item.occurred_at,
            "dedup_key": item.dedup_key,
            "actor_id": item.actor_id,
            "session_id": item.session_id,
            "properties": dict(sorted(item.properties.items())),
            "received_at": item.received_at,
            "source_artifact": item.source_artifact,
        }
        for item in sorted(active_events, key=lambda row: (row.occurred_at, row.event_id))
    ]
    dataset_material = {
        "study_id": study["study_id"],
        "metric_name": metric_name,
        "replay_seed": replay_seed,
        "observations": ordered_observations,
        "events": ordered_events,
        "numerator": numerator,
        "denominator": denominator,
        "metric_value": metric_value,
    }
    dataset_id = sha256(repr(dataset_material).encode("utf-8")).hexdigest()[:16]
    return {
        "dataset_id": f"metric_{dataset_id}",
        "study_id": study["study_id"],
        "metric_name": metric_name,
        "metric_value": metric_value,
        "numerator": numerator,
        "denominator": denominator,
        "validated_observation_count": len(ordered_observations),
        "validated_event_count": len(ordered_events),
        "replay_seed": replay_seed,
        "late_revision_count": observation_late_revisions + event_late_revisions,
        "observation_revision_history": observation_revision_history,
        "event_revision_history": event_revision_history,
        "observations": ordered_observations,
        "events": ordered_events,
    }
