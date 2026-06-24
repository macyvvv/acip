from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SCAN_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".txt"}

@dataclass(frozen=True)
class CheckResult:
    check: str
    ok: bool
    severity: str
    file: str
    detail: str

def iter_text_files():
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file() and path.suffix in SCAN_SUFFIXES:
            yield path

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def pass_result(check: str, detail: str = "passed") -> CheckResult:
    return CheckResult(check, True, "info", "-", detail)

def issue(check: str, file: str, detail: str, severity: str = "error") -> CheckResult:
    return CheckResult(check, False, severity, file, detail)

# Backward-compatible alias for older selftest modules.
def fail(check: str, file: str, detail: str, severity: str = "error") -> CheckResult:
    return issue(check, file, detail, severity)

def print_results(title: str, results: list[CheckResult]) -> int:
    failed = [r for r in results if not r.ok and r.severity == "error"]
    warnings = [r for r in results if not r.ok and r.severity == "warning"]
    print(f"# {title}\n")
    for r in results:
        mark = "PASS" if r.ok else ("WARN" if r.severity == "warning" else "FAIL")
        print(f"[{mark}] {r.check} | {r.file} | {r.detail}")
    print()
    print(f"summary: passed={len([r for r in results if r.ok])} warnings={len(warnings)} failed={len(failed)}")
    return 1 if failed else 0

def markdown_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def internal_markdown_links(text: str):
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for m in pattern.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield target.split("#", 1)[0]

def is_selftest_script(path: Path) -> bool:
    return "scripts" in path.parts and "selftest" in path.parts

def is_template_or_report(path: Path) -> bool:
    name = path.name.upper()
    return "TEMPLATE" in name or "REPORT" in name or "CHECKLIST" in name
