# ROOT_HYGIENE_CONTRACT

Root hygiene is detection-first.

## Rules

- keep only allowlisted root files in the repository root
- classify all other root entries as review candidates
- do not move or delete entries in this EP
- record future move candidates in `platform/docs/current/REFACTORING_QUEUE.md`

## Allowlist

- `README.md`
- `AGENTS.md`
- `VERSION`
- `.gitignore`
- `.env.example`
- `selftest.yml`

## Output

Root hygiene produces a report and a refactoring queue, not a migration.
