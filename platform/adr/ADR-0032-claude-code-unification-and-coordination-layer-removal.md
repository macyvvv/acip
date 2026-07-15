# ADR-0032: Claude Code Unification and Coordination-Layer Removal

## Status

Accepted

## Current Design (superseded)

The repository was operated as two disconnected AI services plus a human:
ChatGPT as architect/reviewer, Codex as implementer, coordinated entirely
through GitHub-committed state because neither service held conversation
memory across sessions. To bridge that gap the repository grew a large
self-referential coordination layer: a worker registry or contract
system for the two "workers" (EP-0103/0107/0113/0120), an execution
kernel/queue/session/journal (EP-0112/0130-0133), a capability router and
task decomposer (EP-0114/0115), a repository governor and continuous
improvement engine (EP-0122/0124/0125), a solution-development planning
pipeline (EP-0135-0142), a repository knowledge graph and agent context
pack builder for repository-derived reasoning (basis 062/065-069), an
event runtime for headless GitHub Actions-triggered execution
(EP-0161-0172), a local supervisor daemon for unattended polling
(EP-0187-0193), and a local execution adapter that shelled out to
`codex exec` with a GPT model-fallback chain (EP-0194-0207).

## Proposed Design (adopted)

Claude Code performs both the architecture/review role (ChatGPT) and the
implementation/test/PR role (Codex) directly, in one interactive session
with the human, with direct read/write access to the repository and git.
The GitHub-committed coordination layer that existed solely to bridge two
memoryless services is removed. What remains:

- The actual product surfaces (`platform/app/products/*`, `platform/app/tools/approval_console_mvp`,
  `platform/somia/`).
- The real issue pipeline: `platform/system/platform/scripts/sync_github_issues.py` →
  `platform/system/runtime/roadmap/issue_portfolio.json` (human-curated priority) →
  `platform/app/tools/approval_console_mvp` (candidate selection + approval) →
  `platform/system/core/agent_issue_bridge.py` → `platform/system/orchestrator/local_execution_adapter.py`,
  which now drives `claude -p` instead of `codex exec` (model chain:
  `claude-haiku-4-5` / `claude-sonnet-5` / `claude-opus-4-8`, floored up for
  high-risk/architecture work).
- Generic repository hygiene that is agent-agnostic: main-branch push
  protection, root-hygiene/layout checks, secret-boundary and
  duplicate/orphan detection (`platform/system/platform/scripts/selftest*`), the
  `validate_ep_*.py` chain for product/hygiene EPs, and `pytest`.
- `platform/basis/` and `platform/adr/` as the historical policy/decision record, now indexed
  at [platform/basis/README.md](../platform/basis/README.md) instead of being unlinked.
- `CLAUDE.md` at the repository root replaces `AGENTS.md` /
  `platform/.platform/system/BOOT.md` / `platform/.platform/system/REVIEW.md` / `platform/.platform/system/DECISION.md` /
  `platform/.platform/system/STYLE.md` as the operating instructions for the agent; those
  files are kept only as historical record of the old protocol.

## Reason for Change

The two-service split was the source of the coordination overhead, not a
requirement of the business. Every layer removed here existed to make up
for ChatGPT and Codex not sharing memory or a terminal session with each
other. Claude Code has neither limitation, so the layer was pure
translation cost with no product value — confirmed by the repository's own
tooling: `check_orphans.py` showed the entire `platform/basis/` policy corpus and
most of this coordination code had zero real usage outside of itself, and
`validate_semantic_selftest.py` showed several of the coordination
workflows were already silently broken (validating scripts that no longer
matched their own contracts).

## Benefits

- ~631 files / ~23,000 lines removed from a repository whose actual
  product code is a small fraction of that.
- One person (the human) now interacts with one agent that does
  architecture, implementation, and review together, instead of relaying
  state between two services by hand.
- Two bugs found and fixed as a side effect: a 4-way-duplicated root
  allowlist definition, and a duplicate-ID suppression list pointing at
  stale archive paths.

## Drawbacks

- Loses the (largely unused) ability to run fully unattended, headless
  execution triggered by GitHub Actions webhooks — the event runtime and
  local supervisor daemon are gone. If unattended execution is wanted
  again, it should be rebuilt against Claude Code's own headless mode
  rather than restoring the deleted GPT-era adapter.
- Some `platform/docs/current/*.md` and `platform/system/runtime/*` artifacts describing the
  removed subsystems were left in place where they were cheap to leave and
  not worth the review time to hunt down individually; they are inert
  (nothing imports or runs them).

## Impact Scope

- Deleted: ~73 `platform/specs/EP-*` directories and their validators, ~62
  `platform/system/orchestrator/*.py` modules, ~29 `.github/workflows/*.yml`,
  ~70 `platform/system/tests/*.py`, the top-level `workers/` and `graph/`
  directories, `platform/system/platform/scripts/{graph,context,runtime,orchestrator,review,
  local_execution/run_codex_adapter.py}`.
- Rewritten: `platform/system/orchestrator/local_execution_adapter.py` (Codex CLI →
  Claude CLI, GPT model chain → Claude model chain), its two test files,
  and `platform/system/platform/scripts/local_execution/resolve_claude_model.py` (renamed
  from `resolve_codex_model.py`).
- Restored after over-deletion (needed by the kept pipeline, not
  coordination-specific): `platform/system/orchestrator/{output_contract,
  event_contract, reference_impact_analyzer, planning_state_builder,
  repository_state_builder, queue_state}.py` and matching tests.
- Unaffected: `platform/app/products/*`, `platform/app/tools/approval_console_mvp`,
  `platform/somia/`, `platform/system/platform/scripts/sync_github_issues.py` and
  `platform/system/platform/scripts/github/*`, git hooks / main-branch protection,
  `platform/basis/`, `platform/adr/`.

## Migration Cost

Low, in the sense that it is already done and `python platform/system/platform/scripts/validate_all.py`
plus `pytest` are green. Medium in review cost given the diff size.

## Recommendation

Strongly recommend. The repository was accumulating coordination-layer
maintenance cost (duplicate/stale validators, disconnected state files
between the approval console and the execution adapter) faster than it
was accumulating product value.

## Rejected Alternatives

- Keep the full coordination layer and just repoint Codex references to
  Claude: rejected because the layer's complexity is a direct function of
  the two-service split, not of which model does implementation; keeping
  it would preserve the translation overhead the human explicitly asked
  to remove.
- Delete the local execution adapter entirely and make issue execution a
  purely manual "open a Claude Code session" action: considered, but the
  human chose to keep one automated entrypoint (the approval console) and
  have it drive Claude non-interactively via `claude -p`, so the adapter
  was rewritten rather than removed.
