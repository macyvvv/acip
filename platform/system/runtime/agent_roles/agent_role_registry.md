# AGENT_ROLE_REGISTRY

## Summary
- Role count: 8
- claude_invocation roles: 5
- pluggable_provider roles: 2
- data_fetch roles: 1
- Missing prompt templates: none
- Missing output contracts: none
- Unknown next_roles references: none

## Roles
- `market_research` (claude_invocation, model_capability=reasoning): Market Research
  - prompt_template_path: system/agent_runtime/role_prompts/market_research.md (exists=true)
  - output_contract_path: contracts/roles/MARKET_RESEARCH_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob', 'WebSearch']
  - next_roles: ['marketing']
- `marketing` (claude_invocation, model_capability=reasoning): Marketing
  - prompt_template_path: system/agent_runtime/role_prompts/marketing.md (exists=true)
  - output_contract_path: contracts/roles/MARKETING_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob', 'WebSearch']
  - next_roles: ['doc_creation']
- `doc_creation` (claude_invocation, model_capability=cost_optimized): Document Creation
  - prompt_template_path: system/agent_runtime/role_prompts/doc_creation.md (exists=true)
  - output_contract_path: contracts/roles/DOC_CREATION_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob']
  - next_roles: terminal
- `scenario_writing` (claude_invocation, model_capability=reasoning): Scenario Writing
  - prompt_template_path: system/agent_runtime/role_prompts/scenario_writing.md (exists=true)
  - output_contract_path: contracts/roles/SCENARIO_WRITING_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob']
  - next_roles: terminal
- `image_generation` (pluggable_provider, model_capability=cost_optimized): Image Generation
  - output_contract_path: contracts/roles/IMAGE_GENERATION_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob']
  - next_roles: terminal
- `video_generation` (pluggable_provider, model_capability=cost_optimized): Video Generation
  - output_contract_path: contracts/roles/VIDEO_GENERATION_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob']
  - next_roles: terminal
- `analytics` (data_fetch, model_capability=cost_optimized): Analytics
  - output_contract_path: contracts/roles/ANALYTICS_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: []
  - next_roles: ['pdca']
- `pdca` (claude_invocation, model_capability=reasoning): PDCA
  - prompt_template_path: system/agent_runtime/role_prompts/pdca.md (exists=true)
  - output_contract_path: contracts/roles/PDCA_OUTPUT_CONTRACT.md (exists=true)
  - allowed_tools: ['Read', 'Grep', 'Glob']
  - next_roles: terminal
