# BUSINESS_AGENT_EXECUTION

business_id: text_syndicate
role_id: market_research
task_id: task-0005-ai-writing-tools
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
I have enough sourced detail now. Here are the findings, formatted per the market_research output contract.

---

# Market Research: AI Writing/Research/Coding Assistant Fact Sheets

**Business:** Text Syndicate | **Task:** Re-ground AI-tools workflow content pillar — Claude (consumer), Perplexity Pro, Cursor, GitHub Copilot
**Verified as of:** 2026-07-17

## Facts

### Fact Sheet 1: Claude (consumer plans, Anthropic)
- **Product name:** Claude (Free / Pro / Max)
- **Price:** Free $0; Pro $20/month; Max 5x $100/month; Max 20x $200/month (web subscription, US pricing)
- **Free-tier limit:** Anthropic does not publish a fixed numeric message cap on claude.com/pricing — free tier is described only qualitatively ("everyday questions"; Pro gives "at least 5x more usage per 5-hour session than Free"). **Do not invent a specific free-tier message count** — no official number exists to cite.
- **verified_as_of:** 2026-07-17
- **Primary source URL:** https://claude.com/pricing

### Fact Sheet 2: Perplexity Pro
- **Product name:** Perplexity Pro
- **Price:** **$20/month, or $200/year (~$16.67/month effective, ~17% savings)**
- **Free-tier limit:** Free plan gets unlimited "Quick Searches" but is capped at **5 Pro Searches per day**; Pro removes the Pro Search cap entirely.
- **verified_as_of:** 2026-07-17
- **Primary source URL:** https://www.perplexity.ai/hub/pricing
- **Verification note (per task instruction):** This figure was cross-checked against multiple independent secondary sources (techjacksolutions.com, felloai.com, finout.io, screenapp.io, costbench.com) and all agree on **$20/mo**. This should replace whatever "materially wrong" Perplexity Pro price appeared in prior content — I don't have visibility into what the old (wrong) figure was, so flag to doc_creation/marketing to also purge any stale figure from existing drafts.

### Fact Sheet 3: Cursor
- **Product name:** Cursor (code editor)
- **Price:** Hobby (free) $0; Pro $20/month; Pro+ $60/month; Ultra $200/month
- **Free-tier limit:** Cursor's own pricing page states only "Limited Agent requests" and "Limited Tab completions" for the Hobby plan — **no official numeric cap is published**. Some third-party aggregators cite ~2,000 Tab completions/month and ~50 Agent requests/month, but these are explicitly unofficial community estimates, not Cursor's own figures. **Do not cite a specific number for Cursor's free tier without labeling it as unofficial/community-sourced.**
- **verified_as_of:** 2026-07-17
- **Primary source URL:** https://cursor.com/pricing
- **⚠️ Flag:** Cursor also switched from a "500 fast requests/month" model to a dollar-denominated credit pool on 2025-06-16 (Pro's $20 subscription = $20 of credit pool; Auto mode is unlimited and doesn't burn credits). Any older draft content citing "500 requests" for Cursor Pro is now stale.

### Fact Sheet 4: GitHub Copilot
- **Product name:** GitHub Copilot (Free / Pro / Pro+ / Business / Enterprise)
- **Price:** Free $0; Pro $10/month; Pro+ $39/month; Business/Enterprise tiers priced separately (per-seat, not consumer-relevant)
- **Free-tier limit:** Free plan includes **2,000 code completions/month** and **50 chat requests/month** (including Copilot Edits), limited to auto-selected models only.
- **verified_as_of:** 2026-07-17
- **Primary source URL:** https://github.com/features/copilot/plans
- **⚠️ Flag:** GitHub moved all Copilot plans to usage-based "AI Credits" billing on 2026-06-01 (1 credit = $0.01). The 2,000-completions/50-chat-requests figures above are the commonly cited Free-plan numbers, but I could not confirm from search snippets whether the Free plan's AI Credit allowance under the new system is stated separately from these completion/chat counts — spot-check the live docs page (docs.github.com/en/copilot/concepts/billing/individual-plans) before quoting in final content.

## Assumptions
- "Claude (consumer plans)" is scoped to Free/Pro/Max only, excluding Team/Enterprise, per the task's framing as individual AI-writing tools.
- Treating Cursor's "Hobby" plan as the free tier referenced by the task (Cursor doesn't use the word "free" as a plan name, but Hobby is $0).

## Hypotheses
- The prior "materially wrong" Perplexity Pro price was likely either the old pre-2024 price point or a confusion with Perplexity Enterprise Pro ($40/seat/month) — not confirmed, since I have no record of what the flagged draft actually said.
- GitHub Copilot's Free-plan numeric limits (2,000 completions/50 chats) may be legacy figures still displayed alongside the new credit system rather than fully superseded by it — not confirmed without a direct page fetch.

## Recommendations
1. **Publish Perplexity Pro at $20/month ($200/year)** with confidence — this is consistently corroborated across five independent sources and matches the official pricing hub URL.
2. **Do not state a specific free-tier request/message count for Claude or Cursor** in content — neither vendor publishes one; use their own qualitative language ("limited," "5x more than free") instead of fabricating a number.
3. **Flag any existing draft citing "500 requests/month" for Cursor Pro as stale** — that model was replaced by the dollar-credit system in June 2025.
4. Before final publish, have a human directly load `github.com/features/copilot/plans` and `docs.github.com/en/copilot/concepts/billing/individual-plans` to confirm whether the 2,000-completions/50-chat free-tier figures still hold under the June 2026 credit-based billing system — I only had search-snippet access, not full page fetches, for any of the four products in this task.

**Named-product fact-sheet requirement:** Applies — this task explicitly names four products for downstream content; all four are covered above, each with price, free-tier limit (or explicit note that none is published), `verified_as_of` date, and source URL.

---

Per the role's read-only contract, I have not written this to any file — the execution adapter is responsible for persisting it to `system/runtime/business_agents/text_syndicate/market_research/{task_id}/latest.{json,md}`.

