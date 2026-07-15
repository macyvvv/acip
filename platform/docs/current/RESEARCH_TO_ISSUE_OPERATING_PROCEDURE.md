# RESEARCH_TO_ISSUE_OPERATING_PROCEDURE

## Purpose
This SOP defines the canonical repository-native path from approved research output to manually created GitHub issues, then through the existing Repository OS execution loop.

The flow is deterministic. Chat context is not canonical.

## Canonical Flow
1. Create a research request artifact.
2. Generate research artifacts under `platform/system/runtime/research/`.
3. Produce a ranked opportunity list.
4. Convert the top opportunity into a research issue draft.
5. Register the draft in `issue_draft_registry.json`.
6. Build the review queue and record review decisions.
7. Promote approved drafts into `approved_issue_drafts.json`.
8. Promote approved drafts into `issue_creation_drafts.json`.
9. Manually create the GitHub issue from the draft body.
10. Run `platform/system/platform/scripts/run_until_idle.sh`.
11. Commit the completion marker only.
12. Clean up runtime observation artifacts if needed.
13. Push the completion-marker commit to `origin/main`.

## Exact Commands

### Read canonical issue creation drafts
```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("platform/system/runtime/research/issue_creation_drafts.json")
print(path.read_text(encoding="utf-8"))
PY
```

### Generate temporary title/body files for GitHub issue creation
```bash
python3 - <<'PY'
import json
from pathlib import Path

drafts = json.loads(Path("platform/system/runtime/research/issue_creation_drafts.json").read_text(encoding="utf-8"))
draft = drafts[0]
Path("/tmp/issue_title.txt").write_text(draft["title"] + "\n", encoding="utf-8")
Path("/tmp/issue_body.md").write_text(draft["issue_body_draft"], encoding="utf-8")
PY
```

### Manually create the GitHub issue
```bash
gh issue create \
  --title "$(cat /tmp/issue_title.txt)" \
  --body-file /tmp/issue_body.md
```

### Execute Repository OS after the issue is created
```bash
./platform/system/platform/scripts/run_until_idle.sh
```

### Commit completion marker only
```bash
git add platform/system/runtime/issues/completed/
git add platform/system/runtime/handoff/completion/latest.json
git add platform/system/runtime/handoff/completion/latest.md
git commit -m "chore: record issue completion marker"
```

### Push completion marker commit
```bash
git push origin main
```

### Runtime artifact cleanup
```bash
rm -f /tmp/issue_title.txt /tmp/issue_body.md
```

## Boundaries
- No automatic GitHub issue creation.
- No supervisor bypass.
- No execution gating changes.
- Runtime observation files are not canonical commit targets.
- Completion markers are canonical commit targets.

## Canonical Runtime Artifacts
- `platform/system/runtime/research/review_queue.json`
- `platform/system/runtime/research/review_decisions.json`
- `platform/system/runtime/research/approved_issue_drafts.json`
- `platform/system/runtime/research/issue_creation_drafts.json`
- `platform/system/runtime/issues/completed/`

## Verified Example
Issue `#36` is the first verified end-to-end example of this research-to-issue flow.

It is the reference case for:
- approved research review decision
- approved issue draft promotion
- issue-creation draft generation
- manual GitHub issue creation
- Repository OS execution handoff

## Operator Notes
- Treat `platform/system/runtime/research/*` as review and handoff state, not source-of-truth business records.
- Treat completion markers as the canonical record that an issue has finished execution.
- If runtime observation files drift, regenerate them deterministically instead of editing by hand.
