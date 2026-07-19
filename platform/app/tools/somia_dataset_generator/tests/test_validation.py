from pathlib import Path
import pytest
from somia_dataset_generator.validation import SpecificationError, validate_character

def test_airi_contract_is_valid():
    contract = validate_character("specs/characters/airi.yaml")
    assert contract["character_id"] == "airi"
    assert contract["adult"] is True

def test_invalid_contract_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema_version: '1.1'\ncharacter_id: airi\nadult: false\n", encoding="utf-8")
    with pytest.raises(SpecificationError):
        validate_character(bad)
