# Requirements

## Functional Requirements

- Read planning and repository state artifacts from a repository root.
- Produce a concise summary for a human reviewer.
- Include mission, objective, health, validation, and worktree status when present.

## Constraints

- Use only repository artifacts.
- Avoid external services.
- Avoid secrets.
- Keep behavior deterministic.

## Acceptance Criteria

- The renderer returns a stable summary for the same input files.
- Missing optional fields degrade gracefully.
- Tests cover the main rendering path.
