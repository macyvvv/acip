# 067 Agent Context Pack Policy

## Conclusion

Agent Context Packs provide bounded repository context for ChatGPT, Codex, and future agents.

## Context Pack Requirements

- purpose
- actor
- current phase
- current objective
- allowed source directories
- required files
- excluded files
- risk notes
- Human boundary
- runtime boundary
- validation command

## Rules

- Context must be generated from Repository.
- Conversation does not override Repository.
- Context packs are read-only inputs.
- Context packs must not contain secrets.
