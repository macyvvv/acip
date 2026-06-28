from pathlib import Path
import json
def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

R = _resolve_repo_root()
i=R/'runtime'/'loaded_context.json';o=R/'runtime'/'dry_run_adapter_report.md';d=json.loads(i.read_text()) if i.exists() else {};o.write_text(f'# Dry Run Adapter\nsource:{d.get("source","none")}');print(o)
