# ADR-0022: Agent Orchestrator

## Status

Proposed

## Context

ACIP now has Repository OS, Knowledge Graph, Agent Context Pack, Runtime Readiness, and dry-run capabilities. The next requirement is a coordination layer that routes work among ChatGPT, Codex, scripts, GitHub Actions, and future approved automation.

## Decision

Adopt Agent Orchestrator as a repository-governed coordination layer.

The orchestrator is not runtime execution. It is a planning, routing, context, and validation preparation layer.

## Human Boundary

Human handles Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and Runtime Transition Approval.

## Consequences

- Task routing becomes explicit.
- Context bundles become reproducible.
- Codex instructions become safer.
- Future runtime integration has a stable interface.
