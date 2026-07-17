from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_SOURCE = REPO_ROOT / "platform" / "system" / "runtime" / "data" / "kabukicho"
PRODUCT_DIR = REPO_ROOT / "businesses" / "kabukicho_survival_map" / "app"
PUBLIC_DIR = REPO_ROOT / "platform" / "web" / "public" / "kabukicho_survival_map"

CATEGORY_FILES = (
    "smoking.json",
    "toilet.json",
    "convenience.json",
    "atm.json",
    "coin_locker.json",
    "lodging.json",
    "karaoke.json",
    "shisha_bar.json",
)
DB_SYNC_SCRIPT = REPO_ROOT / "businesses" / "kabukicho_survival_map" / "app" / "scripts" / "poi_db_sync.py"
BUILD_SCRIPT = REPO_ROOT / "businesses" / "kabukicho_survival_map" / "app" / "build.py"

REQUIRED_FIELDS = (
    "name",
    "lat",
    "lng",
    "description",
    "category",
    "tags",
    "last_updated",
    "reliability_score",
    "source_type",
    "type",
)

VALID_SOURCE_TYPES = {"official", "observed", "inferred"}
VALID_TYPES = {"official", "unofficial"}


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_six_category_files_exist() -> None:
    for filename in CATEGORY_FILES:
        assert (DATA_SOURCE / filename).exists(), f"missing {filename}"


def test_every_entry_matches_issue_33_schema() -> None:
    for filename in CATEGORY_FILES:
        entries = _load(DATA_SOURCE / filename)
        assert len(entries) >= 1, f"{filename} has no entries"
        for entry in entries:
            missing = [field for field in REQUIRED_FIELDS if field not in entry]
            assert not missing, f"{filename}: entry {entry.get('name')} missing {missing}"
            assert isinstance(entry["tags"], list)
            assert 1 <= entry["reliability_score"] <= 5
            assert entry["source_type"] in VALID_SOURCE_TYPES
            assert entry["type"] in VALID_TYPES
            assert isinstance(entry["lat"], (int, float))
            assert isinstance(entry["lng"], (int, float))


def test_unofficial_entries_carry_a_gray_zone_note() -> None:
    # Per issue #33 section 4: unofficial locations must be clearly labeled
    # and carry a disclaimer -- gray_zone_note is this product's mechanism.
    for filename in CATEGORY_FILES:
        for entry in _load(DATA_SOURCE / filename):
            if entry["type"] == "unofficial":
                assert entry.get("gray_zone_note"), f"{filename}: unofficial entry {entry['name']} has no gray_zone_note"


def test_build_output_matches_source() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True)

    for filename in CATEGORY_FILES:
        source = _load(DATA_SOURCE / filename)
        local_copy = PRODUCT_DIR / "data" / filename
        public_copy = PUBLIC_DIR / "data" / filename
        assert local_copy.exists(), f"run build.py -- missing {local_copy}"
        assert public_copy.exists(), f"run build.py -- missing {public_copy}"
        assert _load(local_copy) == source
        assert _load(public_copy) == source


def test_db_export_preserves_runtime_json_shape() -> None:
    subprocess.run([sys.executable, str(DB_SYNC_SCRIPT), "import-json"], check=True)
    subprocess.run([sys.executable, str(DB_SYNC_SCRIPT), "export-json"], check=True)

    for filename in CATEGORY_FILES:
        source = _load(DATA_SOURCE / filename)
        assert len(source) >= 1
        for entry in source:
            missing = [field for field in REQUIRED_FIELDS if field not in entry]
            assert not missing, f"{filename}: entry {entry.get('name')} missing {missing}"


def test_nearby_duplicate_gate() -> None:
    subprocess.run(
        [
            sys.executable,
            str(DB_SYNC_SCRIPT),
            "check-nearby",
            "--threshold-m",
            "40",
            "--hard-m",
            "8",
            "--similar-name-threshold",
            "0.64",
            "--similar-name-radius-m",
            "140",
            "--max-hard-duplicates",
            "10",
        ],
        check=True,
    )


def test_public_build_has_static_files() -> None:
    for filename in ("index.html", "app.js", "style.css"):
        assert (PUBLIC_DIR / filename).exists(), f"run build.py -- missing {filename} in {PUBLIC_DIR}"
