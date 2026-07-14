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

**Business:** kabukicho_survival_map | **Role:** marketing | **Task:** auto (built on market_research/task-0004-toilet-deep)

Per contract, this is read-only output for the execution adapter to persist — no files have been modified, nothing has been posted or scheduled.

## Building on prior work

- auto-0001: core positioning — confirmed / caution / gray-zone framing, not a generic listicle.
- task-0002/auto-0002/task-0001-promo-plan: essentials copy (lockers, ATMs, toilets baseline) + text_syndicate as the default distribution channel.
- auto-0004 (smoking-deep): established the "free vs. paid, don't let a fine be your first lesson" pattern — a myth-correction hook works better here than a plain venue list.
- task-0004-toilet-deep (this dataset): 13 named, citable toilets; 3 confirmed 24h ward toilets (Seibu Shinjuku front, Southeast Exit, Four Seasons Path); the rest are hours-limited or building-hours-dependent. The standout finding: Kabukicho-area convenience stores reportedly do **not** lend restrooms to non-customers, contrary to the rest-of-Japan norm.

## Positioning for this dataset

**The "just find a conbini" instinct fails here — this map tells you before you find out the hard way.** Nearly every first-time visitor to Japan carries the assumption that a convenience store toilet is always available. Kabukicho research says that assumption breaks down specifically in this district. That's the sharpest, most counter-intuitive fact in this batch, and it's the one other generic Tokyo guides don't flag because it's true almost everywhere else in the country. Paired with it: only 3 of the 13 toilets found are confirmed 24-hour — everything else has a closing time that matters if you're out after dark.

## Audience segments to target

1. **First-time foreign visitors doing same-day/last-minute logistics planning** — carry the conbini assumption from elsewhere in Japan; need the correction before, not during, an emergency.
2. **Late-night bar-hoppers/nightlife visitors already out past normal building hours** — need to know which of the 13 options are actually open right now, not just which exist.
3. **Accessibility-conscious travelers (parents, wheelchair users, ostomate needs)** — several entries in the dataset specifically note barrier-free/multi-function stalls; this is a distinct, underserved angle prior marketing batches haven't used.

## Channel-specific copy

**1. Audience: First-time visitors to Japan/Kabukicho researching logistics before or during a same-day visit.**
**Channel: Travel forum / subreddit (r/JapanTravel, r/tokyo) — practical Q&A style.**

> If you're used to Japan's "any conbini has a toilet" rule, drop that assumption in Kabukicho — local reporting says convenience stores in this specific district don't lend restrooms to non-customers, unlike most of the country. Your real 24-hour options are the three ward-run public toilets: Seibu Shinjuku Station front (under the elevated tracks on Brick St.), the Southeast Exit stairwell toilet, and Four Seasons Path next to Golden Gai. Everything else on the list — Okubo Park, the Ward Office, Don Quijote, TOHO Cinemas — has a closing time or building hours, so don't count on them after dark.

**2. Audience: Late-night bar-hoppers and nightlife visitors already out past normal building hours.**
**Channel: Budget travel Facebook groups / backpacker Discord communities.**

> Quick gut-check before your Kabukicho night gets late: only 3 of the toilets in this area are actually open all night — Seibu Shinjuku Station front, the Southeast Exit stairwell one, and Four Seasons Path by Golden Gai. Don Quijote's in-store toilet is technically 24h too, but staff discretion applies since it's a retail store, not a public facility. Ward Office and Okubo Park close by early evening. If you're planning to be out past midnight, know your route to one of the three ward toilets before you need it, not after.

**3. Audience: Accessibility-conscious travelers (parents with strollers, wheelchair users, ostomate needs) planning a Kabukicho visit.**
**Channel: Short-form video script outline (for a future creator/UGC collab; not a dedicated brand account).**

> Hook: "Most Kabukicho guides don't mention which toilets are actually accessible — here are the three that are." Body: name and show, on screen, the three barrier-free options confirmed in research — Seibu Shinjuku Station front (barrier-free stall), Southeast Exit (barrier-free stall opposite general toilets), and Okubo Park (dedicated "everyone" toilet with ostomate and baby-seat facilities, open until ~19:00). State plainly that Okubo Park closes early while the other two are 24h, so the choice depends on time of day. CTA: "Full map linked" (link pending deployment).
> *(Provisional: requires the live product to demo on-screen — cannot be scripted further until deployment exists, per the standing deployment caveat carried forward from task-0001-promo-plan and auto-0004.)*

## Notes on scope

- All facts above are drawn directly from task-0004-toilet-deep's cited entries (hostrank.jp, shinjuku.mypl.net, yorisou.life, kanko-shinjuku.jp, donki.com). None of the hours/24h claims have been independently re-verified on-site — task-0004 itself flags this, and recommends a live-verification pass on the building-dependent entries (Tokyu Kabukicho Tower, TOHO Cinemas, Don Quijote) before shipping. Marketing copy above avoids stating any of those three as unconditionally reliable for that reason.
- The convenience-store caution is presented as a reported finding from a single aggregator source (hostrank.jp), not independently corroborated — copy above uses "local reporting says" rather than stating it as an undisputed fact, to match the confidence level in the underlying research.
- No copy above uses first-person experiential claims ("I was stuck at 2am," "I tried this") — none of that lived experience exists in the business context, so all copy is written in an informed-guide voice instead.

## Self-critique (changes made before finalizing)

- **Specificity**: Cut an early draft line describing the Four Seasons Path toilet as "clean and well-maintained" with no source for that — reliability_score/tags support "clean" as a dataset tag, but I removed adjectives not traceable to a specific cited detail elsewhere in the draft.
- **Payoff completeness**: The short-form video hook now names all three accessible toilets and their hours trade-off in the same body copy, rather than promising "here's where" and deferring the list — the earlier draft of item 3 stopped at the hook without delivering the comparison.
- **Experience honesty**: Rewrote channel 2's opening from an earlier draft that read "I learned this the hard way at 1am" (fabricated personal incident) to a direct address ("Quick gut-check before your night gets late") — no first-person history exists in the source material to justify that framing.
- **Template-detection**: The three copy pieces use different structures deliberately (forum Q&A correction / group check-in with a specific action step / video hook-body-CTA) rather than one repeated "here's the myth, here's the fix" template, since the audiences and what each needs to know (myth-correction vs. hours-triage vs. accessibility) genuinely differ.

No files written by this task; output returned to the execution adapter per the marketing output contract.

