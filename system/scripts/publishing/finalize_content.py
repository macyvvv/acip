from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))


class FinalizeContentError(ValueError):
    pass


def _execution_artifact_path(business_id: str, role_id: str, task_id: str, base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system/runtime/business_agents" / business_id / role_id / task_id / "latest.json"


def _finalized_path(business_id: str, role_id: str, task_id: str, platform: str, base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system/runtime/publishing/finalized" / business_id / role_id / task_id / f"{platform}.json"


def finalize_content(
    business_id: str,
    role_id: str,
    task_id: str,
    platform: str,
    final_text: str,
    finalized_by: str,
    base_path: str | Path = ".",
    *,
    reply_to_external_id: str | None = None,
) -> Path:
    """Human-invoked, one-time act: distill an already-executed role's raw
    output into the one exact string that may later be auto-published. This
    is deliberately NOT a re-run through Approval Console/set_execution_
    approval.py -- it names WHAT will post, it never re-authorizes THAT the
    underlying generation may run (that's already been decided by the
    existing execution-approval pipeline, untouched by this file).

    reply_to_external_id: when set, this content publishes as a reply to an
    existing external post (e.g. an X tweet id) rather than a standalone
    post -- used for the reply-engagement growth workflow. The source
    execution artifact requirement is unchanged: even a reply must trace
    back to a real, successfully-executed marketing/doc_creation task (e.g.
    one whose stdout records the reply candidates considered and the target
    post being replied to), not an ad-hoc unlogged string."""
    artifact_path = _execution_artifact_path(business_id, role_id, task_id, base_path)
    if not artifact_path.exists():
        raise FinalizeContentError(
            f"No execution artifact at {artifact_path} -- the task must have actually run "
            f"through the existing approve->execute pipeline before its output can be finalized."
        )
    artifact = json.loads(artifact_path.read_text())
    if not artifact.get("success"):
        raise FinalizeContentError(
            f"Execution artifact at {artifact_path} does not show success=true -- "
            f"refusing to finalize content from a failed or incomplete run."
        )

    source_execution_hash = hashlib.sha256(str(artifact.get("stdout") or "").encode("utf-8")).hexdigest()
    payload = {
        "business_id": business_id,
        "role_id": role_id,
        "task_id": task_id,
        "platform": platform,
        "final_text": final_text,
        "reply_to_external_id": reply_to_external_id,
        "source_execution_hash": source_execution_hash,
        "finalized_by": finalized_by,
        "finalized_at": datetime.now(timezone.utc).isoformat(),
    }
    path = _finalized_path(business_id, role_id, task_id, platform, base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_finalized_content(business_id: str, role_id: str, task_id: str, platform: str, base_path: str | Path = ".") -> dict | None:
    path = _finalized_path(business_id, role_id, task_id, platform, base_path)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finalize the exact, single string that may auto-publish for one platform.")
    parser.add_argument("--business-id", required=True)
    parser.add_argument("--role-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--platform", required=True, choices=["x", "threads", "notecom"])
    parser.add_argument("--final-text-file", required=True, help="Path to a file containing the exact final text to publish.")
    parser.add_argument("--finalized-by", required=True)
    parser.add_argument(
        "--reply-to",
        default=None,
        help="External post id (e.g. an X tweet id) this content replies to, for the reply-engagement workflow. Omit for a standalone post.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    final_text = Path(args.final_text_file).read_text(encoding="utf-8")
    try:
        path = finalize_content(
            args.business_id,
            args.role_id,
            args.task_id,
            args.platform,
            final_text,
            args.finalized_by,
            ROOT,
            reply_to_external_id=args.reply_to,
        )
    except FinalizeContentError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Finalized content written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
