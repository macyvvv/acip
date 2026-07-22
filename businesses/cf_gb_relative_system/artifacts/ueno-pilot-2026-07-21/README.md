# Ueno station collection pilot attempt — 2026-07-21

## Objective

Operator requested a small trial of real store-artifact collection scoped
to the Ueno station area, as a first real exercise of the
`schemas/store-artifact.json` / `artifacts/S-011/source-register.json`
foundation, ahead of any formal OUTCOME_BACKLOG.md Gate 1/2 area decision.

## Outcome: 0 store-artifact records created

No `data/stores/*.json`-shaped record was produced. This was a deliberate
stop, not a failure to find candidates -- see below.

## What was tried

1. Web search for `上野 コンセプトカフェ 店舗` and `上野 ガールズバー 店舗`.
   Results were almost entirely third-party multi-store aggregator/directory
   sites (con-ca.jp, caba2.net, concafechan.com, moe-navi.jp, gb-walker.jp,
   concafe-life.com, lightbaito.com, concafe-theatlas.com,
   girlsbar-station.com, town-night.jp, gurume-repo.com, nights.fun,
   centrodeartecanario.com), structurally the same kind of compiled listing
   as the 4 sources already denied in `source-register.json`
   (pokepara.jp, moe-sta.com, con-cafe.jp, caferun.jp).
2. Per `source-register.json`'s existing rules, aggregator content was not
   used as a source of record. Only 3 apparent first-party (official)
   sources were found among the search results: a Strikingly-hosted site
   (esora), a lit.link page (のわ), and an X/Twitter profile (のわ).
3. Direct fetch was attempted against all 3 to verify facts firsthand.
   **All 3 returned HTTP 403 Forbidden.**

## Follow-up: reconsidering aggregator use

Given the 403 wall, the operator asked whether aggregator sites *other
than* the originally-named 4 could be used instead. LegalOps was
re-consulted (interactive session, 2026-07-21) and concluded:

- **No principled basis to differentiate.** The original deny reasoning is
  structural (compiled multi-store listings likely carry database-right /
  編集著作物 protection beyond the underlying facts), not tied to the 4
  specific domain names Business Strategy.md happened to cite. The newly
  found aggregators are the same structural type and fall under the same
  reasoning.
- The only defensible aggregator use is as a **discovery lead** (learn a
  store plausibly exists, then verify independently via its own official
  site/SNS) -- functionally the same as the already-allowed
  `search-engine-discovery` entry. Storing address/hours/price text read
  directly from an aggregator page is not defensible.
- **The HTTP 403s are very likely an anti-bot/technical signal, not a
  legal-permission signal.** Widening source-register access would not
  have fixed them, and risks trading a real legal exposure for an
  unverified technical guess.
- Recommendation: hold `source-register.json` as-is. Treat the 403s as a
  separate access/tooling problem (different fetch method, or
  manual/human-assisted verification per `HUMAN_REPLACEMENT_MATRIX.md`'s
  未構築 store-verification-page path) rather than a legal-policy change.

## Decision

Operator paused the pilot here rather than loosening source rules or
fabricating unverified data. `source-register.json` and
`schemas/store-artifact.json` are unchanged by this pilot. No ADR needed
(no scope/architecture change was made) -- this is a evidence record of
an attempted-and-blocked collection pass, kept for traceability so a
future attempt doesn't silently repeat the same blocked path.

## Open follow-up (not decided here)

- Whether to pursue an alternate technical fetch approach for official
  small-business sites (untested against this class of 403).
- Whether manual/human-provided store facts (verification_method:
  `user-report` in `schemas/store-artifact.json`) are an acceptable
  interim path before a store-verification portal exists.
