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
        "content_root": "app/products/kabukicho_survival_map_mvp",
        "product_code_path": "app/products/kabukicho_survival_map_mvp",
        "tracking_issue_numbers": (33, 34, 36),
        "historical_issue_numbers": (),
        "notes": "Location/survival guide product for Kabukicho.",
    },
    {
        "business_id": "somia",
        "display_name": "Somia",
        "status": "active",
        "content_root": "somia",
        "product_code_path": "system/scripts/somia",
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
        "content_root": None,
        "product_code_path": None,
        "tracking_issue_numbers": (),
        "historical_issue_numbers": (),
        "notes": "Provisional slug. Text-only content for Twitter/Threads/note.com, monetized via impressions and affiliate links. No existing code; zero external generation cost, so this is the platform pilot business.",
    },
)


def _path_exists(root: Path, relative: str | None) -> bool:
    if relative is None:
        return False
    return (root / relative).exists()


def build_business_registry(base_path: Path | None = None) -> dict[str, Any]:
    root = Path(base_path) if base_path is not None else get_repo_root()
    records: list[BusinessRecord] = []
    for seed in _SEED_BUSINESSES:
        content_root_exists = _path_exists(root, seed["content_root"])
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
            "system/core/business_registry.py",
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
