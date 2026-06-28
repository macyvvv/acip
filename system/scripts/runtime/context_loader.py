from pathlib import Path
import json
def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

R = _resolve_repo_root()
o=R/'runtime'/'loaded_context.json';o.parent.mkdir(exist_ok=True);o.write_text(json.dumps({'source':'repository','runtime':'dry-run'}));print(o)
