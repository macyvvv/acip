---
name: somia-content-definition-of-done
description: Checklist of what "finished/deliverable" actually means for a somia CONTENT/<id> piece, written after multiple pieces of content 0007 (Nao episode 1) were treated as done while a step had silently not happened -- on-screen text never composited into a chained render, a signature item never actually visible, a loop point never verified by extracting the frame. Use this before telling the operator a render is ready to review, and before merging/shipping any somia content.
---

# somia content: definition of done

Every item below caused a real defect in content 0007 that was initially
reported as fine because the step was *assumed* done (it worked in a
prior version, or the prompt said it should happen) rather than *checked*
in the actual output. "The prompt asked for it" and "it happened last
time" are not evidence it happened this time.

## Checklist (verify each on the actual rendered artifact, not the spec)

1. **On-screen text, if the spec has any** (`script.md`'s `## Text`
   section) — composited into the final video file, not just described in
   the spec. `render_content.py`'s providers never do this automatically
   (see `compositing-somia-onscreen-text` skill). Verify by extracting a
   frame from the exact timestamp window and looking at it — don't assume
   because a compositing step ran for a *different* version of this
   content.
2. **Signature item, if the character has one** (each somia character's
   `CHARACTER.md` names one recurring close-in object/accessory) — visible
   and recognizable in the rendered output, not just named in the prompt.
   A prompt tag doesn't guarantee the model actually renders the element
   clearly; check the keyframe/frame directly.
3. **Outfit/visual identity matches the character's actual reference art**,
   not just a prose paraphrase of it. If a `CHARACTER.md` description and
   the reference sheet images could be read two different ways, re-check
   the images directly — don't rely on a prior pass's interpretation of
   them without re-verifying.
4. **If the piece is a multi-clip chain (loop or multi-act) that's
   supposed to return to (or near) its starting pose** — extract the final
   frame and the opening frame and visually compare them. Don't assume the
   loop closes cleanly because the prompt described a return-to-start
   beat; a chained generation can drift, oscillate, or resolve into a
   different pose than intended.
5. **Any "exactly once" or "never again" behavioral constraint in the
   spec** (e.g. a character turns toward camera exactly once across a
   multi-act sequence) — verify by watching/scrubbing the actual rendered
   result, not by trusting that a later act's prompt correctly encoded the
   constraint. Prompt language describing a continuation can still get
   interpreted by the model as a fresh new beat.
6. **Full creative-team review with no open findings**, when the content
   or character spec was substantively changed this pass (not required
   for a pure re-render of an already-approved spec): color-coordination,
   lighting-design, sound-design, visual-effects, accessibility-review
   (via visualops/creativeops), plus epistemicsops if any claim about the
   content's fidelity to source material is being asserted. Don't report a
   redesign as ready before this review actually happened.

## What this replaces

Before this skill existed, each of these checks lived only as scattered
"must be verified" notes inside individual `script.md` files (see content
0007's Act 3 note as one example) — easy to write once and never
consistently apply to the next piece of content. This skill is the
consolidated version; keep per-content "must verify" notes in `script.md`
for content-specific nuance, but don't rely on them alone.
