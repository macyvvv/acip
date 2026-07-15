# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: marketing
task_id: auto-0004
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
# Marketing — Kabukicho Survival Map

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** auto-0004 (built on market_research/task-0003-smoking-deep)

Per contract, this is read-only output for the execution adapter to persist — no files have been modified.

## Building on prior work

- auto-0001: core positioning ("confirmed vs. caution vs. gray-zone" orientation guide).
- task-0002/auto-0002/task-0001-promo-plan: established essentials copy (lockers, ATMs, toilets, lodging) and a piggyback-on-text_syndicate channel strategy — still the default distribution assumption here.
- task-0003-smoking-deep adds the first smoking-specific dataset: 3 free outdoor designated areas, 2 border-adjacent Ōgado options, and 12 indoor bar/izakaya/yakiniku venues where smoking is allowed but a paid order is required — plus the hard fact that street smoking anywhere in Kabukicho carries a ¥2,000 on-the-spot fine.

This dataset has a sharper marketing hook than prior batches: it's not just "here's a list," it's "the free option and the paid option are getting mixed together elsewhere, and that confusion costs you ¥2,000." That's the angle used below.

## Positioning for this dataset

**Free vs. paid, official vs. commercial — don't let a fine be your first lesson.** Most existing "Kabukicho smoking spot" content (blog listicles, generic maps) mixes ward-designated free outdoor areas with bars/izakayas that merely allow smoking as a side effect of ordering food or drink. This product's differentiator is keeping those two categories visibly distinct, plus surfacing the one border-adjacent case (Ōgado) that other lists quietly fold into "Kabukicho" when it's technically just outside it.

## Audience segments to target

1. **Smokers doing same-day/first-visit logistics planning** — need the free option fast, before they either get fined or end up buying a drink they didn't want just to smoke.
2. **Budget travelers already committed to a bar-hop itinerary** — for this group, the indoor smoking-permitted izakaya/bar list is a value-add on top of a spend they're already planning, not a new cost.
3. **Nightlife-district content audiences (short-form travel/safety content viewers)** — respond to the "here's the fine nobody mentions" hook more than a plain venue list.

## Channel-specific copy

**1. Audience: Smokers researching Kabukicho before/during a same-day visit, weighing free vs. paid options.**
**Channel: Travel forum / subreddit post (r/JapanTravel, r/tokyo) — practical Q&A style.**

> Heads up: street smoking anywhere in Kabukicho is a flat ¥2,000 fine, patrol-enforced, cigarettes and heated tobacco both. The free legal option is the designated outdoor smoking areas (Cinecity Plaza side, and the Kabukicho 1-3-7 spot) — no purchase needed. If those are full or out of your way, several izakayas/bars allow smoking at all seats, but you're expected to order something — that's a different deal than a free public area, and we keep the two separate so you're not surprised either way.

**2. Audience: Budget travelers/bar-hoppers already planning a Kabukicho night out, deciding where to land for a smoke break.**
**Channel: Budget travel Facebook groups / backpacker Discord communities.**

> If you're smoking and already down for a drink anyway, Kabukicho has real options: 24-hour izakaya Ikkenme Sakaba (52 seats, all-smoking), the retro-themed Shinjuku Dagashi Bar, or a Golden Gai bar like Albatross G if you want the narrow-alley experience. All of these need an order — they're not free smoking areas, they're bars that happen to allow it. If you just need a quick free smoke with no purchase, skip these and use the outdoor designated spot near Cinecity Plaza instead.

**3. Audience: Short-form video viewers researching Tokyo nightlife district rules/etiquette (TikTok/Reels/YouTube Shorts).**
**Channel: Short-form video script outline (for a future creator/UGC collab, not a dedicated brand account).**

> Hook: "Kabukicho will fine you ¥2,000 for smoking on the street — here's where you're actually allowed to." Body: show the free outdoor designated area vs. a bar that allows smoking but expects an order, making the free/paid distinction visually obvious (e.g. split-screen "no purchase needed" vs. "order required"). CTA: "Full map linked" (link pending deployment).
> *(Provisional: requires the live product to demo on-screen — cannot be scripted further until deployment exists, per the standing deployment caveat from task-0001-promo-plan.)*

## Notes on scope

- The 2 Ōgado-area entries (public smoking area + Café Renoir branch) are **not used in copy above** because task-0003 flags them as border-adjacent, not strictly inside Kabukicho — using them without that caveat would misrepresent location, so they're held back pending a product-level decision on whether to include "just outside the boundary" fallback options at all.
- Every venue referenced above is sourced from task-0003's citation list (smokingmap.jp, hostrank.jp); none of the pricing, hours, or "all seats smoking" status has been independently re-verified on-site, consistent with task-0003's own caveat that bar smoking permissions are grandfathered per-venue and can be revoked at any time — this copy should be re-checked before it outlives a normal verification cadence for that category.
- No copy has been posted or scheduled. Per contract, this role has no posting IO; publishing requires the separate policy-gated pipeline (ADR-0035) and human finalization.

Marketing content produced and returned to the execution adapter — no files written by this task.

