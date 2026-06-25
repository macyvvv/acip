# REFACTORING_GOVERNANCE_GATE

## Purpose

Gate refactoring before execution.

## Rules

- root migration is deferred to a dedicated EP
- code rewrite is deferred to a dedicated EP
- each migration EP covers one logical concern
- high risk requires Human approval
- rollback plan is mandatory
- validation requirement is mandatory
- changed path allowlist is mandatory
- destructive change is prohibited unless explicitly approved

## Risk Policy

- low: local, reversible, validation-only or report-only change
- medium: limited multi-file change with explicit rollback and validation
- high: broad blast radius, root movement, rewrite, or destructive change
