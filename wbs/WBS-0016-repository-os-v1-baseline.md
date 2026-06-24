# WBS-0016: Repository OS v1.0 Baseline

## Current Phase

Knowledge Factory

## Current Objective

Repository Operating System v1.0 Baseline

## Scope

- version file
- release document
- baseline manifest
- baseline policies
- incremental graph script
- context diff script
- queue update script
- review summary script
- validation workflow

## Out of Scope

- runtime execution
- platform API mutation
- auto posting
- scraping-dependent automation
- secret use

## Acceptance Criteria

- `python scripts/baseline/validate_baseline.py` passes.
- `python scripts/graph/build_incremental_graph.py` runs.
- `python scripts/context/build_context_diff.py` runs.
- `python scripts/orchestrator/update_execution_queue.py` runs.
- `python scripts/review/build_review_gate_summary.py` runs.
