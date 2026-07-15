# KNOWLEDGE_FACTORY

## Mission
Convert chat logs into canonical repository knowledge assets.

## Input
- `platform/inbox/chat_logs/*.md`
- `platform/inbox/chat_logs/*.txt`

## Output
- `platform/knowledge/dashboard.md`
- `platform/knowledge/current_state.md`
- `platform/knowledge/ideas.md`
- `platform/knowledge/decision_log.md`
- `platform/knowledge/glossary.md`
- `platform/knowledge/knowledge_graph.md`
- `platform/knowledge/parking_lot.md`

## Workflow
1. Drop raw logs into `platform/inbox/chat_logs/`
2. Run `python platform/scripts/extract_knowledge.py`
3. Review diffs
4. Commit only reviewed knowledge updates

## Boundaries
- No auto-merge.
- No external mutation.
- No architecture rewrite.
