# Status: in progress, direction found, 2026-07-18 (superseded most of this file's earlier content)

The token-budget wall documented below (and in
`.claude/skills/writing-illustrious-xl-prompts/SKILL.md`) is effectively
**resolved** by a different method than anything tried before it. The
LoRA-training tangent (still described further down for the record) is
no longer the leading path -- it's not needed.

## What's actually true right now

- **`fal-ai/kling-video/o1/reference-to-video` works well and is the new
  leading path.** Instead of generating an SDXL/Illustrious-XL keyframe
  that must carry both identity AND scene tokens (the root cause of every
  prior failure), this endpoint conditions the *video* model directly on
  a reference portrait image (`elements: [{frontal_image_url,
  reference_image_urls}]`) and spends the entire text prompt on
  scene/motion/camera only. A validation test (`test_kling_reference_to_video.py`,
  output `kling_reference_test.mp4` / `kling_ref_frame_*.png`) produced
  clean Illustrious-XL-style linework, consistent face/hair/earring
  across the clip, and a correct window/curtain/sea scene -- no
  token-budget dilution, no garbled text, no distortion. This is
  fully headless/API-driven, unlike the Live2D direction that was
  considered and set aside (see below).
- **The reference portrait's outfit was wrong** (inherited a
  sailor-collar/ribbon/button look from `stage1_portrait.png`'s
  `PORTRAIT_PROMPT` in `render_two_stage.py`, root-caused to "cardigan"
  pulling in school-uniform training-data associations on this
  checkpoint) -- **fixed**: `PORTRAIT_PROMPT`/`NEGATIVE_PROMPT` in
  `render_two_stage.py` corrected after a fresh direct re-check of
  `ref_nao/character_sheets/somia_nao01.png`/`somia_nao02.png` (not the
  TRANSCRIPTION.md summary alone). `stage1_portrait.png` has **not yet
  been regenerated** with the corrected prompt -- do that before the next
  `test_kling_reference_to_video.py` run.
- **The scenario/mechanism itself was found weak, independent of visual
  execution.** Three independent reviews (scenario-writing, a
  philosophical read, a psychological read) converged: Act 2 as designed
  (v5) reads as a generic "she notices you and smiles" trope, legible as
  meaningful mainly to someone who already knows the design intent, not a
  cold viewer. The operator then precisely clarified the brand's
  Fetishism lever (now the authoritative version in
  `businesses/somia/content/BRAND/BRAND_IDENTITY.md`): warmth she shows is
  real-but-passing, driven by her own 幼稚性 (immaturity/unsettledness),
  never a deliberate acknowledgment of the viewer and never a stable
  dependency on the viewer -- she's still searching for what she actually
  needs (依存先を探している), and the viewer is only incidentally
  present. **`script.md` v6 rewrites Act 2, Signature Item, and Visual
  accordingly**: the earring-glint-synced-to-the-turn staging (v5) is
  reversed (it read as a reward timed to the viewer, i.e. staging
  inclusion); the turn/smile is now specified as self-directed/private,
  not a composed acknowledgment. `NAO.md`'s Dependency Trigger section
  and Visual Identity/Outfit section were updated to match.
- **A psychological finding worth remembering for future episodes**: a
  fixed-timing, byte-identical video loop is not good repeat-watch
  psychology (habituation, not variable reward, is the operative
  mechanism for an unchanging stimulus) -- and genuine per-*playback*
  variation is technically impossible with a single pre-rendered file (no
  live/procedural generation in this pipeline). The realistic implication
  discussed: a single clip's job may be a strong first watch, with
  cross-episode variety (not within-clip variety) doing the work of
  sustained repeat engagement. Not yet resolved into a concrete
  cross-episode plan.

## Live2D (considered, set aside for this episode)

A pivot to rigging Nao as a Live2D model (identity locked once via a
static rig, reused across episodes, decoupled from per-episode scene
generation) was seriously evaluated. devops's operational critique found
real, not cosmetic, blockers: Cubism Editor is a Windows-only GUI
application with no path to running in this repo's headless/agent-driven
automation (not on this Mac session, not on any existing GitHub Actions
runner); a community GUI-automation tool (`live2d-automation`) claiming
to bridge that gap is unverified, single-maintainer, and GUI-automation
tools of that kind break silently on vendor UI updates; this repo has no
Git LFS and already strains under committed binary MP4/PNG assets, which
Live2D rig files would worsen; the FREE tier's commercial-use eligibility
is revenue-threshold-gated with no compliance tripwire in this repo. Net
finding: this would not become a single scriptable pipeline step like
`render_content.py` -- it splits into an automated half and a permanently
manual, off-repo half. Not pursued further once the Kling
reference-to-video approach validated as a fully-automatable alternative
that solves the same root problem.

## LoRA-training research (2026-07-18, kept for the record -- not the current path)

fal.ai's own dedicated LoRA-*training* endpoint
(`fal-ai/flux-lora-fast-training`) trains FLUX only; no SDXL/
Illustrious-XL training endpoint was found on fal.ai. Its *inference*
endpoints (`fal-ai/lora`) do accept a `loras` parameter for
externally-trained weights. Civitai's on-site trainer has a native
"illustrious" base-model preset and produces downloadable/portable
epochs (confirmed via primary sources), making it the strongest
candidate *if* this direction is ever revisited -- but it's superseded by
the reference-to-video approach above for this episode's actual problem.

## Before resuming work here

1. Read this file and `script.md`'s full Design Note history (through v6).
2. Regenerate `stage1_portrait.png` via `render_two_stage.py`'s
   `generate_portrait()` with the corrected `PORTRAIT_PROMPT` before
   trusting it as the reference for `test_kling_reference_to_video.py`.
3. The 3-act full episode has not yet been produced via the
   `fal-ai/kling-video/o1/reference-to-video` approach -- only a single
   5s validation clip exists. Building the full 30s/3-act version with
   this method (and verifying the v6 Act 2 staging actually renders as
   self-directed rather than viewer-directed) is the next real step, not
   yet done.
4. `render_3act.py` (single-stage keyframe+Kling chain) is superseded --
   do not resume it.
