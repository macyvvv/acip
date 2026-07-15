# MAIN_PROTECTION_POLICY

## Policy
- Direct push to `main` is prohibited.
- All changes must flow through a feature branch and pull request.
- `AGENTS.md` policy is necessary but not sufficient; technical enforcement is required.

## Required Local Controls
- A pre-push guard must block pushes when the current branch is `main`.
- A repository-contained hook template or installer must make the guard easy to activate.
- Exact activation command: `bash system/scripts/git/install_hooks.sh`
- Expected block message on `main`: `Blocked: direct push to main is prohibited. Switch to a feature branch and open a pull request.`
- Expected allow behavior on feature branches: `Push allowed from branch: <branch-name>`

## GitHub-side Controls (not currently configured)
- Native GitHub branch protection on `main` is the ideal remote backstop
  (require PRs before merge, disable direct pushes, require status checks)
  -- but this repo is private on GitHub's free plan, and native branch
  protection is not available on that plan (same constraint that blocks
  GitHub Pages for this repo). Nothing in this repo's config claims
  otherwise; verify current availability before assuming this has changed.
- Until/unless the plan changes, there is no remote enforcement layer.
  The real protection today is entirely the local pre-push hook below, plus
  PR-based workflow discipline as a human/agent convention.

## Operator Checklist
1. Create a feature branch.
2. Commit on the feature branch.
3. Push the feature branch.
4. Open a pull request.
5. Merge only through review flow.

## Enforcement Boundary
- **Real enforcement today**: the local pre-push hook (see "Required Local
  Controls" above), and only for clones where an operator or agent has
  actually run the installer -- it lives in `.git/hooks/`, which git never
  tracks, so it is opt-in per clone, not automatic.
- **Not enforced**: nothing currently re-checks `main`'s commit history in
  CI for direct-push violations, and (per the note above) there is no
  GitHub-side branch protection configured or available on this plan.
  Documentation alone is not sufficient -- this gap is named explicitly
  here rather than papered over, so a future reader doesn't assume a
  remote backstop exists that doesn't. A CI job that audits `main`'s
  history after the fact would be a real, buildable partial substitute if
  this gap ever needs closing further; not built today.
