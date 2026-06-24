from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
o=R/'runtime'/'loaded_context.json';o.parent.mkdir(exist_ok=True);o.write_text(json.dumps({'source':'repository','runtime':'dry-run'}));print(o)
