from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
print("PASS" if (root/"basis").exists() else "FAIL")
