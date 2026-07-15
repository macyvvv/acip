# ADR-0035: Business Agent Platform Level 3c — Policy-Based Unattended Publishing

## Status

Accepted

## Current Design (superseded)

Levels 0-2 (ADR-0032/0033/0034) automate proposing and concurrently progressing content-generation tasks, but every generation execution still requires a fresh, scope-specific human approval, and nothing in the platform ever posts content anywhere. Every content-role output contract (`contracts/roles/MARKETING_OUTPUT_CONTRACT.md`, `contracts/roles/DOC_CREATION_OUTPUT_CONTRACT.md`) states auto posting is prohibited. `docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`'s Level 3 section describes this as the one remaining capability class ("reducing/removing human approval") explicitly forbidden without a new ADR and the operator's specific, sub-stage-scoped sign-off — and recommends publishing (3c) be automated last, after policy-based execution pre-approval (3a) and scheduled execution (3b), possibly staying permanently human-gated regardless.

## Proposed Design (adopted)

The operator explicitly requested Level 3c directly, via two rounds of clarifying questions on 2026-07-10, choosing:
1. A real publishing mechanism, not a design-only document.
2. Policy-based unattended posting — once a standing policy authorizes a `(business_id, platform)` pair, a specific finalized draft ships without a human reviewing that post's content at trigger time.
3. No platform credentials exist yet for X, Threads, or note.com, so this ships dry-run only.

This explicitly skips the doc's 3a→3b→3c sequencing (3a/3b, about auto-approving *generation*, remain unbuilt) — a deliberate, informed choice by the operator, not an oversight; generation approval itself is completely untouched by this change.

New components, all additive:
- `system/scripts/publishing/providers.py` — provider/registry pattern mirroring `system/scripts/analytics/providers.py`; only `DryRunProvider` implemented, real per-platform adapters (`providers_x.py`/`providers_threads.py`/`providers_notecom.py`) deliberately unbuilt and unregistered until credentials exist.
- `system/core/publishing_policy.py` + hand-authored, PR-reviewed `system/runtime/publishing/policy.json` — standing, revocable authorization per `(business_id, platform)`: enabled flag, allowed source roles (`marketing`/`doc_creation` only), daily/weekly post caps, an affiliate-disclosure-tag requirement. Absence of an entry always means "not authorized" (fail closed).
- `system/scripts/publishing/finalize_content.py` — a human, after a task has executed successfully, distills its raw (often multi-option) output into the one exact string that may post, writing `system/runtime/publishing/finalized/{business_id}/{role_id}/{task_id}/{platform}.json` with a hash of the source execution content. This artifact — not execution approval, and not a proposal-time flag — is the sole eligibility signal a scheduled run acts on.
- `system/core/publishing_control.py` — a second, dedicated kill switch (`is_publishing_paused`/`pause_publishing`/`resume_publishing`), separate from the existing task-proposal switch (`business_agent_automation_control.py`) but checked *in addition to* it: the scheduler stops on either being engaged. No manual-override/force path exists for either.
- `system/core/publishing_state.py` — dedup + daily/weekly counters, sharded per `(business_id, platform)` (not one shared file), locked via the existing `system/core/file_lock.py`, fresh-read-inside-the-lock to prevent double-posting across concurrent runs. A corrupted state file hard-fails the run for that scope rather than being read as empty.
- `system/scripts/publishing/run_scheduled_publish.py` — finds all finalized-content candidates, evaluates policy/cap/dedup/kill-switch/content-integrity/disclosure eligibility, publishes eligible ones via the resolved provider, and writes a JSON+MD audit trail (`system/runtime/publishing/audit/`), surfaced in the existing Approval Console via a new banner.
- Contract amendment: `MARKETING_OUTPUT_CONTRACT.md`/`DOC_CREATION_OUTPUT_CONTRACT.md`'s "auto posting: prohibited" clause now clarifies this applies to the role invocation itself — the role never gains posting IO; only this separate, policy-gated pipeline may post a human-finalized excerpt of its output.

Explicitly **not** built: any real OS-level cron/launchd/daemon trigger (the scheduler ships as a fully-tested, manually-invokable script only — wiring a real recurring trigger runs outside this repo's git-tracked safety net and is deferred as its own future, explicit ask); real provider modules for any platform; any real push/email/Slack notification channel; any generalization of policy-based pre-approval to `pluggable_provider` roles (image/video generation), which remain untouched and still forbidden.

## Reason for Change

Direct, twice-confirmed operator request (2026-07-10): "Level 3cを解決しましょう" (let's resolve Level 3c), followed by explicit selection of "実際の自動投稿の実装" (actual auto-posting implementation) over a design-only document or a human-triggered-per-post assistant tool, and "ポリシーに基づく無人スケジュール投稿" (policy-based unattended scheduled posting) over a per-post human trigger, with confirmation that no platform credentials exist yet. This is the specific, sub-stage-scoped sign-off `docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md` requires before any Level 3 design work begins.

This design was produced via full exploration, an initial design pass, and one adversarial critique pass that found 15 concrete issues in the first draft (several backed by reading actual production code and a real draft artifact, not hypotheticals) — the most consequential being that the first draft's proposal-time `publish_candidate` flag could silently fail to attach or become attached to different content than a human actually reviewed, and that production marketing/doc_creation drafts are multi-option blobs with no field identifying the one final, platform-ready string. Both are fixed by replacing that flag with the `finalize_content.py` step described above.

## Benefits

- Delivers exactly what the operator asked for: unattended, policy-gated posting, without touching the generation-approval gate at all.
- The eligibility model requires an explicit, separate, human-authored artifact (finalized content) in addition to execution approval — an approved-and-executed task with no finalized content is never published, regardless of policy state, closing the "does existing approval silently become posting consent" risk directly.
- Sharded per-scope state avoids reintroducing the cross-business lock contention and single-point-of-corruption failure mode ADR-0034 already identified and rejected for a different piece of shared state.
- Two independent kill switches, both checked by the scheduler, mean an operator using the already-familiar `pause_automation.py` during an incident also stops publishing, without collapsing two genuinely different operator concerns into one switch.
- Retracting one specific not-yet-published draft requires no new mechanism — deleting its finalized-content file is sufficient.

## Drawbacks

- **The core, unavoidable tradeoff**: once policy authorizes a business/platform and a draft is finalized, it can ship with no human reviewing that specific post's actual text at schedule time. Every other design choice here narrows and audits this risk; none removes it, because removing it would mean building something other than what was asked for.
- The disclosure-tag check is a literal string-match heuristic against a small marker list, not a legal compliance guarantee — relevant given `text_syndicate`'s own market_research findings flagged note.com's affiliate-disclosure rules as ambiguous/under-verified.
- Fan-out risk: if an operator finalizes both `marketing` and `doc_creation` output for the same business/platform, both can independently publish as near-duplicate posts — no cross-role content-thread dedup is built, since this codebase has no existing notion of "same content thread" to key off.
- Reserve-then-confirm two-phase state writes are required before any real (non-instant) provider ships — holding a lock across the current `DryRunProvider.publish()` call is safe only because it's instant; this is a documented, required follow-up, not solved now.
- Two more shared switch/state conventions for a future reader to keep straight, on top of the two already introduced by ADR-0033/0034.

## Impact Scope

- New: `system/scripts/publishing/` (`providers.py`, `finalize_content.py`, `run_scheduled_publish.py`, `pause_publishing.py`, `resume_publishing.py`), `system/core/publishing_policy.py`, `system/core/publishing_control.py`, `system/core/publishing_state.py`, this ADR, and the `system/runtime/publishing/` tree.
- Modified (additive only): `app/tools/approval_console_mvp/service.py` (new banner), `docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md` (Level 3c section + Forbidden Now updates), `contracts/roles/MARKETING_OUTPUT_CONTRACT.md`, `contracts/roles/DOC_CREATION_OUTPUT_CONTRACT.md`.
- Unaffected: `system/orchestrator/business_agent_execution_adapter.py`, `system/core/agent_execution_approval.py`, `system/core/business_agent_automation_control.py` (read from, not modified), `system/core/business_agent_task_queue.py`, `system/core/business_agent_handoff.py` (no schema change — the `publish_candidate` flag idea was rejected, so these need zero changes), all `pluggable_provider` roles, Levels 0-2 in full.

## Migration Cost

None. Purely additive/greenfield — `system/runtime/publishing/` is a brand-new tree, and `policy.json` ships absent by default (no policy = fail closed everywhere). The operator adds the first pilot policy entry as their own separate, reviewed commit.

## Recommendation

Recommend, with the drawbacks above stated plainly rather than minimized. This is the first Level 3 sub-stage this platform has built, and it is scoped as narrowly as the operator's own explicit choices allow: publishing only, dry-run only, no real scheduler trigger, no credentials, generation approval untouched.

## Rejected Alternatives

- **A design-only document, no build** (safer, but not what was asked): rejected by direct, twice-confirmed operator choice.
- **Human triggers each post, system only automates the API call**: rejected by direct operator choice in favor of policy-based unattended posting.
- **`publish_candidate` proposal-time flag** (first design draft): rejected after adversarial critique found it could silently fail to attach (`add_task()`'s existing-task no-op) or end up attached to different content than was actually reviewed (`write_business_agent_handoff()`'s unconditional overwrite on scope reuse). Replaced by `finalize_content.py`'s explicit, hash-verified, post-execution artifact.
- **CLI-writable publishing policy** (mirroring `set_execution_approval.py`): rejected — publishing is the one irreversible, externally-visible action in this platform, so authorizing it deserves the same PR-review bar as a code change, not a same-session CLI write.
- **A single shared `publish_state.json` across all businesses/platforms** (first design draft): rejected after the critique noted this reintroduces exactly the cross-business lock contention and single-point-of-corruption blast radius ADR-0034 already rejected for per-task state, for the identical reason.
- **A `--force` kill-switch override** (first design draft, claimed to mirror the existing switch's precedent): rejected after the critique found that precedent doesn't actually exist anywhere in this codebase, and that building a first-of-its-kind bypass flag for the platform's one irreversible action is a predictable path to the switch being silently neutered later.
- **Reusing the existing task-automation kill switch instead of a separate one**: rejected — "stop new task proposals" and "stop posting externally" are different operator concerns; the scheduler checks both switches instead of collapsing them into one.
