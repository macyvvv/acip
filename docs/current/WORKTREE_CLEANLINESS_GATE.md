# WORKTREE_CLEANLINESS_GATE

The repository is clean by default after validation and pytest when no explicit refresh command is invoked.

## Rule

- Any dirty path outside the generated-artifact registry is a failure.
- Generated-artifact paths are only allowed to change during explicit refresh commands.

