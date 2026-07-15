# WORK_PLANNER

## Objective

Generate prioritized next-work candidates from repository projections.

## Principle

- Work Planner is a deterministic recommendation layer.
- Planning State, Repository State, Queue, Handoff, Event Runtime, and Repository Constitution remain authoritative.
- Output is review material, not execution authorization.

## Current Target EPs

- EP-0194 Work Planner Contract
- EP-0195 Candidate Source Aggregator
- EP-0196 Work Candidate Scoring Model
- EP-0197 Issue Candidate Renderer
- EP-0198 Parking Lot and Blocked Candidate Handling
- EP-0199 Work Planner Review Gate
- EP-0200 Work Planner Validation

## Rules

- Do not mutate Queue by default.
- Do not create Issues by default.
- Do not promote blocked or high-risk work without approval.
- Keep candidate scoring deterministic.
