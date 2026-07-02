# Production Pipeline

## Flow

ChatGPT → Script  
Codex → Prompt  
GitHub Actions → API call  
Video API (Runway etc.) → Output

## Storage

- All outputs are stored in `CONTENT/`
- Inputs remain in structured spec files
- Pipeline artifacts must remain reproducible

## Control Rules

- Do not mix spec creation and content rendering
- Do not skip reviewable artifacts
- Do not hide source inputs

