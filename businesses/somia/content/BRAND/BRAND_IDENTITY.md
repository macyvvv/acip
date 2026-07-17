# Brand Identity

## Concept

Somia is built around relational fetishism and emotional dependency as
the core media concept — this is a business built on repeat viewing, not
an art project. The goal is content people come back to compulsively:

- non-sexual emotional dependency, fetishism, and quiet fixation as the
  actual hook — not softened into generic "wholesome comfort"
  regardless of character register (warm or withdrawn)
- a character who quietly wants to be needed by the viewer, and a
  viewer who wants to keep coming back to her
- presence that feels close, intense, and worth returning to daily

## Brand Hierarchy — the four levers, and the mechanism they drive (2026-07-18)

The brand comes first; the five characters are patterned expressions of
it, not the source of it. Every character-level spec should trace back to
these four emotional levers, not the reverse — when a character's
CHARACTER.md and this document seem to disagree, this document's intent
wins and the character spec should be revised, not the other way around.

**The four levers:**
1. **Fetishism** (relational/emotional, not explicit sexuality — see
   "What Somia Is Not" below).
2. **Immersion** (没入感) — the viewer's sense of actually being present
   in the character's world/moment, not watching it from outside.
3. **Longing/frustration** (もどかしさ) — the "almost, not quite" quality
   already present in every individual character's own Dependency
   Trigger/Failure Condition (Mina's "almost comfort," Nao's "close but
   unreachable," Yui's unresolved anxiety, Rena's withheld access,
   Airi's glimpsed-not-explained interior) — this document now names it
   as the brand-level organizing principle those were all already
   independently expressing, not a coincidence across five separate
   character docs.
4. **Emptiness/hollowness** (空虚さ) — newly named at the brand level;
   **not yet explicitly present in any individual CHARACTER.md.** This is
   a real gap, not something to retrofit into all five characters right
   now by guessing — when a character's spec is next revised or a new
   one authored, reasoning through what "emptiness" means for that
   specific character (not a generic sad/hollow filter) is real design
   work for that moment, not something to rush across all five today.

**The mechanism:** these four levers are staged specifically to produce
**違和感** — a deliberate, productive sense of incongruity/unease — which
is what actually creates the "something about this keeps pulling me
back" pull (何度も見たくなる) this brand is built for. 違和感 is not a
side effect to tolerate; it is the actual mechanism connecting the four
levers to repeat viewing. The cross-character signature technique below
(visual noise at the internal-thought beat) is one concrete tool for
staging it, not the only one — pacing, framing, and the "almost, not
quite" resolution of every piece's final beat are also 違和感-staging
tools already in use.

**The one hard boundary on 違和感**: it must stay on the fetishism/
fascination side of the line, never the fear/dread side — see "What
Somia Is Not" below. The same incongruity technique (a brief disturbance
that resolves, an expression that doesn't fully resolve, a text line
that lingers) reads as *productive* unease when it's clearly relational/
psychological, and as *horror* when it borrows dread-grammar (empty
space implying an unseen threat, a jump/startle beat, text that reads as
a warning rather than a wistful line). Every 違和感-staging decision
should be checked against this distinction explicitly, not assumed safe
because the underlying lever (fetishism, longing) is legitimate.

## Character Age & Identity Policy

- Every character is an adult (18+). This is fixed and non-negotiable in
  every spec, prompt, and generated asset.
- Exact age, name, birthday, and biographical facts are intentionally
  never disclosed — this is deliberate mystery, not an oversight. Do not
  invent or expose a specific age/birthdate/name in any spec or content;
  "adult, otherwise undefined" is the correct and complete answer.
- If a reference image or external material states a specific age,
  treat that detail as discardable noise from that source, not canon —
  it does not override this policy.

## What Somia Is Not

- Not explicit sexuality
- Not interaction dependency
- Not a conversational assistant brand
- Not a general-purpose entertainment platform
- Not horror or suspense. Dim empty spaces, a figure suddenly present,
  and ominous on-screen text read as horror when actually rendered, not
  as intimacy — avoid that visual grammar even if the words look
  atmospheric on the page. Fetishism and dependency are the intended
  hooks; fear is not.

## Brand Philosophy

- Each character has her own relationship-to-dependency angle and her own
  visual environment (see `platform/somia/CHARACTER/*.md`) — e.g. Mina/Nao/Yui read
  warm and domestic, Airi/Rena read moody and withdrawn (dim room,
  screen-glow, quiet control). Both are valid; neither is universal.
- **Cross-character signature technique — visual noise at the moment of
  internal thought.** Every character has exactly one beat per piece
  where her composed exterior briefly lets an internal reaction through
  — a controlled break, not a resolution (see each character's own
  Dependency Trigger / Failure Condition). At that specific beat, a burst
  of visual noise should be perceptible at **consistent
  strength/prominence across all five characters** — this is a brand-wide
  signature, not an Airi-exclusive trait, added 2026-07-18 after review
  found `visual-effects` had incorrectly scoped it to Airi alone. The
  concrete texture of that noise is native to each character's own
  visual world, not a single copy-pasted effect:
  - Airi (digital/screen world): glitch fragments, UI-fragment tears,
    chromatic drift — already documented in her own CHARACTER.md.
  - Nao (natural/elemental world): a brief ripple/refraction distortion
    in light through water or moving fabric, not a digital artifact —
    the "noise" reads as a natural-world disturbance, never a screen
    artifact, to stay inside her elemental register.
  - Mina/Rena/Yui: not yet specified per-character (author when their
    next content piece is planned) — do not invent a texture for them
    speculatively; each needs the same "what's her world's native
    disturbance" reasoning Nao and Airi got, not a generic filler effect.
  - The strength/prominence of the noise burst must match across
    characters even though the texture differs — a barely-visible flicker
    for one character and an overt glitch for another would violate the
    "consistent strength" requirement.
- This technique is a direct application of the 違和感 boundary above: a
  digital-glitch texture forced onto a character whose world has no
  digital elements (e.g. Nao) reads as "something wrong intruding" rather
  than "an internal moment breaking through." Keep the texture native to
  the character's own world specifically to stay on the fascination side
  of that line.
- The character relationship is the product surface.
- Mystery (undisclosed identity/backstory) is a deliberate hook, not a
  gap to be filled in. Dread is the thing to avoid, not mystery itself.
- Hidden backstory exists, but it is not exposed as a narrative dump.
- Visual grammar: intentional lighting (warm lamp glow or cool
  screen-glow, matched to the character), a lived-in space, a personal
  object the character holds (see each character's nurture item), and an
  expression that acknowledges the viewer rather than looking past them.

