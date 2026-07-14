# Document Creation Output Contract

## Metadata

- contract_id: DOC_CREATION_OUTPUT_CONTRACT
- actor: doc_creation agent role (claude_invocation)
- input_source: business_registry business context + task description
- output_target: system/runtime/business_agents/{business_id}/doc_creation/{task_id}/latest.{json,md}
- current_objective: produce a complete document artifact for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

## Allowed IO

- read: repository files, existing business_agent runtime artifacts
- write: none (execution adapter writes the artifact, not the invoked agent)
- execute: none
- report: complete document content matching the requested format

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited for the role invocation itself; a separate, policy-gated publishing pipeline (see ADR-0035) may post a human-finalized excerpt of this role's output -- the role never gains posting IO directly
- scraping: prohibited (this role should not need external browsing)
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command: confirm `latest.md` contains complete content, not an outline/placeholder
- expected result: document is directly usable without further drafting
- command: confirm the output states what the self-critique pass changed/cut (see `.claude/agents/doc-creation.md`'s "Self-Critique" section) — specificity, payoff completeness, experience honesty, template-detection
- expected result: no unresolved vague claims, no undelivered promised sections, no fabricated first-person experience presented as real, no verbatim-repeated structure across multiple covered items

## Emergency Stop

- condition: role output is empty or an outline-only stub
- owner: human operator via Approval Console
