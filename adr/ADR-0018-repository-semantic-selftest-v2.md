# ADR-0018: Repository Semantic SelfTest v2

## Status

Proposed

## Context

Repository SelfTest v1 correctly detected missing files and real boundaries, but it also generated false positives. The most visible examples were:

- archive files counted as duplicate canonical ADR/WBS
- explanatory mentions of Current Objective treated as drift
- templates, queues, reports, drafts, and entrypoints treated as dead documents
- selftest scripts matching their own prohibited keyword constants

## Decision

Adopt Repository Semantic SelfTest v2.

v2 introduces:

- `selftest.yml`
- canonical/archive/draft/template/index classification
- declaration-only Current Objective parsing
- graph-oriented repository analysis
- severity model
- archive exclusion for duplicate/orphan/drift checks
- selftest script exclusion for boundary keyword constants

## Consequences

- False positives decrease.
- SelfTest becomes more maintainable.
- Validation behavior becomes configurable.
- Repository health reports become more decision-ready.
