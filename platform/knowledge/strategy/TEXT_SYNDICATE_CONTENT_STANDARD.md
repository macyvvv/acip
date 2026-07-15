# TEXT_SYNDICATE_CONTENT_STANDARD

Status

Canonical (business-specific concretization of `knowledge/strategy/PRODUCT_DEFINITION.md`'s
QOL mission, for the `text_syndicate` business specifically)

---

# Why this exists

On 2026-07-15 a DataOps/MarketingOps audit of already-finalized, human-approved
X drafts for `text_syndicate` found two problems:

1. Most published-ready posts were pure engagement bait ("which AI tool have
   you kept using past week 2?") with zero decision-usable content for a
   real reader.
2. Some drafts contained fabricated specific facts about products no
   `market_research` artifact had ever covered -- a materially wrong
   Perplexity Pro price and invented "70%/50%" savings percentages, both
   hand-caught by a human before publication, with nothing in the pipeline
   itself preventing it.

Both violate this repo's own stated mission
(`knowledge/strategy/PRODUCT_DEFINITION.md`: "QOL is the product"):
engagement-bait content doesn't save a reader anything, and fabricated
facts actively cost a reader time or money if trusted. This document
translates that abstract mission into concrete, checkable criteria
specifically for `text_syndicate`'s content.

---

# What counts as valuable content for text_syndicate

A post passes this bar only if a reader who trusts it and acts on it comes
out ahead -- in time, money, or effort -- not merely "engaged."

1. **Names a real, specific decision the reader can make.** Which of N
   tools to use, whether to upgrade a tier, which limit will actually bite
   them at their usage level -- not a bare question with no informational
   payoff.
2. **Every specific figure is sourced.** Verified via
   `system/scripts/dataops/verify_sourced_facts.py` against a
   `market_research` fact sheet with a `verified_as_of` date. Never a
   number from memory/training data.
3. **States uncertainty honestly.** If research found conflicting or
   unverified information, the post says so rather than asserting false
   precision.
4. **Passes `doc_creation`'s existing self-critique bar** (specificity,
   payoff completeness, experience honesty, template-detection, fact
   provenance) -- this standard sits above that bar, it doesn't replace it.

# What does NOT pass, even if technically postable

- A generic "which tool do you use?" engagement question with no named
  tool, fact, or decision payoff.
- Any specific price/limit/percentage about a named product without a
  sourced fact sheet behind it.
- Content whose only real function is proving the pipeline can post --
  this was the actual state of 4 of the 6 items finalized before this
  audit.

---

# How this gates the pipeline

- `market_research` must produce named-product fact sheets before
  `marketing`/`doc_creation` name those products (see
  `system/agent_runtime/role_prompts/market_research.md` and
  `.claude/agents/market-research.md`, both updated 2026-07-15).
- `doc_creation`/`marketing` may not introduce unsourced figures (see the
  same date's updates to `system/agent_runtime/role_prompts/doc_creation.md`
  and `.claude/agents/doc-creation.md`, plus
  `system/scripts/dataops/verify_sourced_facts.py`).
- A human finalizing content via `system/scripts/publishing/finalize_content.py`
  should check a draft against this standard before finalizing. This
  standard is a checklist for that human judgment, not a claim that
  everything here is machine-enforced end-to-end -- only the sourced-figure
  check is currently mechanical (item 2). Items 1, 3, and 4 still rely on a
  human or the model's own self-critique pass reading the actual content.

---

# Review cadence

Revisit this standard when `pdca` produces its first real recommendation
informed by actual reader engagement data (not just the `git_activity`
proxy), or when the operator's own read of published content suggests the
bar needs to move.
