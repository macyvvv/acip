# ADR-0019: Repository Knowledge Graph

## Status

Proposed

## Context

The Repository Operating System is now broad enough that simple file search and raw markdown links are insufficient. Agentic operation requires a graph of relationships between governance, assets, runbooks, contracts, validation, and runtime readiness.

## Decision

Adopt Repository Knowledge Graph as a derived artifact layer.

## Decision Details

- Source files remain canonical.
- Graph artifacts are generated under `graph/`.
- Graph extraction is local and deterministic.
- Graph extraction performs no external actions.
- Graph extraction must preserve Human Boundary and Runtime Boundary.

## Consequences

- ChatGPT and Codex can reason over Repository structure more reliably.
- Future runtime agents can consume bounded context packs.
- Derived graph artifacts must be regenerated when source files change.
