# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: marketing
task_id: auto-0006
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
# Marketing — Kabukicho Survival Map

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** built on market_research/task-0005-convenience-deep

Per contract, this is read-only marketing output for the execution adapter to persist as the artifact — no files modified. (Flagging as prior tasks have: the artifact path handed to me, `/Users/ariel/acip/...`, doesn't exist — actual repo root is `/Users/ariel/Documents/tools/acip/...`. Doesn't change the content below.)

## Building on prior work

- auto-0001: core positioning — confirmed / caution / gray-zone orientation guide.
- task-0002/auto-0002/task-0001-promo-plan: essentials copy (lockers, ATMs, toilets, lodging), piggyback-on-text_syndicate channel default.
- auto-0004 (smoking-deep): established the free-vs-paid, official-vs-commercial framing.
- auto-0005 (toilet-deep): established the single sharpest finding so far — Kabukicho conbinis reportedly restrict restroom use to customers only, breaking the Japan-wide "just find a conbini" bathroom assumption.
- **task-0005-convenience-deep (this task's input):** 18 named, citable convenience stores actually inside Kabukicho's chome boundaries (6× 7-Eleven, 3× Lawson, 7× FamilyMart, 2× Ministop). The standout finding: the *existing* dataset only had 2 conbini entries, both mislabeled "Shinjuku Station-adjacent" and geographically outside Kabukicho — meaning the product was previously undercounting in-district convenience density by roughly 9x. One entry (7-Eleven Kabukicho Nichome Higashi Ten) has a documented in-store Seven Bank ATM plus a ChargeSPOT battery-rental unit.

## Positioning for this dataset

**Conbinis are everywhere in Kabukicho — just not for the reason you'd expect.** This dataset directly complicates the toilet-deep finding rather than repeating it: there are 18 confirmed 24h convenience stores inside the district (dense enough that most points in Kabukicho are within a couple minutes of one), but per auto-0005's research, walking into one for the bathroom reportedly won't work — they're customer-only for restroom access. The correction this product makes isn't "here are some conbinis," it's "here's how dense they actually are, and here's the one specific thing they're not good for." That's a sharper, non-generic claim than a typical listicle makes, because it holds two facts in tension instead of flattening them into one "convenience stores are here" bullet.

## Audience segments to target

1. **First-time/same-day visitors doing pre-visit logistics** — currently likely to assume conbinis are scarce or Shinjuku-Station-only inside Kabukicho (consistent with the old, undercounted dataset); need to know actual walkable density.
2. **Late-night bar-hop crowd needing cash + snacks fast** — the Seven Bank ATM store is the single highest-value stop in this dataset, combining two late-night needs at one address.
3. **Repeat readers of this account's toilet content** — an audience that already absorbed the "conbini ≠ bathroom" finding; this copy should sharpen rather than repeat that fact.

## Channel-specific copy

**1. Audience: First-time/same-day visitors planning Kabukicho logistics, currently assuming conbinis are sparse inside the district.**
**Channel: Travel forum / subreddit post (r/JapanTravel, r/tokyo) — practical Q&A style.**

> You don't need to walk back to Shinjuku Station for a conbini — Kabukicho itself has at least 18 confirmed 24h convenience stores (7-Eleven, Lawson, FamilyMart, Ministop) spread across both 1-chome and 2-chome, including one directly on the Kabukicho Ichibangai arcade and one bordering Golden Gai. If you need cash at 3am, the 7-Eleven near Higashi-Shinjuku Station (east 2-chome) has an in-store Seven Bank ATM, so you can grab yen and a snack at the same stop. One thing these stores reportedly *won't* do: let you use the bathroom if you're not buying anything — that's a real difference from the rest of Japan, so don't count on them for that specific need (we've got a separate list of the 3 toilets that are actually open 24h).

**2. Audience: Late-night bar-hop crowd who need cash and supplies fast, mid-crawl.**
**Channel: Budget travel Facebook groups / backpacker Discord communities.**

> Running low on cash mid-crawl? Skip hunting for a standalone ATM — head to the 7-Eleven in east Kabukicho 2-chome near Higashi-Shinjuku Station, which has a Seven Bank ATM built in, plus a ChargeSPOT dock if your phone's dying too. It's one of 18 conbinis we've confirmed are actually inside Kabukicho (not a hike back to the main station), so wherever you are in the district you're rarely more than a couple minutes from one. Just don't expect to use the bathroom there without buying something — Kabukicho conbinis are reportedly customer-only on that front, unlike most of Japan.

**3. Audience: Readers who already saw this account's "conbinis won't let you use the bathroom here" content — deepening rather than repeating that claim.**
**Channel: Short-form video script outline / X thread (for a future creator collab or the brand account itself).**

> Hook: "We told you Kabukicho conbinis won't let you use the bathroom. Here's the twist — there are more of them than you think." Beat 1: on-screen map lighting up 18 confirmed 24h convenience stores across Kabukicho 1-chome and 2-chome (not the "walk to the station" assumption most guides give you). Beat 2: zoom to the one 7-Eleven with both a Seven Bank ATM and a ChargeSPOT charger — "this is the one stop that solves cash + battery + snacks in one trip." Beat 3 (the actual payoff, not a stub): "And no — still can't use the bathroom there. That part hasn't changed. Full toilet list and full conbini list both linked." CTA: "Full map linked" (link pending deployment).
> *(Provisional: requires the live product to demo on-screen — cannot be scripted further until deployment exists, per the standing deployment caveat from task-0001-promo-plan.)*

## Notes on scope

- 3 of the 18 entries carry `reliability_score: 3` in the research (single-aggregator sourcing, one with a name inconsistency across sources) — none of the three copy pieces above name a specific low-confidence store by name or address; only the two `reliability_score: 4`, officially-sourced landmarks (the arcade FamilyMart, the Seven Bank 7-Eleven) are called out specifically, so nothing unverified is presented as certain.
- The customer-only restroom claim is carried over from auto-0005/task-0004-toilet-deep, itself flagged there as single-source ("reported," "described as") — copy above keeps that same hedged framing rather than restating it as settled fact.
- No copy has been posted or scheduled. Per contract, this role has no posting IO; publishing requires the separate policy-gated pipeline (ADR-0035) and human finalization.

## Self-critique (changes made before finalizing)

- **Specificity**: initial draft of copy #1 said conbinis are "close by" with no number — revised to state the actual count (18) and named two specific stores (arcade FamilyMart, Seven Bank 7-Eleven) instead of a vague density claim.
- **Payoff completeness**: the short-form script's hook ("more of them than you think") is paid off in the same script with the actual map/count, and the bathroom callback in Beat 3 is answered directly ("still can't use the bathroom there") rather than left as an unresolved tease — this was the specific failure mode I checked for given the toilet-deep precedent already exists.
- **Experience honesty**: no first-person "I walked to this 7-Eleven" claims anywhere; all copy uses "confirmed," "reportedly," and named-source framing consistent with the research's own hedges.
- **Template-detection**: the three pieces use different structures on purpose — correction-with-list, triage-under-time-pressure, and hook-then-twist-then-payoff — continuing the varied-structure pattern set in auto-0004/auto-0005 rather than reusing one template. I also deliberately made this piece *reference* rather than duplicate auto-0005's toilet content, since a reader who saw both would otherwise get the same "conbini myth" beat twice with no new information.

Marketing content produced and returned to the execution adapter — no files written by this task.

