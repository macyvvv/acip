# RB-0001: Mission to Issue

## Objective

Convert a Human mission into repository-governed GitHub issues without assigning routine structuring work to Human.

## Trigger

Human provides or approves a mission.

## Inputs

- Mission statement
- Current Phase
- Current Objective
- Repository conventions
- Relevant ADR/WBS

## Steps

1. ChatGPT structures the mission.
2. ChatGPT identifies scope and out of scope.
3. ChatGPT identifies required issues.
4. Codex creates or updates repository files as instructed.
5. Validation script confirms required structure.
6. Human approves only if strategic approval is required.

## Human Boundary

Human provides Mission and Approval only.

## Done Condition

Issue-ready work items exist with owner, scope, acceptance criteria, and validation path.
