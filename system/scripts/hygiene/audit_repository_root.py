from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ROOT_ALLOWLIST = {
    "README.md",
    "AGENTS.md",
    "VERSION",
    ".gitignore",
    ".env.example",
    "selftest.yml",
}

REFACTOR_CANDIDATE_SUFFIXES = (
    "_PACK.md",
    "MANIFEST.md",
)


@dataclass(frozen=True)
class RootEntry:
    name: str
    kind: str
    status: str


@dataclass(frozen=True)
class RootHygieneAudit:
    allowlist: tuple[str, ...]
    entries: tuple[RootEntry, ...]
    candidates: tuple[str, ...]


def audit_repository_root(root: str | Path = ROOT) -> RootHygieneAudit:
    root_path = Path(root)
    entries = []
    candidates = []
    for path in sorted(root_path.iterdir(), key=lambda item: item.name):
        if path.name.startswith(".git"):
            continue
        if path.name in ROOT_ALLOWLIST:
            entries.append(RootEntry(name=path.name, kind="allowlisted", status="keep"))
        elif path.is_dir():
            entries.append(RootEntry(name=path.name, kind="directory", status="review"))
        else:
            kind = "markdown" if path.suffix == ".md" else "file"
            status = "review"
            if path.suffix == ".md" and (path.name.endswith(REFACTOR_CANDIDATE_SUFFIXES) or path.name.startswith("README_EP")):
                candidates.append(path.name)
            entries.append(RootEntry(name=path.name, kind=kind, status=status))
    return RootHygieneAudit(
        allowlist=tuple(sorted(ROOT_ALLOWLIST)),
        entries=tuple(entries),
        candidates=tuple(sorted(set(candidates))),
    )


def write_root_hygiene_report(report: RootHygieneAudit, md_path: str | Path, json_path: str | Path) -> None:
    md_path = Path(md_path)
    json_path = Path(json_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_lines = ["# ROOT_HYGIENE_REPORT", "", "## Allowlist", ""]
    md_lines.extend(f"- {name}" for name in report.allowlist)
    md_lines.extend(["", "## Candidates", ""])
    md_lines.extend(f"- {name}" for name in report.candidates) or md_lines.append("- none")
    md_lines.extend(["", "## Entries", ""])
    md_lines.extend(f"- {entry.name} ({entry.kind}, {entry.status})" for entry in report.entries)
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
