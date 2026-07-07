# Image Generation Output Contract

## Metadata

- contract_id: IMAGE_GENERATION_OUTPUT_CONTRACT
- actor: image_generation agent role (pluggable_provider — vendor call, not a direct claude_invocation)
- input_source: business_registry business context + scenario/prompt text + provider registry module
- output_target: system/runtime/business_agents/{business_id}/image_generation/{task_id}/latest.{json,md} + generated media path
- current_objective: produce an image artifact for one business via a pluggable, business-agnostic provider registry
- approval_required: yes (one-shot approval gate; each real run against a paid vendor is an explicit, separately-costed decision)

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
