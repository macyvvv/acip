#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def _load_contract(path: Path) -> dict[str, object]:
    contract: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("  - "):
            if current_key is None:
                continue
            contract.setdefault(current_key, [])  # type: ignore[assignment]
            cast_list = contract[current_key]
            if isinstance(cast_list, list):
                cast_list.append(line[4:])
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            if value:
                contract[key] = value
            else:
                contract[key] = []
    return contract


def main() -> int:
    contract_rel = sys.argv[1] if len(sys.argv) > 1 else "specs/EP-0104/ep_contract.yaml"
    contract_path = ROOT / contract_rel
    if not contract_path.exists():
        print(f"FAIL: missing {contract_rel}")
        return 1
    contract = _load_contract(contract_path)
    required = ["id", "name", "status", "objective", "inputs", "outputs", "validation"]
    missing = [key for key in required if key not in contract]
    if missing:
        print("# EP Contract Validation")
        for key in missing:
            print(f"FAIL: missing {key}")
        return 1
    if contract.get("id") != contract_path.parent.name:
        print("# EP Contract Validation")
        print(f"FAIL: id must be {contract_path.parent.name}")
        return 1
    print("# EP Contract Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
