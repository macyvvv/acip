from __future__ import annotations
from pathlib import Path
import json
from jsonschema import Draft202012Validator
from .config import load_yaml

class SpecificationError(ValueError):
    pass

def validate_character(character_path: str | Path, schema_path: str | Path = "schemas/character.schema.json") -> dict:
    character = load_yaml(character_path)
    with Path(schema_path).open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    errors = sorted(Draft202012Validator(schema).iter_errors(character), key=lambda e: list(e.path))
    if errors:
        messages = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            messages.append(f"{location}: {error.message}")
        raise SpecificationError("Character specification validation failed:\n" + "\n".join(messages))
    return character
