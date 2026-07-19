# Script 0035 — "Stays Anyway" (Yui, episode 1)

## Character

Yui

## Design Note (2026-07-19, first production pass — builds into the 0035 stub slot)

0035 was previously a bare 12s single-beat stub ("half-rises to leave,
then settles back down, rabbit pulled to chest"). This version replaces
it entirely with a 4-act + bridge sequence (~40s) staging Yui's full
five-step Daily Loop (notice → anxious → withdraw → hesitate → stays
anyway) as one continuous scene, following the production lessons and
chaining method Nao's 0007 established (per-act keyframe generation,
each act's video conditioned on the prior act's actual last frame, a
closing bridge segment via `fal-ai/kling-video/o1/image-to-video`'s
two-point `start_image_url`/`end_image_url` interpolation).

**Sourced from, and changed from, the ten single-shot stubs (0031–0040):**

- **0031** (notice, freeze-not-retreat, "You're here. I didn't move."):
  kept the freeze-not-retreat structure and the phrase "I didn't move,"
  cut "You're here" — that line addresses the viewer directly
  ("you"), which risks staging the notice beat as acknowledgment-for-
  the-viewer, exactly what `BRAND_IDENTITY.md`'s Fetishism lever
  forbids. Reworded to a self-referential fragment (see Act 2 text).
- **0033** (withdraws, hood stalls half-raised): the physical device
  (hand stalling on the hood, neither finishing nor abandoning the
  motion) is reused for Act 2's withdrawal beat, but retimed and
  re-motivated per Laing rather than staged as hiding-from-the-viewer.
- **0035** (half-rise then resettle, rabbit to chest): the structural
  spine for Acts 3–4 — kept, but split across two acts and slowed down,
  since the stub's single 12s clip compressed hesitate + stays-anyway
  into one beat where this version needs them legible as two.
- **0037** (contained flinch, shoulders draw inward, "Sorry. I'll be
  quieter."): the shoulder-draw-inward physical detail is reused for
  Act 2's withdrawal, but the apology line is cut — an apology is
  addressed outward (implicitly to someone), which is a half-step
  toward the same address-to-viewer problem as 0031's cut line, and
  also risks the "protection satisfaction" failure condition (an
  apology this legible invites a viewer's completed, resolved
  reassurance response).
- **0038** (body half-turns toward an exit, stalls, settles back): the
  Kafka-structure "calculation to leave" is built from this stub's
  device (a turn toward an unseen exit that never completes), retimed
  into Act 3 and re-motivated as private/unspoken rather than
  viewer-directed ("if you—" is cut for the same address-to-viewer
  reason as above). **Revised after philosophy-review**: Kafka's own
  structure (per `YUI.md`'s citation) is specifically a *contingent
  right to remain curdling into "removal would be a relief to
  everyone"* — the calculation always has an implied beneficiary, never
  no one. An earlier draft of this section said the calculation was "a
  kindness to no one in particular," which strips the beneficiary out
  entirely and collapses the Kafka-specific mechanism into generic
  Laing-style self-erasure. Fixed below to keep an implied (unnamed,
  non-viewer-addressed) beneficiary — see Act 3.
- **0039** (fingertips hovering just short of the rabbit, "Maybe it's
  fine. Maybe."): reused close to verbatim for Act 3's text — this
  line was already self-referential and already unresolved by design,
  no address-to-viewer problem, a good fit as-is.
- **0040** (settles into blanket nook, chin on rabbit, released breath,
  no smile, "I didn't disappear this time."): reused for Act 4's
  closing posture and (split, see Text section) closing line — "this
  time" is kept specifically because it already refuses full
  resolution (implies recurrence, not a solved problem), which is
  exactly the Failure Condition's requirement.
- **0032, 0034, 0036**: not drawn on. 0032's window-seat and 0036's
  doorframe settings don't fit the single composite location; 0034's
  rabbit-as-shield raise/lower is a strong device but was judged
  redundant with 0039's fingertip-hover for a hesitation beat and
  would have made Act 3 do two similar gestures instead of one clear
  one.

**Deliberate departure from Nao's 0007 mechanism, stated explicitly for
review:** this episode contains **no acknowledgment-of-the-viewer beat
at all** — Yui never glances toward or tracks the lens, not once,
across any act. Nao's episode built its whole Act 2 around a single
brief attention-catch toward camera direction, and even that
(self-directed, non-address) version drew three rounds of correction
before it read correctly. Given Yui's Dependency Trigger is about
whether she's *allowed to occupy the space* at all — not about the
viewer specifically — the safer and more precise choice is to keep the
camera a witness to a fully private five-beat sequence, never staged as
something happening *toward* anyone. This should make this episode less
exposed to the Fetishism-lever failure mode than 0007's first attempts
were, not more.

**New for this pass — Yui's native signature-disturbance texture**
(`BRAND_IDENTITY.md`'s cross-character noise-burst technique was
unspecified for Yui prior to this piece, to be authored "when their
next content piece is planned" — this is that piece). See Signature
Disturbance section below.

## Review Pass (2026-07-19): findings from philosophy-review,
character-psychology, liberal-arts-review, filmmaker, apparel-stylist,
visual-effects, and sound-design — all applied below, summarized here
for traceability

- **Act 1 legibility gap** (character-psychology + philosophy-review,
  independently): with no acknowledgment-of-viewer beat anywhere in the
  piece, nothing disambiguated "notices presence" from generic anxious
  drift for a cold viewer. Fixed: a non-visual, non-address audio cue
  (a single breath-catch in the ambient bed) now lands at the same
  moment as the gaze-drift, giving the notice beat an external trigger
  without breaking the no-acknowledgment discipline.
- **Act 2's hood-stall held no internal event** (liberal-arts-review):
  the ~3.5s hold relied on on-screen text alone, which is a different
  device from an embodied arriving/receding element — the same
  distinction that ruled out "periodic wind motion" for Nao's Act 1.
  Fixed: continued breath and a faint secondary grip-adjustment now
  occur inside the hold itself.
- **Act 3's Signature Disturbance needed an explicit no-startle guard**
  (liberal-arts-review, horror-boundary risk) and **its "drifts or
  doubles" phrasing was an unresolved either/or, not a committed
  technique** (visual-effects): fixed to one named technique
  (double-exposure ghosting, with an explicit magnitude and frame
  count) plus an explicit no-startle/no-flinch-toward-it instruction
  matching Act 1's own discipline, plus horror-adjacent negative-prompt
  exclusions (see `prompt.md`).
- **The Winnicott/Kafka pairing at Act 3 was asserted more than
  staged** (philosophy-review): fixed with an explicit causal clause —
  the disturbance is now stated as what *arrests* the calculated rise,
  not merely simultaneous with it.
- **Act 4/Bridge structurally over-resolved despite correct
  content-level restraint** (character-psychology): landing the bridge
  on Act 1's *literal* identical first frame, plus describing Act 4's
  camera move as a "release of tension," both work against the
  Failure Condition's "stay a little unresolved" requirement as strong
  formal-closure signals. Fixed: the bridge now holds just short of
  Act 1's exact frame, and the camera language no longer describes
  resolution.
- **A real camera-continuity gap existed at the Act 3→4 boundary**
  (filmmaker): 28.0–30.0s had no stated camera behavior between the
  end of the Acts 1–3 push-in and the start of Act 4's ease-back — an
  underspecified chain-boundary inflection point, the same defect
  class as Nao's Act 3 oscillation. Fixed: Act 4's first ~2s now
  explicitly continues the prior push-in rate before inflecting.
- **The bridge left the rabbit's residual grip differential
  unaddressed** (filmmaker) and **the shared prompt block contradicted
  Act 2's own staging** (apparel-stylist: "held to chest" vs. Act 2's
  "held one-armed" in the same generation call) — both fixed in
  `prompt.md`.
- **No foreground disclosure device across the full ~41s** (filmmaker):
  a single fixed setup with no foreground element risks monotony over
  a longer runtime than Nao's static-hold problem ever ran uncaught.
  Fixed: a near-frame blanket-edge element added, whose position shifts
  slightly across acts (see Camera section).
- **The disturbance's audio analogue was written as a discrete onset
  synced to the visual beat** (sound-design) — for Yui specifically
  this risks reading as *her* voice/breath producing the texture, worse
  than Nao's analogous bird-call risk since the disturbance is
  explicitly not something she causes. Fixed: rewritten as a modulation
  of the continuous room-hush bed rather than a new discrete layer, and
  a real-recording sourcing direction (a processed flutter-echo
  recording) proposed rather than a purely synthetic description — see
  Audio section.
- **`YUI.md` has no Audio Traits section** (sound-design, a real gap
  unlike Nao/Airi/Rena/Mina) — flagged for a follow-up edit to
  `YUI.md` once this episode's audio language is validated, not fixed
  in this file.
- **Hoodie construction language was thinner than the language that
  actually converged on the locked portrait** (apparel-stylist): fixed
  in `prompt.md` to match the fuller, already-approved phrasing.
- Confirmed correct, no change: the "silver-gray hair" wording and its
  negative-prompt inversion (excluding black/brown rather than silver/
  gray) both correctly match the locked reference portrait rather than
  fighting it (apparel-stylist); the Signature Disturbance's core
  grounding in Yui's own established "blurred edges/unstable spacing"
  motif is sound (liberal-arts-review); no reaction-shot pairing and no
  lighting shift accompany the disturbance (visual-effects) — preserve
  both.

## Second Review Pass (2026-07-19, post-render redesign)

The first fully-rendered cut surfaced problems no text-only review had
caught, and drew direct operator feedback that triggered a substantive
rework, not a patch. Findings applied below:

- **Rabbit-dependency vs. viewer protectiveness** (character-psychology):
  a continuously double-arm-embraced comfort object competes with,
  rather than reinforces, the viewer's own protective response — a
  visibly "already held" object satisfies the same perceptual cue that
  would otherwise route to the viewer (the same mechanism `YUI.md`
  already names for narrative over-resolution, just not previously
  applied to the object itself). Fixed: one-armed hold is now the
  baseline across every act (Act 1 included — it was previously the one
  act still using a double-arm embrace at open); Act 3's peak no longer
  uses grip-tightening as the primary visible intensity signal (an
  exposed hand and uneven breath carry the beat instead, grip stays a
  small secondary detail); a partial-release beat is added at the
  Act 2→3 transition, exposing a hand/wrist at a moment of rising, not
  resolved, tension. **Design target this episode is now built toward,
  stated explicitly so it can be checked against**: the viewer should
  feel an unresolved urge to physically steady her — watching someone
  catch themselves mid-fall — paired with knowing she doesn't know
  they're there and the moment never completes into rescue or
  reassurance. Not "I protected her" (satisfaction, a Failure
  Condition). "I wanted to reach in and couldn't."
- **Act 1 fails to hook a cold viewer** (filmmaker): a static-reading
  opening with no perceivable event inside the first ~1-2s (the actual
  swipe-decision window on short-form vertical platforms) and an
  opening pose that's the most visually concealed instant in the whole
  piece. Fixed: the near-frame foreground element (previously a static
  blanket edge) now visibly settles into place in the first ~0.5s, so
  frame one already shows motion before any character beat; the
  push-in's opening rate is bumped above "barely perceptible" for
  roughly the first second before decelerating into the same constant
  low rate that continues through Act 3 (a single deceleration before
  the vector is "established" is not the oscillation/restart defect
  this discipline otherwise guards against); the opening pose is
  marginally less buried (one-armed rabbit hold, per the rebalance
  above, already achieves most of this on its own — more of her face
  and posture reads immediately rather than being hidden behind a
  double-arm hug).
- **Setting changed to a couch, not a floor cushion** (operator
  direction, applied whole-piece rather than left as the accidental
  Act 4 furniture drift an earlier render introduced): a small couch/
  loveseat tucked into the room's corner nook, established from Act 1's
  opening frame and held consistent across every act and the bridge —
  this is a deliberate visual choice, not a defect to fix back to floor
  cushion, see Visual Identity and Timeline below.
- **Portrait re-locked as v3** (apparel-stylist, `YUI.md`, separate from
  this script): true black hair and ordinary human ears, fixed via
  positive construction language (explicit adult-proportion phrasing
  paired with "petite," explicit ear-shape description) rather than
  negation alone, seed pinned for a fair before/after comparison. See
  `YUI.md`'s Visual Identity for the full account.

## Signature Item

**Small white stuffed rabbit, always held.** Yui's equivalent of Nao's
blue teardrop earring — the one recurring, close-in object that must
read as recognizably hers in every piece of her content. Every act's
image prompt must name it explicitly and keep it visible in-frame; her
grip on it changes across acts (see Timeline) but the rabbit itself is
never set down, dropped, or left out of frame. **Held one-armed by
default, not embraced with both arms** (revised 2026-07-19, Second
Review Pass) — a continuously double-arm-held object reads as already
sufficiently protected, competing with rather than inviting the
viewer's own protective response; one arm holding the rabbit against
her side leaves the other hand, her shoulder-line, and more of her
posture visibly exposed and unguarded across every act, including the
opening frame.

## Signature Disturbance (new, authored for this episode)

Yui's world is neither elemental (Nao: water/light refraction) nor
digital (Airi: glitch/UI-tear) — her established visual world is
*spatial*: "a soft room with blurred edges and unstable spacing," per
`YUI.md`'s Visual Identity. Her native disturbance texture is a brief,
localized **loss of coherence in the room's already-soft geometry**,
committed to one specific, named technique (revised after visual-
effects flagged the original "drifts or doubles" phrasing as an
unresolved either/or with no comparably strong training-data analogue
to Nao's/Airi's effects, risking under-rendering to invisibility):
**double-exposure ghosting**. The nearest visible edge of the
cushion-nook (or, if that edge is out of frame at this moment, the
nearest wall line) briefly renders as two near-identical overlapping
lines, offset laterally by roughly 3–5% of frame width, both
simultaneously visible for approximately 4–6 frames at 24fps (under a
quarter second), then the ghost line fades back into the primary line,
returning to a single clean edge — a brief duplicate-then-merge, not a
gradual drift. This is not a digital artifact and not a light/water
effect — it reads as the room's own geometry briefly losing its grip,
which is the direct visual analogue of Winnicott's unintegration (dread
of *coming apart*, not of an absent other): the room's failure to hold
its own coherent shape is the direct cause of the disturbance, the same
way Winnicott's holding-environment failure is what produces
unthinkable anxiety in the first place, not a decorative pairing.
**The disturbance is what arrests her partial rise** (see Act 3) — a
causal relationship, not two events that merely share a timestamp. Per
`BRAND_IDENTITY.md`'s consistency requirement, its strength/prominence
must be perceptible at the same level as Nao's water-ripple and Airi's
glitch burst — not a barely-visible flicker; the frame-count and offset
above are specified for exactly this reason. It occurs exactly once, at
Act 3's most spatially unstable framing (see Timeline), and must not be
paired with or timed to any acknowledgment beat — there isn't one in
this episode, which removes that risk by construction rather than by
careful sequencing. **No startle, no widened eyes, no reactive flinch
toward the disturbance itself** — matching Act 1's own no-startle
discipline (see Act 1) — her only response is the already-described
grip-tightening on the rabbit, an internal reaction, never an external
one; a startle/gasp response would push this into horror-trailer
grammar, which `BRAND_IDENTITY.md`'s "What Somia Is Not" boundary
explicitly forbids.

## Outfit / Visual Identity (as locked, with known imperfections carried forward)

Oversized hoodie worn like something to hide inside (hands drawn up
into or gripping the sleeves at points, per Surface Behavior), thin
choker, twin-tail hair with slight asymmetry, soft/fluffy texture.
**Updated 2026-07-19, Second Review Pass: a portrait re-lock attempt
is in progress, aiming for true black hair and ordinary human ears
per the operator's rejection of the prior imperfections (see
`YUI.md`'s Visual Identity for the live status) — this script's
prompts should describe her hair as black, matching the character
bible, once a corrected portrait is actually confirmed and locked; do
not switch the video prompts away from "silver-gray" language until
that confirmation happens, since the video calls condition on
whichever portrait file is actually locked.** Palette: #2B2633 near-black, #66506A muted
plum, #9D7A93 dusty rose, #E2C6D1 pale pink, #F7E9EE near-white pink.
Eyes: large, glossy, a restrained/ambiguous "teary impression" — per
YUI.md, never literal streaming tears, never sparkle/star-highlight
rendering.

## Timeline (~40s across 4 chained ~9s clips + a 4s closing bridge)

### Act 1 — 0.0–9.0s: notices presence, anxiety begins (establishes the space and the loop's opening posture)

**Setting and opening-pose rewrite, 2026-07-19 Second Review Pass**
(operator direction on the couch; character-psychology on the rabbit
hold; filmmaker on the cold-open hook): Yui is curled small on a small
couch tucked into the corner of the room (replacing the earlier floor-
cushion staging — a deliberate visual choice, held consistent across
every act and the bridge, not a defect), a loose blanket around her
legs, the rabbit held one-armed against her side rather than embraced
with both arms — her other hand and more of her posture stay visibly
open and unguarded from the very first frame. Chin low, gaze downward
— this exact posture is the loop's opening state and must be rendered
precisely enough to match against Act 4's ending frame later. The
room's edges are soft-focus and its proportions are quietly uneven
(per her established background motif), a baseline visual condition
present from frame one. **The first ~0.5s now carries a small,
perceivable event before any character motion**: the near-frame
foreground element (the loose blanket edge, closest to camera at
lower-frame) visibly settles into its resting position in this window
— something is already moving in the very first frame, rather than
the shot reading as a static lockoff during the platform's actual
swipe-decision window. **The camera's push-in also starts at a
slightly higher, clearly-perceptible rate for roughly this first
second**, decelerating into the same constant low rate that continues
unbroken through Act 3 — a single deceleration before the piece's
push-in vector is "established" is not the reversal/re-acceleration
defect this discipline otherwise guards against. For the next ~2.5s
(to ~3.0s) she is simply still, breath visible in slow chest movement
— a real held presence, not a locked composition. At ~3.0–4.5s, the
one narrative event of this act: her head lifts by a small, controlled
degree and her gaze drifts toward the middle distance of the room —
not toward the lens, at no point in this act or any other does her
gaze fix on or track the camera — as she registers that she is no
longer alone. **This moment needs an external trigger a cold viewer
can register, since there is no acknowledgment-of-viewer beat anywhere
in this episode to otherwise confirm "she noticed something"** (added
after character-psychology and philosophy-review independently
flagged the same gap): a single, near-imperceptible breath-catch in
the ambient audio bed lands at the same instant as the head-lift (see
Audio section) — a non-visual, non-address cue that gives the notice
beat an external cause without any gaze reaction. No startle, no gasp.
By ~5.0s her fingers visibly tighten on the rabbit's arm (a small,
incremental grip-tightening, not a clutch), the first physical sign of
anxiety building. This tightening continues steadily and only in one
direction through to the end of the act — no loosening, no
oscillation. Final frame: gaze at middle distance (not lens), grip
visibly tighter than the opening frame, otherwise same curled posture,
rabbit still held one-armed. No on-screen text in this act (matches
"speaks quietly or almost not at all" — the first act should be
legible purely through posture).

### Act 2 — 9.0–18.0s: anxiety peaks, withdrawal begins (Laing: a flinch from her own occupied space)

Keyframed from Act 1's last frame; prompt reasserts hair color, outfit,
choker, couch setting, and rabbit (still held one-armed) explicitly to
guard against drift across the chain. The anxiety-tightening carried
over from Act 1 continues for ~1–2s, then resolves into withdrawal: her
shoulders draw inward (a small, contained flinch — not a collapse, not
dramatic, reusing 0037's shoulder device), and her weight shifts
fractionally away from the room's open middle and deeper into the
corner, as if her own occupied space had suddenly become uncertain
territory rather than her spot. This must read as her body unsure it
has standing to be there — a flinch away from her own presence in the
room, not a flinch from being looked at, and not social shyness.
Concretely: her free hand (the one not holding the rabbit — the
one-armed hold means this hand was already free, not a new release)
moves to draw her hood up (reusing 0033's device) — the hand's motion
stalls at the hood's halfway point by ~14.5s and holds there, neither
completing nor abandoning the pull, for the remainder of the act. This
is one continuous, single-direction arc (lift → stall → hold) — it
does not restart, reverse, or repeat. **The hold itself is not empty
duration** (added after liberal-arts-review found the original draft
relied on the on-screen text alone to carry the ~3.5s stall, the same
"duration dressed as stillness" problem the ma/held-moment discipline
already ruled out for open-ended wind motion elsewhere in this
production): her breath continues visibly against the stalled hand.
On-screen text appears 15.0–17.5s: `I didn't move.` (see Text section
for full reasoning). Final frame: hood half-raised, hand resting
against the fabric at the stalled point, shoulders still drawn in,
weight still angled into the corner, rabbit-holding arm unchanged from
Act 1 — this exact stalled state is Act 3's starting point.

**Partial-release beat, added 2026-07-19 Second Review Pass**
(character-psychology: replaces the "faint secondary grip-adjustment"
this draft previously used at this point, which spiked object-contact
right when the vulnerability signal should shift toward her, not the
rabbit): rather than tightening her grip further here, in the last
~2s of the act her rabbit-holding arm loosens slightly, fractionally
opening the hold at a moment of rising, not resolved, tension —
exposing a little more of her hand and wrist against the rabbit's side
without releasing it. This is a small, deliberate loosening, not a
drop, and it is not a relief gesture (it happens while the hood-stall
tension is still fully active) — it reads as the object-grip briefly
losing priority to something else claiming her attention, not as
calming down.

### Act 3 — 18.0–28.0s: withdrawal completes into a private calculation to leave, then hesitates (Kafka structure; Winnicott's most spatially unstable framing)

Keyframed from Act 2's last frame (hand already stalled mid-hood-pull,
rabbit-holding arm already fractionally loosened per the Act 2 partial-
release beat). **Continuation, not a new beat** — the stalled hand
either completes lowering back down or stays where it is (director's-
choice detail, not load-bearing) within the first ~1s, its job is only
to release the prior stall cleanly, not to introduce a new gesture. The
real event of this act: at ~20.0–23.0s, a private, unspoken calculation
plays out physically — not distress at being seen, a quiet arithmetic
that leaving might be the more considerate thing to do. One hand
presses flat against the couch cushion as if to rise, weight shifts up
and forward by a small, real amount (not a full stand, a genuine
partial rise), body angling a few degrees toward the room's unseen
doorway — reusing 0038's device, retimed and re-motivated per the
Kafka-structure note in `YUI.md` (presence experienced as a burden
whose withdrawal would be a kindness to *someone* — the calculation
stays diffuse and unnamed, but per Kafka's actual structure it is never
a kindness to no one at all; revised after philosophy-review flagged
that an earlier draft's "kindness to no one in particular" stripped out
the implied beneficiary Kafka's mechanism requires and collapsed it
into generic self-erasure — never staged as distress at the viewer, and
never given a named beneficiary either, just not an entirely
unmotivated one). At ~23.0s, this is interrupted mid-motion, before the
rise completes: **this is Act 3's most spatially unstable framing, and
it is the disturbance itself that arrests the rise** — not two events
sharing a timestamp, the room's coherence failing is what stops her
(see Signature Disturbance section for the exact technique).

**Peak-vulnerability signal rewrite, 2026-07-19 Second Review Pass**
(character-psychology: the original draft routed the whole piece's
single highest-intensity moment into grip-tightening on the rabbit —
exactly the channel that competes with, rather than invites, the
viewer's protective response, at exactly the moment that response
should be strongest). At this exact instant her free hand — the one
not on the rabbit, still pressed against the cushion from the arrested
rise — visibly tenses, fingers curling slightly against the fabric; her
breath catches and holds for a beat rather than continuing its steady
rhythm; her shoulder-line draws in fractionally. **Her grip on the
rabbit changes only a small, secondary amount here** — noticeably less
than the magnitude the original draft specified — it is present but
subordinate to the hand/breath/shoulder signal, not the main carrier of
the beat. (Per Winnicott: the defense against the dread of the room
itself coming apart is still real here, it's just no longer staged as
the *only* legible channel for it.) No startle, no widened eyes, no
reactive flinch toward the disturbance — her responses (hand tension,
breath-catch, shoulder draw, small rabbit-grip increment) are all
internal reactions, none of them a flinch or startle. The partial-rise
motion arrests here and does not complete or reverse further — she is
caught between positions, weight still partly forward, hand still on
the cushion, for the remainder of the act.
On-screen text appears 24.5–27.0s: `Maybe it's fine. Maybe.` Final
frame: weight arrested mid-rise, free hand still tense against the
cushion, breath just resuming its rhythm, rabbit grip only slightly
tighter than Act 2's loosened hold, room geometry settled back to
baseline (the disturbance has already resolved by this point, not
still visible in the final frame).

### Act 4 — 28.0–37.0s: hesitation resolves into staying, settling back toward the opening posture (the loop's closing beat)

Keyframed from Act 3's last frame (weight still arrested mid-rise). The
arrested rise does not complete upward — instead, over ~1–3s, her
weight lowers back down onto the cushion, one continuous downward arc,
no false starts. This is not staged as relief or a resolved decision —
it settles the way 0035's and 0040's original stubs specified: quiet,
provisional, no smile forming at any point in this act. By ~31–33s the
blanket resettles around her legs, the hood (if it was raised in Act 2)
lowers back partway on its own from the settling motion rather than a
deliberate second gesture, and her grip on the rabbit loosens from its
Act 3 peak back down toward (not all the way past) its Act 1 opening
level — one continuous loosening arc, not a full release. Her posture
by ~34s should read as close to Act 1's opening frame as the chain
allows: curled on the same cushion, rabbit held to her chest with both
arms, chin lowering toward it, gaze low — this is the deliberate loop
target, built from the start rather than bolted on after. On-screen
text appears in two short beats rather than one line, per the sparse-
distribution requirement: `I didn't disappear.` at 33.0–35.0s, then
`Not this time.` at 35.5–37.0s — kept as two fragments with a real gap
between them (not one continuous sentence) so it reads as quiet and
provisional rather than a settled, comforting conclusion; "this time"
is load-bearing — it implies the loop could recur, not that the
question is closed. Final frame: the loop-target posture, breath still
visibly present (not frozen).

### Bridge — 37.0–41.0s: settle toward, but not fully onto, the opening frame

Generated via `fal-ai/kling-video/o1/image-to-video` with
`start_image_url` = Act 4's extracted last frame. **Revised after
character-psychology flagged the original design (`end_image_url` =
Act 1's literal first frame, the same file) as a structural over-
resolution** — landing the interpolation on the *exact* pixel-identical
opening frame is one of the strongest "this is complete" signals
available in visual storytelling, working directly against the
Failure Condition's "stay a little unresolved" requirement regardless
of how carefully the intervening acts avoided resolution. Fixed:
`end_image_url` = a frame extracted a beat *before* Act 1's literal
first frame would be reached — practically, this means treating the
bridge's target as "the state Act 1 opens on, approached but not
landed on," e.g. by using a frame from very early in Act 1 (not frame
zero) as the interpolation target, so the loop is implied by extreme
closeness rather than completed by exact return. The render pipeline
should extract this near-opening frame the same way `extract_last_frame()`
extracts sharp candidate frames — pick a frame a small amount into
Act 1 rather than its literal first frame. Content: the blanket
settles a fraction further, her breathing continues at a slow, even
rate, **her grip on the rabbit settles its final small amount toward
Act 1's opening looseness** (added after filmmaker noted the original
draft left this residual hand/rabbit differential between the two
endpoint images unaddressed, an unguided motion the model would
otherwise have to invent), and the room's blurred edges make one
final, very small, gentle re-settle toward their Act 1 opening
configuration — a soft exhale of the space itself, not a repeat of the
Signature Disturbance event (that fires exactly once, in Act 3; this
is calmer and smaller). No on-screen text. No camera movement beyond
whatever the interpolation itself introduces.

## Visual

Yui stays physically confined to the same corner cushion nook across
all four acts and the bridge — the space itself never changes, only
her relationship to how much of it she'll let herself occupy (grip
tightness, posture curl, distance from the corner) changes. Her gaze
never fixes on or tracks the camera at any point in the piece — this
is a fully private sequence, witnessed rather than addressed, distinct
from Nao's episode which built its Act 2 around one brief attention-
catch toward camera direction. A gaze-lock, a smile offered outward, a
second Signature Disturbance event, or a fully completed/relieved
"problem solved" settling in Act 4 would all be failure conditions —
the first three per `BRAND_IDENTITY.md`'s Fetishism lever and the
Signature Disturbance's "exactly once" design above, the last per
YUI.md's own Failure Condition ("protection satisfaction," a viewer
feeling their urge to protect her simply, completely satisfied, is a
failure state — Act 4 must stay quiet and provisional, never
triumphant).

## Camera

One fixed setup across all five segments: a static, slightly
off-center medium-close framing at a low, seated-eye-level height
facing the cushion nook (the off-center framing is deliberate — a
perfectly symmetrical composition would undercut the "unstable
spacing" motif). **A near-frame foreground element — the loose edge of
the blanket, closest to camera at lower-frame — is present from Act 1
and shifts position slightly across acts** (added after filmmaker
flagged the absence of any foreground disclosure device across the
full ~41s runtime as a real monotony risk, longer than Nao's static-
hold problem ever ran before being caught; this reuses the same
foreground-depth technique that fixed Nao's Act 1, at a much smaller
scale appropriate to a single continuous location rather than a scene
change). Across Acts 1–3, a single, continuous, barely perceptible
push-in at a constant rate — no reversal, no re-acceleration, no
pause-and-resume — accumulating to a small total frame-scale change by
Act 3's end, the same "single unambiguous arc" discipline that fixed
Nao's Act 3 oscillation defect; this rate/direction must be restated
inside each act's own per-call instruction, not stated once here and
assumed to carry across independently-generated chained calls (see
`prompt.md`). **Act 4's first ~2s (28.0–30.0s) explicitly continues
this same push-in rate** — added after filmmaker identified an
undefined camera window between the end of the Acts 1–3 push-in and
the start of Act 4's ease-back, the same underspecified-chain-boundary
defect class as Nao's Act 3 oscillation — before inflecting, at exactly
the ~30s settle point and not before, into the camera's only direction
change in the whole piece: a single slow ease-back at roughly the same
rate, reversed. This is staged as the settling motion continuing, not
described as resolving anything (revised after character-psychology
flagged the original "visually reinforcing the release of tension"
language as itself a formal-resolution signal fighting the Failure
Condition's unresolved requirement). The bridge holds the ease-back's
final position static; the interpolation itself supplies whatever
motion is needed to approach (not land on) Act 1's opening frame, per
the revised Bridge section above.

## Audio

**Revised after sound-design review** — the original draft described
the Signature Disturbance's audio cue as a new, discrete layer
appearing at 23.0s. For Yui specifically this risks a worse version of
the same misattribution risk Nao's episode already found with an
onset-synced bird call ("she's making that sound") — worse here
because the disturbance is explicitly the *room's* event, not
something she causes, and the script's own Timeline is emphatic that
her grip is a reaction to the room, not its source. Fixed: the
disturbance cue is now a brief modulation of the continuous room-hush
bed (comb-filter/pitch-bend applied to the ongoing texture, rising and
resolving), never a sound appearing from silence.

- Base: quiet room hush, low ambient stillness, held throughout the
  entire piece without dropping out — every other cue below modulates
  this bed, none of them are separate layers appearing from nothing
- Character noise: close, high-frequency detail, sparse
  particle-like breath/fabric texture (per her "pauses frequently"
  trait — audio should have real gaps, not a continuous bed)
- Act 1, ~3.0–4.5s: a single, near-imperceptible breath-catch in the
  ambient bed, timed to the head-lift/gaze-drift — the external,
  non-visual trigger for the "notices presence" beat (see Act 1;
  added after character-psychology and philosophy-review both flagged
  the beat's legibility gap)
- Action cues: fabric-shift/grip-tightening texture building through
  Act 2, including the faint secondary grip-adjustment during the
  hood-stall hold (see Act 2)
- Act 3, ~23.0s: the room-hush bed itself briefly takes on a
  comb-filter/pitch-bend quality — the audio analogue of the Signature
  Disturbance — rising and resolving within roughly the same window as
  the visual double-exposure ghosting (4–6 frames at 24fps), then
  returning to the plain bed. Proposed real-recording source (per
  sound-design, to validate before build rather than assume correct on
  first pass, the same iterative process Nao's umineko layer went
  through): a real flutter-echo recording — a short impulse (e.g. a
  door-latch click or handclap) captured between two close, hard-
  parallel real surfaces, with the direct impulse largely removed,
  leaving only the comb-filtered flutter tail — layered into the
  continuous bed rather than a synthetic filter sweep from scratch.
- A real silence gap (per her "pauses frequently" trait and Nao's own
  established strong-silence-contrast technique): near-total quiet for
  ~1.5s immediately after the Act 3 disturbance resolves (~23.5–25.0s),
  before the "Maybe it's fine. Maybe." text appears — the pause reads
  as her own hesitation, not a technical gap
- Act 4: a settling blanket/breath-release texture as she resettles
- Optional voice: none
- Standing gap (carried forward from Nao's NOTES.md): no audio
  synthesis pipeline exists in this codebase yet — this spec, like all
  prior ones, is unrealized in the actual deliverable, not fixed by
  this pass.
- **Separate standing gap, new finding this pass**: unlike Nao/Airi/
  Rena/Mina, `YUI.md` has no Audio Traits section at all — this
  episode's audio language is the first attempt to define her audio
  identity, not a spec being checked against an established bible
  entry. Follow-up: once this episode's audio direction is validated
  (real flutter-echo source tested, not just described), distill it
  into a proper Audio Traits section in `YUI.md` matching the other
  four characters' format.

## Text

Four short fragments distributed across Acts 2–4 (none in Act 1 or
the bridge), all self-referential rather than addressed outward (no
"you"), deliberately not resolving into one complete, comforting
sentence:

- `I didn't move.` (Act 2, 15.0–17.5s)
- `Maybe it's fine. Maybe.` (Act 3, 24.5–27.0s)
- `I didn't disappear.` (Act 4, 33.0–35.0s)
- `Not this time.` (Act 4, 35.5–37.0s)

**Color/placement spec (added 2026-07-19, accessibility-review finding
against the actual rendered frames):** the rendered footage sits in a
narrow-value, low-contrast lavender/beige range throughout — no color
in Yui's own palette except `#2B2633` near-black has real luminance
separation from every background frame. Use `#2B2633` text with a
soft outer stroke/subtle scrim (not a flat pale-pink or near-white
treatment, which would sit flush against the hoodie/wall values).
Placement: upper-third safe zone, clear of hair/rabbit/hoodie — do
not default to lower-third caption placement, since the character and
hoodie occupy the center and lower two-thirds of frame throughout.
