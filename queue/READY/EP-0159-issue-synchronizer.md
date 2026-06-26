# EP-0159 Issue Synchronizer

status: READY
pack_id: PACK-0004
ep_range: EP-0156..EP-0160
objective: Synchronize completion markers to GitHub Issue comment format.

## Scope

- Build deterministic issue comment payloads.
- Include completion status, commit SHA, validation, pytest, worktree state, and next action.
- Keep the repository as the source of truth.

## Success Criteria

- Issue comment body can be generated deterministically from repository state.
