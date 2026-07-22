"""Batch runner for collect.py -- fetch+draft many stores in one pass.

Candidate discovery (finding a store's own official site/SNS URL) is
NOT automated by this tool: there is no search-API credential in this
environment, and fetching a third-party aggregator site for discovery
purposes would still mean requesting a denied domain -- collect.py's
assert_allowed() refuses that regardless of intent. Candidates must be
compiled by a human/LLM web-search pass first (see
artifacts/ueno-pilot-2026-07-21/README.md for how the Ueno list here was
built) and supplied as a JSON list:

    [{"store_id": "...", "url": "...", "name_hint": "..."}, ...]

Every candidate goes through the same source-register check, fetch, and
draft pipeline as a single `collect.py` run -- this only adds looping,
per-item error isolation (one bad URL never stops the batch), and a
summary. Output is still always DRAFT-only; nothing here promotes a
record into data/stores/.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import collect

TOOL_ROOT = Path(__file__).resolve().parent


def run_batch(
    candidates_path: Path,
    cache_root: Path,
    fetcher: collect.Fetcher = collect.default_fetcher,
) -> dict:
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    results: list[dict] = []

    for candidate in candidates:
        store_id = candidate["store_id"]
        url = candidate["url"]
        entry: dict = {"store_id": store_id, "url": url, "name_hint": candidate.get("name_hint")}

        try:
            record = collect.fetch_and_cache(url, store_id, cache_root, fetcher=fetcher)
        except collect.SourceDenied as exc:
            entry.update(outcome="denied", reason=str(exc))
            results.append(entry)
            continue
        except Exception as exc:  # noqa: BLE001 -- isolate failures, keep the batch going
            entry.update(outcome="error", reason=str(exc))
            results.append(entry)
            continue

        if record["outcome"] != "success":
            entry.update(outcome=record["outcome"], http_status=record["http_status"])
            results.append(entry)
            continue

        html = Path(record["raw_path"]).read_text(encoding="utf-8")
        draft = collect.draft_store_artifact(store_id, url, html, record["attempted_at"])
        draft_path = cache_root / f"{store_id}.draft.json"
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        entry.update(
            outcome="drafted",
            draft_path=str(draft_path),
            needs_review=draft["needs_review"],
            phone=draft.get("phone"),
        )
        results.append(entry)

    summary = {
        "total": len(results),
        "drafted": sum(1 for r in results if r["outcome"] == "drafted"),
        "denied": sum(1 for r in results if r["outcome"] == "denied"),
        "other_failure": sum(1 for r in results if r["outcome"] not in ("drafted", "denied")),
        "results": results,
    }
    (cache_root / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch-run store_collector's fetch+draft pipeline.")
    parser.add_argument("candidates", type=Path, help="JSON file: [{store_id, url, name_hint}, ...]")
    parser.add_argument("--cache-root", type=Path, default=TOOL_ROOT / "cache")
    args = parser.parse_args(argv)

    summary = run_batch(args.candidates, args.cache_root)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
    for result in summary["results"]:
        print(f"  {result['outcome']:8s} {result['store_id']:30s} {result['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
