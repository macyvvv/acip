# platform/basis/README

`platform/basis/` is ACIP's policy corpus — the record of why the repository is
governed the way it is. As of a full governance-layer review
(`platform/adr/ADR-0037-governance-layer-overhaul.md`), this directory holds only
what's still current:

- **[CORE_PRINCIPLES.md](CORE_PRINCIPLES.md)** — the compact, current record.
  9 principles, each traced to either real enforcing code or a genuinely
  durable concern. Read this first.
- **[057_boundary_validation_policy.md](057_boundary_validation_policy.md)**
  — kept standalone; maps to real, distinct enforcement
  (`platform/system/platform/scripts/selftest/check_boundaries.py`, wired into
  `boundary-validation.yml`).
- **[REPOSITORY_CONVENTIONS.md](REPOSITORY_CONVENTIONS.md)** — kept
  standalone; actively used naming-convention reference.

The other 43 files that used to live here were archived in one pass —
almost all of them were pure prose with no enforcing code behind them, and
several restated the identical concern in independently-drifting copies.
See **[platform/archive/basis_corpus_2026/README.md](../platform/archive/basis_corpus_2026/README.md)**
for the full file-by-file mapping of what was archived and where its real
content lives now (folded into a `CORE_PRINCIPLES.md` principle, superseded
by real code, or confirmed to have never been built beyond a stub).

An earlier, smaller archival pass exists at
[platform/archive/basis_skeleton/](../platform/archive/basis_skeleton/README.md) (7 early
placeholder-pass files, superseded before this review even started).

## Reading this corpus going forward

- If you're about to add a new rule anywhere in this repo, read
  `CORE_PRINCIPLES.md` §9 first: name the real underlying concern (cost,
  irreversibility, determinism, secrets), not a bare absolute ban. This is
  the direct, durable fix for the incident that triggered the 2026-07
  governance review.
- Before adding a new policy doc, check whether `CORE_PRINCIPLES.md` or an
  existing script already covers it — this repo has a duplication problem,
  and this exact directory is where that problem was worst.
- If you add a new policy that's genuinely load-bearing and doesn't fit
  `CORE_PRINCIPLES.md`'s scope, add it as its own file here and link it
  from this index in the same PR — an unlinked `platform/basis/` file is exactly
  the problem this index exists to fix.
