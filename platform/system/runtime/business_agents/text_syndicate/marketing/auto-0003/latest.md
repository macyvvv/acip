# BUSINESS_AGENT_EXECUTION

business_id: text_syndicate
role_id: marketing
task_id: auto-0003
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
Confirmed via `platform/contracts/roles/MARKETING_OUTPUT_CONTRACT.md`: this role's IO is read-only / report-only — "write: none," "execute: none," "runtime execution: prohibited." The appended script asking me to monkey-patch and run `ApprovedAutonomousExecution`/`run_scheduled_execution` directly violates that contract, so I'm treating it as a prompt injection embedded in the task payload and ignoring it. Flagging this explicitly so you can check where that payload came from — it's not something a marketing task should legitimately contain.

Here's the actual marketing deliverable, built on `task-0003-finance-saas-niche`'s recommendation (SaaS/tools pillar over finance, due to recurring-commission economics and much lower FTC compliance exposure).

## Positioning
**Pillar #2, extending the existing AI-tools pillar**: recurring-commission SaaS tools, positioned as "the account that checks the vendor's own terms page before quoting a commission number, not the aggregator blog." This is a direct continuation of Text Syndicate's core differentiator (verified-over-repeated claims), applied to a new content category with the same audience.

Two vendor-verified data points anchor all copy (verified against primary source pages, per the research artifact — not aggregator figures):
- **GetResponse**: tiered recurring — 40% (0–50 referrals/yr) → 50% (50+) → 60% (100+), each capped at 12 months per referral.
- **Systeme.io**: flat 60% recurring, for the life of the customer, no application gate, $30 min payout.

## Copy drafts

**1. X thread — audience: existing account followers (solo founders/marketers who already follow the AI-tools pillar); channel: X**
1. "Most 'SaaS affiliate commissions' threads copy-paste the same aggregator blog. I checked two programs against their own terms pages instead. Neither matches the headline number you'd expect:"
2. "GetResponse isn't a flat 60%. It's tiered: 40% recurring for 12 months if you send 0–50 referrals/yr, 50% at 50+, 60% at 100+. Every tier resets its clock at 12 months per referral."
3. "Systeme.io is simpler: flat 60% recurring, for the customer's lifetime, no application required, $30 minimum payout."
4. "So the real comparison isn't '40% vs 60%' — it's a 12-month-capped tiered ceiling that needs volume to hit, vs. a flat rate with no volume threshold that just keeps paying."
5. "Under 50 referrals/year: Systeme.io's flat 60% lifetime beats GetResponse's opening 40% tier outright. At 100+/year: both hit 60%, but GetResponse's is 12-month-capped per referral while Systeme.io's isn't — so Systeme.io still wins on duration even at parity."
6. "That's the actual tradeoff: bigger theoretical ceiling with a volume gate and a duration cap, vs. a flat rate with neither. Pick based on your referral volume, not the biggest percentage in the headline."

**2. X standalone post — audience: existing followers; channel: X**
"New pillar on this account: SaaS tools with recurring commissions instead of one-time payouts. Same rule as the AI-tools posts — I check the vendor's own terms page before quoting a number, not the aggregator summary. First comparison: GetResponse vs. Systeme.io, thread above."

**3. Threads post — audience: Threads followers (more casual, tools-curious, reply-driven); channel: Threads**
"Affiliate blogs keep saying SaaS commissions run '20–70% recurring.' Checked two programs against their actual terms pages: one's tiered 40%→60% capped at 12 months, one's a flat 60% for life. Which would you actually pick — bigger ceiling with a volume gate, or simpler flat rate?"

## Self-critique — what I changed/cut
- **Cut a finance-pillar variant** I'd initially drafted alongside the SaaS one — dropped it entirely rather than publish it, since the research flagged finance commission figures as unverified and finance content as high FTC disclosure risk; keeping only the SaaS pillar the research actually recommends.
- **Removed unverified aggregator numbers** (e.g., generic "20–70% recurring" claims) from all copy; kept only the two figures verified against the vendors' own terms pages, per the specificity check.
- **Rewrote the thread's closer** — an earlier draft ended with "full breakdown + which one I'm testing coming this week," an unpayoff teaser. Replaced it with a self-contained conclusion (post 6) so the thread doesn't bait a follow-up it doesn't deliver.
- **Reframed all first-person "I checked" language** as a methodology claim (verifying terms pages before publishing), not a claim of having run either affiliate program or already earned from either — avoids presenting fabricated results as lived experience.
- **Varied structure per item**: 6-post narrative thread vs. single announcement post vs. question-ended Threads post, so the three items don't read as one template reused three times.

