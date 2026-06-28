from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
CONFIG_PATH = ROOT / "selftest.yml"
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".txt"}

@dataclass(frozen=True)
class Result:
    check: str
    ok: bool
    severity: str
    file: str
    detail: str

@dataclass(frozen=True)
class Doc:
    path: Path
    rel: str
    text: str
    kind: str
    h1: str | None

def result(check: str, ok: bool, file: str = "-", detail: str = "passed", severity: str = "error") -> Result:
    return Result(check, ok, "info" if ok else severity, file, detail)

def load_config() -> dict[str, Any]:
    # Minimal YAML parser for this controlled config shape.
    # Supports top-level sections, nested maps, and list values.
    import yaml  # PyYAML is available in GitHub-hosted runners frequently, but keep fallback below.
    try:
        return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return load_config_fallback()

def load_config_fallback() -> dict[str, Any]:
    # conservative fallback containing required semantics
    return {
        "canonical_space": {"exclude_dirs": ["archive", ".git", "__pycache__"]},
        "entrypoints": ["README.md", "README_REPOSITORY_COMPLETE_PACK.md", "PROJECT.md", "STATE.md", "ROADMAP.md", "CHANGELOG.md", "AGENTS.md"],
        "draft_dirs": ["knowledge/draft"],
        "template_markers": {"filename_contains": ["TEMPLATE", "REPORT", "CHECKLIST", "PROMPT"]},
        "index_markers": {"filename_contains": ["INDEX", "QUEUE", "REGISTRY"]},
        "approved_current_objectives": ["Canonical Asset Production", "Agent OS Foundation", "Repository Operating System Stabilization"],
        "current_objective_declaration_patterns": [r"^Current Objective\s*:\s*(.+)$", r"^current_objective\s*:\s*(.+)$"],
        "runtime_boundary": {"prohibited_keyword_fragments": [["auto", "_post("], ["publish", "_to_platform("], ["run", "_runtime_agent("], ["scrape", "_platform("]]},
        "human_boundary": {"prohibited_routine_patterns": ["human must manually", "human should manually", "human is responsible for routine", "human performs routine"]},
        "secret_boundary": {"allowlist_files": [".env.example"], "patterns": {}},
    }

def is_excluded(path: Path, config: dict[str, Any]) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    excluded = set(config.get("canonical_space", {}).get("exclude_dirs", []))
    return bool(parts & excluded)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def classify(path: Path, text: str, config: dict[str, Any]) -> str:
    r = rel(path)
    if r.startswith("archive/"):
        return "archive"
    for d in config.get("draft_dirs", []):
        if r.startswith(d.rstrip("/") + "/"):
            return "draft"
    fname = path.name.upper()
    for marker in config.get("template_markers", {}).get("filename_contains", []):
        if marker.upper() in fname:
            return "template"
    for marker in config.get("index_markers", {}).get("filename_contains", []):
        if marker.upper() in fname:
            return "index"
    if path.name in set(config.get("entrypoints", [])):
        return "entrypoint"
    if "scripts/selftest" in r or "scripts/selftest_v2" in r:
        return "selftest"
    return "canonical"

def iter_docs(config: dict[str, Any]) -> list[Doc]:
    docs: list[Doc] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if ".git" in path.parts:
            continue
        text = read(path)
        docs.append(Doc(path=path, rel=rel(path), text=text, kind=classify(path, text, config), h1=h1(text)))
    return docs

def markdown_links(text: str):
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for m in pattern.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield target.split("#", 1)[0]

def print_results(title: str, results: list[Result]) -> int:
    failed = [r for r in results if not r.ok and r.severity == "error"]
    warnings = [r for r in results if not r.ok and r.severity == "warning"]
    print(f"# {title}\n")
    for r in results:
        mark = "PASS" if r.ok else ("WARN" if r.severity == "warning" else "FAIL")
        print(f"[{mark}] {r.check} | {r.file} | {r.detail}")
    print()
    print(f"summary: passed={len([r for r in results if r.ok])} warnings={len(warnings)} failed={len(failed)}")
    return 1 if failed else 0
