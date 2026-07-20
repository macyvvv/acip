from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptFragment:
    """One labeled section of the assembled prompt. `order` is a fixed,
    hand-assigned position (v1's existing section order, extended with fixed
    slots for the two newly-wired-in sections) -- not a priority/weighting
    signal. `category` is a plain section identity used to look up its label
    in `_LABELS`."""

    category: str
    order: int
    text: str


_LABELS = {
    "IDENTITY_LOCK": "IDENTITY LOCK",
    "REFERENCE_INTERPRETATION": "REFERENCE INTERPRETATION",
    "OUTFIT_LOCK": "OUTFIT LOCK",
    "STYLE_LOCK": "STYLE LOCK",
    "SCENE": "SCENE",
    "EXPRESSION_REGISTER": "EXPRESSION REGISTER",
    "ENVIRONMENT_REGISTER": "ENVIRONMENT REGISTER",
    "IDENTITY_PRIORITY_NOTE": "IDENTITY PRIORITY NOTE",
    "PROHIBITED": "PROHIBITED",
}

# Fixed category ordering (design doc §2.3). Existing v1 categories keep
# their existing relative order; the two newly-wired-in categories are
# inserted next to the existing section they're topically closest to.
_ORDER = {
    "IDENTITY_LOCK": 0,
    "REFERENCE_INTERPRETATION": 1,
    "OUTFIT_LOCK": 2,
    "STYLE_LOCK": 3,
    "SCENE": 4,
    "EXPRESSION_REGISTER": 5,
    "ENVIRONMENT_REGISTER": 6,
    "IDENTITY_PRIORITY_NOTE": 7,
    "PROHIBITED": 8,
}

_OPENING_SENTENCE = "Create one portrait-oriented LoRA training image of the same adult fictional woman."
_CLOSING_SENTENCE = "Preserve identity over scene novelty. Natural adult anatomy, coherent visible hands, no text, no watermark."


def _joined(values: list[str]) -> str:
    return "; ".join(values)


def resolve_register(character: dict, dimension_name: str, sampled_bucket: str) -> str:
    """Expression Engine lookup (design doc §3.2). `character[<dimension_name>_register]`
    is either:
      - a list (v1 shape) -> the full list is returned, joined, unconditionally
        (identical to v1 behavior, regardless of which bucket was sampled).
      - a dict keyed by sampling-policy bucket names (v2 shape) -> only the
        entry matching `sampled_bucket` is returned. A dict-shaped register is
        a declared commitment to cover every bucket in the matching sampling
        policy dimension, so a missing bucket is a hard error here, not a
        silent fallback -- the same failure posture `build_prompt()` already
        uses for a dimension key that isn't in `allowed_variation`."""
    register = character[f"{dimension_name}_register"]
    if isinstance(register, list):
        return _joined(register)
    if sampled_bucket not in register:
        raise ValueError(
            f"{dimension_name}_register is dict-shaped but has no entry for bucket "
            f"{sampled_bucket!r} (declared buckets: {sorted(register)})"
        )
    return register[sampled_bucket]


def validate_dimension_registers(character: dict, policy: dict) -> None:
    """Exhaustively checks every (dimension, bucket) pair the sampling policy
    can produce against any dict-shaped `<dimension>_register` field, so an
    incomplete v2-shaped register is caught once at plan-creation time --
    before any slot is built or any API call happens -- rather than
    discovered slot-by-slot mid-generation. list-shaped (v1) registers are
    unconditional and need no such check."""
    for dimension_name, buckets in policy["dimensions"].items():
        register_key = f"{dimension_name}_register"
        register = character.get(register_key)
        if not isinstance(register, dict):
            continue
        missing = sorted(set(buckets) - set(register))
        if missing:
            raise ValueError(
                f"{register_key} is dict-shaped but is missing entries for buckets "
                f"{missing} declared in the sampling policy's {dimension_name!r} dimension"
            )


def _build_fragments(character: dict, dimensions: dict[str, str]) -> list[PromptFragment]:
    fragments = [
        PromptFragment("IDENTITY_LOCK", _ORDER["IDENTITY_LOCK"], _joined(character["identity_lock"])),
        PromptFragment("OUTFIT_LOCK", _ORDER["OUTFIT_LOCK"], _joined(character["outfit_lock"])),
        PromptFragment("STYLE_LOCK", _ORDER["STYLE_LOCK"], _joined(character["style_lock"])),
        PromptFragment(
            "SCENE",
            _ORDER["SCENE"],
            f"framing={dimensions.get('framing', 'unspecified')}; "
            f"angle={dimensions.get('angle', dimensions.get('view', 'unspecified'))}; "
            f"expression={dimensions.get('expression', 'unspecified')}; "
            f"gaze={dimensions.get('gaze', 'natural')}; environment={dimensions.get('environment', 'simple quiet interior')}",
        ),
        PromptFragment(
            "EXPRESSION_REGISTER",
            _ORDER["EXPRESSION_REGISTER"],
            resolve_register(character, "expression", dimensions.get("expression", "")),
        ),
        PromptFragment(
            "ENVIRONMENT_REGISTER",
            _ORDER["ENVIRONMENT_REGISTER"],
            resolve_register(character, "environment", dimensions.get("environment", "")),
        ),
        PromptFragment(
            "PROHIBITED",
            _ORDER["PROHIBITED"],
            f"{_joined(character['negative_lock'])}; {_joined(character['cross_character_exclusions'])}",
        ),
    ]

    # Newly-wired-in, optional fields (design doc §4): a v1 spec simply
    # doesn't have these keys, so the fragment is omitted, not an error.
    if character.get("reference_interpretation"):
        fragments.append(
            PromptFragment(
                "REFERENCE_INTERPRETATION",
                _ORDER["REFERENCE_INTERPRETATION"],
                character["reference_interpretation"],
            )
        )
    if character.get("identity_priority_note"):
        fragments.append(
            PromptFragment(
                "IDENTITY_PRIORITY_NOTE",
                _ORDER["IDENTITY_PRIORITY_NOTE"],
                character["identity_priority_note"],
            )
        )

    return fragments


def _render(fragments: list[PromptFragment]) -> str:
    # `reference_interpretation`/`identity_priority_note` are hand-written
    # prose that already end in a period (unlike the joined-phrase fragments,
    # which don't) -- strip one trailing period before adding ours so we
    # never emit "..".
    ordered = sorted(fragments, key=lambda f: f.order)
    return " ".join(f"{_LABELS[f.category]}: {f.text.rstrip('.')}." for f in ordered)


def build_prompt(character: dict, dimensions: dict[str, str]) -> str:
    missing = set(dimensions) - set(character["allowed_variation"])
    if missing:
        raise ValueError(f"Sampling dimensions not authorized by character contract: {sorted(missing)}")
    fragments = _build_fragments(character, dimensions)
    return f"{_OPENING_SENTENCE} {_render(fragments)} {_CLOSING_SENTENCE}"
