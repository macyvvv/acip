# 049 Secret Boundary Policy

## Conclusion

Secrets must never be committed or exposed through prompts, logs, issues, PRs, or generated files.

## Secrets Include

- API keys
- PATs
- OAuth tokens
- cookies
- passwords
- session tokens
- private credentials

## Rule

Use GitHub Secrets, local `.env`, or approved secret manager.
