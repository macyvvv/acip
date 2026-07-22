from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import collect  # noqa: E402
import collect_batch  # noqa: E402


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _mixed_fetcher(url: str, user_agent: str) -> collect.FetchResult:
    if "example-store-b" in url:
        raise TimeoutError("simulated network failure")
    body = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    return collect.FetchResult(url=url, status=200, body=body)


def test_batch_isolates_failures_and_continues(tmp_path: Path) -> None:
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps(
            [
                {"store_id": "example-store-a", "url": "https://example-store-a.invalid/", "name_hint": "A"},
                {"store_id": "example-store-b", "url": "https://example-store-b.invalid/", "name_hint": "B"},
                {"store_id": "example-store-c", "url": "https://www.pokepara.jp/some/store", "name_hint": "C (denied)"},
            ]
        ),
        encoding="utf-8",
    )
    cache_root = tmp_path / "cache"

    summary = collect_batch.run_batch(candidates_path, cache_root, fetcher=_mixed_fetcher)

    assert summary["total"] == 3
    assert summary["drafted"] == 1
    assert summary["denied"] == 1
    assert summary["other_failure"] == 1

    outcomes = {r["store_id"]: r["outcome"] for r in summary["results"]}
    assert outcomes["example-store-a"] == "drafted"
    assert outcomes["example-store-b"] == "error"
    assert outcomes["example-store-c"] == "denied"

    assert (cache_root / "example-store-a.draft.json").exists()
    assert not (cache_root / "example-store-b.draft.json").exists()
    assert not (cache_root / "example-store-c.draft.json").exists()


def test_batch_summary_is_persisted_to_cache_root(tmp_path: Path) -> None:
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps([{"store_id": "example-store-a", "url": "https://example-store-a.invalid/"}]),
        encoding="utf-8",
    )
    cache_root = tmp_path / "cache"

    collect_batch.run_batch(candidates_path, cache_root, fetcher=_mixed_fetcher)

    saved = json.loads((cache_root / "batch_summary.json").read_text(encoding="utf-8"))
    assert saved["total"] == 1
    assert saved["results"][0]["store_id"] == "example-store-a"
