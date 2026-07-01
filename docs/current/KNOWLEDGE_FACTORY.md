# KNOWLEDGE_FACTORY

## Mission
Convert chat logs into canonical repository knowledge assets.

## Input
- `inbox/chat_logs/*.md`
- `inbox/chat_logs/*.txt`

## Output
- `knowledge/dashboard.md`
- `knowledge/current_state.md`
- `knowledge/ideas.md`
- `knowledge/decision_log.md`
- `knowledge/glossary.md`
- `knowledge/knowledge_graph.md`
- `knowledge/parking_lot.md`

## Workflow
1. Drop raw logs into `inbox/chat_logs/`
2. Run `python scripts/extract_knowledge.py`
3. Review diffs
4. Commit only reviewed knowledge updates

## Boundaries
- No auto-merge.
- No external mutation.
- No architecture rewrite.
