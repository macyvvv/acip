# Analytics Output Contract

## Metadata

- contract_id: ANALYTICS_OUTPUT_CONTRACT
- actor: analytics agent role (data_fetch — a pluggable platform-API adapter, not a claude_invocation)
- input_source: platform API for the selected provider (X/Threads/note.com/...); dry_run by default
- output_target: system/runtime/business_agents/{business_id}/analytics/{task_id}/latest.{json,md} + business_agent_stats[{business_id}:analytics].metrics
- current_objective: fetch real performance metrics for a business so the pdca role has real data to Check against
- approval_required: yes (one-shot approval gate, same as every other role)

## Allowed IO

- read: the selected platform's analytics/insights API endpoints only
- write: none to the repository beyond the designated artifact and KPI store
- execute: the selected provider's fetch call, and nothing else
- report: fetched metrics (impressions, engagement, click-through, affiliate conversions, etc. as available per platform), provider name, fetch timestamp

## Prohibited IO

- external API mutation: read-only; this role must never post, edit, or delete platform content
- auto posting: yes, prohibited
- scraping: prohibited outright — official APIs only, since platform ToS violations are a real business risk
- secret use: only the specific platform API key/token required for the selected provider, read from environment, never logged
- runtime execution: limited to the provider adapter module; no arbitrary code execution

## Validation

- command: confirm the default provider remains `dry_run` (no network call, no API key, empty metrics) unless a real provider is explicitly selected and configured
- expected result: selecting the default provider never incurs cost, never requires API access, and never blocks the pipeline

## Emergency Stop

- condition: a provider call is about to run without an explicit non-default provider selection and configured credentials, or without approval
- owner: human operator via Approval Console

## Known Gaps (do not silently paper over)

- No real provider is implemented yet. X's analytics-capable API tiers are paid, Threads requires Meta Graph API app approval, and note.com has no official public analytics API — each needs the operator to obtain platform API access before a real provider can be registered.
