# repository_operational_summary

## Purpose

Print a concise operational summary from repository planning and state artifacts.

## Scope

- Read `runtime/planning/latest.json`
- Read `runtime/repository_state/latest.json`
- Render a human-readable summary

## Non-Goals

- No network access
- No mutation of repository OS artifacts
- No platform API integration
- No secret handling

## Release-Prep Criterion

The utility is release-prep ready when it can deterministically render the same summary from the same repository artifacts and its tests pass.
