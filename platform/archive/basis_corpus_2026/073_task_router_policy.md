# 073 Task Router Policy

## Conclusion

Task routing must assign work to Human, ChatGPT, Codex, scripts, GitHub Actions, or future approved automation based on responsibility and risk.

## Routing Rules

| Work Type | Owner |
|---|---|
| Mission | Human |
| Approval | Human |
| Emergency Stop | Human |
| Strategy Review | ChatGPT |
| Priority / Scope Review | ChatGPT |
| Codex Instruction | ChatGPT |
| Implementation | Codex |
| Test / Commit | Codex |
| Deterministic Validation | scripts |
| CI enforcement | GitHub Actions |
| Future routine execution | approved automation |

## Rules

- Human must not receive routine execution work.
- Codex must not approve its own scope changes.
- Runtime execution requires explicit approval.
- Repository overrides conversation.
