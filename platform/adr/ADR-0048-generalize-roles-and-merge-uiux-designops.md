# ADR-0048: Generalize project-locked roles; merge uiux-designops into ux-research

## Status

Accepted by operator approval on 2026-07-19.

## Context

Following ADR-0047 (five new `creativeops` specialists: `philosophy-review`,
`character-psychology`, `liberal-arts-review`, `filmmaker`,
`apparel-stylist`) and a same-day pass reconciling `psychologyops`,
`uiux-designops`, and `web-designops` (three Ops roles added by a
concurrent session building `businesses/music_platform`, not yet
reflected in `opsboard.md`), the operator reviewed the full roster and
raised two distinct concerns:

1. **Roles were written too project-locked.** ADR-0047's five roles
   embedded somia-specific dependencies directly into their operative
   instructions — "Read the specific character's `CHARACTER.md`..." as a
   literal step, hard-coded references to specific somia characters
   (Rena, Airi, Yui, Mina, Nao) inside "What you check"/"Hard rules"
   sections rather than as illustrative grounding. A role definition
   should work for any project with analogous content, using the
   triggering incident as grounding/example, not as a hard dependency on
   one project's file names.
2. **Possible over-fragmentation**, with an explicit, important
   qualification: **"used together" is not a valid merge reason; "same
   responsibility under a different name" is.** The operator specifically
   rejected the reasoning pattern ADR-0047's own "Rejected Alternatives"
   section used (keeping philosophy/psychology/liberal-arts separate
   partly because they don't share VisualOps's same-defect-attribution
   problem) as insufficient grounds *for* merging anything — co-occurrence
   in a review pass says nothing about whether two roles are actually
   the same job.

Auditing the roster against the second criterion found one genuine case:
`ux-research` (`productops.md`, pre-existing) and `uiux-designops`
(added by the concurrent music_platform session) both describe the same
responsibility — user-flow design, usability, information architecture,
accessibility, human-factor risks in product UI — created independently
by different sessions without either checking for the other. This is
exactly "same responsibility, different name," not two roles that merely
work well together.

No other genuine duplicates were found on this pass. Roles that
co-occur or sound similar but check different things were confirmed
distinct and left separate: `character-psychology` (narrative/character
psychology in generated content) vs. `psychologyops` (product-flow human
factors) check fundamentally different things despite both using
"psychology" framing; `philosophy-review`/`character-psychology`/
`liberal-arts-review` check framework-fit, behavioral-plausibility, and
technique-grammar respectively — different questions that happen to be
reviewed together, not the same question asked three ways;
`color-coordination`/`lighting-design`/`visual-effects` are genuinely
distinct crafts (palette, illumination, dynamic technique) that
`visualops` mediates specifically because they can attribute the same
on-screen defect differently — a real coordination need, not evidence
they're actually one job.

## Decision

**Generalize** the following role files: strip hard-coded project
dependencies (literal `CHARACTER.md`/`BRAND_IDENTITY.md` read
instructions, named-character examples) out of operative "What you
check"/"Hard rules"/"What you own" sections, and move the originating
incident into a clearly-marked "Example" section at the end of each
file, explicitly noted as illustrative and not a requirement that the
cited project exists:

- `philosophy-review`, `character-psychology`, `liberal-arts-review`,
  `filmmaker`, `apparel-stylist` (all `creativeops` specialists,
  ADR-0047)
- `psychologyops`, `web-designops` (Ops-level)
- `accessibility-review` (`creativeops` specialist, ADR-0045) — was
  already framed as "for somia" throughout; generalized to "for video/
  short-form content" with the same example-section treatment.

**Merge** `uiux-designops` into the pre-existing `ux-research`
(`productops` specialist): deleted `uiux-designops.md`; folded its
concrete grounding (mobile tap-target size, tooltip ESC/outside-click
behavior, next-action/primary-CTA consistency) into `ux-research.md` as
generalized checklist items plus an Example section; updated
`productops.md`, `opsboard.md`, `CLAUDE.md` role counts and references
accordingly (15 Ops → 14; `uiux-designops` removed from Ops enumeration).

## Boundaries

- Generalizing a role's *language* does not change its *reporting line*
  or its position in the roster — `philosophy-review` etc. still report
  to `creativeops`, `psychologyops`/`web-designops` are still
  standalone Ops.
- The merge criterion this ADR establishes is narrow and specific: two
  roles merge only when their actual scope (not their typical co-usage)
  is the same responsibility. This is not a general mandate to reduce
  role count — `color-coordination`/`lighting-design`/`visual-effects`
  and `philosophy-review`/`character-psychology`/`liberal-arts-review`
  were explicitly reviewed against this criterion and correctly kept
  separate.

## Consequences

Benefits:
- Every `.claude/agents/` role can now be invoked meaningfully for any
  project in this repo with analogous content, not only the one that
  happened to motivate it — the actual point of a reusable role
  definition.
- One fewer role to keep synchronized (`uiux-designops` deleted), and
  the `ux-research`/former-`uiux-designops` overlap can't silently
  diverge into two half-maintained near-duplicates over time.
- The "same responsibility vs. used-together" distinction is now a
  documented, citable standard for future role additions/audits
  (`trainerops` should apply it going forward), rather than a one-off
  judgment call.

Costs:
- Slightly longer files (each now carries an "Example" section in
  addition to the generalized instructions).
- Historical WBS documents in `businesses/music_platform/` that name
  `uiux-designops` as an item owner (`STATIC_MOCK_IMPROVEMENT_WBS.md`,
  `STATIC_MOCK_EXECUTION_REPORT.md`) were deliberately left unedited —
  they're that business's own historical execution record of what was
  actually invoked at the time, not a place to retroactively rewrite
  role names. Future readers of those docs should know `uiux-designops`
  no longer exists as a separate file and map it to `ux-research`.

## Rejected Alternatives

- Keep `uiux-designops` as a thin alias/wrapper pointing to
  `ux-research`: rejected — an alias role that does nothing but
  redirect is exactly the kind of no-real-responsibility fragmentation
  the operator flagged; deleting it outright is more honest than
  keeping a placeholder.
- Retroactively edit `music_platform`'s WBS/execution-report docs to
  rename `uiux-designops` to `ux-research`: rejected — those documents
  record what was actually invoked during that business's real
  execution history; editing them to match a later registry change
  would misrepresent that history.
- Apply the same merge scrutiny to every role pair repo-wide in this
  pass, not just the one the operator's framing directly surfaced:
  rejected — a full exhaustive pairwise audit is a larger, separate
  effort; this pass fixed the specific case found and documented the
  reusable criterion for `trainerops`/future audits to apply
  incrementally rather than blocking on a complete sweep now.

## Validation

- `uiux-designops.md` no longer exists; `ux-research.md` states the
  merge in its own frontmatter description.
- `productops.md`, `opsboard.md`, `CLAUDE.md` all reflect 14 Ops (down
  from 15) and no longer enumerate `uiux-designops`.
- Each generalized file's operative sections (excluding the "Example"
  section) contain no hard-coded reference to a specific business's file
  names (`CHARACTER.md`, `BRAND_IDENTITY.md`) or named characters as a
  requirement — verified by re-reading each file after editing.
