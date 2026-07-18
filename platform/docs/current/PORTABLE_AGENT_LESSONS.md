# Portable Agent Lessons

A deliberately repo-independent record of operating lessons learned while
running Claude Code agents/subagents/skills. Every entry here is written to
make sense with **zero context from this specific repository** — no file
paths, no business/product names, no assumptions about this project's own
structure. The intent is that this file (or its individual entries) can be
copied into a different project's own `CLAUDE.md` or skills directory as a
starting seed, not just read here.

Entries are proposed by the `trainerops` role and added only after human
confirmation that they're genuinely portable (see `platform/adr/
ADR-0044-trainerops-and-portable-lessons.md`). Keep entries short, name the
concern plainly, and state why it's true rather than just asserting it.

## Agent architecture

- **Subagents cannot invoke other subagents.** If you design a hierarchy
  where a "coordinator" role is meant to sequence and dispatch several
  "specialist" roles, the coordinator cannot actually call them itself when
  running as a subagent — only the top-level orchestrator session can invoke
  subagents. Write coordinator-role instructions to plan sequencing and
  verify output, not to claim they "manage" or "invoke" anything directly —
  otherwise the role's own documentation will overstate what it can do, and
  it may confidently claim to have done something it structurally cannot.

- **A subagent's tool list is a hard boundary, not a suggestion.** A role
  scoped to read-only tools (e.g. Read/Grep/Glob) genuinely cannot write
  files or run scripts, even if its instructions describe a job that sounds
  like it should. When a role's job requires producing a real, persisted
  artifact (not just an in-conversation opinion), route that through
  whatever your project's actual execution pipeline is — don't let an
  advisory-only role's draft output get treated as if it went through real
  execution.

## Data pipelines with a "source of truth vs. derived copy" split

- If a pipeline has a canonical source (a database, a config-generation
  step) and one or more derived/exported copies (JSON files, generated
  docs, a deployable bundle), **editing a derived copy directly and then
  re-running the generation step will silently overwrite your edit** with
  whatever the stale canonical source still says — because the canonical
  source was never told about your edit. This fails silently: the
  generation step exits cleanly, prints success, and the edit is simply
  gone.
  - The fix is always the same shape: push your edit *into* the canonical
    source first (an explicit "import" step), *then* run generation.
  - After making an edit like this, verify it actually survived by
    re-reading the file — don't trust a clean exit code alone.
  - This is worth writing down as an explicit skill/runbook the moment it's
    hit even once, because the failure mode looks like success and is easy
    to repeat without realizing it happened the first time.

## AI-generated content and fabrication risk

- **A language model can generate fluent first-person "I did X" claims with
  zero relationship to anything that actually happened.** Before publishing
  any AI-generated content that asserts personal experience, a specific
  timeline ("I tested this for 30 days"), or a specific numeric
  judgment/score presented as the result of real evaluation, read the raw
  draft text yourself and check: did this actually happen, or does it just
  read like it did? Plausibility is not evidence of truth for model output.
- **A disclosure/labeling requirement does not cure a fabricated claim.**
  Marking fabricated content as sponsored/an ad discloses that a claim is
  promotional; it does not make a false claim true. These are two
  independent problems (is this disclosed as advertising vs. is this
  actually true) and need two independent fixes.
- **Independent review needs an actually-independent check, not another AI
  pass over the same generation.** One AI-generated finding "confirmed" by
  another AI-generated review, where the second pass never checked a
  primary source, produces the appearance of corroboration without the
  substance. If you want real verification, ground at least one leg of it
  in something outside the generation process itself (a primary source, a
  human read, a real test run).

## Working in a shared or automated environment

- **Before running any tooling that requires a clean working tree, check
  what's actually dirty before clearing it.** In an environment where other
  automated processes might be concurrently writing to the same working
  directory, an unfamiliar uncommitted file is not automatically safe to
  discard or force past — it may be another process's in-progress work.
  Isolate your own changes (a fresh branch, staging only the files you
  actually authored) rather than forcing a global clean state.
- **Reserved/special shell variable names can silently break scripts.**
  A variable named `status` (or similar shell-builtin-adjacent names) can
  be read-only in some shells (e.g. zsh), causing an assignment to fail
  with an error that's easy to misread as an unrelated problem. When a
  small polling/monitoring script fails immediately with no obvious cause,
  check for a variable-naming collision with the shell itself before
  assuming the logic is wrong.

## Governance/documentation debt

- **Unenforced "policy" documentation accumulates independently of any
  single mistake.** A document or convention that once had a real reason to
  exist can silently stop being read or executed by anything, while
  continuing to assert things that are no longer true (a stale path, an
  outdated constraint, a plan assumption nobody re-verified). This isn't
  a one-time cleanup problem — it recurs. A periodic, owned "does this
  still match reality, and is anything actually still reading this?" pass
  is the durable fix, not a single audit.
- **When a role/agent definition claims a capability, spot-check whether
  it's still literally true**, especially after any change to what tools
  or invocation mechanism that role actually has access to. Role
  documentation drifts from role reality the same way any other
  documentation does.

## Image-generation prompt engineering (SDXL/CLIP-family models)

- **These models don't parse grammatical negation.** Writing "NOT a tank
  top" or "NOT off-shoulder" inside a *positive* prompt tends to reinforce
  the excluded concept rather than remove it -- the negation word itself
  carries little to no weight in the text encoder's embedding. Put every
  concept you want absent from the output only in a dedicated negative
  prompt, never as a negation clause in the positive one. Confirmed by a
  real failure: a positive prompt accumulating several "NOT X" clauses
  produced a broken, unusable generation, not just a subtle miss.
- **There is a hard effective prompt-attention budget, roughly 75 tokens.**
  Past that point, later tokens get diluted or dropped, and there is no
  reliable reordering or trimming trick that reliably preserves everything
  once a prompt is over budget -- confirmed across four consecutive
  attempts that each combined multiple competing requirements (character
  identity plus a scene) in one prompt, where each attempt sacrificed a
  *different* required element depending on ordering. When one prompt
  cannot fit everything it needs to carry reliably, don't assume adding
  more descriptive detail is free, and consider whether the task should be
  split into multiple generation passes instead of one prompt trying to
  do everything.
