# 065 Repository Knowledge Graph Policy

## Conclusion

ACIP must maintain a Repository Knowledge Graph so ChatGPT, Codex, and future approved agents can reason from the same repository-governed structure.

## Purpose

The Repository Knowledge Graph converts files, policies, ADRs, WBS, runbooks, contracts, workflows, registries, and knowledge assets into queryable relationships.

## Node Types

- policy
- ADR
- WBS
- runbook
- contract
- workflow
- validation_script
- registry
- catalog
- knowledge_asset
- control_file
- README

## Edge Types

- references
- governs
- implements
- validates
- depends_on
- supersedes
- archives
- derives_from
- blocks
- escalates_to

## Rules

- Repository overrides conversation.
- Graph output is derived, not canonical.
- Source files remain canonical.
- Human should not maintain graph edges manually when extraction can be automated.
- Runtime implementation remains out of scope until approved.
