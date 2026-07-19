from __future__ import annotations

# SDXL/Illustrious-XL-family checkpoints have a ~75-effective-token budget
# per CLIP encoder chunk (see businesses/somia/content/BRAND/
# PORTRAIT_METHODOLOGY.md's "Token budget" section, and the same lesson
# rediscovered independently for Nao's content 0007 "v5.1 token-budget
# defect" and Yui's v3/v4/v7/v10 portrait regeneration failures). This
# doctrine existed as prose only, with no enforcing code, until it was
# silently violated multiple times in one session -- this module is the
# minimal enforcement mlops recommended, not a general tokenizer.
#
# No `transformers`/`tiktoken` dependency: CLIP's BPE tokenizer isn't a
# drop-in match for GPT-style tokenizers anyway, so a documented word/
# punctuation heuristic is more honest than a precise-looking wrong
# number. This is a warn/refuse guard, not a byte-accurate token counter.

# Calibrated against Yui's actual session history, not just the doctrinal
# ~75-token figure: v6/v8 (~117-120 estimated tokens) rendered ears/hair
# correctly and are this project's known-good baseline, so the refuse
# threshold must sit comfortably above them -- a guard that blocks the
# only working prompt on record is worse than no guard. v10 (~206) is the
# clearly-failed outlier this is meant to catch.
WARN_THRESHOLD = 90
REFUSE_THRESHOLD = 150


def estimate_token_count(text: str) -> int:
    """Cheap heuristic: ~1.3 tokens per whitespace-separated word, which
    approximates BPE sub-word splitting for comma-separated tag prompts
    reasonably well without a real tokenizer dependency."""
    words = text.replace(",", " ").split()
    return int(len(words) * 1.3)


def check_prompt_budget(prompt: str, *, label: str = "prompt") -> None:
    """Warn on stderr past WARN_THRESHOLD; raise past REFUSE_THRESHOLD.
    Callers that intentionally need a longer prompt should catch and
    proceed explicitly rather than silently swallowing this."""
    import sys

    count = estimate_token_count(prompt)
    if count > REFUSE_THRESHOLD:
        raise ValueError(
            f"{label}: estimated ~{count} tokens, over the {REFUSE_THRESHOLD}-token refuse "
            f"threshold (~75-token single-chunk budget per PORTRAIT_METHODOLOGY.md). "
            "Identity-critical tags placed after this point risk truncation/dilution -- "
            "shorten the prompt or split into a separate generation pass."
        )
    if count > WARN_THRESHOLD:
        print(
            f"WARNING: {label} estimated ~{count} tokens, over the {WARN_THRESHOLD}-token "
            "warn threshold -- tags near the end may be truncated or diluted. "
            "Put identity-critical tags (species/ears, hair color, required props) early.",
            file=sys.stderr,
        )
