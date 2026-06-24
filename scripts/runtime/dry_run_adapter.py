from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
i=R/'runtime'/'loaded_context.json';o=R/'runtime'/'dry_run_adapter_report.md';d=json.loads(i.read_text()) if i.exists() else {};o.write_text(f'# Dry Run Adapter\nsource:{d.get("source","none")}');print(o)
