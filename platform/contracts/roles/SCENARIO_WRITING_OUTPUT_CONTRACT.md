# Scenario Writing Output Contract

## Metadata

- contract_id: SCENARIO_WRITING_OUTPUT_CONTRACT
- actor: scenario_writing agent role (claude_invocation)
- input_source: business_registry business context + existing character/brand/content specs + task description
- current_objective: produce a complete script/scenario/narrative artifact for one business
- approval_required: yes (one-shot approval gate, same as repo-dev execution)

This role has **two real output shapes today** — which one applies
depends on the business. Documented here explicitly (2026-07-14, per a
repo-wide process consultation) because the original single shape below
described a path Somia's actual pipeline never used, and that drift went
unnoticed until multiple subagents flagged it independently.

### Shape A — generic one-shot business (e.g. kabukicho_survival_map)

- output_target: `platform/system/runtime/business_agents/{business_id}/scenario_writing/{task_id}/latest.{json,md}`
- Freeform markdown deliverable; no fixed section schema beyond "complete,
  directly usable content."

### Shape B — Somia structured content (the actual recurring case)

- output_target: `businesses/platform/somia/content/CONTENT/{content_id}/` (a bare numeric id, e.g.
  `0001`, `0011` — not a `{business_id}/{task_id}` path), containing:
  - `prompt.md` with `## Image Prompt (KV)`, `## Negative Prompt`,
    `## Animation Instruction`, `## Camera Instruction` sections
  - `script.md` with a `## Character` section (or `metadata.json`'s
    `character` field — one of the two must be present), a `## Text`
    section (first backtick-quoted line becomes on-screen text), and a
    `## Audio` section (audio notes)
  - `metadata.json` (character, and whatever else the task needs;
    `render_content.py` later appends a `render` key to this same file —
    do not pre-populate that key)
- This exact shape is parsed by `platform/system/platform/scripts/platform/somia/content_spec.py`'s
  `load_content_spec()` — a missing required section or file raises
  `ContentSpecError`. Validate against it before considering a batch
  complete; a malformed heading fails silently otherwise.
- `audio.json` may exist alongside these three files per existing
  convention, but `content_spec.py` does not read it — `script.md`'s
  `## Audio` section is authoritative for audio notes. Treat `audio.json`
  as legacy/unused unless a future change makes it authoritative instead.

## Allowed IO

- read: repository files, existing business_agent runtime artifacts, existing character/brand/content specs
- write (Shape A): none — execution adapter writes `latest.{json,md}`, not the invoked agent
- write (Shape B): the agent writes `prompt.md`/`script.md`/`metadata.json` directly under `businesses/platform/somia/content/CONTENT/{content_id}/`
- execute: none
- report: complete scenario/script content

## Prohibited IO

- external API mutation: yes, prohibited
- auto posting: yes, prohibited
- scraping: prohibited (this role should not need external browsing)
- secret use: prohibited
- runtime execution: prohibited (no code execution beyond read-only tools)

## Validation

- command (Shape A): confirm `latest.md` contains complete scenario content consistent with referenced specs
- command (Shape B): run `load_content_spec()` against the content dir and confirm it doesn't raise `ContentSpecError`
- expected result: scenario is directly usable by the image_generation/video_generation roles without further drafting
- command: confirm the output states what the self-critique pass changed/cut (see `.claude/agents/scenario-writing.md`'s "Self-Critique" section) — specificity, payoff completeness, continuity honesty, template-detection
- expected result: no vague beats generation roles can't render, no scenes that cut away before their setup pays off, no invented continuity-breaking details, no verbatim-repeated structure across a batch

## Emergency Stop

- condition: scenario contradicts an existing character/brand spec for the business
- owner: human operator via Approval Console
