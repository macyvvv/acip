# ADR-0047: Formalize philosophy/psychology/liberal-arts/filmmaker/apparel-stylist as CreativeOps specialists

## Status

Accepted by operator approval on 2026-07-19. Amended same-day by
`platform/adr/ADR-0048-generalize-roles-and-merge-uiux-designops.md`: the
five roles this ADR added were initially written with somia-specific
dependencies baked into their operative instructions; the operator
flagged this as over-fitting to one project, and ADR-0048 generalized
all five (and two other roles from a separate concurrent addition) to
work for any project with analogous content, moving the somia grounding
into an illustrative Example section instead.

## Context

During content 0007's production (Nao's first episode, "Window"), five
review lenses were used repeatedly as ad hoc direct `Agent` prompts with
explicit framing instructions — never via `subagent_type`, since no role
definition existed for any of them:

- **Philosopher** — root-caused Act 2's gaze-lock defect to the reference
  portrait's frontal gaze fighting the video model's gaze-preservation,
  and grounded `BRAND_IDENTITY.md`'s Fetishism lever and multiple
  characters' Reference Vocabulary sections in specific philosophical
  sources (Kierkegaard, Sartre's *le regard* for Rena, Laing's
  ontological insecurity for Yui, Derrida's conditional hospitality for
  Mina, and explicit rejections — Buber's I-Thou and Levinas's
  face-to-face ruled out for Rena, 付喪神/tsukumogami ruled out for
  Airi).
- **Psychologist** — caught the Act 1 static-hold defect via cold-viewer
  attention/orienting-response research (most viewers drop off in 1-3s
  without visual change) that no craft-only (color/lighting/sound)
  review was positioned to catch, and pushed the Fetishism lever's
  precise mechanism (real-but-passing want, driven by 幼稚性, no settled
  dependency) toward its current, sharper form.
- **Liberal-arts** — flagged that a held moment "needs something
  arriving/receding inside it, not just periodic wind motion" to
  actually use ma/held-moment technique correctly, and supplied the
  mono-no-aware, kehai, kaimami, and ichigo-ichie vocabulary now written
  into several characters' Reference Vocabulary sections.
- **Filmmaker** — diagnosed why Act 1's 10s hold read as boring rather
  than intentional (fixed via emaki/pillow-shot foreground-disclosure
  technique) and why a continuous camera push-in kept reading as
  restarting/oscillating at act boundaries.
- **Apparel stylist** — diagnosed, across five same-day revisions, why
  specific outfit prompt wording (bare garment names, certain modifier
  combinations) kept pulling the wrong training-data cluster on the
  Illustrious-XL checkpoint, and the fabric-behavior-vs-fabric-name
  distinction that actually fixed it — later confirmed as a transferable,
  checkpoint-level lesson (not Nao-specific) when the same instability
  reproduced across Airi, Rena, and Yui during the four-character
  portrait rollout that followed content 0007.

The operator separately established a **standing rule**: philosopher,
psychologist, and liberal-arts lenses must be included in every somia
scenario/render review, not only at initial concept authoring — already
captured in `.claude/skills/somia-content-definition-of-done/SKILL.md`
and a persistent memory (`feedback_somia_review_lenses.md`). That rule
existed before any of these three had a formal role definition, meaning
every invocation required hand-writing framing instructions from
scratch, with no fixed checklist, no explicit reporting line, and no
guarantee a fresh session would reconstruct the same rigor.

The operator then asked directly to register these as proper agents, and
asked for a review of what else currently-ad-hoc-only should be
formalized — `filmmaker` and `apparel-stylist` are the other two lenses
that had already been invoked as unregistered direct prompts in this same
production history and clearly repeat.

## Decision

Add five new interactive specialist roles under `creativeops`:

- `philosophy-review`
- `character-psychology` (distinct from the pre-existing `psychologyops`
  Ops role, which is product-flow human factors — anxiety, decision
  fatigue, UI trust — not narrative/character psychology)
- `liberal-arts-review`
- `filmmaker`
- `apparel-stylist`

All five report to `creativeops`, matching the existing
`sound-design`/`accessibility-review` pattern (a direct specialist, not a
further sub-tier) — the five don't have the tightly-coupled shared-defect-
attribution problem that specifically justified `visualops`'s existence
as a sub-coordinator (ADR-0045's amendment), so no additional
sub-coordinator layer is warranted here.

`philosophy-review`, `character-psychology`, and `liberal-arts-review`
are marked in `creativeops.md` as a **standing required trio** for every
somia scenario/render review, not merely available specialists —
formalizing the rule already in force via `SKILL.md` and memory, now with
an actual role definition and reporting line behind it.

## Boundaries

- `character-psychology` reviews narrative/character psychology in
  rendered somia content; `psychologyops` reviews product-flow human
  factors. Naming was chosen specifically to avoid the two being confused
  or invoked interchangeably.
- `filmmaker` reviews camera/pacing craft; it does not decide
  color/light/sound correctness (existing `visualops` trio +
  `sound-design`) or which generation model/endpoint to use
  (`modelops`/`mlops`).
- `apparel-stylist` reviews outfit/accessory prompt vocabulary; it does
  not decide broader palette/lighting correctness (`color-coordination`/
  `lighting-design`) or content strategy.
- None of these five roles are added to the unattended registry
  (`platform/system/core/agent_role_registry.py`) — interactive-only,
  per the ADR-0039/ADR-0041/ADR-0043/ADR-0044/ADR-0045 pattern.

## Consequences

Benefits:
- The standing philosopher/psychologist/liberal-arts review rule now has
  an actual checklist and reporting line behind it instead of depending
  on the orchestrator reconstructing framing instructions from memory
  each time.
- `filmmaker` and `apparel-stylist` — both of which caught real,
  otherwise-uncaught defects in content 0007's actual production history
  — get the same standing.
- Lessons already proven transferable across characters (the
  apparel-stylist findings reproducing for Airi/Rena/Yui, not just Nao)
  are now anchored to a role definition (and
  `businesses/somia/content/BRAND/PORTRAIT_METHODOLOGY.md`) instead of
  living only in session memory.

Costs:
- Five more role definitions to keep coherent — `creativeops` now
  coordinates eleven specialists total (up from six), the largest
  fan-out of any Ops role in the repository.
- Real risk of an even-more-crowded review pass if all eleven
  specialists are invoked on every piece regardless of relevance —
  `creativeops` should still exercise judgment about which specialists a
  given review actually needs, except for the three-lens standing rule,
  which is not optional.

## Rejected Alternatives

- A `visualops`-style sub-coordinator nested under `creativeops` for the
  three narrative-depth roles (philosophy/psychology/liberal-arts):
  rejected — `visualops` exists specifically because
  `color-coordination`/`lighting-design`/`visual-effects` can genuinely
  disagree about which of them explains the *same* on-screen defect
  (shared-attribution problem). Philosophy/psychology/liberal-arts
  reviews operate on different questions (framework fit, viewer-response
  plausibility, technique-grammar correctness) that don't collide the
  same way — no incident in 0007's history showed two of these three
  disputing ownership of one finding.
- Merge `character-psychology` into the existing `psychologyops` role
  instead of a new name: rejected — `psychologyops`'s entire scope
  (anxiety reduction, decision fatigue, UI trust, commitment friction) is
  product-flow, not narrative content; conflating them risks either
  diluting `psychologyops`'s product focus or under-serving somia's
  actual need, and the operator's own framing treated these as
  clearly distinct lenses.
- Single combined "narrative-depth" role covering philosophy + psychology
  + liberal arts: rejected — same reasoning ADR-0045 already used against
  a single combined "art-review" role; the three are different enough
  disciplines (formal philosophical argument, psychological/behavioral
  plausibility, cultural/literary technique) that a single generalist
  role reproduces the shallow-coverage problem ADR-0041 rejected for
  business/product/legal.

## Validation

- Each new role has a unique frontmatter name and explicit reporting
  line to `creativeops`.
- `creativeops.md` lists all five in its `Manages:` line and its "Agents
  you manage" section, and marks the three-lens standing rule explicitly.
- Automated registry remains unchanged (none of the five added).
