# Marketing Output Contract

## Metadata

- contract_id: MARKETING_OUTPUT_CONTRACT
- actor: marketing agent role (claude_invocation)
- input_source: business_registry business context + prior market_research artifacts + task description
- output_target: system/runtime/business_agents/{business_id}/marketing/{task_id}/latest.{json,md}
- current_objective: produce positioning/messaging/channel-specific copy for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, web search results
- write: none (execution adapter writes the artifact, not the invoked agent)
- execute: none
- report: positioning statement, target audience/channel, copy drafts

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited for the role invocation itself; a separate, policy-gated publishing pipeline (see ADR-0035) may post a human-finalized excerpt of this role's output -- the role never gains posting IO directly
- scraping: not prohibited outright, but must respect target site terms
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command: confirm `latest.json` parses and names an explicit audience/channel for every copy draft
- expected result: valid JSON, no unattributed audience/channel claims
- command: confirm the output states what the self-critique pass changed/cut (see `.claude/agents/marketing.md`'s "Self-Critique" section) — specificity, payoff completeness, experience honesty, template-detection
- expected result: no unresolved vague claims, no undelivered hooks/teasers, no fabricated first-person experience presented as real, no verbatim-repeated structure across multiple drafted items

## Emergency Stop

- condition: role output implies content has been published/posted
- owner: human operator via Approval Console
