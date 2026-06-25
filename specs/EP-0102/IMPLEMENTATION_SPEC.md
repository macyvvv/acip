# EP-0102 Implementation Spec

## Conclusion

Implement a repository-native Codex Development Pipeline so future EPs are specified by ChatGPT and implemented by Codex.

## Target Flow

Human -> ChatGPT spec -> Codex implementation -> Validation -> Commit -> ChatGPT review

## Scope

- Spec templates
- Codex prompts
- Implementation rules
- Review rules
- Quality gate
- Codex execution runbook
- Spec scaffolding script
- Spec validation script
- EP-0102 validation script
- GitHub Actions workflow
- README

## Out of Scope

- Runtime external execution
- Platform API mutation
- Auto posting
- Secret use
- Approval bypass
- New framework adoption
- Broad unrelated refactor

## Non-Negotiable Rules

- Repository overrides conversation.
- Codex must inspect current repository state before editing.
- Codex must implement minimal necessary diff.
- Codex must not delete existing implementation files unless explicitly required by the spec.
- Codex must run validation before commit.
