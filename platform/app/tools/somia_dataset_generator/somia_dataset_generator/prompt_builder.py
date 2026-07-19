from __future__ import annotations

def _joined(values: list[str]) -> str:
    return "; ".join(values)

def build_prompt(character: dict, dimensions: dict[str, str]) -> str:
    missing = set(dimensions) - set(character["allowed_variation"])
    if missing:
        raise ValueError(f"Sampling dimensions not authorized by character contract: {sorted(missing)}")
    return (
        "Create one portrait-oriented LoRA training image of the same adult fictional woman. "
        f"IDENTITY LOCK: {_joined(character['identity_lock'])}. "
        f"OUTFIT LOCK: {_joined(character['outfit_lock'])}. "
        f"STYLE LOCK: {_joined(character['style_lock'])}. "
        f"SCENE: framing={dimensions.get('framing', 'unspecified')}; "
        f"angle={dimensions.get('angle', dimensions.get('view', 'unspecified'))}; "
        f"expression={dimensions.get('expression', 'unspecified')}; "
        f"gaze={dimensions.get('gaze', 'natural')}; environment={dimensions.get('environment', 'simple quiet interior')}. "
        f"EXPRESSION REGISTER: {_joined(character['expression_register'])}. "
        f"ENVIRONMENT REGISTER: {_joined(character['environment_register'])}. "
        f"PROHIBITED: {_joined(character['negative_lock'])}; {_joined(character['cross_character_exclusions'])}. "
        "Preserve identity over scene novelty. Natural adult anatomy, coherent visible hands, no text, no watermark."
    )
