from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

_KNOWN_PLATFORMS = frozenset({"x", "threads", "notecom"})
_ALLOWED_SOURCE_ROLES = frozenset({"marketing", "doc_creation"})
_REQUIRED_FIELDS = (
    "policy_id",
    "business_id",
    "platform",
    "enabled",
    "provider",
    "allowed_source_roles",
    "max_posts_per_day",
    "authored_by",
    "authored_at",
    "reason",
)


class PublishingPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class PublishingPolicyRecord:
    policy_id: str
    business_id: str
    platform: str
    enabled: bool
    provider: str
    allowed_source_roles: tuple[str, ...]
    max_posts_per_day: int
    max_posts_per_week: int | None
    require_disclosure_tag_for_affiliate_content: bool
    authored_by: str
    authored_at: str
    reason: str


def _policy_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system/runtime/publishing/policy.json"


def _validate_policy_record(raw: dict) -> PublishingPolicyRecord:
    missing = [field for field in _REQUIRED_FIELDS if field not in raw]
    if missing:
        raise PublishingPolicyError(f"Policy entry missing required field(s): {', '.join(missing)}")

    platform = raw["platform"]
    if platform not in _KNOWN_PLATFORMS:
        raise PublishingPolicyError(f"Unknown platform '{platform}'. Known platforms: {sorted(_KNOWN_PLATFORMS)}")

    allowed_source_roles = tuple(raw["allowed_source_roles"])
    disallowed = [role for role in allowed_source_roles if role not in _ALLOWED_SOURCE_ROLES]
    if disallowed:
        raise PublishingPolicyError(
            f"allowed_source_roles contains disallowed role(s) {disallowed}. "
            f"Only {sorted(_ALLOWED_SOURCE_ROLES)} may ever auto-publish."
        )

    max_posts_per_day = raw["max_posts_per_day"]
    if not isinstance(max_posts_per_day, int) or max_posts_per_day <= 0:
        raise PublishingPolicyError("max_posts_per_day must be a positive integer")

    max_posts_per_week = raw.get("max_posts_per_week")
    if max_posts_per_week is not None and (not isinstance(max_posts_per_week, int) or max_posts_per_week <= 0):
        raise PublishingPolicyError("max_posts_per_week must be a positive integer when present")

    return PublishingPolicyRecord(
        policy_id=str(raw["policy_id"]),
        business_id=str(raw["business_id"]),
        platform=str(platform),
        enabled=bool(raw["enabled"]),
        provider=str(raw["provider"]),
        allowed_source_roles=allowed_source_roles,
        max_posts_per_day=max_posts_per_day,
        max_posts_per_week=max_posts_per_week,
        require_disclosure_tag_for_affiliate_content=bool(raw.get("require_disclosure_tag_for_affiliate_content", False)),
        authored_by=str(raw["authored_by"]),
        authored_at=str(raw["authored_at"]),
        reason=str(raw["reason"]),
    )


def load_publishing_policies(base_path: str | Path = ".") -> list[PublishingPolicyRecord]:
    path = _policy_path(base_path)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise PublishingPolicyError(f"{path} is not valid JSON: {exc}") from exc
    return [_validate_policy_record(entry) for entry in raw.get("policies", [])]


def get_publishing_policy(business_id: str, platform: str, base_path: str | Path = ".") -> PublishingPolicyRecord | None:
    """None on missing file, missing entry, a disabled entry, or a malformed
    entry -- absence always means "not authorized." A malformed entry for a
    DIFFERENT business/platform still raises (loudly, at load time) rather
    than being silently skipped, since a broken policy file is itself worth
    surfacing -- but this function itself never returns anything permissive
    by default."""
    for record in load_publishing_policies(base_path):
        if record.business_id == business_id and record.platform == platform:
            return record if record.enabled else None
    return None
