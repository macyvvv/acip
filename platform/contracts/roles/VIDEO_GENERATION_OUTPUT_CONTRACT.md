# Video Generation Output Contract

## Metadata

- contract_id: VIDEO_GENERATION_OUTPUT_CONTRACT
- actor: video_generation agent role (pluggable_provider — vendor call, not a direct claude_invocation)
- input_source: a `businesses/somia/content/CONTENT/{content_id}/` spec, loaded via `platform/system/scripts/somia/content_spec.py::load_content_spec()`
- output_target: `businesses/somia/content/CONTENT/{content_id}/` — provider writes `keyframe.png` (gitignored, see `.gitignore`'s `businesses/somia/content/CONTENT/**/keyframe*.png`) and a video file into that same directory, then `platform/system/scripts/somia/render_content.py::render()` appends a `render` key (`provider`, `model`, `keyframe_path`, `video_path`, `rendered_at`, `notes`) to that content id's existing `metadata.json`
- current_objective: produce a video artifact (with its keyframe image as a byproduct of the same provider call) for one Somia content item via a pluggable, vendor-agnostic provider registry
- approval_required: yes (one-shot approval gate; each real run against a paid vendor is an explicit, separately-costed decision)

Documented against the actual implementation 2026-07-14, after a repo-wide
consultation found the previous `output_target`
(`system/runtime/business_agents/{business_id}/video_generation/{task_id}/`)
was never used by any real code — Somia is the only implementation of
this role, and it has no notion of `business_id`/`task_id` at all.

## Important: image generation is not a separate stage here

There is no independent image-generation provider call in this
pipeline. `platform/system/scripts/somia/providers.py` is a
`VideoGenerationProvider` registry; each real provider
(`providers_illustrious_kling.py`, `providers_kling.py`,
`providers_pika.py`) generates the keyframe image and the video inside
one `generate()` call. If a business ever needs standalone image-only
generation independent of video, that would be new code, not something
this role already does — see `IMAGE_GENERATION_OUTPUT_CONTRACT.md`'s own
note on this.

## Allowed IO

- read: the `businesses/somia/content/CONTENT/{content_id}/` spec (via `load_content_spec()`)
- write: `keyframe.png`, the video file, and the `render` key appended to that content id's `metadata.json` — nothing else
- execute: the selected vendor provider's API call (`SOMIA_VIDEO_PROVIDER` env var / `--provider` flag; default `dry_run`), and nothing else
- report: provider name, model, keyframe/video paths, cost if known

## Prohibited IO

- external API mutation: only the single selected provider call is allowed; no other external mutation
- auto posting: yes, prohibited
- scraping: prohibited
- secret use: only the specific vendor API key required for the selected provider (`SOMIA_VIDEO_API_KEY` or equivalent), read from environment, never logged
- runtime execution: limited to the provider adapter module; no arbitrary code execution

## Known Gaps (honest, not yet fixed)

- **No cost tracking.** `RenderResult` has no cost field; neither
  `providers_kling.py` nor `providers_pika.py` estimate or report cost
  anywhere, despite this contract requiring it "if known." Currently
  never known.
- **Approval gate is not enforced in code.** Provider selection today is
  just an env var / CLI flag — nothing in `render_content.py` or
  `providers.py` checks or records an approval before a paid provider
  runs. The `approval_required: yes` above is a stated intent, not an
  enforced mechanism, unlike Level 3a/3c's real
  `execution_pre_approval_policy.py` gate for business-agent execution.
  Do not assume this is enforced; treat every real (non-`dry_run`)
  invocation as needing a manual go-ahead until this gap is closed.
- **No retry/backoff or resume.** `fal_client.py`'s `fal_request`/`await_result`
  raise immediately on any transient HTTP failure (429/500/gateway
  timeout) with no retry, and there is no way to resume against an
  already-submitted job if the process dies mid-poll — a transient
  network blip during a multi-minute render loses the whole (paid) job.
- **Duration/caption downgrades are silent.** Real providers cap
  duration below spec (e.g. 10s vs. a 12s request) and don't composite
  on-screen text — this is only ever surfaced as a free-text string in
  `RenderResult.notes`, not a structured field `render_content.py` can
  act on, so nothing distinguishes "rendered exactly to spec" from
  "rendered with a silent downgrade" without reading prose.

## Validation

- command: confirm the default provider remains `dry_run` (no network call, no API key) unless a real provider is explicitly selected
- expected result: selecting the default provider never incurs cost or requires a vendor API key

## Emergency Stop

- condition: a provider call is about to run without an explicit non-default provider selection, or without approval
- owner: human operator via Approval Console
