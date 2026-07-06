# AGENTS.md

> Superseded by [CLAUDE.md](CLAUDE.md) for how Claude should operate in this
> repo. Kept as historical record of the ChatGPT+Codex protocol.

## Codex Role

Codex is the repository preparation, review, and implementation agent.

## Current Phase

```text
Phase 0: GitHub foundation and constitution readiness
```

Runtime implementation is not approved.

## Required Behavior

- Read `README.md`
- Read `AGENTS.md`
- Read `basis/`
- Read relevant ADRs
- State conclusion first
- Separate facts, assumptions, and proposals
- Never push directly to `main`
- Never implement runtime behavior before approval

## Prohibited

- direct push to `main`
- auto posting
- scraping-dependent architecture
- platform API integration in Phase 0
- runtime agent implementation in Phase 0
- changing upstream policy without ADR
