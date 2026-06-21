# GitHub Connector Usage

## Recommendation

ChatGPT should access GitHub through the GitHub Connector, not through a PAT.

## PAT / API Key

Keep API keys for:

- CI/CD
- local scripts
- future ACIP internal automation
- GitHub Actions secrets

Do not paste long-lived secrets into chat.
