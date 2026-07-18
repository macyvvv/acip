---
name: compositing-somia-onscreen-text
description: Composites a somia CONTENT/<id> spec's on-screen text onto its rendered video.mp4, which render_content.py's providers (illustrious_kling, kling, pika) never do automatically -- every one of them returns spec_deviations noting "on_screen_text: not composited into the video (requires a separate compositing pass)". Use this after running render_content.py for any somia content whose script.md/prompt.md has non-empty on-screen text, before treating that content as finished/deliverable. This machine's ffmpeg build has no drawtext filter (freetype not compiled in), so this uses a Chrome-headless-screenshot + colorkey + overlay workaround instead.
---

# Compositing on-screen text onto a somia render

## Why this is a separate step

`render_content.py`'s video providers (`providers_illustrious_kling.py`,
`providers_kling.py`, `providers_pika.py` via `providers_fal_common.py`)
generate the keyframe and video but never burn in `spec.on_screen_text` --
every provider's `RenderResult.spec_deviations` explicitly says so. A
render is not complete/deliverable until this step runs, if the spec has
on-screen text at all (check `script.md`'s `## Text` section /
`ContentSpec.on_screen_text` -- some specs have none).

## Why not `ffmpeg drawtext`

This machine's `ffmpeg` (verify with `ffmpeg -filters | grep drawtext`) has
no `drawtext` filter -- the build lacks libfreetype. Don't waste time
retrying drawtext variations; go straight to the Chrome-headless route
below.

## Why not `blend=screen` for the transparency workaround

Chrome's `--screenshot` CLI flag does not produce true alpha transparency
even with `background: transparent` in CSS -- it flattens to a background
color. The natural-seeming fix (render text on a black background, then
`blend=all_mode=screen`) introduces a magenta/purple color cast across the
**entire frame**, not just the text area -- a PC-range vs. video-range
mismatch between how the PNG and the h264 video are interpreted. Confirmed
by direct before/after frame comparison. Use `colorkey` + `overlay`
instead, which does not have this problem.

## Steps

1. **Write an HTML file** with the exact on-screen text, styled to match
   the brand's quiet/elegant register (a thin serif -- `Didot` or
   `Baskerville` from `/System/Library/Fonts/Supplemental/`, not a bold
   sans -- white-ish text, subtle shadow for legibility, positioned per
   the shot, e.g. lower-third). Background **must be solid black**
   (`#000000`), not `transparent`:
   ```html
   <style>
     html, body { margin:0; padding:0; width:1440px; height:1440px; background:#000000; }
     .wrap { width:1440px; height:1440px; display:flex; align-items:flex-end; justify-content:center; padding-bottom:180px; box-sizing:border-box; }
     .line { font-family: Didot, Georgia, serif; font-size:52px; letter-spacing:0.04em; color:rgba(255,255,255,0.94); text-shadow:0 2px 10px rgba(0,0,0,0.45); }
   </style>
   <div class="wrap"><div class="line">Your text here.</div></div>
   ```
   Match `width`/`height` to the actual video resolution (check with
   `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video.mp4` --
   somia renders have been 1440x1440 square so far, don't assume this holds forever).

2. **Screenshot it with Chrome headless**:
   ```
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless --disable-gpu --hide-scrollbars --window-size=<W>,<H> \
     --screenshot=/tmp/text_overlay.png /tmp/text_overlay.html
   ```
   The `CVDisplayLinkCreateWithCGDisplay failed` stderr lines are harmless
   headless-mode noise, not a real failure -- check the PNG was actually
   written, not the stderr content.

3. **Composite with ffmpeg** using `colorkey` (not `blend`) to key out the
   black background, with a fade timed to the spec's on-screen-text window
   (e.g. `script.md` said text appears 7.0-9.0s):
   ```
   ffmpeg -y -i video.mp4 -loop 1 -i /tmp/text_overlay.png \
     -filter_complex "[1:v]format=rgba,colorkey=0x000000:0.20:0.10,fade=t=in:st=7:d=0.6:alpha=1,fade=t=out:st=9:d=0.6:alpha=1[txt];[0:v][txt]overlay=0:0:shortest=1[outv]" \
     -map "[outv]" -map "0:a?" -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a copy \
     video_final.mp4
   ```
   In zsh, quote `"0:a?"` -- an unquoted trailing `?` is interpreted as a
   glob and fails with "no matches found".

4. **Verify before/after with extracted frames**, don't trust a clean
   ffmpeg exit alone:
   ```
   ffmpeg -y -ss <t_before_fade_in> -i video_final.mp4 -update 1 -frames:v 1 /tmp/check_before.png
   ffmpeg -y -ss <t_during_text> -i video_final.mp4 -update 1 -frames:v 1 /tmp/check_after.png
   ```
   Confirm: no text/no color shift in the "before" frame, correct text +
   correct (unshifted) scene color in the "during" frame.

5. **Record what you did** in the content's `metadata.json` under a
   `post_processing` key (method, output path, verification performed) --
   this step has no automated record the way `render_content.py`'s own
   `render` block does, so it's easy for a future pass to not realize it
   already happened, or to not know how, without this.

## Output convention

Keep the raw provider output (`video.mp4`) alongside the composited
deliverable (`video_final.mp4`) -- don't overwrite the raw render. The
raw file is useful if the text/timing needs to change without re-spending
on a real video generation call.
