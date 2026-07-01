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

## Required GitHub Controls
- Branch protection on `main` must require pull requests before merge.
- Direct pushes to `main` should be disabled where available.
- Optional required status checks should be enabled where available.

## Operator Checklist
1. Create a feature branch.
2. Commit on the feature branch.
3. Push the feature branch.
4. Open a pull request.
5. Merge only through review flow.

## Enforcement Boundary
- This policy is enforced locally by hook/script checks and remotely by GitHub branch protection.
- Documentation alone is not sufficient.
