#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
OUT = ROOT / "graph"
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".txt"}
EXCLUDE_PARTS = {".git", "archive", "__pycache__", ".pytest_cache", ".venv", "venv"}

def is_text(path: Path) -> bool:
    return path.is_file() and path.suffix in TEXT_SUFFIXES and not (set(path.parts) & EXCLUDE_PARTS)

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def node_type(path: Path) -> str:
    r = rel(path)
    if r.startswith("basis/"): return "policy"
    if r.startswith("adr/"): return "adr"
    if r.startswith("wbs/"): return "wbs"
    if r.startswith("runbooks/"): return "runbook"
    if r.startswith("contracts/"): return "contract"
    if r.startswith(".github/workflows/"): return "workflow"
    if r.startswith("scripts/"): return "script"
    if r.startswith("registry/"): return "registry"
    if r.startswith("catalog/"): return "catalog"
    if r.startswith("knowledge/"): return "knowledge_asset"
    if path.name.startswith("README"): return "readme"
    return "document"

def markdown_links(text: str):
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = m.group(1).split("#", 1)[0].strip()
        if target and not target.startswith(("http://", "https://", "mailto:", "#")):
            yield target

def main() -> int:
    nodes = []
    edges = []
    path_to_id = {}

    files = [p for p in ROOT.rglob("*") if is_text(p)]
    for p in files:
        r = rel(p)
        text = p.read_text(encoding="utf-8", errors="ignore")
        nid = r
        path_to_id[r] = nid
        nodes.append({
            "id": nid,
            "type": node_type(p),
            "path": r,
            "title": h1(text) or p.stem,
            "source": "repository",
        })

    for p in files:
        r = rel(p)
        text = p.read_text(encoding="utf-8", errors="ignore")
        for target in markdown_links(text):
            candidate = (p.parent / target).resolve()
            if candidate.exists():
                tr = candidate.relative_to(ROOT).as_posix()
                edges.append({"source": r, "target": tr, "type": "references", "evidence": target})

        for script in re.findall(r"python\s+([A-Za-z0-9_./-]+\.py)", text):
            if (ROOT / script).exists():
                edges.append({"source": r, "target": script, "type": "validates", "evidence": script})

    OUT.mkdir(parents=True, exist_ok=True)
    graph = {"nodes": nodes, "edges": edges}
    (OUT / "repository_graph.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# Repository Graph", "", f"- nodes: {len(nodes)}", f"- edges: {len(edges)}", "", "## Nodes"]
    for n in nodes:
        lines.append(f"- `{n['id']}` ({n['type']}) {n.get('title','')}")
    (OUT / "repository_graph.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"nodes={len(nodes)} edges={len(edges)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
