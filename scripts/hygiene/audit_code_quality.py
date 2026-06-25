from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import ast
import json


ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = ("scripts", "orchestrator", "workers", "agent_runtime")


@dataclass(frozen=True)
class CodeQualityFinding:
    path: str
    category: str
    detail: str


@dataclass(frozen=True)
class CodeQualityAudit:
    findings: tuple[CodeQualityFinding, ...]
    checked_files: tuple[str, ...]


def audit_code_quality(root: str | Path = ROOT) -> CodeQualityAudit:
    root_path = Path(root)
    findings = []
    checked_files = []
    for directory in TARGET_DIRS:
        for path in (root_path / directory).rglob("*.py"):
            checked_files.append(path.relative_to(root_path).as_posix())
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            if any(isinstance(node, ast.ImportFrom) and node.level > 0 for node in ast.walk(tree)):
                findings.append(CodeQualityFinding(path=path.as_posix(), category="import_path", detail="relative import used"))
            if "subprocess" in source and "check_call" in source:
                findings.append(CodeQualityFinding(path=path.as_posix(), category="subprocess", detail="subprocess usage present"))
    return CodeQualityAudit(findings=tuple(findings), checked_files=tuple(sorted(set(checked_files))))


def write_code_quality_report(report: CodeQualityAudit, md_path: str | Path, json_path: str | Path) -> None:
    md_path = Path(md_path)
    json_path = Path(json_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_lines = ["# CODE_QUALITY_BASELINE", "", "## Findings", ""]
    if report.findings:
        md_lines.extend(f"- {finding.path}: {finding.category} ({finding.detail})" for finding in report.findings)
    else:
        md_lines.append("- none")
    md_lines.extend(["", "## Checked Files", ""])
    md_lines.extend(f"- {path}" for path in report.checked_files)
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
