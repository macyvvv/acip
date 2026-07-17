# ADR-0043: Add `epistemicsops`, a Cross-Cutting AI-Failure-Mode Auditor

## Status

Accepted by operator approval on 2026-07-17.

## Context

While preparing `text_syndicate`'s first real (non-dry-run) X posts, the
operator and the orchestrator caught four already-drafted posts and a
note.com article asserting fabricated first-person experience as fact --
invented testing timelines ("I tested 6 AI tools for 30 days"), invented
past actions ("I cancelled Notion AI after 3 months"), and invented numeric
grading (`Execution: 8/10`) presented as the account's own hands-on
testing, none of which had actually happened. `marketingops` confirmed this
was a real platform-policy risk (X bars claiming behavior you didn't
actually do); `legalops` confirmed it was an independent 景品表示法
優良誤認/FTC fake-testimonial compliance risk that a disclosure tag alone
does not cure.

This was caught by the orchestrator reading the actual draft text before
finalizing it, not by any dedicated role. The failure mode -- an LLM
generating fluent, specific-sounding, testimonial-shaped content that
reads as genuine lived experience but isn't -- is not unique to this one
incident. It is a structural property of how these models generate text
(optimizing for plausibility, not for truthful provenance), and nothing in
the current 25-role interactive layer has this as its explicit job. The
existing `*-research` roles (`market-research`, `legal-research`,
`business-strategy`, `ux-research`) are scoped to producing findings, not
to auditing whether findings (their own or another role's) reflect a
category error between "plausible" and "actually true/actually happened."

The operator separately asked for "a meta perspective that understands
what AI cannot do, and works to overcome it" -- explicitly framed as
understanding AI-ness vs. human-ness, at a level bundling/overseeing the
research-shaped roles.

## Decision

Add one new interactive Ops role: `epistemicsops`.

- **Position**: cross-cutting, like `secops` -- no role reports to it in
  the sequencing sense, but it can flag any role's output, with particular
  standing focus on the four `*-research` roles and any role producing
  first-person/testimonial-shaped or numerically-specific content
  (`marketing`, `doc-creation`).
- **Job**: review content and findings for AI-typical failure modes that
  are orthogonal to factual correctness review (which `dataops`/`secops`/
  domain Ops already cover) -- specifically: fabricated first-person
  experience presented as fact, unfounded specificity (plausible-sounding
  numbers/scores with no real source), overconfidence not warranted by the
  evidence actually gathered, self-referential agreement (one AI-generated
  finding "confirmed" by another AI-generated review with no independent
  grounding), and the general gap between what a model can *generate*
  fluently and what it can *know* to be true.
- **Not**: a fact-checker for domain-specific claims (that stays with
  `dataops`/`legalops`/`secops`/the relevant Ops), and not a replacement
  for the human judgment call on what to publish -- it flags, the operator
  and orchestrator decide.
- Update `opsboard` from nine to ten Ops.

Human retains final judgment on what gets published; `epistemicsops`
produces findings and flags, not authorization.

## Execution Authority

`epistemicsops` is a `.claude/agents/` interactive-session role only, per
the same pattern ADR-0041 established. It is not added to
`platform/system/core/agent_role_registry.py`, generated registry JSON,
pre-approval policies, schedules, or unattended execution. Adding an
unattended-registry counterpart requires a separate ADR, output contract,
and policy review, per ADR-0039's dual-authority rule.

## Boundaries

- `epistemicsops` flags; it does not correct content itself, and it does
  not gate publication -- that remains the operator's and orchestrator's
  call, same as any other Ops advisory role.
- Does not duplicate `secops` (security/credential/dependency surface),
  `legalops` (regulatory/contractual risk), or `dataops` (schema/pipeline
  integrity) -- those stay the authority on their own domains even when a
  finding also happens to be an AI-fabrication case (as this incident was,
  simultaneously a platform-policy, legal, and epistemic problem; each Ops
  role covers its own facet, `epistemicsops` covers the fabrication-as-
  fabrication facet specifically).
- Does not replace the orchestrator's own read-before-finalize discipline
  (per the new `running-business-agent-tasks` skill) -- it is a second,
  specialized check, not the only check.

## Consequences

Benefits:

- The failure mode that actually occurred this session (caught by luck of
  the orchestrator reading raw drafts, not by design) now has a named,
  invocable owner.
- `*-research` roles gain a standing, independent-of-self reviewer for
  their own tendency to overstate confidence or specificity.
- Names a real, durable concern (per CORE_PRINCIPLES #9) rather than a
  one-off "don't fabricate testimonials" rule that would go stale the
  moment the next failure mode looks slightly different.

Costs:

- An eleventh Ops role definition (ten Ops + fifteen specialists +
  opsboard = 26 roles) to keep coherent.
- Cross-cutting scope risks overlap-confusion with `secops` if not kept
  disciplined to its specific lane (epistemic/fabrication, not
  security/legal/data-integrity).

## Rejected Alternatives

- Fold this into `secops`'s existing cross-cutting mandate: rejected --
  `secops`'s lane (credentials, dependencies, external-facing surfaces) is
  a different, already-coherent scope; stretching it to cover content
  epistemics would blur both.
- Fold this into each `*-research` role's own self-critique step:
  rejected -- the whole problem is that a role cannot reliably audit its
  own fabrication tendency from inside the same generation process;
  independent review is the point.
- Skip a dedicated role and rely on the orchestrator alone: rejected --
  this session's incident was caught, but by chance (reading raw drafts
  before finalizing), not by a systematic check; a named role makes the
  check repeatable and invocable on demand rather than incidental.

## Validation

- `epistemicsops` has a unique frontmatter name and an explicit
  cross-cutting (not managed-by/manages) reporting line, matching
  `secops`'s existing pattern.
- `opsboard` recognizes ten Ops.
- Automated registry remains unchanged (interactive-only, per ADR-0039).
