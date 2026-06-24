from pathlib import Path
r=Path(__file__).resolve().parents[1]
req=["basis","adr","wbs","docs","catalog","registry","contracts","runbooks","control",".github"]
import sys
sys.exit(0 if all((r/x).exists() for x in req) else 1)
