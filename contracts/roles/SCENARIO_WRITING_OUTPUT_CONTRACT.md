# Scenario Writing Output Contract

## Metadata

- contract_id: SCENARIO_WRITING_OUTPUT_CONTRACT
- actor: scenario_writing agent role (claude_invocation)
- input_source: business_registry business context + existing character/brand/content specs + task description
- output_target: system/runtime/business_agents/{business_id}/scenario_writing/{task_id}/latest.{json,md}
- current_objective: produce a complete script/scenario/narrative artifact for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, existing character/brand/content specs
- write: none (execution adapter writes the artifact, not the invoked agent)
- execute: none
- report: complete scenario/script content

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited
- scraping: prohibited (this role should not need external browsing)
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command: confirm `latest.md` contains complete scenario content consistent with referenced specs
- expected result: scenario is directly usable by the image_generation/video_generation roles without further drafting

## Emergency Stop

- condition: scenario contradicts an existing character/brand spec for the business
- owner: human operator via Approval Console
