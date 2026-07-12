# 069 Agent IO Contract Policy

## Conclusion

Agent IO Contracts define safe interfaces between Repository, ChatGPT, Codex, validation scripts, and future runtime agents.

## Required Fields

- input source
- output target
- allowed mutations
- prohibited mutations
- validation command
- rollback path
- approval requirement
- emergency stop condition

## Rules

- Human approval is required for runtime mutation.
- Repository-derived context is allowed.
- Secret-bearing IO is prohibited until approved.
