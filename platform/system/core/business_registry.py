from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


@dataclass(frozen=True)
class BusinessRecord:
    business_id: str
    display_name: str
    status: str
    content_root: str | None
    product_code_path: str | None
    tracking_issue_numbers: tuple[int, ...]
    historical_issue_numbers: tuple[int, ...]
    content_root_exists: bool
    product_code_path_exists: bool
    notes: str


_SEED_BUSINESSES: tuple[dict[str, Any], ...] = (
    {
        "business_id": "kabukicho_survival_map",
        "display_name": "Kabukicho Survival Map",
        "status": "active",
        "content_root": "businesses/kabukicho_survival_map/app",
        "product_code_path": "businesses/kabukicho_survival_map/app",
        "tracking_issue_numbers": (33, 34, 36),
        "historical_issue_numbers": (),
        "notes": (
            "Location/survival guide product for Kabukicho. Fixed 2026-07-14: "
            "previously pointed at kabukicho_survival_map_mvp (an earlier, much "
            "smaller, superseded prototype) -- see CLAUDE.md's explicit warning "
            "not to confuse the two. This is the real, from-scratch app."
        ),
    },
    {
        "business_id": "somia",
        "display_name": "Somia",
        "status": "active",
        "content_root": "businesses/platform/somia/content",
        "product_code_path": "platform/system/scripts/somia",
        "tracking_issue_numbers": (45, 46),
        "historical_issue_numbers": (),
        "notes": "AI character media / video content business. Image/video generation roles require paid vendor APIs (fal.ai/Kling).",
    },
    {
        "business_id": "music_platform",
        "display_name": "Music Platform",
        "status": "greenfield",
        "content_root": None,
        "product_code_path": None,
        "tracking_issue_numbers": (),
        "historical_issue_numbers": (32,),
        "notes": "Was PRODUCT-0002 (issue #32), closed and code deleted. Revived as a greenfield business by explicit operator decision. Likely needs paid audio-generation APIs eventually.",
    },
    {
        "business_id": "text_syndicate",
        "display_name": "Text Syndicate",
        "status": "greenfield",
        # Set 2026-07-15 per this business's first real PDCA cycle's own
        # recommendation: with content_root unset, the credential-free
        # git_activity analytics provider had nothing to measure at all,
        # leaving pdca permanently Check-empty. text_syndicate has no
        # product code (still genuinely greenfield -- product_code_path
        # stays None), but its drafted content is real, committed history
        # under this path.
        "content_root": "platform/system/runtime/business_agents/text_syndicate",
        "product_code_path": None,
        "tracking_issue_numbers": (),
        "historical_issue_numbers": (),
        "notes": "Provisional slug. Text-only content for Twitter/Threads/note.com, monetized via impressions and affiliate links. No existing code; zero external generation cost, so this is the platform pilot business.",
    },
    {
        "business_id": "cf_gb_relative_system",
        "display_name": "CF/GB Relative System",
        "status": "greenfield",
        "content_root": "businesses/cf_gb_relative_system/app",
        "product_code_path": "businesses/cf_gb_relative_system/app",
        "tracking_issue_numbers": (),
        "historical_issue_numbers": (),
        "notes": (
            "Greenfield business registered for the Phase -1 enabling work. "
            "The app path is canonical; executable product code is introduced "
            "by the delivery-skeleton work package."
        ),
    },
)


def _path_exists_any(root: Path, *relative_paths: str | None) -> bool:
    return any(_path_exists(root, relative_path) for relative_path in relative_paths)


def _path_exists(root: Path, relative: str | None) -> bool:
    if relative is None:
        return False
    return (root / relative).exists()


def build_business_registry(base_path: Path | None = None) -> dict[str, Any]:
    root = Path(base_path) if base_path is not None else get_repo_root()
    records: list[BusinessRecord] = []
    for seed in _SEED_BUSINESSES:
        content_root = seed["content_root"]
        if seed["business_id"] == "somia":
            content_root_exists = _path_exists_any(root, content_root, "businesses/somia/content")
        else:
            content_root_exists = _path_exists(root, content_root)
        product_code_path_exists = _path_exists(root, seed["product_code_path"])
        records.append(
            BusinessRecord(
                business_id=seed["business_id"],
                display_name=seed["display_name"],
                status=seed["status"],
                content_root=seed["content_root"],
                product_code_path=seed["product_code_path"],
                tracking_issue_numbers=tuple(seed["tracking_issue_numbers"]),
                historical_issue_numbers=tuple(seed["historical_issue_numbers"]),
                content_root_exists=content_root_exists,
                product_code_path_exists=product_code_path_exists,
                notes=seed["notes"],
            )
        )

    drifted = [
        record.business_id
        for record in records
        if record.status == "active"
        and (
            (record.content_root is not None and not record.content_root_exists)
            or (record.product_code_path is not None and not record.product_code_path_exists)
        )
    ]

    registry = {
        "source_artifacts": [
            "platform/system/core/business_registry.py",
        ],
        "summary": {
            "business_count": len(records),
            "active_count": sum(1 for item in records if item.status == "active"),
            "greenfield_count": sum(1 for item in records if item.status == "greenfield"),
            "dormant_count": sum(1 for item in records if item.status == "dormant"),
            "drifted_business_ids": drifted,
        },
        "businesses": [asdict(item) for item in records],
    }
    return registry


def get_business(business_id: str, base_path: Path | None = None) -> BusinessRecord | None:
    registry = build_business_registry(base_path)
    for item in registry["businesses"]:
        if item["business_id"] == business_id:
            return BusinessRecord(**item)
    return None
