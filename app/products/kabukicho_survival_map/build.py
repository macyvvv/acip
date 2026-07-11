from __future__ import annotations

import shutil
from pathlib import Path

# Static-site "build": no bundler, no backend -- per issue #33's constraints
# (no over-engineering). system/runtime/data/kabukicho/ is the canonical data
# source; this copies it plus the static HTML/JS/CSS into two places:
#   - this product dir's own data/ (so index.html can be opened/served locally)
#   - web/public/kabukicho/ (the deployable static bundle)

PRODUCT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PRODUCT_DIR.parents[2]
DATA_SOURCE = REPO_ROOT / "system" / "runtime" / "data" / "kabukicho"
PUBLIC_DIR = REPO_ROOT / "web" / "public" / "kabukicho"

STATIC_FILES = ("index.html", "app.js", "style.css")


def build() -> None:
    if not DATA_SOURCE.exists():
        raise FileNotFoundError(f"Data source not found: {DATA_SOURCE}")

    local_data_dir = PRODUCT_DIR / "data"
    public_data_dir = PUBLIC_DIR / "data"
    local_data_dir.mkdir(parents=True, exist_ok=True)
    public_data_dir.mkdir(parents=True, exist_ok=True)

    for data_file in DATA_SOURCE.glob("*.json"):
        shutil.copy2(data_file, local_data_dir / data_file.name)
        shutil.copy2(data_file, public_data_dir / data_file.name)

    for static_file in STATIC_FILES:
        shutil.copy2(PRODUCT_DIR / static_file, PUBLIC_DIR / static_file)

    print(f"Copied {len(list(DATA_SOURCE.glob('*.json')))} data file(s) to {local_data_dir} and {public_data_dir}")
    print(f"Copied {len(STATIC_FILES)} static file(s) to {PUBLIC_DIR}")


if __name__ == "__main__":
    build()
