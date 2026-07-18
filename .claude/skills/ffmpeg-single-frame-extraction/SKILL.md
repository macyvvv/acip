---
name: ffmpeg-single-frame-extraction
description: Two ffmpeg gotchas hit twice while building somia's chained multi-clip video pipeline -- extracting a video's last frame to feed into the next generation step, and generating a single solid-color/masked PNG from a lavfi source. Both look like they should be one-liners and both fail in non-obvious ways without the right flags. Use whenever writing ffmpeg commands that produce exactly one still-image output.
---

# ffmpeg: producing exactly one still image

## Extracting a specific frame from a video (e.g. the last frame, to chain into the next generation step)

```bash
ffmpeg -y -sseof -0.1 -i input.mp4 -update 1 -frames:v 1 output.png
```

- `-sseof -0.1` seeks to 0.1s before end-of-file -- close enough to the
  last frame without risking seeking past EOF.
- `-update 1 -frames:v 1` are both required together. Without `-update 1`,
  ffmpeg may treat a single-file PNG output as if it were part of an
  image-sequence pattern and behave unexpectedly (warnings or wrong
  output) even with `-frames:v 1` present alone.

## Generating a single still image from an infinite lavfi source (e.g. a solid-color canvas or mask)

```bash
ffmpeg -y -f lavfi -i color=white:size=1024x1024 \
  -vf drawbox=x=192:y=192:w=640:h=640:color=black:t=fill \
  -frames:v 1 -update 1 output.png
```

- `color=...:size=...` (and similar lavfi sources like `nullsrc`,
  `testsrc`) generate an **infinite** stream by default -- with no frame
  limit, ffmpeg doesn't know when to stop and treats the PNG output as an
  image-sequence target.
- Confirmed failure mode: omitting `-frames:v 1 -update 1` here produced
  exit code 234, not a silent wrong-output -- the command fails outright
  rather than degrading gracefully, which makes it look like a syntax
  error in the filter graph when the actual problem is the missing output
  frame-count flags.
- The fix is the same pair of flags as the last-frame-extraction case
  above: always pass both `-frames:v 1` and `-update 1` when the desired
  output is a single still image, regardless of whether the source is a
  real video or a synthetic lavfi generator.
