# REPOSITORY_STATE_PROJECTION

Repository State is a projection, not SSOT.

## Rules

- Existing SSOTs remain authoritative.
- Repository State Builder aggregates inputs and does not own independent state.
- Missing optional inputs degrade gracefully.
- Generated projection must be reproducible.
