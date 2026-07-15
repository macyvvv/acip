# Image Generation Output Contract

## Metadata

- contract_id: IMAGE_GENERATION_OUTPUT_CONTRACT
- actor: image_generation agent role (pluggable_provider — vendor call, not a direct claude_invocation)
- input_source: business_registry business context + scenario/prompt text + provider registry module
- output_target: `platform/system/runtime/business_agents/{business_id}/image_generation/{task_id}/latest.{json,md}` + generated media path
- current_objective: produce a standalone image artifact for one business via a pluggable, business-agnostic provider registry
- approval_required: yes (one-shot approval gate; each real run against a paid vendor is an explicit, separately-costed decision)

## Important: this role has no implementation today

A repo-wide consultation (2026-07-14) confirmed there is no dedicated
image-generation provider registry anywhere in the repo, and no
`platform/system/runtime/business_agents/*/image_generation/` directory has ever
been created. The only place image generation actually happens is as the
keyframe half of Somia's `video_generation` provider call chain (see
`VIDEO_GENERATION_OUTPUT_CONTRACT.md`) — a fused text-to-image step
inside `providers_illustrious_kling.py`/`providers_kling.py`/`providers_pika.py`'s
`generate()`, using `fal-ai/lora` (text-to-image), writing straight to
`businesses/platform/somia/content/CONTENT/{content_id}/keyframe.png`. That path is **not** this
contract's `output_target`, and this role is not currently invocable as
an independent stage for Somia.

Separately, Somia's production pipeline notes
(`businesses/platform/somia/content/PRODUCTION/PIPELINE.md`) name an img2img reference-consistency
step (`fal-ai/lora/image-to-image`, `noise_strength≈0.45` against a
character's `ref_*/keyframe.png`) as "the single biggest quality lever" —
but that step is marked `[manual]` there and has no provider adapter code
at all. It is done by hand outside this contract's scope entirely,
which is exactly why the parameter name this repo has previously gotten
wrong (`noise_strength`, not `strength`) is easy to get wrong: it's never
been exercised by tested code, only by one-off scripts.

This contract's `output_target`/shape below is kept as the intended
generic convention for a future business that needs standalone image-only
generation independent of video — implement against it if/when that need
is real, rather than assuming it already works.

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, scenario/prompt specs
- write: generated media file to the artifact output path only
- execute: the selected vendor provider's API call, and nothing else
- report: provider name, model/version used, output path, cost if known

## Prohibited IO

- external API mutation: only the single selected provider call is allowed; no other external mutation
- auto posting: yes, prohibited
- scraping: prohibited
- secret use: only the specific vendor API key required for the selected provider, read from environment, never logged
- runtime execution: limited to the provider adapter module; no arbitrary code execution

## Validation

- command: confirm the default provider remains `dry_run` (no network call, no API key) unless a real provider is explicitly selected
- expected result: selecting the default provider never incurs cost or requires a vendor API key

## Emergency Stop

- condition: a provider call is about to run without an explicit non-default provider selection, or without approval
- owner: human operator via Approval Console
