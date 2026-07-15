# BUSINESS MIGRATION MAP (Phase 1)

## Scope Boundary (Option 2)

### In Scope For Current Continuation

- businesses/
- platform/
- docs/current/ROOT_MIGRATION_SPLIT_PLAN.md
- businesses/dreamcore_video/content/README.md
- businesses/dreamcore_video/content/ideas/DCL-001_falling_without_ground.md
- businesses/dreamcore_video/content/ideas/DCL-002_platform_minus_one.md
- businesses/dreamcore_video/content/ideas/DCL-003_roundabout_of_rain.md
- businesses/dreamcore_video/content/ideas/DCL-004_escalator_to_midnight.md
- businesses/dreamcore_video/content/ideas/DCL-005_tunnel_of_white_lines.md
- businesses/dreamcore_video/content/ideas/DCL-006_stairwell_same_floor.md
- businesses/dreamcore_video/content/ideas/DCL-007_waiting_room_with_no_name.md
- businesses/dreamcore_video/content/ideas/DCL-008_overhead_bridge_forever.md
- businesses/dreamcore_video/content/ideas/DCL-009_pool_at_3am.md
- businesses/dreamcore_video/content/ideas/DCL-010_carpark_level_zero.md
- businesses/dreamcore_video/content/ideas/DCL-011_gate_32_never_boards.md
- businesses/dreamcore_video/content/ideas/DCL-012_hotel_corridor_404.md
- wbs/WBS-DC-0002-dreamcore-video-loop-first-ideas.md

### Explicitly Out of Scope For Current Continuation

- system/runtime/agent_handoff/scopes/text_syndicate/**
- system/runtime/agent_execution/scopes/text_syndicate/**
- system/runtime/business_agents/text_syndicate/**
- unrelated runtime state files outside migration planning

## Policy

- Non-breaking bootstrap only in phase 1
- No file moves in this step
- Update `system/runtime/business/business_registry.md` only when each move is completed

## Root Exception Rule

The following stay at repository root as config/meta exceptions:

- `.git/`, `.github/`, `.gitignore`
- `.env`, `.env.example`
- `README.md`, `CLAUDE.md`, `AGENTS.md`
- `VERSION`, `requirements-dev.txt`, `netlify.toml`, `selftest.yml`

Everything else is expected to converge into either `platform/` or `businesses/`.

## Planned moves

- app/products/kabukicho_survival_map -> businesses/kabukicho_survival_map/app
- somia -> businesses/somia/content
- dreamcore_video -> businesses/dreamcore_video/content
- physics_math_visualization -> businesses/physics_math_visualization/content

## Planned platform convergence groups

- adr/ -> platform/adr/
- baseline/ -> platform/baseline/
- basis/ -> platform/basis/
- context/ -> platform/context/
- contracts/ -> platform/contracts/
- docs/ -> platform/docs/
- specs/ -> platform/specs/
- system/ -> platform/system/
- scripts/ -> platform/scripts/
- archive/ -> platform/archive/
- knowledge/ -> platform/knowledge/
- packs/ -> platform/packs/
- wbs/ -> platform/wbs/
- app/ -> platform/app/
- inbox/ -> platform/inbox/
- releases/ -> platform/releases/
- web/ -> platform/web/
- .system/ -> platform/.system/
- scratch/ -> platform/scratch/

### Platform convergence status (2026-07-16)

- adr/ -> platform/adr/ (done, compatibility symlink in place)
- baseline/ -> platform/baseline/ (done, compatibility symlink in place)
- basis/ -> platform/basis/ (done, compatibility symlink in place)
- context/ -> platform/context/ (done, compatibility symlink in place)
- contracts/ -> platform/contracts/ (done, compatibility symlink in place)
- docs/ -> platform/docs/ (done, compatibility symlink in place)
- scripts/ -> platform/scripts/ (done, compatibility symlink in place)
- specs/ -> platform/specs/ (done, compatibility symlink in place)
- archive/ -> platform/archive/ (done, compatibility symlink in place)
- knowledge/ -> platform/knowledge/ (done, compatibility symlink in place)
- packs/ -> platform/packs/ (done, compatibility symlink in place)
- wbs/ -> platform/wbs/ (done, compatibility symlink in place)
- system/ -> platform/system/ (done, compatibility symlink in place)
- app/ -> platform/app/ (done, compatibility symlink in place)
- inbox/ -> platform/inbox/ (done, compatibility symlink in place)
- releases/ -> platform/releases/ (done, compatibility symlink in place)
- web/ -> platform/web/ (done, compatibility symlink in place)
- .system/ -> platform/.system/ (done, compatibility symlink in place)
- scratch/ -> platform/scratch/ (done, compatibility symlink in place)

## First Low-Risk Move Set (Proposal)

1. Move top-level dreamcore_video to businesses/dreamcore_video/content (done)
2. Move top-level physics_math_visualization to businesses/physics_math_visualization/content (done)
3. Move top-level somia to businesses/somia/content (done)
4. Move app/products/kabukicho_survival_map to businesses/kabukicho_survival_map/app (done)
5. Keep original paths as temporary compatibility links until references are updated (done)
6. Update only business_registry paths that are fully moved and validated (done for moved roots)

## Pre-Move Validation Checklist

- Confirm no in-flight edits in move source paths
- Confirm docs and WBS links to moved paths are known
- Confirm rollback command is prepared before move
- Run repository validation after each move batch

## Rollback Rule

- If any post-move validation fails, restore moved path immediately and postpone registry updates

## Greenfield placeholders

- businesses/music_platform
- businesses/text_syndicate
