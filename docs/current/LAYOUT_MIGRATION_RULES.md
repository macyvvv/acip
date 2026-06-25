# LAYOUT_MIGRATION_RULES

## Rules

- Do not delete files as a migration mechanism.
- Move one logical concern per EP.
- Do not mix markdown migration with code migration.
- Update internal references when a file moves.
- Keep import path changes in a separate EP.
- Require rollback planning for every migration EP.
- Require validation before and after migration.
- Treat high-risk migrations as Human approval required.

## Scope

The first pass is report-only and warns on root allowlist violations instead of blocking execution.
