# Logo Spec

## Symbol

- Crescent moon + star (adopted design option 1: minimal, moon outline + single star)

## Color

- Lavender-grey: #A8A4B8
- Black: #111111
- Single color only (white or black depending on background), never both at once

## Minimum Size

- 24px width minimum (mobile legibility floor)

## Asset File

- `businesses/somia/content/BRAND/assets/somia_logo1.png` (added 2026-07-18).
  This is a circular presentation/hero graphic (gradient disc background,
  black moon outline + white star + "somia" wordmark) — it does not itself
  satisfy the "single color only, never both black and white at once"
  overlay-mark rule above. Treat it as source art to extract the actual
  single-color overlay mark from, not as the overlay asset itself.

## Placement

- Default placement: bottom-right

## Opacity

- 60% to 80%

## Size Rules

- Small enough to support content without dominating it
- Must remain legible on mobile and short-form video
- Must not cover the character face area

## Do

- Use as a quiet identity anchor
- Keep placement consistent
- Preserve negative space

## Don't

- Do not make it the focal point
- Do not change symbol geometry per asset
- Do not place it over key facial expressions

## Addendum (2026-07-19, ChatGPT-assisted logo iteration — decisions only,
asset not yet produced into this repo)

A separate design pass (conducted via ChatGPT, not yet materialized as a
new file under `assets/`) iterated the flat monogram further and reached
these additional fixed constraints, layered on top of the rules above:

- **Current flat design is the base canonical** — this iteration refines
  it, does not replace the crescent-moon-outline symbol described above.
- **A group of 3 dots sits to the right of the moon** and their position
  relative to the right edge is fixed — do not reposition them; per the
  operator, their placement is meaningful, not decorative.
- **`somia` wordmark sits below the monogram**, with the moon/wordmark
  size ratio and relative position fixed — future edits may scale the
  whole lockup together (for icon legibility at small sizes) but must
  not change the internal proportions.
- **Icon-scale legibility**: reduce surrounding whitespace and push the
  lockup closer to the canvas edges so the monogram stays legible when
  scaled down to app-icon sizes (e.g. short-form platform profile
  icons).
- **No drop shadow / no embossed or disc-relief treatment** — rejected
  as too three-dimensional against the flat-design mandate.
- **A flat shadow treatment is still an open experimental option** (not
  yet adopted as canonical): a long flat shadow or a background color-
  plane shift, consistent with a fixed light source from the upper-left
  at effectively infinite distance (i.e. a parallel/directional shadow,
  not a point-light falloff) — if pursued, apply this light-source
  convention rather than inventing a new one per asset.
- **Explicitly rejected**: repositioning the moon or the 3 dots,
  changing their relative sizes, adding new elements (e.g. a center
  star beyond what's already specified above), and any dimensional/
  embossed shadow rendering.

This addendum records the decisions; the actual updated flat-lockup
asset (moon + 3 dots + wordmark, edge-scaled for icon use) has not yet
been generated into `assets/` — do not assume it exists until a new
file is added here.

