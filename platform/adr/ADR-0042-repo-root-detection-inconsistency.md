# ADR-0042: Repository-Root Detection Is Inconsistent and Produces Duplicate-Path Writes

## Status

Proposed. Discovered 2026-07-17 while fixing CLAUDE.md's validation-command paths; not yet fixed, no decision made on the approach below.

## Context

While correcting CLAUDE.md's references to `platform/system/scripts/validate_all.py` and `check_repo_os_status.sh`, running the corrected `check_repo_os_status.sh` still failed:

```
can't open file '/Users/ariel/Documents/tools/acip/platform/platform/system/scripts/validate_all.py'
```

Root cause: `check_repo_os_status.sh` computes `$ROOT` by walking up from the script's own directory looking for the first parent containing `.git`, `pyproject.toml`, or `README.md`. Two stray, untracked-by-design artifacts satisfy that check one level too early:

- `platform/README.md` exists (a legitimate file, tracked in git) — it alone is enough to make the walk stop at `platform/` instead of continuing to the true repo root.
- `platform/.git/` also exists as a real, **untracked** directory containing only a stray `hooks/` subfolder. Its origin is unknown; it is not a git submodule pointer, just an ordinary directory that happens to be named `.git`.

Either one independently causes any "walk up until I find a repo-root marker" heuristic to misidentify `platform/` as the repository root.

This is not confined to `check_repo_os_status.sh`. The codebase has at least two different, incompatible conventions for what `base_path`/`ROOT` means across scripts that share the same core modules:

- `platform/system/scripts/agent/run_approved_autonomous_execution.py` sets `ROOT = Path(__file__).resolve().parents[3]`, which is `platform/` itself, and passes it to `ApprovedAutonomousExecution(ROOT)`. Consumers like `approved_autonomous_execution.py` then do `self.base_path / "system" / "runtime" / ...`, correct under this convention.
- `platform/system/scripts/business_agent/run_scheduled_execution.py` computes `ROOT` via the same repo-root-marker walk described above (real repo root, `acip/`, when the stray files aren't in the way) and passes *that* to the same `ApprovedAutonomousExecution` / `run_scheduled_execution`.
- `platform/system/core/execution_pre_approval_state.py`'s `_state_path()` hardcodes a `"platform/system/runtime/agent_handoff/pre_approval_state"` prefix, i.e. it assumes `base_path` is the true repo root — the second convention, not the first.

Live evidence this actually happens: `platform/platform/system/runtime/agent_handoff/pre_approval_state/` exists on disk (untracked) with real state files for `kabukicho_survival_map/marketing`, `kabukicho_survival_map/doc_creation`, and `text_syndicate/market_research`. This is the pre-approval daily/weekly cap tracking state — the exact mechanism that gates how many autonomous executions a role gets per day. Depending on which entry point (manual CLI vs. scheduled wake) and which moment the stray `platform/README.md`/`platform/.git/` condition was hit, a role's cap counters may have been split across two different files (`platform/system/runtime/agent_handoff/pre_approval_state/...` and `platform/platform/system/runtime/agent_handoff/pre_approval_state/...`), silently doubling its effective daily budget.

## Why this is not fixed in this change

This touches runtime execution-state semantics (`execution_pre_approval_state.py`'s path contract) and possibly the `ROOT`/`base_path` convention used by multiple entry-point scripts (`run_approved_autonomous_execution.py`, `run_scheduled_execution.py`, and anything else that constructs `ApprovedAutonomousExecution`/`BusinessAgentExecutionAdapter`). Per this repository's operating rules, changes affecting execution-time behavior and data model paths require stopping for explicit confirmation and an ADR before implementation — this document is that stop, not the fix.

## Options for a follow-up fix (not decided)

1. **Unify on repo-root as the one `base_path` convention.** Fix `run_approved_autonomous_execution.py`'s `ROOT` to walk up one more level (or use the same repo-root-marker search as `run_scheduled_execution.py`), and audit every `self.base_path / "system" / ...` call site in `approved_autonomous_execution.py` / `business_agent_execution_adapter.py` to become `self.base_path / "platform" / "system" / ...`.
2. **Unify on `platform/` as the one `base_path` convention.** Fix `execution_pre_approval_state.py`'s `_state_path()` to drop its hardcoded `"platform/"` prefix, and fix `run_scheduled_execution.py`'s repo-root walk to return `platform/` (or have its caller pass `ROOT / "platform"`).
3. **Either way**, harden the repo-root-marker heuristic (used in `check_repo_os_status.sh` and `run_scheduled_execution.py`) so a nested `README.md` or stray `.git`-named directory below the true root can't be mistaken for it — e.g. require the marker to be `.git` **and** contain a `refs/` subdirectory, or only accept the outermost match instead of the first.
4. Delete the stray untracked `platform/.git/hooks/` directory (harmless on its own, but worth removing once its origin is understood, so it stops masking real root-detection bugs like this one).

## Consequences if left unaddressed

- `platform/system/scripts/check_repo_os_status.sh` (the script CLAUDE.md's "CIの `validate-all.yml` 相当の統合ステータス" line points to) does not run successfully today.
- Pre-approval daily/weekly execution caps may already be split across two state files for any business/role whose task happened to run through the affected code path, meaning the caps documented in policy may not reflect the actual number of autonomous executions that occurred.
- Any other code that resolves "the repo root" via a similar upward marker search is exposed to the same misidentification as long as `platform/README.md` and the stray `platform/.git/` remain.

## Immediate, low-risk mitigation applied in this change

- `platform/system/scripts/check_repo_os_status.sh` line 19 was corrected from a hardcoded `platform/system/platform/scripts/validate_all.py` to `platform/system/scripts/validate_all.py` — necessary regardless of which option above is chosen, but insufficient on its own while `$ROOT` itself can still resolve to `platform/`.
- No change was made to `execution_pre_approval_state.py`, `run_approved_autonomous_execution.py`, or `run_scheduled_execution.py` — those require the decision above first.
