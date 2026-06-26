# Work Planner Contract

## Principles

- Projection only; not a source of truth.
- Deterministic candidate scoring.
- Review material, not execution authorization.

## Required Inputs

- `runtime/planning/latest.json`
- `runtime/repository_state/latest.json`
- `runtime/repository_constitution/constitution.json`
- `queue/`
- `packs/`
- `runtime/handoff/latest.json`
- `runtime/event_runtime/`
- root hygiene migration plans if present

## Required Output Fields

- `generated_at`
- `mission_alignment`
- `current_phase`
- `current_objective`
- `candidate_items`
- `parking_lot`
- `blocked_candidates`
- `source_artifacts`

## Candidate Fields

- `candidate_id`
- `title`
- `proposed_pack_or_ep`
- `objective`
- `rationale`
- `mission_contribution`
- `management_cost_reduction`
- `risk_reduction`
- `strategic_value`
- `operational_value`
- `learning_value`
- `dependencies`
- `blocked_by`
- `approval_required`
- `recommended_action`
- `issue_body_draft`
