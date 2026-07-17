# ADR-0045: Add CreativeOps and an Art-Department Specialist Layer

## Status

Accepted by operator approval on 2026-07-18. Amended same-day to add a
fifth specialist, `visual-effects` (see Amendment below) — same decision
being completed, not a new independent choice, so folded into this ADR
rather than opened as a separate one.

## Amendment (2026-07-18): `visual-effects`

A full 5-role review of the finished Nao episode (content `0007`) by the
operator, the four original specialists, and the orchestrator surfaced a
capability gap the operator identified directly: neither
`color-coordination` (palette correctness) nor `lighting-design` (light
direction/mood) owns translating a character's *internal psychological
concept* into an actual on-screen visual technique. A character bible can
name a concept precisely (e.g. Airi's "thought leakage," "feelings leak
out of her unconsciously") and still have nothing in the rendered content
that makes a viewer perceive it — both existing specialists could sign
off ("palette correct," "lighting register correct") on content that
never attempts the effect at all.

Added `visual-effects` as a fifth specialist under `creativeops`,
checking whether a character's stated internal-state language is actually
given a concrete technique (glitch fragments, light-streaks,
double-exposure, chromatic drift, etc.) rather than left as unrealized
prose, subject to the same horror-grammar boundary
(`BRAND_IDENTITY.md`) already binding `lighting-design`.

Updated counts: 20 specialists, 33 total interactive roles.

## Context

Producing somia's first flagship episode (content `0007`, see the
`feat/somia-character-reference-sheets` PR) surfaced two real defects that
no existing role owns:

1. Content 0007's original keyframe prompt specified a graphite/dark
   palette that directly contradicted Nao's own `CHARACTER.md` Visual
   Identity (light ocean-blue/white/silver). This shipped as a committed
   spec until caught incidentally while rewriting the scenario for an
   unrelated reason (duration/quality feedback), not by any color-review
   step.
2. `render_content.py`'s video providers never composite on-screen text
   into the final render (a known, documented `spec_deviations` entry on
   every provider). This was solved ad hoc this session (see the
   `compositing-somia-onscreen-text` skill) but nothing had previously
   verified the text was legible/accessible (contrast against a
   variable, moving background; legible at mobile/short-form scale;
   correct behavior for autoplay-muted playback contexts where on-screen
   text is often the only carrier of the line).

Neither `mlops` (pipeline mechanics: does the generation call succeed)
nor `modelops` (which model/vendor to use) owns visual/audio *craft*
correctness — whether the actual color, light, sound, and text choices in
a given piece of content are right, consistent with the character bible,
and perceivable by a real viewer. This is a distinct discipline from
"did the pipeline run" and from "which checkpoint should we use."

## Decision

Add one new interactive Ops role, `creativeops` (the creative-director
function), and four new interactive specialist roles it manages:

- `color-coordination` — verifies a piece of content's actual color
  choices (keyframe prompt, rendered output) match the character's own
  `CHARACTER.md` Visual Identity section; flags contradictions like the
  0007 graphite/light-blue mismatch before render, not after.
- `lighting-design` — verifies lighting direction/mood matches each
  character's established register (e.g. Rena's low-intensity spotlight
  vs. Nao's high-key natural light) and stays internally consistent
  within one piece of content.
- `sound-design` — verifies `audio.json`/script audio notes match each
  character's Audio Traits (frequency range, texture, silence-contrast
  behavior) in `CHARACTER.md`.
- `accessibility-review` — verifies on-screen text is legible (contrast
  against a moving/variable background, size at actual target playback
  scale) and that content functions correctly for autoplay-muted
  playback contexts common on short-form platforms (where on-screen text
  may be the only line a viewer actually receives).

`creativeops` coordinates these four the way other Ops roles coordinate
their specialists (plan sequencing, verify output — cannot itself invoke
them, per the constraint documented in ADR-0043's commit and the other
Ops role files) and owns overall cross-craft cohesion judgment for a
piece of content (do the color/light/sound/text choices work together,
not just individually correct).

Update `opsboard` from eleven to twelve Ops.

## Boundaries

- `creativeops`/its specialists review craft correctness and cohesion;
  they do not decide business/content strategy (that's `businessops`),
  do not pick the underlying model/vendor (`modelops`), and do not run
  the generation pipeline (`mlops`).
- `accessibility-review` here means content perceivability (contrast,
  legibility, autoplay-muted behavior) — not a general software/product
  accessibility audit; that distinction matters because somia is video
  content, not an application UI (`ux-research`/`quality-assurance`
  remain the accessibility owners for actual product UI, e.g.
  kabukicho_survival_map).
- None of these five roles are added to the unattended registry
  (`platform/system/core/agent_role_registry.py`) — interactive-only,
  per the ADR-0039/ADR-0041/ADR-0043/ADR-0044 pattern.

## Consequences

Benefits:
- Both defects that motivated this ADR now have a standing, named owner
  instead of being caught incidentally.
- Color/lighting/sound consistency against each character's bible
  becomes a checkable step, not something that depends on whoever
  happens to be looking at the content that day noticing a mismatch.

Costs:
- Five more role definitions (twelve Ops + nineteen specialists +
  opsboard = 32 roles) to keep coherent.
- `creativeops` risks overlap-confusion with `modelops` (both touch
  "does this look right") if not kept disciplined to its lane: `modelops`
  decides which model to use; `creativeops` decides whether what that
  model produced is craft-correct.

## Rejected Alternatives

- Fold color/lighting/sound review into `mlops`: rejected — `mlops`'s job
  is pipeline reliability (did the call succeed, are artifacts where
  they should be), not craft judgment; conflating them risks neither
  getting real attention.
- Fold this into `modelops`: rejected — `modelops` decides *which model*;
  whether a specific render's color/light/sound is actually correct
  given the model used is a different, per-content judgment call.
- Single combined "art-review" role instead of four specialists under
  one Ops: rejected — color, lighting, sound, and accessibility are
  different enough disciplines (visual vs. audio vs. perceivability)
  that a single generalist role would produce the same shallow-coverage
  problem ADR-0041 already rejected for business/product/legal roles.

## Validation

- Each new role has a unique frontmatter name and explicit reporting
  line (`color-coordination`/`lighting-design`/`sound-design`/
  `accessibility-review` report to `creativeops`; `creativeops` reports
  to `opsboard`).
- `opsboard` recognizes twelve Ops.
- Automated registry remains unchanged.
