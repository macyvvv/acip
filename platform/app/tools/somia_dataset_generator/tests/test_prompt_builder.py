from somia_dataset_generator.prompt_builder import build_prompt
from somia_dataset_generator.validation import validate_character

def test_prompt_contains_primary_airi_discriminators():
    character = validate_character("specs/characters/airi.yaml")
    prompt = build_prompt(character, {
        "framing": "upper_body",
        "angle": "three_quarter_left",
        "expression": "quietly_tired_neutral",
        "gaze": "lowered",
        "environment": "monitor_glow",
    })
    assert "short-to-medium layered wolf cut" in prompt
    assert "triangular hairpin" in prompt
    assert "no long hair" in prompt
    assert "adult fictional woman" in prompt
