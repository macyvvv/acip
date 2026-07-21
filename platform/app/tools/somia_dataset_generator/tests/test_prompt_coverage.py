"""Prompt Coverage Test (design doc §5): the structural guard against the
class of bug this whole revision started from -- a character-spec field
(`reference_interpretation`, `identity_priority_note`) declared required by
the schema, reviewed and rewritten by hand, that never actually reached
`build_prompt()`'s output. Three layers:

5.1 static  -- every schema-declared field has an explicit, reviewed disposition.
5.2 dynamic -- fields disposed as prompt content actually reach build_prompt()'s
               output, using synthetic sentinel values (isolates the mechanism
               from any specific character's real wording).
5.3 real    -- the real Airi spec's actual current content is detectably
               present in a real build_prompt() call (the same check the
               original manual review did by hand, now automated).
"""

import json

import pytest

from somia_dataset_generator.paths import character_schema_path, character_spec_path
from somia_dataset_generator.prompt_builder import build_prompt
from somia_dataset_generator.validation import validate_character

# Every top-level field in schemas/character.schema.json must appear here.
# "prompt_fragment": always reaches build_prompt()'s output (unconditionally,
#   or -- for *_register fields -- via the sampled bucket for dict-shaped v2
#   registers, or in full for list-shaped v1 registers).
# "prompt_fragment_conditional": reaches build_prompt()'s output, but which
#   *portion* depends on the sampled dimension bucket (Expression Engine
#   fields).
# "export_only": consumed by the Export stage, not the generation prompt.
# "validation_only": consumed only by schema/dimension validation, never
#   inserted as prompt or caption text.
# "not_prompt_content": bookkeeping/metadata; correctly not prompt content.
FIELD_DISPOSITIONS = {
    "schema_version": "not_prompt_content",
    "character_id": "not_prompt_content",
    "trigger_token": "export_only",
    "adult": "not_prompt_content",
    "identity_lock": "prompt_fragment",
    "outfit_lock": "prompt_fragment",
    "style_lock": "prompt_fragment",
    "expression_register": "prompt_fragment_conditional",
    "environment_register": "prompt_fragment_conditional",
    "allowed_variation": "validation_only",
    "negative_lock": "prompt_fragment",
    "cross_character_exclusions": "prompt_fragment",
    "reference_interpretation": "prompt_fragment",
    "identity_priority_note": "prompt_fragment",
    "caption": "export_only",
}


def _schema_field_names() -> set[str]:
    with character_schema_path().open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    return set(schema["properties"])


# --- 5.1 Static coverage: every schema field has a declared disposition ----


def test_every_schema_field_has_a_declared_disposition():
    schema_fields = _schema_field_names()
    table_fields = set(FIELD_DISPOSITIONS)
    missing_from_table = schema_fields - table_fields
    stale_in_table = table_fields - schema_fields
    assert not missing_from_table, (
        f"schema field(s) {sorted(missing_from_table)} have no entry in FIELD_DISPOSITIONS -- "
        "a new/renamed schema field must be given an explicit disposition (this is the exact "
        "gap that let reference_interpretation/identity_priority_note go dead in v1)"
    )
    assert not stale_in_table, (
        f"FIELD_DISPOSITIONS has entry/entries {sorted(stale_in_table)} for fields no longer "
        "in the schema -- remove the stale entry"
    )


# --- 5.2 Dynamic coverage: sentinel injection -------------------------------


def _minimal_character(**overrides) -> dict:
    character = {
        "character_id": "test_char",
        "allowed_variation": ["framing", "angle", "expression", "gaze", "environment"],
        "identity_lock": ["SENTINEL_IDENTITY_LOCK"],
        "outfit_lock": ["SENTINEL_OUTFIT_LOCK"],
        "style_lock": ["SENTINEL_STYLE_LOCK"],
        "expression_register": ["SENTINEL_EXPRESSION_REGISTER"],
        "environment_register": ["SENTINEL_ENVIRONMENT_REGISTER"],
        "negative_lock": ["SENTINEL_NEGATIVE_LOCK"],
        "cross_character_exclusions": ["SENTINEL_CROSS_CHARACTER_EXCLUSIONS"],
    }
    character.update(overrides)
    return character


def _minimal_dimensions(**overrides) -> dict:
    dimensions = {
        "framing": "close_up", "angle": "front",
        "expression": "neutral", "gaze": "lowered", "environment": "quiet_desk",
    }
    dimensions.update(overrides)
    return dimensions


@pytest.mark.parametrize(
    "field, sentinel",
    [
        ("identity_lock", "SENTINEL_IDENTITY_LOCK"),
        ("outfit_lock", "SENTINEL_OUTFIT_LOCK"),
        ("style_lock", "SENTINEL_STYLE_LOCK"),
        ("negative_lock", "SENTINEL_NEGATIVE_LOCK"),
        ("cross_character_exclusions", "SENTINEL_CROSS_CHARACTER_EXCLUSIONS"),
    ],
)
def test_prompt_fragment_field_reaches_the_prompt(field, sentinel):
    character = _minimal_character()
    prompt = build_prompt(character, _minimal_dimensions())
    assert sentinel in prompt, f"{field}'s content did not reach build_prompt()'s output"


@pytest.mark.parametrize(
    "field, label",
    [
        ("reference_interpretation", "REFERENCE INTERPRETATION"),
        ("identity_priority_note", "IDENTITY PRIORITY NOTE"),
    ],
)
def test_dead_field_reaches_the_prompt_when_present(field, label):
    sentinel = f"SENTINEL_{field.upper()}, this is a full sentence."
    character = _minimal_character(**{field: sentinel})
    prompt = build_prompt(character, _minimal_dimensions())
    assert f"SENTINEL_{field.upper()}" in prompt, f"{field} did not reach build_prompt()'s output"
    assert f"{label}:" in prompt


def test_expression_engine_selects_only_the_sampled_bucket():
    character = _minimal_character(expression_register={
        "bucket_a": "SENTINEL_BUCKET_A",
        "bucket_b": "SENTINEL_BUCKET_B",
    })
    prompt = build_prompt(character, _minimal_dimensions(expression="bucket_a"))
    assert "SENTINEL_BUCKET_A" in prompt
    assert "SENTINEL_BUCKET_B" not in prompt


def test_environment_engine_selects_only_the_sampled_bucket():
    character = _minimal_character(environment_register={
        "bucket_a": "SENTINEL_ENV_A",
        "bucket_b": "SENTINEL_ENV_B",
    })
    prompt = build_prompt(character, _minimal_dimensions(environment="bucket_b"))
    assert "SENTINEL_ENV_B" in prompt
    assert "SENTINEL_ENV_A" not in prompt


# --- 5.3 Real-spec smoke assertion ------------------------------------------


def test_real_airi_spec_prompt_fragment_content_is_detectable():
    """Runs the same check §5.2 does synthetically, but against Airi's real,
    current spec content -- the automated equivalent of the original manual
    review (which grepped final_prompt.txt for specific phrases by hand)."""
    character = validate_character(character_spec_path("airi"))
    dimensions = {
        "framing": "upper_body", "angle": "three_quarter_left",
        "expression": "fragile_softness", "gaze": "lowered", "environment": "dim_private_room",
    }
    prompt = build_prompt(character, dimensions)

    list_fields = ["identity_lock", "outfit_lock", "style_lock", "negative_lock", "cross_character_exclusions"]
    for field in list_fields:
        for item in character[field]:
            assert item in prompt, f"{field} item not found in prompt: {item!r}"

    for field in ["reference_interpretation", "identity_priority_note"]:
        # Rendered text has one trailing period normalized (prompt_builder._render);
        # compare with the same normalization instead of assuming an exact substring.
        assert character[field].rstrip(".") in prompt, f"{field} content not found in prompt"

    # expression_register/environment_register are still list-shaped (v1) in
    # the real Airi spec today, so (unlike the synthetic conditional test
    # above) every item is expected to appear regardless of sampled bucket.
    for field in ["expression_register", "environment_register"]:
        assert isinstance(character[field], list), (
            f"{field} is no longer list-shaped -- update this test to sample-bucket-aware "
            "assertions (see test_expression_engine_selects_only_the_sampled_bucket) if/when "
            "Airi's spec migrates to the v2 dict shape"
        )
        for item in character[field]:
            assert item in prompt, f"{field} item not found in prompt: {item!r}"
