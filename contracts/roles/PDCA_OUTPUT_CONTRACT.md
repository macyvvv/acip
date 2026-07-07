# PDCA Output Contract

## Metadata

- contract_id: PDCA_OUTPUT_CONTRACT
- actor: pdca agent role (claude_invocation)
- input_source: business_agent_stats KPI history for the business + prior role artifacts
- output_target: system/runtime/business_agents/{business_id}/pdca/{task_id}/latest.{json,md}
- current_objective: produce a plan-do-check-act report and next-task recommendations for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, business_agent_stats KPI store
- write: none (execution adapter writes the artifact, not the invoked agent)
- execute: none
- report: plan/do/check/act sections, concrete next-task recommendations per role

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited
- scraping: prohibited
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command: confirm `latest.json` contains all four PDCA sections, none empty without an explicit "insufficient evidence" note
- expected result: concrete, business-specific next actions, not generic advice

## Emergency Stop

- condition: report recommends an action that would relax the one-shot approval baseline
- owner: human operator via Approval Console
