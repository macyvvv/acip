# WBS-0013: Repository Knowledge Graph and Runtime Integration Preparation

## Current Phase

Knowledge Factory

## Current Objective

Repository Operating System Stabilization

## Conclusion

This WBS adds Repository Knowledge Graph and runtime integration preparation without starting runtime execution.

## Scope

- graph schema
- graph extraction scripts
- graph validation
- context pack schema
- agent IO contracts
- runtime dry-run specification
- GitHub Actions workflow
- report templates

## Out of Scope

- runtime agent execution
- auto posting
- platform API integration
- scraping-dependent automation
- secret use
- external database
- new frameworks

## Acceptance Criteria

- `python scripts/graph/build_repository_graph.py` runs.
- `python scripts/graph/validate_repository_graph.py` passes.
- `python scripts/context/build_agent_context_pack.py` runs.
- Runtime boundary remains intact.
