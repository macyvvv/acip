"""Prompt Builder v2 (design doc: prompt_builder_v2_design.md) -- PromptFragment
internal representation, the Expression Engine, dead-field wiring, and the
v1-compatibility golden-output guarantee."""

import pytest

from somia_dataset_generator.planner import create_plan
from somia_dataset_generator.prompt_builder import (
    PromptFragment,
    build_prompt,
    resolve_register,
    validate_dimension_registers,
)


def _minimal_character(**overrides) -> dict:
    character = {
        "character_id": "test_char",
        "schema_version": "1.1",
        "allowed_variation": ["framing", "angle", "expression", "gaze", "environment"],
        "identity_lock": ["identity trait one", "identity trait two"],
        "outfit_lock": ["outfit trait one"],
        "style_lock": ["style trait one"],
        "expression_register": ["expression trait one"],
        "environment_register": ["environment trait one"],
        "negative_lock": ["negative trait one"],
        "cross_character_exclusions": ["exclusion one"],
    }
    character.update(overrides)
    return character


def _minimal_dimensions(**overrides) -> dict:
    dimensions = {
        "framing": "close_up",
        "angle": "front",
        "expression": "neutral",
        "gaze": "lowered",
        "environment": "quiet_desk",
    }
    dimensions.update(overrides)
    return dimensions


# --- PromptFragment / Expression Engine unit tests -------------------------


def test_prompt_fragment_is_a_frozen_dataclass():
    fragment = PromptFragment(category="IDENTITY_LOCK", order=0, text="hello")
    assert fragment.category == "IDENTITY_LOCK"
    assert fragment.order == 0
    assert fragment.text == "hello"
    with pytest.raises(AttributeError):
        fragment.text = "changed"  # frozen


def test_resolve_register_list_shape_is_unconditional():
    character = _minimal_character(expression_register=["a", "b", "c"])
    # sampled bucket is irrelevant for list-shaped (v1) registers
    assert resolve_register(character, "expression", "anything") == "a; b; c"
    assert resolve_register(character, "expression", "") == "a; b; c"


def test_resolve_register_dict_shape_selects_the_sampled_bucket():
    character = _minimal_character(expression_register={"bucket_a": "text A", "bucket_b": "text B"})
    assert resolve_register(character, "expression", "bucket_a") == "text A"
    assert resolve_register(character, "expression", "bucket_b") == "text B"


def test_resolve_register_dict_shape_raises_on_unknown_bucket():
    character = _minimal_character(expression_register={"bucket_a": "text A"})
    with pytest.raises(ValueError, match="no entry for bucket"):
        resolve_register(character, "expression", "bucket_missing")


def test_validate_dimension_registers_passes_for_list_shape():
    character = _minimal_character()
    policy = {"dimensions": {"expression": {"neutral": 1, "sad": 1}}}
    validate_dimension_registers(character, policy)  # must not raise


def test_validate_dimension_registers_passes_when_dict_covers_all_buckets():
    character = _minimal_character(expression_register={"neutral": "n", "sad": "s"})
    policy = {"dimensions": {"expression": {"neutral": 1, "sad": 1}}}
    validate_dimension_registers(character, policy)  # must not raise


def test_validate_dimension_registers_raises_for_incomplete_dict():
    character = _minimal_character(expression_register={"neutral": "n"})
    policy = {"dimensions": {"expression": {"neutral": 1, "sad": 1}}}
    with pytest.raises(ValueError, match="missing entries for buckets"):
        validate_dimension_registers(character, policy)


def test_create_plan_fails_fast_on_incomplete_dict_register_before_any_slot_is_built():
    character = _minimal_character(
        character_id="test_char",
        expression_register={"neutral": "n"},  # missing "sad", which the policy below declares
    )
    policy = {
        "policy_id": "p1",
        "dimensions": {
            "framing": {"close_up": 1},
            "angle": {"front": 1},
            "expression": {"neutral": 1, "sad": 1},
            "gaze": {"lowered": 1},
            "environment": {"quiet_desk": 1},
        },
        "constraints": {},
    }
    with pytest.raises(ValueError, match="missing entries for buckets"):
        create_plan(character, policy, count=4, seed=0)


# --- Dead-field wiring -------------------------------------------------------


def test_reference_interpretation_is_wired_in_when_present():
    character = _minimal_character(reference_interpretation="Use the canonical reference image set.")
    prompt = build_prompt(character, _minimal_dimensions())
    assert "REFERENCE INTERPRETATION: Use the canonical reference image set." in prompt


def test_identity_priority_note_is_wired_in_when_present():
    character = _minimal_character(identity_priority_note="Hair silhouette is the primary discriminator.")
    prompt = build_prompt(character, _minimal_dimensions())
    assert "IDENTITY PRIORITY NOTE: Hair silhouette is the primary discriminator." in prompt


def test_reference_interpretation_fragment_is_omitted_when_absent():
    character = _minimal_character()  # no reference_interpretation key at all
    prompt = build_prompt(character, _minimal_dimensions())
    assert "REFERENCE INTERPRETATION:" not in prompt


def test_identity_priority_note_fragment_is_omitted_when_absent():
    character = _minimal_character()  # no identity_priority_note key at all
    prompt = build_prompt(character, _minimal_dimensions())
    assert "IDENTITY PRIORITY NOTE:" not in prompt


def test_wired_in_fields_do_not_produce_a_double_period():
    character = _minimal_character(
        reference_interpretation="Ends with a period already.",
        identity_priority_note="This one too.",
    )
    prompt = build_prompt(character, _minimal_dimensions())
    assert ".." not in prompt


# --- v1 compatibility: golden-output regression -----------------------------


_GOLDEN_V1_PROMPT = (
    "Create one portrait-oriented LoRA training image of the same adult fictional woman. "
    "IDENTITY LOCK: identity trait one; identity trait two. "
    "OUTFIT LOCK: outfit trait one. "
    "STYLE LOCK: style trait one. "
    "SCENE: framing=close_up; angle=front; expression=neutral; gaze=lowered; environment=quiet_desk. "
    "EXPRESSION REGISTER: expression trait one. "
    "ENVIRONMENT REGISTER: environment trait one. "
    "PROHIBITED: negative trait one; exclusion one. "
    "Preserve identity over scene novelty. Natural adult anatomy, coherent visible hands, no text, no watermark."
)


def test_golden_output_v1_shape_is_byte_identical():
    """The concrete, automatable form of "compatibility with the current
    Builder" (design doc §1.2): a purely v1-shaped character (list-shaped
    registers, no reference_interpretation/identity_priority_note keys)
    must produce exactly this string -- unchanged from v1's actual output
    format. If this test ever fails, v2's fallback path has drifted from v1
    behavior for specs that haven't opted into any v2 shape."""
    character = _minimal_character()
    prompt = build_prompt(character, _minimal_dimensions())
    assert prompt == _GOLDEN_V1_PROMPT
