# Somia character portrait methodology

Distilled from content 0007 (Nao)'s actual production history — five
same-day prompt revisions, four of which chased a new defect rather than
fixing the original one, before the operator's fix (revert to a known-good
state, stop iterating blind) actually worked. This is what made that
portrait's "taste" (art style, linework, rendering register) consistent
and reproducible; use it before generating a new character's portrait, not
just Nao's.

Full incident history: `businesses/somia/content/CONTENT/0007/NOTES.md`
and `render_two_stage.py`'s inline changelog comments.

## Pipeline

- Endpoint: `fal-ai/lora` (text-to-image only — no reference image,
  no img2img). Nao's portrait was NOT generated from any of the
  ChatGPT-era concept sheets or the `ref_*/prompt.md` img2img drafts
  that predate this method — those are a different, superseded approach.
- Checkpoint: `https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/resolve/main/Illustrious-XL-v2.0.safetensors`
- `guidance_scale: 7.5`
- **No `seed` is set.** Every call is a fully independent random draw.
  This is not a missing nice-to-have — it is the actual root cause of
  most of Nao's portrait defects (see "Iteration discipline" below).
- Identity-only prompt, zero scene tags — see "Token budget" below.

## Prompt structure (the actual style-consistency mechanism)

Cross-character visual consistency does NOT come from a shared subject
description. It comes from reusing the same **style-anchor phrase
cluster**, checkpoint, and guidance_scale across every character, while
only the identity content changes:

```
1girl, solo, adult woman, portrait, upper body, delicate soft face,
[character-specific eyes/eyebrows], delicate fine linework, [hair],
[signature accessory, singular/continuous-shape language], [outfit,
fabric-behavior + construction language], illustration, anime style,
clean plain background
```

The load-bearing phrases are `delicate soft face`, `delicate fine
linework`, `illustration, anime style`, and `clean plain background` —
these four appeared unchanged across every revision of Nao's prompt that
kept the correct linework/rendering register. When one revision (the
"cashmere/loungewear" pivot) introduced unusual non-anime-register
vocabulary elsewhere in the prompt, it visibly shifted the *entire*
render's linework and coloring style, not just the described garment —
confirmed by the operator comparing frames directly. **Unusual vocabulary
anywhere in the prompt is a style-consistency risk, not just a
content risk.**

## Token budget: identity only, no scene

Every SDXL/Illustrious-XL-family checkpoint has roughly a 75-effective-token
budget per generation. Competing for that budget with scene tags (window,
curtain, sea, lighting) is what caused every one of the earlier
single-stage Nao attempts to sacrifice some required element (scene OR
outfit OR face/earring). Portrait generation must describe identity ONLY
— face, hair, signature accessory, outfit. If a scene is needed later, do
it as a separate generation (inpaint/outpaint around the fixed portrait,
as `render_two_stage.py`'s Stage 2 does) so the portrait's own token
budget stays 100% on identity.

**Enforcement (added 2026-07-19, mlops):** this doctrine existed as prose
only, with no code checking it, and was silently violated multiple times
during Yui's portrait regeneration (v6/v8 ran ~117-120 estimated tokens,
v10 ran ~206 -- see "Known failure modes" below). `platform/system/scripts/
somia/prompt_budget.py`'s `check_prompt_budget()` now warns/refuses before
submission; `render_character_portraits.py`'s `generate_portrait()` and
`generate_portrait_img2img()` both call it. Thresholds are calibrated
against this project's actual working prompts (v6/v8), not just the
doctrinal 75-token figure, since a guard that blocks the only known-good
prompt on record is worse than no guard.

**Not yet built, flagged for future consideration (mlops):** whether
`fal-ai/lora` auto-chunks over multiple 77-token CLIP segments or hard-
truncates past the first chunk is unknown and untested — this can only be
determined by a real (billed) empirical test, not static analysis; get
explicit sign-off before running it. Separately, the current retry
workflow (hand-editing `CHARACTERS` dict-literal entries in
`render_character_portraits.py` per attempt, accumulating dead version-
history comments) was flagged as process-inadequate for a task that
produced 10 attempts in one session — a thin one-off CLI taking prompt/
negative/params as arguments, with each attempt's prompt saved as a
versioned file under `ref_<character>/` instead of a code comment, would
structurally enforce single-variable isolation instead of relying on
convention. Not built; a process change, not a pure pipeline fix.

## Known failure modes (transferable, not Nao-specific)

- **A single ambiguous word can pull in a whole unwanted cluster.** On
  this checkpoint's Danbooru-tag training data, "cardigan" alone
  co-occurs so heavily with school-uniform layering (sailor collar, neck
  ribbon, blazer buttons) that it pulled that whole cluster in even with
  zero competing scene tags. Separately, the bare word "roots" (as in
  hair roots) got misread as a literal text/caption label. Before using
  any single word, consider what else it commonly co-occurs with on a
  Danbooru-style tagset, not just its literal meaning.
- **Two co-occurring modifiers can jointly trigger a cluster that neither
  triggers alone.** "covered shoulders" + "round modest neckline"
  together read as a strong turtleneck/knitwear trigger, even though
  scene curtain fabric in the same generation correctly rendered sheer
  from unrelated wording. Test combinations, not just individual terms.
- **Fabric *behavior* language beats fabric *name* language** for getting
  a specific material quality to actually render. "Sheer fabric" as a
  bare tag was not enough; describing translucency, light passing
  through, and how the fabric drapes/moves was what actually worked
  elsewhere in the same prompt (the curtain).
- **Name construction, not garment/collar type, for anything that keeps
  misfiring.** "round modest neckline" and other named collar/neckline
  terms repeatedly pulled a decorative-collar or turtleneck cluster.
  Construction language ("falls open and away from the throat, no
  collar") describes the same physical outcome without naming a garment
  category the checkpoint associates with something else.
- **Describe a signature accessory as one continuous shape**, not a
  composite. Nao's earring rendered as a two-part stud+dangling-chain
  shape across multiple attempts despite negative-prompt exclusions,
  because the positive prompt only implied "one item" rather than stating
  it as one continuous shape hanging directly from its anchor point.
- **Move every excluded element into `NEGATIVE_PROMPT` explicitly** —
  don't rely on the positive prompt to "outcompete" an unwanted cluster
  by omission. Everything the character must NOT show (an accessory
  another character owns, an unwanted collar shape, unwanted skin
  exposure) belongs as an explicit negative-prompt term.
- **Check the shared `NEGATIVE_PROMPT` baseline against the target
  character's actual required accessories before reusing it.** Nao's
  tuned negative prompt excludes `choker` (correct for her — she doesn't
  wear one) — copying it verbatim for Rena or Yui, both of whom have a
  choker as a named Visual Identity accessory, would actively fight their
  own design. Reuse the baseline's quality/safety/style exclusions;
  re-derive the garment/accessory exclusions per character from her own
  Hard Constraints and NG list.
- **An externally-proposed diagnosis is not evidence until it's tested as
  a single-variable, seeded comparison against a known-good prompt.**
  Yui v10 tried an external review's full-prompt rewrite (emotion words
  like "hesitant"/"restrained smile" replaced entirely with shape/
  muscle-state language) as an unseeded, ~250-word full replacement of
  the ~110-word v6/v8 prompt that was already working. The result
  (unfinished-sketch style, outfit/rabbit/choker/palette entirely absent)
  is fully explained by the *already-documented* long-prompt/
  simultaneous-multi-change failure mode above — v10 changed prompt
  length and wording strategy at the same time, which is exactly the
  confound "Iteration discipline" exists to prevent. It is NOT evidence
  that the emotion words were the problem: v6 used the identical
  emotion phrases ("trying to smile", "restrained smile", "hesitant
  expression") and rendered correctly on the two traits being chased
  that session. Before adopting any external-review hypothesis about
  *which words* are causing a defect, isolate it: take the last
  known-good full prompt, pin a `seed`, and change only the words the
  hypothesis targets — nothing else. A hypothesis that arrives bundled
  with unrelated prompt-length or structure changes cannot be judged on
  its own claim.

## Iteration discipline (the actual fix that ended the loop)

Because there is no seed, two prompts that look like small, targeted
edits can land in genuinely different regions of the checkpoint's output
distribution — there is no way to isolate "what the prompt change did"
from "what pure random variance did." Nao's portrait went through three
consecutive same-day "fix attempts" that each introduced a NEW, different
defect (a lace/embroidered collar; then a spurious tear-like droplet
under the eye plus a wrong color; then a more elaborate two-part earring)
rather than converging.

- **Do not iterate prompt wording call-to-call expecting comparable
  results.** Without a seed, you cannot tell whether a change fixed
  something or just landed a different random draw.
- **If a revision doesn't clearly work, revert to the last known-good
  full prompt state rather than layering another targeted fix on top of
  a broken one.** This is what actually ended Nao's defect-trading loop.
- **If real prompt-only comparison is ever needed, pin a `seed` first**
  (`fal-ai/lora` accepts one) so successive attempts are actually
  comparable, instead of repeating unseeded full regenerations.
- **Accept one known imperfection rather than trading it for an unknown
  new one.** Nao's locked portrait still reads as a somewhat more
  structured top than the reference sheets' literal sheer-fabric
  intent, and her earring still occasionally shows as two-part. Both are
  documented, accepted imperfections, not oversights — see NAO.md's
  Visual Identity section.

## Cross-character rollout findings (2026-07-19, Airi/Rena/Mina/Yui)

Generating all four remaining characters in one pass surfaced lessons the
single-character (Nao) history didn't:

- **Describing a light/glow effect as being IN or ON a character (her eyes
  reflecting it, her skin catching it) is unstable and tends to render as
  HER glowing** — glowing eyes, a glowing aura, glowing skin — pulling
  toward fantasy-elemental imagery (crystal, water/ice spirit) instead of
  ambient environmental light. This happened across five independent
  draws for Airi regardless of how the glow was worded (abstract "glow",
  a concrete "computer monitor's light reflected in her eyes" rewrite).
  What actually worked: describing the light as belonging explicitly to
  the *background/environment*, with the character's own eyes/skin
  stated as plain and unlit ("the light belongs to the background, not
  to her"). If a character's identity genuinely involves being lit by
  something (screen glow, spotlight), keep the light source and the
  character explicitly decoupled in the prompt.
- **Loose/sketchy or painterly rendering can show up even with `delicate
  fine linework, illustration, anime style` present**, when other
  vocabulary in the prompt pulls toward a different illustration
  tradition (formal-eveningwear/fashion-illustration vocabulary, for
  Rena). If a draft comes back in the wrong linework register, add
  explicit clean-cel-shading anchors (`clean cel-shaded anime
  illustration, flat clean coloring, crisp thin outlines`) and exclude
  the observed failure mode by name (`sketchy lines, loose linework,
  marker illustration, ink wash, painterly, watercolor`) rather than
  assuming the shared style-anchor phrases alone are always sufficient.
- **This checkpoint has a visible default pull toward silver/light hair**
  when a character's stated hair color isn't reinforced strongly. Nao's
  prompt reinforces her hair color with an explicit gradient description
  ("deep navy blue hair at top blending to pale sky blue at the ends, two
  tone blue hair") — a single adjective ("black twin tails," "matte
  sheen") was not enough for Rena or Yui and both drew silver/gray hair
  at least once. If hair color keeps missing, state it with the same
  gradient/multi-clause weight Nao's prompt uses, not a single adjective,
  and add the wrong colors to the negative prompt explicitly (`silver
  hair, gray hair, white hair, light-colored hair`).
- **A composition/framing miss (extreme close-up, cropped below the
  shoulders) is a distinct failure mode from a content miss**, and is
  fixed differently: reinforce framing language immediately next to
  `portrait, upper body` (`full head and shoulders clearly visible,
  centered composition`) and add explicit close-up/crop exclusions,
  rather than adjusting the identity content.
- **Not every character converges in the same number of draws, and that's
  fine.** Mina and Yui's core design converged in one and two draws
  respectively; Rena took four; Airi was still not converged after six
  draws and was deliberately left on hold rather than forcing further
  draws or accepting a partial miss as "locked." Holding is a legitimate
  outcome — see `ref_airi/candidate_portrait_v1.png` for the most recent
  attempt when this is picked back up.
- **A long, heavily-claused prompt can start losing negative-prompt
  adherence, not just drift stylistically.** Airi's v6 draft (the longest
  version of her prompt, after several rounds of added framing/hair/
  exclusion clauses) ignored explicit negative-prompt terms that had been
  respected in earlier, shorter drafts — an ornamental border/frame
  appeared despite `border, frame` being excluded, and glowing eyes
  appeared despite `glowing eyes` being excluded. This is a different
  failure mode from "the wrong content was chosen" — it looks like
  prompt-length/attention dilution rather than a content decision. If a
  character's prompt has grown long across several revision rounds and
  problems start recurring that were previously fixed, consider cutting
  the prompt back down rather than adding another clause on top —
  starting over from a short, minimal description may be more productive
  than continuing to layer fixes.

## Locking a portrait once it's approved

Once the operator approves a portrait, **stop regenerating it.** Promote
the approved file to `businesses/somia/content/CONTENT/ref_<character>/canonical_portrait_v1.png`
(versioned filename — a future deliberate revision becomes `v2`, never
overwrites `v1`) and treat it as the character's fixed identity anchor for
every future episode's video generation (conditioning via
`reference-to-video`'s `elements` parameter, as `render_final_3act.py`
does for Nao). See NAO.md's Visual Identity section for the exact
precedent this follows.
