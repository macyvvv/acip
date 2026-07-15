# runtime_scaffolding_2026 (archived)

`system/runtime/workers/` and `system/runtime/governor/` were flagged
during a repo-wide "is our current process/refactoring debt fine as-is"
consultation (2026-07-14, run across all 15 acip subagents plus
`opsboard`'s synthesis) as looking like more of the same
mostly-unenforced "repository operating system" pattern that
`adr/ADR-0037-governance-layer-overhaul.md` already found and partly
cleaned up (see also `archive/root_scaffolding_2026/` for that pass'
root-level directory cluster). This is a distinct, later finding, not
part of ADR-0037's original 18-directory list — recorded as an addendum
to that ADR rather than a new one, since it's the same pattern and the
same archival criterion.

Confirmed via `git grep` across `*.py`, `*.yml`, `docs/`, `system/`, and
`app/` before archiving: zero code or workflow references to either
directory's path.

| Archived directory | Contents | Notes |
|---|---|---|
| `workers/` | `WORKER_LIFECYCLE.md`, `worker_lifecycle.json` | The JSON stub hardcoded `worker_name: null` / `current_ep: null` — never populated by any script. The markdown described a ChatGPT/Codex-era worker registry concept that was never wired to a real queue. |
| `governor/` | `GOVERNOR_RECOMMENDATIONS.md`, `governor_recommendations.json` | The JSON stub's `active_ep`/`next_ep` fields (`EP-0108`/`EP-0109`) were stale relative to current `docs/current/STATE.md`, with an empty `candidates: []` that was never populated. `docs/current/GOVERNOR_RECOMMENDATION_SSOT.md` described this path as a "source of truth" that no code ever read from or wrote to. |

`docs/current/GOVERNOR_RECOMMENDATION_SSOT.md` is updated in the same
change to point here instead of describing a live mechanism.
