"""Resolves specs/config/schemas relative to the installed package location,
not the process's current working directory -- the CLI must behave the same
regardless of the directory it's invoked from."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def character_spec_path(character_id: str) -> Path:
    return PROJECT_ROOT / "specs" / "characters" / f"{character_id}.yaml"


def sampling_policy_path(character_id: str) -> Path:
    return PROJECT_ROOT / "specs" / "sampling" / f"{character_id}_v1.yaml"


def character_schema_path() -> Path:
    return PROJECT_ROOT / "schemas" / "character.schema.json"


def runtime_config_path() -> Path:
    return PROJECT_ROOT / "config" / "runtime.yaml"
