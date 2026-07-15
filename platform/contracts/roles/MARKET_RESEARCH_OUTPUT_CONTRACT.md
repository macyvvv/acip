# Market Research Output Contract

## Metadata

- contract_id: MARKET_RESEARCH_OUTPUT_CONTRACT
- actor: market_research agent role (claude_invocation)
- input_source: business_registry business context + task description
- output_target: platform/system/runtime/business_agents/{business_id}/market_research/{task_id}/latest.{json,md}
- current_objective: produce evidence-grounded facts/assumptions/hypotheses/recommendations for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, web search results
- write: none (execution adapter writes the artifact, not the invoked agent)
- execute: none
- report: facts, assumptions, hypotheses, recommendations, evidence citations

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited
- scraping: not prohibited outright, but must respect target site terms; prefer public search
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command: confirm `latest.json` parses (it is an execution-adapter log — `business_id`/`role_id`/`task_id`/`resolved_model`/`stdout`/`exit_code`/etc., not a `facts`/`recommendations`-shaped payload) and that its `stdout` field contains clearly labeled Facts/Assumptions/Hypotheses/Recommendations sections, non-empty
- command: if the task named or implied specific products/tools downstream content will name, confirm `stdout` contains a fact-sheet entry per product (price, free-tier limit, `verified_as_of` date, source URL) — required 2026-07-15 after a DataOps audit found `doc_creation` fabricating specific prices/percentages for products no market_research artifact had ever covered (e.g. a materially wrong Perplexity Pro price, invented "70%/50%" savings figures)
- expected result: valid JSON, no placeholder/canned text reused across unrelated businesses; every named product has a dated, sourced fact sheet entry when the task calls for naming products

Corrected 2026-07-14: the previous wording ("contains non-empty
`facts`/`recommendations` lists") described a top-level JSON shape no
real artifact has ever had — every real `latest.json` on disk is the
adapter's own execution-log shape, with the actual research content as
markdown prose inside `stdout`. Fixed to describe what's actually
produced and actually checkable.

## Emergency Stop

- condition: role output references a business other than the one in scope
- owner: human operator via Approval Console
