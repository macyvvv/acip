# REVIEW

## Purpose

Define the mandatory review checklist before ChatGPT, Codex, or future agents answer, modify, or propose changes.

## Review Checklist

Before responding, verify:

1. Project Goal
2. Current Phase
3. Repository Constitution
4. Current State
5. Adopted Design
6. Existing GitHub Artifacts
7. Current User Request

## Architecture Review

Check:

- consistency with platform/docs/current/PROJECT.md
- consistency with platform/docs/current/STATE.md
- consistency with platform/basis/
- consistency with ADRs
- responsibility boundaries
- layer violations
- duplicated responsibility
- undefined terms
- untestable requirements
- operational complexity
- future maintainability

## Optimization Review

Evaluate whether the current approach is:

- globally optimal
- locally optimal only
- over-engineered
- under-specified
- operationally fragile
- inconsistent with GitOps
- inconsistent with Human Approval Minimal

## Required Separation

Always separate:

- Facts
- Assumptions
- Proposals

## Existing Artifact Rule

If an artifact already exists in GitHub, do not propose creating a duplicate.

Review the existing artifact and propose only the delta.

## Critical Review Rule

Do not flatter.

Do not agree by default.

If a design is weak, say so.

If previous ChatGPT guidance was inconsistent, say so.

## Output Requirement

When giving a recommendation, include:

- conclusion
- next action
- reason
- details
- future proposal only when useful
