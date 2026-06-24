from __future__ import annotations

from collections import defaultdict, Counter
from pathlib import Path
import re
import importlib.util

from semantic_common import ROOT, Result, Doc, result, markdown_links

REQUIRED_DIRS = [
    "basis", "adr", "wbs", "docs", "catalog", "registry", "contracts",
    "runbooks", "control", "scripts", ".github", ".github/ISSUE_TEMPLATE", ".github/workflows"
]

REQUIRED_FILES = [
    "README_REPOSITORY_COMPLETE_PACK.md",
    "README_AGENT_OS.md",
    "README_RUNTIME_READINESS.md",
    "basis/026_autonomy_first_policy.md",
    "basis/037_autonomous_workflow_policy.md",
    "basis/042_execution_contract_policy.md",
    "basis/046_runtime_readiness_boundary.md",
    "basis/053_repository_selftest_policy.md",
    "basis/061_semantic_selftest_policy.md",
    "adr/ADR-0018-repository-semantic-selftest-v2.md",
    "wbs/WBS-0012-repository-semantic-selftest-v2.md",
    "selftest.yml",
]

def check_required() -> list[Result]:
    out = []
    for d in REQUIRED_DIRS:
        p = ROOT / d
        out.append(result(f"required dir: {d}", p.is_dir(), d, "missing" if not p.is_dir() else "passed"))
    for f in REQUIRED_FILES:
        p = ROOT / f
        out.append(result(f"required file: {f}", p.is_file(), f, "missing" if not p.is_file() else "passed"))
    return out

def check_runtime_boundary(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    fragments = config.get("runtime_boundary", {}).get("prohibited_keyword_fragments", [])
    prohibited = ["".join(x) for x in fragments]
    for d in docs:
        if d.kind in {"archive", "selftest"}:
            continue
        for kw in prohibited:
            if kw in d.text:
                out.append(result("runtime boundary operational keyword", False, d.rel, kw))
    return out or [result("runtime boundary", True)]

def check_human_boundary(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    patterns = config.get("human_boundary", {}).get("prohibited_routine_patterns", [])
    for d in docs:
        if d.kind in {"archive", "selftest", "template"}:
            continue
        lower = d.text.lower()
        for p in patterns:
            if p in lower:
                out.append(result("human boundary routine assignment", False, d.rel, p, "warning"))
    return out or [result("human boundary", True)]

def check_current_objective(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    approved = set(config.get("approved_current_objectives", []))
    patterns = [re.compile(p) for p in config.get("current_objective_declaration_patterns", [])]
    for d in docs:
        if d.kind in {"archive", "template", "selftest"}:
            continue
        for line in d.text.splitlines():
            for pat in patterns:
                m = pat.match(line.strip())
                if not m:
                    continue
                value = m.group(1).strip().strip('"').strip("'")
                if value and value not in approved and value.upper() not in {"TBD", "TODO"}:
                    out.append(result("current objective declaration drift", False, d.rel, value))
    return out or [result("current objective declarations", True)]

def check_duplicates(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    canonical = [d for d in docs if d.kind != "archive"]
    adr_nums = defaultdict(list)
    wbs_nums = defaultdict(list)
    h1s = defaultdict(list)
    for d in canonical:
        if d.h1:
            h1s[d.h1.lower()].append(d.rel)
        m = re.search(r"ADR-(\d{4})", Path(d.rel).name)
        if m:
            adr_nums[m.group(1)].append(d.rel)
        m = re.search(r"WBS-(\d{4})", Path(d.rel).name)
        if m:
            wbs_nums[m.group(1)].append(d.rel)
    for num, paths in adr_nums.items():
        if len(paths) > 1:
            out.append(result("duplicate canonical ADR number", False, ", ".join(paths), num))
    for num, paths in wbs_nums.items():
        if len(paths) > 1:
            out.append(result("duplicate canonical WBS number", False, ", ".join(paths), num))
    for title, paths in h1s.items():
        if len(paths) > 1:
            out.append(result("duplicate H1", False, ", ".join(paths), title, "warning"))
    return out or [result("duplicate detection", True)]

def check_links(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    for d in docs:
        if d.kind == "archive" or not d.path.suffix == ".md":
            continue
        for target in markdown_links(d.text):
            candidate = (d.path.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                out.append(result("internal link escapes repo", False, d.rel, target))
                continue
            if not candidate.exists():
                out.append(result("broken internal link", False, d.rel, target))
    return out or [result("link integrity", True)]

def check_orphans(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    references = Counter()
    by_rel = {d.rel: d for d in docs}
    for d in docs:
        if d.path.suffix != ".md" or d.kind == "archive":
            continue
        for target in markdown_links(d.text):
            candidate = (d.path.parent / target).resolve()
            if candidate.exists():
                references[candidate.relative_to(ROOT).as_posix()] += 1
    for d in docs:
        if d.path.suffix != ".md":
            continue
        if d.kind in {"archive", "entrypoint", "draft", "template", "index", "selftest"}:
            continue
        if not d.h1:
            out.append(result("missing H1", False, d.rel, "markdown document has no H1", "warning"))
        if references[d.rel] == 0 and d.rel.startswith(("basis/", "adr/", "wbs/")):
            out.append(result("unreferenced governance doc", False, d.rel, "no inbound markdown reference", "warning"))
    return out or [result("orphan/dead document detection", True)]

def check_workflows(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    workflows = ROOT / ".github" / "workflows"
    for wf in workflows.glob("*.yml"):
        txt = wf.read_text(encoding="utf-8", errors="ignore")
        for script in re.findall(r"python\s+([A-Za-z0-9_./-]+\.py)", txt):
            if not (ROOT / script).exists():
                out.append(result("workflow-script consistency", False, wf.relative_to(ROOT).as_posix(), f"missing script: {script}"))
    return out or [result("workflow-script consistency", True)]

def check_secrets(docs: list[Doc], config: dict) -> list[Result]:
    out = []
    secret_cfg = config.get("secret_boundary", {})
    allowlist = set(secret_cfg.get("allowlist_files", []))
    patterns = {
        "openai_key": r"sk-[A-Za-z0-9_-]{20,}",
        "github_token": r"gh[pousr]_[A-Za-z0-9_]{20,}",
        "aws_access_key": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----",
    }
    patterns.update(secret_cfg.get("patterns", {}) or {})
    compiled = [(k, re.compile(v)) for k, v in patterns.items()]
    for d in docs:
        if Path(d.rel).name in allowlist:
            continue
        for name, pat in compiled:
            if pat.search(d.text):
                out.append(result("secret boundary", False, d.rel, f"possible {name}"))
    return out or [result("secret boundary", True)]

def build_graph_summary(docs: list[Doc], config: dict) -> list[Result]:
    counts = Counter(d.kind for d in docs)
    detail = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    return [result("semantic classification graph", True, "-", detail)]
