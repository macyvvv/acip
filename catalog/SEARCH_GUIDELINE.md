# Search Guideline

## Conclusion

Before creating a new asset, ACIP must search existing assets and indexes to avoid duplication.

## Search Order

1. `registry/ASSET_REGISTRY.md`
2. type-specific indexes
3. `catalog/`
4. `basis/`
5. `docs/`
6. `adr/`
7. `wbs/`
8. full repository search

## Search Keys

Search by:

- asset_id
- title
- category
- tag
- source_path
- related ADR
- related WBS
- source asset id
- lifecycle status
- risk level
- value category

## Rules

- Repository overrides conversation.
- Chat memory is not a search substitute.
- Duplicate candidates should be merged, linked, or explicitly rejected.
- Human should not perform mechanical search if ChatGPT, Codex, or future automation can do it.
