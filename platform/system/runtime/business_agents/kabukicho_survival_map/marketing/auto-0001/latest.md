# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: marketing
task_id: auto-0001
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
I now have enough grounding. Here is the marketing output, building on the market research artifact and product's actual scope/safety framing.

# Marketing — Kabukicho Survival Map

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** auto-0001 (built on market_research/task-0001)

Per contract, this is read-only marketing output for the execution adapter to capture as the artifact — I have not written or modified any files.

## Positioning Statement

For first-time and infrequent visitors to Kabukicho who need fast, risk-aware orientation after dark, Kabukicho Survival Map is a mobile-first guide that separates confirmed information from caution and gray-zone notes — unlike generic listing sites, it tells you what's *verified*, what's *uncertain*, and what to *watch out for*, so your first move is a safe one.

This directly reflects the product's actual structure (`source_note` / `caution_note` / `gray_zone_note` / `last_verified_note` fields and the category-first mobile UX in `platform/app/products/kabukicho_survival_map_mvp/README.md`) — no claims beyond what the product delivers today.

## Target Audiences & Channels

1. **Audience: First-time/infrequent foreign tourists visiting Kabukicho at night.**
   **Channel: Bilingual (JP/EN) travel forums and subreddits (e.g. r/JapanTravel, r/tokyo).**
   Copy (EN, forum post style):
   > Heading to Kabukicho after dark for the first time? Most guides just list bars. This one tells you what's confirmed, what's shady, and where your quickest way out is if things feel off. Categories: navigation, essentials, safety, escape routes — split into "confirmed," "caution," and "gray-zone" so you're not guessing which part to trust.

2. **Audience: Solo travelers and safety-conscious visitors researching before arrival.**
   **Channel: Instagram/X short-form post (image: category breakdown screenshot).**
   Copy:
   > Kabukicho doesn't need another list of "top 10 bars." It needs an exit plan. Our map splits every spot into confirmed / caution / gray-zone — so you always know what's solid info and what's a maybe. 🇯🇵🌃

3. **Audience: Local/expat community members who could contribute verified updates (UGC pipeline).**
   **Channel: Local Tokyo expat Facebook groups / Discord communities.**
   Copy:
   > We're building a community-verified survival map for Kabukicho — safety notes, escape routes, and honest gray-zone flags. If you know the area, your update could be the one detail that keeps someone safe tonight. (Contribution path: repo PR / issue-based submission — no app account needed.)

## Notes on Scope

- No copy here implies the product currently *has* a live UGC intake mechanism — market research flagged that as a single-placeholder gap (H2). The community-contribution copy in item 3 is framed as an invitation to a to-be-defined process, not a claim that submission is live today.
- No copy has been posted or scheduled; per contract, this role has no posting IO. Any use of this copy requires the separate policy-gated publishing pipeline (ADR-0035) and human finalization.

