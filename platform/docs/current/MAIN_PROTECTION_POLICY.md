# MAIN_PROTECTION_POLICY

## Policy
- Direct push to `main` is prohibited.
- All changes must flow through a feature branch and pull request.
- `AGENTS.md` policy is necessary but not sufficient; technical enforcement is required.

## Required Local Controls
- A pre-push guard must block pushes when the current branch is `main`.
- A repository-contained hook template or installer must make the guard easy to activate.
- Exact activation command: `bash platform/system/scripts/git/install_hooks.sh`
- Expected block message on `main`: `Blocked: direct push to main is prohibited. Switch to a feature branch and open a pull request.`
- Expected allow behavior on feature branches: `Push allowed from branch: <branch-name>`

## GitHub-side Controls (available, but not currently configured)
- **Corrected 2026-07-17**: this repo is actually **public** (verified via
  `gh api repos/macyvvv/acip` -> `private: false`), not private as this
  document previously claimed. GitHub provides native branch protection
  for free on public repos regardless of plan, so the "this plan doesn't
  support it" reasoning that used to justify skipping GitHub-side
  protection is factually wrong -- protection is available today and
  simply has not been turned on (confirmed via
  `gh api repos/macyvvv/acip/branches/main/protection` -> `404 Branch not
  protected`). Whether to enable it is an open operator decision, not a
  platform limitation; not enabled as of this writing.
- Native GitHub branch protection on `main` (require PRs before merge,
  disable direct pushes, require status checks) remains the ideal remote
  backstop over the current local-only enforcement below. Enabling it is
  tracked as a follow-up decision, not done in this pass.
- Until it is enabled, there is no remote enforcement layer. The real
  protection today is entirely the local pre-push hook below, plus
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
  CI for direct-push violations, and native GitHub branch protection is
  available on this (public) repo but not yet configured (see above).
  Documentation alone is not sufficient -- this gap is named explicitly
  here rather than papered over, so a future reader doesn't assume a
  remote backstop exists that doesn't. A CI job that audits `main`'s
  history after the fact would be a real, buildable partial substitute if
  this gap ever needs closing further; not built today.
