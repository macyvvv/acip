# 074 Context Resolution Policy

## Conclusion

Context resolution must prefer repository-derived graph and context pack over conversation memory.

## Context Priority

1. Repository conventions
2. Current state
3. Architecture
4. ADR
5. WBS
6. Graph artifacts
7. Agent Context Pack
8. Conversation

## Rules

- Conversation cannot override Repository.
- Context bundle must identify source files.
- Excluded files must remain excluded.
- Secrets must not be included.
- Runtime implementation remains out of scope until approved.
