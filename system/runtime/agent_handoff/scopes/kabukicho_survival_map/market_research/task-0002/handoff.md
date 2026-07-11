# AGENT_HANDOFF

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0002
task_description: Per issue #33's MVP spec, research real Kabukicho (Shinjuku) POIs across 6 categories (the original 4 plus 2 additions the operator just requested). For each category, produce entries with: name, approximate lat/lng, description, tags (array), reliability_score (1-5), source_type (official/observed/inferred), type (official/unofficial). Categories and their required per-category tag/attribute sets:
1. Smoking areas -- tags: indoor, outdoor, rain_ok, crowded, hidden, unsafe
2. Toilets -- tags: clean, dirty, free, long_wait, gender_separated
3. Convenience stores -- standard tags (24h, etc.)
4. ATMs -- standard tags (24h, international_card_ok, etc.)
5. Coin lockers (NEW) -- must capture size/capacity (e.g. small/medium/large) and explicit suitcase-compatibility (suitcase_ok / suitcase_too_big)
6. Lodging facilities including internet cafes (NEW) -- must capture shower availability (shower_available / no_shower), approximate price band, and whether it's 24h/overnight-stay-friendly
For unofficial/gray-zone locations (e.g. pachinko parlors, certain lodging), flag clearly per the spec's disclaimer requirement. This is read-only research output only -- no files should be written; the execution adapter persists this artifact. Build on kabukicho_survival_map/market_research/task-0001's existing context where relevant, but this task's job is the detailed 6-category POI research task-0001 didn't cover.
request_id: REQ-KABUKICHO-SURVIVAL-MAP-MARKET-RESEARCH-TASK-0002
next_action: Review the handoff and, if approved, continue through the existing execution flow.
