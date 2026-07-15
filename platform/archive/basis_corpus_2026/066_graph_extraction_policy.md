# 066 Graph Extraction Policy

## Conclusion

Graph extraction must be deterministic, reproducible, and safe.

## Extraction Sources

- markdown H1
- file path
- ADR number
- WBS number
- markdown links
- workflow script references
- registry rows
- explicit relation tables
- frontmatter when available

## Rules

- Extraction must not mutate source files.
- Extraction must not call external APIs.
- Extraction must not require secrets.
- Extraction may write derived artifacts under `graph/`.
- Repository source files override derived graph artifacts.
