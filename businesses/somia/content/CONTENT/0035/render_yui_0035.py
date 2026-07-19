#!/usr/bin/env python3
"""Production render for content 0035 (Yui, "Stays Anyway"), her first
episode. Adapted from businesses/somia/content/CONTENT/0007/render_final_3act.py
(Nao's validated methodology) after a full multi-lens review pass -- see
script.md's Review Pass section and prompt.md's Revision note for the
full reasoning behind every prompt choice below.

Structural differences from Nao's episode, all deliberate (see script.md
Design Note):
- 4 acts (not 3) + a closing bridge, mapping her 5-step Daily Loop.
- No acknowledgment-of-viewer beat anywhere -- she never looks toward
  camera, in any act.
- The bridge targets a frame extracted a beat INTO Act 1, not Act 1's
  literal first frame -- the loop is approached, not landed on exactly
  (character-psychology's structural-over-resolution finding).
- A new per-character signature technique (double-exposure ghosting of
  the room's geometry, Act 3 only) is authored here for the first time.

Identity anchor: reuses the already-locked
`businesses/somia/content/CONTENT/ref_yui/canonical_portrait_v1.png`
directly -- no Stage 1 regeneration, per PORTRAIT_METHODOLOGY.md's
locking discipline and YUI.md's own note that both approved draws
rendered silver-gray hair (accepted imperfection, not re-rolled).

Real fal.ai spend: 4 video generations at $0.112/sec (9+9+10+9=37s) plus
a 4s bridge generation, ~$4.59 total, pre-approved by the operator for
this whole episode. Run from repo root: PYTHONPATH=platform
.venv/bin/python businesses/somia/content/CONTENT/0035/render_yui_0035.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from system.core.dotenv import load_dotenv  # noqa: E402
from system.scripts.somia import fal_client  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent
REF_YUI_DIR = CONTENT_DIR.parent / "ref_yui"
RUNNER = "fal-ai/kling-video/o1/reference-to-video"
BRIDGE_RUNNER = "fal-ai/kling-video/o1/image-to-video"
ASPECT_RATIO = "9:16"

# Shared negative-space guidance is folded directly into each prompt below
# (reference-to-video has no negative_prompt field, confirmed for Nao's
# episode and unchanged here -- positive-only phrasing throughout).

ACT1_PROMPT = (
    "@Element1, an ordinary human girl with ordinary rounded human ears, not pointed, not elf ears, no "
    "fantasy features, curled small on a floor cushion tucked into the corner of a plain modest room with "
    "soft, hazy, blurred-focus edges and quietly uneven proportions -- the wall lines and corners should "
    "read as gently soft-focus and slightly imprecise throughout, not a sharp, clean, detailed bedroom -- "
    "a loose blanket around her legs and its near edge visible at the bottom of frame, small white stuffed "
    "rabbit held to her chest with both arms, chin low near its head, gaze downward, silver-gray twin-tail "
    "hair, oversized soft hoodie with thick fabric loosely swallowing her hands at the cuffs, thin choker, "
    "her lips stay gently closed throughout the entire clip, no open mouth, no visible teeth, held still for "
    "the first three seconds of the clip -- breath and a minute weight shift only, not a locked frame -- "
    "then her head lifts by a small controlled degree and her gaze drifts toward the middle distance of the "
    "room, never toward the camera, no gaze-lock at any point, as she quietly registers she is no longer "
    "alone, no startle, no gasp, no widened eyes, lips staying closed, from that moment her grip on the "
    "rabbit tightens incrementally in one direction only through to the end of the clip, it does not loosen "
    "or oscillate, the camera holds a fixed, slightly off-center medium-close framing at low seated-eye-level "
    "and pushes in continuously at a slow constant rate starting from the very first frame, no reversal, "
    "no re-acceleration, no cuts, anime illustration style"
)

ACT2_PROMPT = (
    "@Element1 continuing from @Image1, an ordinary human girl with ordinary rounded human ears, not pointed, "
    "no elf ears, still curled in the same corner cushion nook with soft hazy blurred-focus edges, silver-gray "
    "twin-tail hair, oversized soft hoodie, thin choker, her lips stay closed throughout, no open mouth, rabbit "
    "held one-armed against her side, the grip-tightening "
    "already in progress from the moment before continues for one to two seconds then resolves into a small, "
    "contained inward flinch of her shoulders -- not dramatic, not a collapse -- and her weight shifts a "
    "fraction deeper into the corner, one hand releases the rabbit partway and moves to draw her hood up, "
    "this lifting motion stalls at the hood's halfway point partway through the clip and holds there for the "
    "remainder, it does not complete the pull and does not lower back down, one single continuous arc only, "
    "it does not restart or reverse, during this held stall her breath continues visibly and a faint, "
    "separate small tightening occurs again in her grip on the rabbit's arm, distinct from the earlier "
    "tightening, the camera continues the exact same slow constant push-in rate established from the start, "
    "no change in rate or direction, no cuts, anime illustration style"
)

ACT3_PROMPT = (
    "@Element1 continuing from @Image1, an ordinary human girl with ordinary rounded human ears, not pointed, "
    "no elf ears, hood still half-raised where it stalled, silver-gray twin-tail hair, lips closed throughout, "
    "in the first second the stalled hand releases the hood motion, lowering or simply resting, then a real "
    "but small partial rise begins -- one hand presses flat against the cushion, her weight shifts up and "
    "forward a genuine but small amount, her body angles a few degrees toward an unseen doorway in the room, "
    "not a full stand, quiet and private, not directed at the camera -- partway through this motion it "
    "arrests suddenly, interrupted before completing: the nearest visible edge of the cushion nook briefly "
    "renders as two faint overlapping lines offset slightly sideways from each other, visible for a bare "
    "instant before the second line fades back into the first, resolving to one single clean edge again, a "
    "brief architectural double-exposure in the room itself, not a light flare, not a digital glitch, purely "
    "the room's own soft edges briefly losing their coherence, the small white rabbit held in her arms stays "
    "completely stable and unaffected through this, only the room's edge is involved, at the exact same "
    "instant her grip on the rabbit reaches the single tightest point of the whole sequence, caused by "
    "witnessing this, not by anything else, no startle, no widened eyes, no flinch toward it, her only "
    "visible response is the grip, the partial rise does not complete and does not reverse further, her "
    "weight stays arrested partway forward for the rest of the clip, the camera continues the same constant "
    "slow push-in rate throughout, unchanged, but this push-in stays very small and subtle across the whole "
    "clip -- by the final frame her knees, the cushion edge, and both her hands holding the rabbit must still "
    "be clearly visible in frame, a wide/medium-full shot, NOT a tight close-up on her face or upper body, "
    "if uncertain keep the framing wider rather than tighter, no cuts, anime illustration style"
)

ACT4_PROMPT = (
    "@Element1 continuing from @Image1, an ordinary human girl with ordinary rounded human ears, not pointed, "
    "no elf ears, weight still arrested partway through rising, silver-gray twin-tail hair, lips closed, "
    "neutral or faintly worried mouth, absolutely no smile, no upturned mouth corners, no content or pleased "
    "expression, her expression stays a little unresolved and uncertain throughout, never reads as fully at "
    "ease or satisfied, "
    "the same floor cushion nook and room corner established in every prior act -- a low floor cushion in a "
    "room corner, NOT a couch, NOT a sofa, NOT any raised seating furniture, no throw pillows, the furniture "
    "and room must exactly match Acts 1-3, "
    "for the first two seconds the camera continues the exact same push-in rate as before, no pause, "
    "then her arrested rise does not complete upward -- instead her weight lowers back down onto the cushion "
    "in one single continuous downward motion, no false starts, no smile forming at any point, as this "
    "settles the camera begins its only direction change in the whole sequence, a single slow easing "
    "backward at roughly the same rate, reversed, beginning only once her weight has settled and not before, "
    "this easing-back must be clearly visible and obvious on screen, not subtle -- by the end of the clip the "
    "framing must have visibly loosened back out to a wide/medium-full shot closely matching how the sequence "
    "began, with her knees, the cushion edge, and her full curled posture clearly back in frame, NOT still a "
    "tight close-up, "
    "the blanket resettles around her legs, the raised hood lowers back down partway on its own from the "
    "settling motion rather than a separate deliberate gesture, her grip on the rabbit loosens gradually from "
    "its tightest point back toward a much looser hold without fully releasing, one continuous loosening "
    "motion, by the end of the clip her posture and framing closely resemble how she began this whole "
    "sequence -- curled on the same cushion, rabbit held to her chest with both arms, chin lowering toward it, "
    "gaze low, wide/medium-full shot -- close to that opening posture but not required to match it exactly, "
    "her breath stays visibly present throughout, never frozen still, no cuts, anime illustration style"
)

BRIDGE_PROMPT = (
    "the woman in @Image1, an ordinary human girl with ordinary rounded human ears, not pointed, no elf ears, "
    "remains curled on the floor cushion in the corner nook, silver-gray twin-tail hair, lips closed, "
    "small white stuffed rabbit held to her chest, framed in the same wide/medium-full shot as the rest of "
    "the sequence with her knees and the cushion edge visible, NOT a tight close-up, the blanket around her "
    "settles a fraction further, her "
    "breathing continues at a slow even rate, her grip on the rabbit eases the last small remaining amount "
    "into a looser, calmer hold, the soft edges of the room make one final small, gentle re-settle, calmer "
    "and much smaller than any prior disturbance, transitioning smoothly toward the framing and posture shown "
    "in @Image2, camera holds its position with only the motion the transition itself requires, no cuts, "
    "anime illustration style"
)

# Durations match script.md's Timeline exactly: Act1 9s, Act2 9s, Act3 10s
# (18.0-28.0s), Act4 9s, bridge 4s.
ACT_DURATIONS = {"act1": "9", "act2": "9", "act3": "10", "act4": "9"}
BRIDGE_DURATION = "4"


def generate_act(act_name: str, prompt: str, portrait_url: str, start_frame_url: str | None, duration: str) -> Path:
    key = fal_client.api_key()
    elements = [{"frontal_image_url": portrait_url, "reference_image_urls": [portrait_url]}]
    payload = {
        "prompt": prompt,
        "elements": elements,
        "duration": duration,
        "aspect_ratio": ASPECT_RATIO,
    }
    if start_frame_url:
        payload["image_urls"] = [start_frame_url]

    checkpoint = CONTENT_DIR / f".fal_checkpoint_{act_name}.json"
    submission = fal_client.submit_resumable(RUNNER, payload, key, checkpoint)
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    video_url = result["video"]["url"]
    video_path = CONTENT_DIR / f"final_{act_name}.mp4"
    fal_client.download(video_url, video_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"{act_name}: {video_path}")
    return video_path


def generate_bridge(prompt: str, start_frame_url: str, end_frame_url: str, duration: str) -> Path:
    key = fal_client.api_key()
    payload = {
        "prompt": prompt,
        "start_image_url": start_frame_url,
        "end_image_url": end_frame_url,
        "duration": duration,
        "aspect_ratio": ASPECT_RATIO,
    }
    checkpoint = CONTENT_DIR / ".fal_checkpoint_bridge.json"
    submission = fal_client.submit_resumable(BRIDGE_RUNNER, payload, key, checkpoint)
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    video_url = result["video"]["url"]
    video_path = CONTENT_DIR / "final_bridge.mp4"
    fal_client.download(video_url, video_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"bridge: {video_path}")
    return video_path


def _laplacian_variance(image_path: Path) -> float:
    """Sharpness score -- reused verbatim from render_final_3act.py."""
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(image_path), "-vf", "convolution=-1 -1 -1 -1 8 -1 -1 -1 -1",
            "-f", "rawvideo", "-pix_fmt", "gray", "-"
        ],
        check=True, capture_output=True,
    )
    data = result.stdout
    if not data:
        return 0.0
    mean = sum(data) / len(data)
    variance = sum((b - mean) ** 2 for b in data) / len(data)
    return variance


def extract_last_frame(video_path: Path, out_path: Path) -> Path:
    """Sharpest-of-several-candidates extraction -- reused verbatim from
    render_final_3act.py (mlops finding: the literal last frame of a
    continuous push-in clip carries the most motion blur)."""
    candidates_dir = out_path.parent / f".{out_path.stem}_candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    offsets = ["-1.0", "-0.7", "-0.4", "-0.2", "-0.1"]
    scored: list[tuple[float, Path]] = []
    for i, offset in enumerate(offsets):
        candidate_path = candidates_dir / f"candidate_{i}.png"
        proc = subprocess.run(
            ["ffmpeg", "-y", "-sseof", offset, "-i", str(video_path), "-update", "1", "-frames:v", "1", str(candidate_path)],
            capture_output=True,
        )
        if proc.returncode != 0 or not candidate_path.exists():
            continue
        score = _laplacian_variance(candidate_path)
        scored.append((score, candidate_path))
        print(f"  candidate at {offset}s: sharpness={score:.1f}")

    if not scored:
        subprocess.run(
            ["ffmpeg", "-y", "-sseof", "-0.1", "-i", str(video_path), "-update", "1", "-frames:v", "1", str(out_path)],
            check=True, capture_output=True,
        )
        return out_path

    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_score, best_path = scored[0]
    best_path.replace(out_path)
    print(f"  selected sharpest candidate (score={best_score:.1f}) as {out_path.name}")
    return out_path


def extract_near_opening_frame(video_path: Path, out_path: Path, offset_s: float = 1.2) -> Path:
    """Bridge target per the character-psychology revision: NOT Act 1's
    literal first frame (that would be a structural over-resolution --
    the loop landing on an exact pixel-identical return). Extracts a
    frame a beat into Act 1 instead, so the bridge approaches the opening
    state without landing on it exactly."""
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(offset_s), "-i", str(video_path), "-frames:v", "1", str(out_path)],
        check=True, capture_output=True,
    )
    return out_path


def _act_or_generate(act_name: str, prompt: str, portrait_url: str, start_frame_url: str | None, duration: str) -> Path:
    """Resumability guard, reused from render_final_3act.py."""
    existing = CONTENT_DIR / f"final_{act_name}.mp4"
    if existing.exists():
        print(f"{act_name}: {existing} already exists, skipping regeneration (delete it first to force a re-render)")
        return existing
    return generate_act(act_name, prompt, portrait_url, start_frame_url, duration)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    key = fal_client.api_key()

    portrait_path = REF_YUI_DIR / "canonical_portrait_v1.png"
    print(f"Using Yui's locked identity reference: {portrait_path}")
    if not portrait_path.exists():
        print("ERROR: canonical_portrait_v1.png not found -- Yui's portrait must be locked before this can run.")
        return 1
    portrait_url = fal_client.upload(portrait_path, key)
    print(f"uploaded portrait: {portrait_url}")

    act1_path = _act_or_generate("act1", ACT1_PROMPT, portrait_url, None, ACT_DURATIONS["act1"])
    act1_last_frame = extract_last_frame(act1_path, CONTENT_DIR / "final_act1_last_frame.png")
    act1_last_frame_url = fal_client.upload(act1_last_frame, key)
    act1_near_opening = extract_near_opening_frame(act1_path, CONTENT_DIR / "final_act1_near_opening_frame.png")
    act1_near_opening_url = fal_client.upload(act1_near_opening, key)

    act2_path = _act_or_generate("act2", ACT2_PROMPT, portrait_url, act1_last_frame_url, ACT_DURATIONS["act2"])
    act2_last_frame = extract_last_frame(act2_path, CONTENT_DIR / "final_act2_last_frame.png")
    act2_last_frame_url = fal_client.upload(act2_last_frame, key)

    act3_path = _act_or_generate("act3", ACT3_PROMPT, portrait_url, act2_last_frame_url, ACT_DURATIONS["act3"])
    act3_last_frame = extract_last_frame(act3_path, CONTENT_DIR / "final_act3_last_frame.png")
    act3_last_frame_url = fal_client.upload(act3_last_frame, key)

    act4_path = _act_or_generate("act4", ACT4_PROMPT, portrait_url, act3_last_frame_url, ACT_DURATIONS["act4"])
    act4_last_frame = extract_last_frame(act4_path, CONTENT_DIR / "final_act4_last_frame.png")
    act4_last_frame_url = fal_client.upload(act4_last_frame, key)

    bridge_existing = CONTENT_DIR / "final_bridge.mp4"
    if bridge_existing.exists():
        print(f"bridge: {bridge_existing} already exists, skipping regeneration (delete it first to force a re-render)")
        bridge_path = bridge_existing
    else:
        bridge_path = generate_bridge(
            BRIDGE_PROMPT, act4_last_frame_url, act1_near_opening_url, duration=BRIDGE_DURATION
        )

    concat_list = CONTENT_DIR / "final_concat_list.txt"
    concat_list.write_text(
        f"file '{act1_path.name}'\nfile '{act2_path.name}'\nfile '{act3_path.name}'\n"
        f"file '{act4_path.name}'\nfile '{bridge_path.name}'\n",
        encoding="utf-8",
    )
    combined_path = CONTENT_DIR / "final_video_41s.mp4"
    # Full re-encode via the concat filter, not the concat demuxer's -c copy,
    # per Nao's confirmed playback-freeze bug at act boundaries (independently
    # generated clips restart H.264 parameter sets at each cut).
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(act1_path), "-i", str(act2_path), "-i", str(act3_path),
            "-i", str(act4_path), "-i", str(bridge_path),
            "-filter_complex", "[0:v][1:v][2:v][3:v][4:v]concat=n=5:v=1:a=0[v]",
            "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-r", "24", "-crf", "16", "-preset", "slow", str(combined_path),
        ],
        check=True,
        cwd=CONTENT_DIR,
    )
    print(f"combined ~41s video (audio/text not yet composited): {combined_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
