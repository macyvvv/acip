# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: marketing
task_id: task-0001-promo-plan
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
Good, no deployment/hosting config exists — confirms the "no deployment target decided" premise. I have sufficient context to produce the output now.

# Marketing — Kabukicho Survival Map

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** task-0001-promo-plan (built on market_research/task-0002 and marketing/auto-0002)

Per contract, this is read-only output for the execution adapter to persist — no files have been modified.

## Provisional-planning caveat

`platform/app/products/kabukicho_survival_map_mvp/` has no deployment, hosting, or domain configuration checked in (confirmed by directory listing: README, architecture, requirements, `src/`, `data/`, `tests/` only — no `deploy/`, no hosting config, no live URL). Every recommendation below is written for a **product that does not yet exist at a public URL**. Channel choice, SEO strategy, and "where do we send people" all assume a destination that isn't decided. Treat this as a promotion *framework* to slot a URL/App Store link into once deployment is chosen, not a launch-ready plan. Re-run this task once hosting is confirmed, since mobile-web vs. native-app vs. PWA changes which channels (App Store Optimization vs. web SEO) actually apply.

## Building on prior work

- auto-0001: core positioning ("confirmed vs. caution vs. gray-zone" orientation guide).
- task-0002 (market_research): sourced essentials dataset (smoking areas, toilets, konbini, ATMs, coin lockers, lodging) with two standout hooks — the Tokyu Kabukicho Tower gender-neutral toilet reversal, and coin lockers reported full by 10am.
- auto-0002 (marketing): three audience/channel copy drafts (forums, safety-niche social, budget-travel communities) built on that dataset.

This task answers a narrower question those didn't cover: **should this product run its own dedicated channel, or ride on text_syndicate-style syndication accounts** — and what does a location-utility tool need that a generic content account doesn't.

## Dedicated presence vs. piggyback on text_syndicate channels

**Recommendation: piggyback initially, split off only if traction justifies it.**

- text_syndicate (per `platform/system/runtime/business_agents/text_syndicate/marketing/task-0001` and `task-0002`) already operates X/Threads/note.com accounts built for repeat, general-purpose content syndication. A brand-new dedicated Kabukicho Survival Map account starts at zero followers and zero algorithmic trust — for a single-city, single-district niche tool, that's a slow, resource-heavy way to reach launch-day users.
- A location-specific *utility* tool's actual discovery paths (local SEO, maps/travel forums, short-form video) don't depend on owning a branded social account at all — a Google listing, a forum post, or a TikTok/Reels demo works whether or not "Kabukicho Survival Map" has its own handle.
- Piggybacking lets Kabukicho-specific posts (using the task-0002 dataset) go out on text_syndicate's existing note.com/X/Threads reach immediately, while a dedicated account is reserved for **if** the product gets its own domain and sustained content cadence (e.g. seasonal Kabukicho updates, verified-POI refresh announcements) — at that point a dedicated handle earns its keep as a direct-to-user support/update channel.
- **Audience: internal/product decision-makers.** **Channel: this report (not public copy).** This is a recommendation, not published copy — flagged as such per contract.

## Audience segments to target

1. **Tourists (same-day arrivals, luggage/cash/first-hours logistics)** — already covered in auto-0002 copy #1 (r/JapanTravel-style forum post). Best fit: local SEO + travel forums, not social.
2. **Nightlife workers (hosts/hostesses, bar/club staff working Kabukicho shifts)** — a segment auto-0002 did not cover. This group needs different content: not "first visit" orientation but *shift-logistics* utility — nearest 24h konbini/ATM for end-of-shift cash-outs, nearest capsule/net-cafe for a missed last train. Distinct from tourist framing; should not be blended into the same copy.
3. **First-time visitors researching before arrival (pre-trip planning, not day-of)** — overlaps with tourists but earlier in the funnel; targets search/SEO rather than in-the-moment forum Q&A.

## Channel-specific copy

**1. Audience: Nightlife workers finishing late shifts, needing fast essentials (cash, food, backup lodging for missed last train).**
**Channel: Piggyback post via text_syndicate's X/Threads account, local-Tokyo/nightlife-adjacent framing, short-form.**

> Missed the last train out of Kabukicho? Before you panic-search: Seven Bank ATMs near Kabukicho take most international *and* Japanese cards with a flat ~¥110 fee, and Booth Net Cafe & Capsule (near the Godzilla head) runs ~¥3,000/night if you need a place to crash. We map what's actually open at 3am vs. what just says it is.

**2. Audience: First-time visitors, pre-trip planning phase (searching before they land, not day-of).**
**Channel: Local SEO — landing page copy/meta description, once a URL exists.**

> Kabukicho Survival Map — know what's confirmed, what needs caution, and what's gray-zone before you go. Coin lockers, ATMs, toilets, and late-night essentials near Shinjuku's Kabukicho district, sourced and flagged by reliability, not guessed.
*(Provisional: this is meta/landing copy for local search indexing — has no effect until a domain exists for Google to index. Flagging per the deployment caveat above.)*

**3. Audience: Short-form video viewers researching Tokyo nightlife districts (travel-content TikTok/Reels/YouTube Shorts audience).**
**Channel: Short-form video script outline (for a future creator/UGC collab, not a dedicated brand account).**

> Hook: "Kabukicho's coin lockers are full by 10am — here's what nobody tells you." Body: quick walkthrough of 2–3 sourced essentials (locker crunch, ATM reliability, the toilet gender-separation reversal at Tokyu Kabukicho Tower) with on-screen text citing that these are sourced, not guessed. CTA: "Full map linked" (link pending deployment).
*(Provisional: video-format demo channels require the actual map product to demo on-screen — cannot be produced or scripted in detail beyond this outline until deployment exists.)*

## Notes on scope

- No copy claims final/verified data — task-0002's own caveats (approximate coordinates, unverified pricing/gender-separation status) apply to all copy above, same as auto-0002.
- No copy has been posted or scheduled. Per contract, this role has no posting IO; publishing requires the separate policy-gated pipeline (ADR-0035) and human finalization.
- The piggyback-vs-dedicated recommendation and channel list above are provisional pending a deployment/hosting decision — re-run or amend once that decision is made, since it materially changes which channels (SEO vs. ASO, web vs. app-store) are actually applicable.

Marketing content produced and returned to the execution adapter — no files written by this task.

