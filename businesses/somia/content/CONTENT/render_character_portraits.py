#!/usr/bin/env python3
"""Generates a locked-identity portrait for each of Airi/Rena/Mina/Yui,
matching Nao's successful methodology (content 0007) -- see
businesses/somia/content/BRAND/PORTRAIT_METHODOLOGY.md for the full
reasoning this script follows.

Pipeline: fal-ai/lora text-to-image only (no reference image, no img2img
-- distinct from the older, superseded ref_*/prompt.md img2img drafts),
same checkpoint/guidance_scale as Nao's locked portrait, identity-only
prompt (no scene tags, full token budget on face/hair/accessory/outfit).

No seed is set -- every run is an independent random draw per character.
Per PORTRAIT_METHODOLOGY.md's iteration discipline: do not re-run this
script for a character expecting a matching result once its output is
approved and promoted to ref_<character>/canonical_portrait_v1.png.

Real fal.ai spend: 1 image generation per character (4 total).
Run from repo root: PYTHONPATH=platform .venv/bin/python
businesses/somia/content/CONTENT/render_character_portraits.py [character ...]
(no args = all four)
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from system.core.dotenv import load_dotenv  # noqa: E402
from system.scripts.somia import fal_client  # noqa: E402
from system.scripts.somia.prompt_budget import check_prompt_budget  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent
TEXT2IMG_RUNNER = "fal-ai/lora"
MODEL_NAME = "https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/resolve/main/Illustrious-XL-v2.0.safetensors"
GUIDANCE_SCALE = 7.5

# Nao's tuned baseline (render_two_stage.py's NEGATIVE_PROMPT), with the
# Nao-specific hair/eye-color exclusions and "choker" removed -- "choker" is
# a required Visual Identity accessory for Rena and Yui, so it can't be a
# blanket exclusion; each character's negative prompt below adds back
# whatever exclusions her own design actually needs.
BASE_NEGATIVE = (
    "photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, "
    "bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, "
    "cleavage, exposed skin emphasis, bare shoulder, off shoulder, exposed collarbone, "
    "tank top, camisole, thin straps, sleeveless, revealing neckline, child, loli, school "
    "uniform, sailor collar, sailor fuku, neck ribbon, ribbon, bow, bowtie, necktie, "
    "buttons, button front, double breasted, lace collar, frilled collar, ruffled collar, "
    "high collar shirt, blazer, age indicators, confrontational expression, flat colors, "
    "minimalist, abstract, poster art, silhouette, graphic design, solid color background, "
    "heavy makeup, sharp features, generic face, indoor artificial lighting, empty room, "
    "abandoned space, horror atmosphere, dark atmosphere, heavy decoration, flashy colors, "
    "excessive ornamentation, text, watermark, caption, logo, UI, letters, words, subtitles, "
    "border, frame, chart, diagram, sketch lines, monochrome, grid, collage, multiple panels"
)

CHARACTERS = {
    "airi": {
        # v4 (2026-07-19): four independent draws (v1 x2, v2, v3) all failed
        # differently but shared one thing: describing the glow as IN/ON her
        # (reflected in her eyes, glowing) consistently got rendered as HER
        # glowing -- glowing eyes, a glowing aura, glowing skin -- pulling
        # toward fantasy-elemental imagery instead of ambient screen light.
        # Operator clarified the actual intent: the light belongs to the
        # background/environment, not to her -- she should read as plain
        # and unlit, lit only incidentally by an off-frame source. Fixed the
        # broken-composition/fantasy-elemental problem, but overcorrected:
        # hair rendered as a uniform pale light-blue wash with no black at
        # all, and cropped below the shoulders so the hairpin/outfit never
        # appeared.
        # v5 (2026-07-19): operator: the hairstyle itself has to match
        # AIRI.md's spec closely (explicitly a point she cares about), and
        # wants the color pushed toward deep purple -- not necessarily
        # replacing the black-to-dark-blue gradient, a purple mesh/streak
        # blended through it is fine. Rewrote the hair clause with the same
        # multi-clause weight Nao's gradient description uses (a single
        # adjective wasn't enough for other characters either -- see
        # PORTRAIT_METHODOLOGY.md's cross-character findings), and
        # strengthened framing so the hairpin and shoulders/outfit actually
        # appear in frame.
        "prompt": (
            "1girl, solo, adult woman, portrait, upper body, waist-up framing, both shoulders "
            "and upper arms clearly visible, hairpin clearly visible in her hair, centered "
            "composition, delicate soft face, deep plain unlit eyes, not glowing, soft "
            "eyebrows, delicate fine linework, pale blue ambient light falling softly across "
            "one side of her face from an unseen off-frame source, the light belongs to the "
            "background, not to her, black hair blended with deep purple mesh streaks running "
            "through it, fading to dark blue at the ends, slightly messy tousled waves, one "
            "small angular metal hairpin, minimal ornamentation, gaze turned slightly away and "
            "downward, ambiguous unreadable expression, not smiling, not crying, loose "
            "off-shoulder thin knit top slipping down one shoulder, soft draping fabric, no "
            "hood, no zipper, illustration, anime style, clean plain background"
        ),
        "negative_extra": (
            "choker, hoodie, hood, tracksuit, zip-up jacket, thick sweater, bright smile, "
            "sustained direct eye contact, cheerful expression, extreme close-up, cropped face, "
            "partial face, close-up on eye, macro shot, cropped below shoulders, floating "
            "object, disembodied object, glasses, eyewear, goggles, VR headset, glowing eyes, "
            "glowing skin, glowing body, light-emitting eyes, screen glare artifact, fantasy "
            "elemental effect, magical aura, water spirit, ice spirit, swirling energy effect, "
            "wings, fins, ornamental armor, monochrome, sketch lines, scribble style, uniform "
            "single-tone hair, solid light blue hair, no black hair"
        ),
    },
    "rena": {
        # v2 (2026-07-19): operator asked for a full prompt change -- v1's
        # "matte black fitted top... light-absorbing fabric" wording pulled a
        # combat/tactical-harness aesthetic (exposed straps, a garbled
        # text-label artifact on the chest) instead of the intended opulent/
        # luxurious register. Replaced with explicit formal-eveningwear
        # vocabulary grounded in her Detail Notes (wine glass, controlled
        # opulent interior) instead of generic "fitted top" construction
        # language, and added explicit combat/tactical/text exclusions.
        # v3 (2026-07-19): operator: v2's outfit/hair/setting all landed
        # correctly, but the smile itself was wrong for her KV -- reads as
        # too warm/inviting. Replaced "faint unreadable smile" with a cool,
        # resigned, non-smiling register.
        # v4 (2026-07-19): operator: v3's render style diverged too far from
        # Nao/Mina/Yui's clean cel-shaded look (came out as a loose sketch/
        # marker illustration) -- a cross-character consistency problem, not
        # a content problem. Added explicit clean-cel-shading style anchors
        # (matching the shared style-anchor phrases in
        # PORTRAIT_METHODOLOGY.md) and excluded sketchy/painterly rendering.
        # Also: operator insists on black hair specifically (silver/gray hair
        # is unspecified-but-wrong here, unlike the earlier judgment that it
        # was acceptable since unspecified) -- reinforced explicitly, same
        # fix pattern as Yui's.
        "prompt": (
            "1girl, solo, adult woman, portrait, upper body, delicate soft face, deep composed "
            "eyes with minimal movement, soft eyebrows, delicate fine linework, clean cel-shaded "
            "anime illustration, flat clean coloring, crisp thin outlines, long sleek straight "
            "solid black hair with a matte sheen, single black choker as the one core accessory, "
            "cool detached expression, faintly world-weary, no smile, lips closed and still, "
            "gaze held steady and level, quietly unimpressed, elegant black velvet evening "
            "gown, modest high neckline, long sleeves, no straps, deep plum and wine-red trim, "
            "opulent formal wear, illustration, anime style, clean plain background"
        ),
        "negative_extra": (
            "casualwear, streetwear, bright colors, pastel colors, cute expression, open smile, "
            "smiling, warm expression, friendly expression, direct sustained eye contact, "
            "combat outfit, tactical gear, military uniform, battle armor, sci-fi armor, "
            "harness straps, crop top, exposed midriff, bare shoulder, off shoulder, text, "
            "label, tag, writing on clothing, nametag, patch, badge, sporty, silver hair, gray "
            "hair, white hair, light-colored hair, sketchy lines, loose linework, marker "
            "illustration, ink wash, painterly, watercolor"
        ),
    },
    "mina": {
        "prompt": (
            "1girl, solo, adult woman, portrait, upper body, delicate soft face, soft "
            "downward-tilted gaze, gentle warm brown eyes, soft eyebrows, delicate fine "
            "linework, soft loosely gathered bun with escaped strands framing the face, single "
            "small crescent-shaped hairpin, a small incomplete smile with a flicker of "
            "hesitation, loose warm cream knit top with a softly folded open collar, gentle "
            "drape, warm amber-toned light, illustration, anime style, clean plain background"
        ),
        "negative_extra": (
            "choker, cardigan, turtleneck, mock neck, ribbed collar, bright harsh lighting, "
            "full toothy smile, direct eye contact"
        ),
    },
    "yui": {
        # v2 (2026-07-19): operator rejected v1 -- eyes read as off-taste
        # (glittery sparkle/star-highlight moe-style rendering, not the calm
        # delicate anime eye register the rest of the roster uses) and
        # "泣きすぎ" (overshot into literal streaming tears/teardrop beads
        # down the face, not the "faint teary impression" asked for).
        # Reworded the eye clause toward calm/delicate rendering matching
        # the shared style anchor, explicitly said not crying/no visible
        # tears, and added sparkle/tear/wrong-hair-color exclusions.
        # v3 (2026-07-19): v2 was approved and locked, but two independent
        # downstream video draws both rendered a pointed/elf-like ear
        # despite explicit "not pointed, no elf ears" text negation on the
        # video calls -- and on closer inspection the v2 portrait itself
        # already carried the ear shape (image-conditioning, not a video-
        # prompt problem), plus hair rendered silver-gray both times despite
        # this prompt already saying "deep black". Operator rejected both
        # as things to keep accepting and asked for a real fix, with a
        # theory that pointed ears may ride the same training-data
        # neighborhood as youthful/small-stature proportions on this
        # checkpoint (per apparel-stylist review) -- so v3 pairs "petite"
        # with explicit adult-proportion construction language instead of a
        # bare "adult" tag, adds a dedicated positive ear-shape clause
        # (describing the shape, not just negating elf-ness), and
        # strengthens the hair clause with the same multi-clause weight
        # that worked for Nao/Airi rather than a single adjective. Seed
        # pinned per PORTRAIT_METHODOLOGY.md's iteration discipline, since
        # this is a targeted fix being judged against the prior draws.
        # v3/v4 (2026-07-19): apparel-stylist's positive-construction
        # strategy (explicit adult-proportion clauses + a dedicated
        # positive ear-shape description) made things categorically worse
        # across two independent draws -- ears rendered even larger/more
        # pointed each time, and the added clause volume itself seems to
        # have destabilized the whole generation (art style drifted
        # off-model both times, twin tails/rabbit/hoodie/choker all
        # vanished). Abandoned.
        # v5 (2026-07-19): operator's own hand-written prompt, close to
        # v2's wording with two insertions ("normal human"/not-elf-eared
        # opener, "slender and petite" in place of a bare "adult"). Fixed
        # the hair color (first draw to render true black) but the ear
        # still rendered pointed, and the art style drifted rough/dark
        # (rabbit, hoodie, choker all missing from frame) -- likely
        # because the prompt mixed natural-language prose ("she is
        # wearing", "and the hoodie's loose hood") with tag-style
        # fragments; this provider's own code comment
        # (providers_illustrious_kling.py) already documents that this
        # Danbooru-trained checkpoint needs consistent comma-separated
        # tags, not prose, or output quality visibly degrades.
        # v6 (2026-07-19): a prompt proposed via external review (ChatGPT),
        # restructured as consistent Danbooru-style tags throughout
        # (matching v2's register, unlike v5's prose mixing), keeping
        # v5's hair-color phrasing that worked and adding an explicit
        # "human ears, rounded ears" positive tag pair alongside adult-
        # proportion tags. Also lowers guidance_scale from the pipeline
        # default 7.5 to 5.5 and adds num_inference_steps=32, per the
        # external review's reasoning that a lower CFG may reduce how
        # strongly the checkpoint pulls toward the elf-ear/youthful
        # archetype cluster apparel-stylist identified as the likely
        # cause (higher CFG amplifies whatever the model's strongest
        # learned association is for this feature combination).
        "prompt": (
            "masterpiece, best quality, 1girl, solo, adult human woman, ordinary human, human "
            "ears, rounded ears, slender adult proportions, small frame, narrow shoulders, jet "
            "black hair, deep blue-black hair, slightly asymmetrical twin tails, soft layered "
            "bangs, soft grey-violet eyes, half-lidded eyes, slightly tired eyes, weak eye "
            "focus, small black choker, soft oversized black hoodie, long sleeves covering "
            "fingertips, hood resting naturally, holding a small white rabbit plush close to "
            "chest, trying to smile, restrained smile, hesitant expression, gaze slightly "
            "downward, muted plum and dusty rose color palette, illustration, anime style, "
            "plain background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fantasy race, demon, fairy, animal ears, "
            "child, loli, baby face, sparkle eyes, star pupils, moe eyes, crying, tears, "
            "confident, energetic, silver hair, white hair, grey hair, chibi"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        # v11 (2026-07-19): controlled A/B re-run of this exact v6 prompt,
        # unchanged, now that prompt_weighting=True is wired into
        # generate_portrait() -- isolates whether the missing prompt_weighting
        # flag alone explains v6's missing outfit/rabbit/choker, with no
        # wording change at all. Paired against yui_v10's same-seed re-run.
        "candidate_filename": "candidate_portrait_v11_promptweighting.png",
        "seed": 777001,
    },
    # v7 (2026-07-19, not kept as a runnable entry): tried adding
    # waist-up framing language plus a large batch of new negative-prompt
    # exclusions on top of v6's working prompt, all at once. Severe
    # regression -- rendered a completely different character archetype
    # (dark teal/gold hair, ornate fantasy military uniform, cross
    # earring, purple background), no hoodie/rabbit/choker/palette at
    # all. The ear itself was fine (rounded, human) but everything else
    # broke. This checkpoint is evidently very sensitive to prompt-
    # length/composition changes bundled together -- confirms the
    # earlier v3/v4/v5 pattern (any large simultaneous edit risks a full
    # archetype swap, not just the intended targeted change).
    "yui_v8": {
        # v8 (2026-07-19): revert to v6's exact working prompt (ears and
        # hair both correct there) and change exactly ONE thing -- insert
        # "portrait, upper body" right after "solo," and nothing else, no
        # new negative-prompt additions, no other wording changes. Single-
        # variable test per PORTRAIT_METHODOLOGY.md's iteration discipline,
        # specifically because v7 showed this checkpoint reacts badly to
        # multiple simultaneous prompt changes.
        "prompt": (
            "masterpiece, best quality, 1girl, solo, portrait, upper body, adult human woman, "
            "ordinary human, human ears, rounded ears, slender adult proportions, small frame, "
            "narrow shoulders, jet black hair, deep blue-black hair, slightly asymmetrical twin "
            "tails, soft layered bangs, soft grey-violet eyes, half-lidded eyes, slightly tired "
            "eyes, weak eye focus, small black choker, soft oversized black hoodie, long sleeves "
            "covering fingertips, hood resting naturally, holding a small white rabbit plush "
            "close to chest, trying to smile, restrained smile, hesitant expression, gaze "
            "slightly downward, muted plum and dusty rose color palette, illustration, anime "
            "style, plain background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fantasy race, demon, fairy, animal ears, "
            "child, loli, baby face, sparkle eyes, star pupils, moe eyes, crying, tears, "
            "confident, energetic, silver hair, white hair, grey hair, chibi"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        "candidate_filename": "candidate_portrait_v8.png",
        "output_character": "yui",
    },
    "yui_v10": {
        # v10 (2026-07-19): full-prompt replacement from an external
        # review (ChatGPT) "YUI Morphological Reconstruction Specification"
        # -- the core methodology shift from v3-v9's emotion-word prompting
        # ("hesitant", "trying to smile", "restrained") to pure shape/
        # muscle-state description ("slightly lowered outer eye corners",
        # "small relaxed mouth", "very low smile intensity"), on the
        # documented theory that this checkpoint maps emotion-words to a
        # narrow, strong "yandere/intense" archetype cluster rather than
        # rendering the intended vulnerability. Used verbatim as supplied,
        # not rephrased. Note: this spec keeps "soft oversized charcoal
        # hoodie" as the outfit, NOT reconciled with the operator's
        # separate finding that the original character sheet
        # (ref_yui/character_sheets/somia_yui03.png) actually shows a
        # black lace camisole under an off-shoulder oversized cardigan,
        # not a hoodie -- flagged to the operator, not yet resolved, kept
        # as hoodie here since that's what this spec says and changing it
        # would violate the single-source-of-truth intent of using the
        # spec verbatim.
        "prompt": (
            "masterpiece, best quality, 1girl, solo, adult human woman, ordinary human, "
            "slender adult proportions, small adult frame, narrow shoulders, mature skeletal "
            "proportions, soft rounded adult face, short lower face, small soft chin, gentle "
            "cheeks, low cheekbone definition, large softly rounded eyes, slightly lowered outer "
            "eye corners, large low-contrast grey-violet irises, medium-large pupils, single tiny "
            "eye highlight, soft upper eyelids, subtle lower eyelids, weakly focused gaze, gaze "
            "slightly downward, thin soft eyebrows, nearly horizontal eyebrows, low brow tension, "
            "small relaxed mouth, neutral mouth corners, barely parted lips, very low smile "
            "intensity, small rounded human ears, deep blue-black hair, low-gloss soft hair, fine "
            "hair strands, light separated bangs, slightly uneven bangs, natural medium-volume "
            "twin tails, subtle twin-tail asymmetry, thin black choker, soft oversized charcoal "
            "hoodie, long sleeves covering the fingertips, hood resting naturally on the "
            "shoulders, holding a small white rabbit plush close to the chest, low emotional "
            "intensity, relaxed facial muscles, muted plum and dusty rose accents, clean plain "
            "low-saturation background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fairy ears, demon ears, animal ears, child, "
            "loli, baby face, childlike body proportions, oversized head, chibi, sharp eyes, "
            "narrow eyes, fox eyes, tsurime, glaring, seductive eyes, small irises, tiny pupils, "
            "sparkle eyes, star pupils, multiple bright eye highlights, angry eyebrows, highly "
            "arched eyebrows, furrowed brows, smirk, grin, evil smile, wide smile, open-mouth "
            "smile, seductive smile, yandere, manic expression, confident expression, long face, "
            "sharp jaw, gaunt face, prominent cheekbones, heavy bangs, thick blunt bangs, high "
            "twin tails, drill hair, silver hair, grey hair, white hair, crying, tears, "
            "teardrops, streaming tears, bright saturated colors, neon colors, exposed skin "
            "emphasis"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        # v12 (2026-07-19): controlled A/B re-run of this exact v10 prompt,
        # unchanged, now with prompt_weighting=True and the same seed as
        # yui_v11's re-run of v6, so the two can be compared as a real
        # controlled experiment (fixed seed, one variable -- prompt content
        # -- differing) rather than two independent random draws.
        "candidate_filename": "candidate_portrait_v12_promptweighting.png",
        "seed": 777001,
        "output_character": "yui",
    },
    "yui_v13": {
        # v13 (2026-07-19): synthesis attempt after the operator's ranked
        # review of everything so far -- v1/v2 (the locked baseline) and v8
        # are closest to concept, v1 closest of all. v11/v12 (this
        # session's prompt_weighting=True controlled A/B) proved the
        # rabbit/choker/hoodie render correctly once prompt_weighting is
        # on, but both introduced NEW defects the operator flagged: v11's
        # raised hand actually reads as gripping the rabbit's ear, not a
        # peace sign (a real composition failure, hand and rabbit merged
        # confusingly), both v11/v12 have an off-concept
        # confident/coquettish expression instead of hesitant, an
        # unexplained hair "spike" ornament, and twin-tails that don't
        # match the intended shape (loop/drill-like, not long soft
        # asymmetric tails).
        #
        # v13 = v1/v2's original locked prompt (proven for pose/props/
        # rabbit/hoodie/choker/expression when not truncated) as the base,
        # with only the two changes already independently proven to work
        # inserted (v6/v8/v9/v11's "human ears, rounded ears" placed early;
        # v6/v8's "jet black hair, deep blue-black hair" hair phrasing),
        # plus three new, narrowly-targeted additions for the newly-found
        # defects: explicit twin-tail construction language, an explicit
        # no-hair-ornament negative, and an explicit hand-pose lock so the
        # newly-unlocked prompt_weighting doesn't invent a gesture again.
        # Same seed as v11/v12 for a continued controlled comparison.
        "prompt": (
            "1girl, solo, adult woman, human ears, rounded ears, portrait, upper body, delicate "
            "soft face, delicate soft dark eyes, calm gentle anime-style eye rendering, not "
            "crying, soft eyebrows, delicate fine linework, jet black hair, deep blue-black "
            "hair, long soft twin-tails past the shoulders, tied high, slightly asymmetric, "
            "loose strands, not curled, not drill-shaped, not buns, soft fluffy hair texture, "
            "one thin black choker, small white stuffed rabbit held close against her chest "
            "with both hands together, no raised hand, no gesture, no peace sign, hesitant "
            "expression between withdrawal and a smile, gaze lowered and averted, oversized "
            "hoodie covering her hands, loose hood on her shoulders, muted plum and dusty rose "
            "palette, illustration, anime style, plain background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fantasy race, demon, fairy, animal ears, "
            "child, loli, baby face, sparkle eyes, star pupils, moe eyes, crying, tears, "
            "confident, energetic, seductive, smug, silver hair, white hair, grey hair, chibi, "
            "hair ornament, star decoration, spiky bangs, spiked hair strand, sparkle in hair, "
            "hair accessory, peace sign, v-sign, raised hand, waving, pointing"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        "candidate_filename": "candidate_portrait_v13.png",
        "seed": 777001,
        "output_character": "yui",
    },
    "yui_v14": {
        # v14 (2026-07-19): identical prompt/negative to v13 -- the
        # peace-sign gesture persisted in v13 DESPITE explicit "no raised
        # hand, no gesture, no peace sign" negation, which is strong
        # evidence seed 777001 itself has a locked-in compositional prior
        # toward that pose that text negation can't override (not a
        # wording problem). Only the seed changes here, isolating that
        # one variable per the methodology's iteration discipline.
        "prompt": (
            "1girl, solo, adult woman, human ears, rounded ears, portrait, upper body, delicate "
            "soft face, delicate soft dark eyes, calm gentle anime-style eye rendering, not "
            "crying, soft eyebrows, delicate fine linework, jet black hair, deep blue-black "
            "hair, long soft twin-tails past the shoulders, tied high, slightly asymmetric, "
            "loose strands, not curled, not drill-shaped, not buns, soft fluffy hair texture, "
            "one thin black choker, small white stuffed rabbit held close against her chest "
            "with both hands together, no raised hand, no gesture, no peace sign, hesitant "
            "expression between withdrawal and a smile, gaze lowered and averted, oversized "
            "hoodie covering her hands, loose hood on her shoulders, muted plum and dusty rose "
            "palette, illustration, anime style, plain background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fantasy race, demon, fairy, animal ears, "
            "child, loli, baby face, sparkle eyes, star pupils, moe eyes, crying, tears, "
            "confident, energetic, seductive, smug, silver hair, white hair, grey hair, chibi, "
            "hair ornament, star decoration, spiky bangs, spiked hair strand, sparkle in hair, "
            "hair accessory, peace sign, v-sign, raised hand, waving, pointing"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        "candidate_filename": "candidate_portrait_v14.png",
        "seed": 918273,
        "output_character": "yui",
    },
    "yui_v15": {
        # v15 (2026-07-19): same seed as v14 (918273) -- fixed the
        # peace-sign artifact, kept unchanged to preserve that. Operator
        # feedback on v14: (1) rendering drifted toward a soft painterly/
        # watercolor look, too far from Nao's clean anime-illustration
        # register -- add explicit anime-linework language and negative
        # exclusions against painterly/watercolor rendering; (2) twin-tail
        # height must be clearly HIGH (not low pigtails/braids) --
        # "tied high" wasn't strong enough, strengthened to explicit
        # high-on-the-head placement with an explicit low-pigtail
        # negative; (3) also widened framing back toward upper-body/
        # waist-up since v14's crop was too tight to confirm rabbit/
        # choker/ears at all.
        "prompt": (
            "1girl, solo, adult woman, human ears, rounded ears, portrait, upper body, "
            "waist-up framing, delicate soft face, delicate soft dark eyes, calm gentle "
            "anime-style eye rendering, not crying, soft eyebrows, clean anime line art, cel "
            "shading, jet black hair, deep blue-black hair, twin-tails tied very high near the "
            "top of the head, not low pigtails, long soft strands, slightly asymmetric, not "
            "curled, not drill-shaped, soft fluffy hair texture, one thin black choker, small "
            "white stuffed rabbit held close against her chest with both hands together, no "
            "raised hand, no gesture, hesitant expression, gaze lowered and averted, oversized "
            "hoodie covering her hands, loose hood, muted plum and dusty rose palette, "
            "illustration, anime style, plain background"
        ),
        "negative_extra": (
            "elf, elf ears, pointed ears, long ears, fantasy race, demon, fairy, animal ears, "
            "child, loli, baby face, sparkle eyes, star pupils, moe eyes, crying, tears, "
            "confident, seductive, silver hair, white hair, grey hair, chibi, hair ornament, "
            "star decoration, spiky bangs, sparkle in hair, peace sign, v-sign, raised hand, "
            "watercolor, painterly, soft blended shading, textured canvas background, sketch, "
            "low twintails, low pigtails, braids, extreme close-up, cropped face"
        ),
        "guidance_scale": 5.5,
        "num_inference_steps": 32,
        "candidate_filename": "candidate_portrait_v15.png",
        "seed": 918273,
        "output_character": "yui",
    },
}

# CHARACTERS holds three parallel, independently-runnable Yui entries
# ("yui" = v6, "yui_v8", "yui_v10") accumulated across this session's
# iteration history -- nothing prevents accidentally invoking a stale one
# (flagged by dataops, 2026-07-19). This constant is the single source of
# truth for "which attempt is actually current"; update it, don't assume
# the bare "yui" key means the latest.
CURRENT_YUI_KEY = "yui"  # v6: best result so far (correct ears/hair; outfit/rabbit/choker
# not yet confirmed with prompt_weighting=True) -- update after the next real test.


def generate_portrait(character: str) -> Path:
    spec = CHARACTERS[character]
    check_prompt_budget(spec["prompt"], label=f"{character} portrait prompt")
    key = fal_client.api_key()
    checkpoint = CONTENT_DIR / f".fal_checkpoint_portrait_{character}.json"
    payload = {
        "model_name": MODEL_NAME,
        "prompt": spec["prompt"],
        "negative_prompt": f"{BASE_NEGATIVE}, {spec['negative_extra']}",
        "guidance_scale": spec.get("guidance_scale", GUIDANCE_SCALE),
        # Per fal.ai's own fal-ai/lora API docs (confirmed 2026-07-19 research):
        # without this flag, fal.ai hard-truncates prompts at the standard
        # ~77-token CLIP chunk instead of chunking/averaging past it. This was
        # never set anywhere in this codebase before today -- the likely real
        # root cause of Yui's outfit/rabbit/choker tags (placed after ~77
        # tokens in most attempts) never rendering, independent of wording.
        # See PORTRAIT_METHODOLOGY.md's Token budget section.
        "prompt_weighting": True,
    }
    if "seed" in spec:
        payload["seed"] = spec["seed"]
    if "num_inference_steps" in spec:
        payload["num_inference_steps"] = spec["num_inference_steps"]
    submission = fal_client.submit_resumable(
        TEXT2IMG_RUNNER,
        payload,
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["images"][0]["url"]
    out_dir = CONTENT_DIR / f"ref_{spec.get('output_character', character)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    version = spec.get("candidate_filename", "candidate_portrait_v1.png")
    path = out_dir / version
    fal_client.download(url, path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"{character}: {path}")
    return path


IMG2IMG_RUNNER = "fal-ai/lora/image-to-image"


def generate_portrait_img2img(
    character: str,
    base_image_path: Path,
    prompt: str,
    negative_extra: str,
    strength: float,
    candidate_filename: str,
    guidance_scale: float | None = None,
) -> Path:
    """img2img pass: keeps the base image's overall structure (face/ears/
    hair) at low-to-moderate strength while letting the prompt fill in
    missing elements (hoodie/rabbit/choker) rather than risking a full
    archetype swap the way repeated text2img attempts did for Yui v3-v8."""
    check_prompt_budget(prompt, label=f"{character} img2img prompt")
    if not 0.0 <= strength <= 1.0:
        raise ValueError(f"strength must be in [0.0, 1.0], got {strength}")
    key = fal_client.api_key()
    image_url = fal_client.upload(base_image_path, key)
    checkpoint = CONTENT_DIR / f".fal_checkpoint_portrait_{character}_img2img.json"
    payload = {
        "model_name": MODEL_NAME,
        "prompt": prompt,
        "negative_prompt": f"{BASE_NEGATIVE}, {negative_extra}",
        "guidance_scale": guidance_scale if guidance_scale is not None else GUIDANCE_SCALE,
        "image_url": image_url,
        "strength": strength,
        "prompt_weighting": True,  # see generate_portrait()'s comment -- fal.ai truncates at ~77 tokens without this
    }
    submission = fal_client.submit_resumable(IMG2IMG_RUNNER, payload, key, checkpoint)
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["images"][0]["url"]
    out_dir = CONTENT_DIR / f"ref_{character}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / candidate_filename
    fal_client.download(url, path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"{character} (img2img, strength={strength}): {path}")
    return path


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    targets = sys.argv[1:] or list(CHARACTERS.keys())
    for character in targets:
        if character not in CHARACTERS:
            print(f"unknown character: {character} (known: {', '.join(CHARACTERS)})")
            return 1
        generate_portrait(character)
    print(
        "\nAll candidates saved as ref_<character>/candidate_portrait_v1.png -- "
        "NOT promoted to canonical_portrait_v1.png automatically. Review each "
        "against her CHARACTER.md before locking one in, per "
        "PORTRAIT_METHODOLOGY.md's iteration discipline."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
