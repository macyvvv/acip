# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: marketing
task_id: auto-0005
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
# Marketing — Kabukicho Survival Map

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** auto-triggered by market_research/task-0004-toilet-deep

Read-only output per the contract — no repository files modified, no content posted or scheduled.

## Building on prior work

- auto-0001: core positioning ("confirmed vs. caution vs. gray-zone" orientation guide).
- task-0001-promo-plan/auto-0002: piggyback-on-text_syndicate channel strategy (still the default distribution assumption — no dedicated account or deployment exists yet).
- auto-0004 (smoking dataset): established the pattern this dataset repeats — a naive "official Japan norm" assumption fails specifically in Kabukicho, and that gap is the sharpest hook, not the raw venue count.
- task-0004-toilet-deep (market_research): found 13 distinct, citable toilet locations (short of the 15–20 target, explicitly not padded with unverified venues) and two standout facts: (1) Kabukicho-area convenience stores reportedly do **not** lend restrooms to non-customers, unlike the rest of Japan; (2) only three locations are confirmed genuinely 24h (Seibu-Shinjuku front, Southeast Exit, Four Seasons Path) — everything else carries a building-hours or park-hours caveat.

## Positioning for this dataset

**The "just find a conbini" instinct fails here.** Everywhere else in Japan, a convenience store toilet is the default fallback. In Kabukicho, that assumption reportedly doesn't hold — stores don't lend restrooms to non-customers. That's a sharper, more falsifiable hook than "here are 13 toilets": it targets the specific wrong assumption a first-time visitor is most likely to carry into the district, and it's the kind of thing a generic map or listicle won't warn you about because it contradicts national norms.

The secondary structural point — three ward-run 24h toilets vs. everything else being hours-limited — gives the copy a concrete "if it's late, go here specifically" answer instead of a flat list.

## Audience segments to target

1. **First-time visitors doing same-day/late-night logistics** — the group most likely to reflexively try a conbini first and get turned away; needs the correction stated plainly, not buried.
2. **Parents/accessibility-conscious visitors** — task-0004 flags barrier-free/multi-function stalls at several of the 24h entries (Seibu-Shinjuku front, Southeast Exit, Four Seasons Path, Okubo Park); this is a distinct need from "any toilet, fast."
3. **Late-night bar/club patrons already out past midnight** — need specifically the 24h subset, not the daytime-only entries (Ward Office, Okubo Park's ~19:00 close, Food Pocket's 23:00 close), since those will read as available but won't be.

## Channel-specific copy

**1. Audience: First-time visitors doing day-of/late-night logistics in Kabukicho, carrying the default "find a conbini" assumption from elsewhere in Japan.**
**Channel: Travel forum / subreddit post (r/JapanTravel, r/tokyo) — practical Q&A style.**

> Don't do what works everywhere else in Japan and assume a conbini toilet is your backup here — in Kabukicho, stores are reported to not lend restrooms to non-customers. What actually works at any hour: the ward-run 24h toilets at Seibu-Shinjuku Station front (Brick St., under the elevated tracks), Shinjuku Station Southeast Exit (under the stairs to the meetup plaza), or Four Seasons Path beside Golden Gai (has an intercom call button, useful if you want the safety signal at night). Everything else in the area — Don Quijote, TOHO Cinemas, the Ward Office — closes with the building or has set hours, so don't count on them after dark.

**2. Audience: Parents and accessibility-conscious visitors planning stops in Kabukicho, prioritizing barrier-free facilities over sheer proximity.**
**Channel: Budget/family travel Facebook groups and forums — reference-style cheat sheet, not narrative.**

> Kabukicho toilet stops with barrier-free/multi-function stalls, ranked by whether you can count on them late:
> - **24h, always open:** Seibu-Shinjuku Station front, Shinjuku Station Southeast Exit, Four Seasons Path (Golden Gai side) — all three have a barrier-free stall.
> - **Daytime only, closes early:** Okubo Park (~19:00 close) — has an "everyone" stall with ostomate/baby-seat facilities, useful if you're there before evening.
> - **Skip after dark:** Shinjuku Ward Office — weekday office hours only, not a backup option at night.

**3. Audience: Short-form video viewers researching Tokyo nightlife-district rules/etiquette (TikTok/Reels/YouTube Shorts).**
**Channel: Short-form video script outline (for a future creator/UGC collab, not a dedicated brand account).**

> Hook: "In Kabukicho, the convenience store won't let you use the bathroom — here's what actually will." Body: quick correction of the national-norm assumption, then a fast three-location rundown of the confirmed 24h options (Seibu-Shinjuku front, Southeast Exit, Four Seasons Path), visually distinguishing "always open" from "closes with the building" (e.g. a clock icon on the hours-limited ones). CTA: "Full map linked" (link pending deployment).
> *(Provisional: requires the live product to demo on-screen — cannot be scripted further until deployment exists; per README, deployment is explicitly not yet decided.)*

## Self-Critique

- **Specificity**: Initial drafts leaned on "reported to not lend restrooms" without repeating the caveat every time it mattered for the reader's decision-making — kept it in copy #1 (where it's the whole hook) and copy #2's framing, but did not overstate it as confirmed fact beyond what task-0004 itself claims (it flags this as a single-source, not independently re-verified claim).
- **Payoff completeness**: Copy #3's hook ("here's what actually will") is followed through with the three named locations in the same script outline — cut an earlier draft line that teased "and one surprising 24h option" without naming it, since that would have been an undelivered hook.
- **Experience honesty**: No first-person "I tried this" framing used anywhere — all claims are attributed to the sourced dataset (task-0004), consistent with the contract's prohibition on fabricated lived experience.
- **Template-detection**: Restructured copy #2 as a ranked reference list instead of forum-style prose (matching copy #1's structure) once it was clear the accessibility-focused audience needed a scannable format, not a narrative — this is the concrete structural variation between the three pieces, not just different wording on the same template.

## Notes on scope

- All copy above is sourced from task-0004-toilet-deep's citation list (hostrank.jp, shinjuku.mypl.net, kanko-shinjuku.jp, city.shinjuku.lg.jp); none of the hours, barrier-free claims, or the conbini-restriction claim have been independently re-verified on-site, consistent with task-0004's own caveat.
- The commercial/hours-sensitive entries (Tokyu Kabukicho Tower, TOHO Cinemas, Don Quijote) are deliberately not featured as primary recommendations in any copy above, matching task-0004's recommendation to do a live-verification pass on those before shipping — they're the fastest-to-go-stale subset of this dataset.
- No copy has been posted or scheduled. Per contract, this role has no posting IO; publishing requires the separate policy-gated pipeline (ADR-0035) and human finalization.

Marketing content produced and returned to the execution adapter — no files written by this task.

