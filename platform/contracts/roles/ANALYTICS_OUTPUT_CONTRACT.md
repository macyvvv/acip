# Analytics Output Contract

## Metadata

- contract_id: ANALYTICS_OUTPUT_CONTRACT
- actor: analytics agent role (data_fetch — a pluggable platform-API adapter, not a claude_invocation)
- input_source: platform API for the selected provider (X/Threads/note.com/...); dry_run by default
- output_target: platform/system/runtime/business_agents/{business_id}/analytics/{task_id}/latest.{json,md} + business_agent_stats[{business_id}:analytics].metrics
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

- **No real platform provider is implemented yet.** X's analytics-capable API tiers are paid, Threads requires Meta Graph API app approval, and note.com has no official public analytics API — each needs the operator to obtain platform API access before a real provider can be registered. This is a genuine external blocker, not something buildable from inside this repo.
- **`git_activity` (added 2026-07-14) is a real, credential-free interim provider** (`ANALYTICS_PROVIDER=git_activity`) — but it reports repository-activity proxy metrics (commits/files-touched in the last 30 days, days since last commit for the business's own `content_root`/`product_code_path`), not platform audience/engagement data. It exists so `pdca` has at least one non-`dry_run`, non-empty metrics source to Check against while real platform access is pending — do not mistake its output for impressions/engagement/conversions, and its own `notes` field says so explicitly every time.
- The KPI store itself (`platform/system/core/kpi_store.py`, `platform/system/runtime/platform/knowledge/kpi.json`) already exists and is wired into every business-agent role execution via `update_business_agent_kpi()` — run/success/failure counts are real for several roles today. Only the `metrics` sub-field has been empty, because `analytics` had never been invoked with a non-`dry_run` provider before `git_activity` existed. A 2026-07-14 repo-process consultation initially reported "no KPI store exists" — that was inaccurate; the store exists, only real metrics were missing. Corrected here so the record doesn't repeat that error.
