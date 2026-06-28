# Agent Router

## Conclusion

Agent Router maps tasks to the correct actor.

## Routing Table

| Task | Actor |
|---|---|
| Mission definition | Human |
| Approval | Human |
| Emergency Stop | Human |
| Strategy review | ChatGPT |
| Priority review | ChatGPT |
| Codex instruction | ChatGPT |
| Implementation | Codex |
| Test / commit | Codex |
| Validation | scripts |
| CI enforcement | GitHub Actions |
| Routine future execution | approved automation |

## Rule

Human must not receive routine execution tasks.
